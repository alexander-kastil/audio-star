using AudioStar.Core;
using AudioStar.Library.Data;
using AudioStar.Library.Music;

namespace AudioStar.Library.Dlna;

internal sealed record BrowseResult(IReadOnlyList<DidlObject> Objects, int TotalMatches)
{
    public int NumberReturned => Objects.Count;
}

internal sealed class DlnaFaultException(int code, string description) : Exception(description)
{
    public int Code { get; } = code;
}

internal static class Paging
{
    public static IReadOnlyList<T> Slice<T>(IReadOnlyList<T> all, int start, int count)
    {
        var from = Math.Clamp(start, 0, all.Count);
        var take = count <= 0 ? all.Count - from : Math.Min(count, all.Count - from);
        return all.Skip(from).Take(take).ToList();
    }
}

internal sealed class DlnaBrowser(ITrackCatalog catalog, Func<IReadOnlyList<string>> folders)
{
    public const string RootId = "0";
    public const string AllId = "all";
    public const string AlbumsId = "albums";
    public const string ArtistsId = "artists";
    public const string GenresId = "genres";
    public const string FoldersId = "folders";

    private const char Separator = '\u001f';

    public async Task<BrowseResult> BrowseAsync(string objectId, bool metadataOnly, int start, int count, Uri baseUri, string rootTitle, CancellationToken cancellationToken)
    {
        if (metadataOnly)
        {
            var self = await DescribeAsync(objectId, baseUri, rootTitle, cancellationToken);
            return new BrowseResult([self], 1);
        }
        return await ChildrenAsync(objectId, start, count, baseUri, cancellationToken);
    }

    public async Task<BrowseResult> SearchAsync(string text, int start, int count, Uri baseUri, CancellationToken cancellationToken)
    {
        var query = new LibraryQuery(Search: text, Limit: 0);
        var tracks = await catalog.GetTracksAsync(query, cancellationToken);
        var page = Paging.Slice(tracks, start, count);
        return new BrowseResult(page.Select(t => TrackObject(t, AllId, baseUri)).ToList(), tracks.Count);
    }

    private async Task<BrowseResult> ChildrenAsync(string objectId, int start, int count, Uri baseUri, CancellationToken cancellationToken)
    {
        switch (objectId)
        {
            case RootId:
                return Wrap(
                [
                    Container(AllId, RootId, "All tracks", null),
                    Container(AlbumsId, RootId, "Albums", null),
                    Container(ArtistsId, RootId, "Artists", null),
                    Container(GenresId, RootId, "Genres", null),
                    Container(FoldersId, RootId, "Folders", null)
                ], start, count);
            case AllId:
                {
                    var total = await catalog.CountTracksAsync(new LibraryQuery(Limit: 0), cancellationToken);
                    var limit = count <= 0 ? 0 : count;
                    var page = await catalog.GetTracksAsync(new LibraryQuery(Offset: Math.Max(0, start), Limit: limit), cancellationToken);
                    return new BrowseResult(page.Select(t => TrackObject(t, AllId, baseUri)).ToList(), total);
                }
            case AlbumsId:
                {
                    var albums = await catalog.GetAlbumsAsync(null, cancellationToken);
                    return Wrap(albums.Select(a => AlbumObject(a, baseUri)).ToList(), start, count);
                }
            case ArtistsId:
                {
                    var artists = await catalog.GetArtistsAsync(null, cancellationToken);
                    return Wrap(artists.Select(a => Container("ar:" + Pack(a.Name), ArtistsId, a.Name, a.TrackCount)).ToList(), start, count);
                }
            case GenresId:
                {
                    var genres = await catalog.GetGenresAsync(cancellationToken);
                    return Wrap(genres.Select(g => Container("ge:" + Pack(g.Name), GenresId, g.Name, g.TrackCount, DidlLite.GenreClass)).ToList(), start, count);
                }
            case FoldersId:
                return Wrap(folders().Select(f => FolderObject(f, FoldersId)).ToList(), start, count);
        }
        var (kind, parts) = Unpack(objectId);
        switch (kind)
        {
            case "al":
                return await TracksAsync(new LibraryQuery(Album: parts[0], Artist: parts.Length > 1 ? parts[1] : null, Limit: 0), objectId, start, count, baseUri, cancellationToken);
            case "ar":
                return await TracksAsync(new LibraryQuery(Artist: parts[0], Limit: 0), objectId, start, count, baseUri, cancellationToken);
            case "ge":
                return await TracksAsync(new LibraryQuery(Genre: parts[0], Limit: 0), objectId, start, count, baseUri, cancellationToken);
            case "fo":
                return await FolderChildrenAsync(parts[0], objectId, start, count, baseUri, cancellationToken);
            default:
                throw new DlnaFaultException(701, "No such object");
        }
    }

    private async Task<BrowseResult> TracksAsync(LibraryQuery query, string parentId, int start, int count, Uri baseUri, CancellationToken cancellationToken)
    {
        var tracks = await catalog.GetTracksAsync(query, cancellationToken);
        return Wrap(tracks.Select(t => TrackObject(t, parentId, baseUri)).ToList(), start, count);
    }

    private async Task<BrowseResult> FolderChildrenAsync(string directory, string parentId, int start, int count, Uri baseUri, CancellationToken cancellationToken)
    {
        var tracks = await catalog.GetTracksUnderAsync(directory, cancellationToken);
        var root = directory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        var subfolders = new SortedDictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var direct = new List<LibraryTrack>();
        foreach (var track in tracks)
        {
            var relative = track.Path[root.Length..];
            var separator = relative.IndexOfAny([Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar]);
            if (separator < 0)
            {
                direct.Add(track);
            }
            else
            {
                var name = relative[..separator];
                subfolders.TryAdd(name, root + name);
            }
        }
        var objects = subfolders.Values.Select(p => FolderObject(p, parentId)).Concat(direct.Select(t => TrackObject(t, parentId, baseUri))).ToList();
        return Wrap(objects, start, count);
    }

    private async Task<DidlObject> DescribeAsync(string objectId, Uri baseUri, string rootTitle, CancellationToken cancellationToken)
    {
        switch (objectId)
        {
            case RootId:
                return Container(RootId, "-1", rootTitle, 5);
            case AllId:
                return Container(AllId, RootId, "All tracks", null);
            case AlbumsId:
                return Container(AlbumsId, RootId, "Albums", null);
            case ArtistsId:
                return Container(ArtistsId, RootId, "Artists", null);
            case GenresId:
                return Container(GenresId, RootId, "Genres", null);
            case FoldersId:
                return Container(FoldersId, RootId, "Folders", null);
        }
        var (kind, parts) = Unpack(objectId);
        switch (kind)
        {
            case "tr" when long.TryParse(parts[0], out var id):
                var track = await catalog.GetTrackAsync(id, cancellationToken) ?? throw new DlnaFaultException(701, "No such object");
                return TrackObject(track, AllId, baseUri);
            case "al":
                return Container(objectId, AlbumsId, parts[0], null, DidlLite.AlbumClass);
            case "ar":
                return Container(objectId, ArtistsId, parts[0], null);
            case "ge":
                return Container(objectId, GenresId, parts[0], null, DidlLite.GenreClass);
            case "fo":
                return FolderObject(parts[0], FoldersId);
            default:
                throw new DlnaFaultException(701, "No such object");
        }
    }

    private static BrowseResult Wrap(IReadOnlyList<DidlObject> all, int start, int count) => new(Paging.Slice(all, start, count), all.Count);

    private static DidlObject Container(string id, string parentId, string title, int? childCount, string upnpClass = DidlLite.ContainerClass) =>
        new(id, parentId, title, true, upnpClass, childCount);

    private static DidlObject AlbumObject(LibraryAlbum album, Uri baseUri) =>
        new("al:" + Pack(album.Album, album.AlbumArtist), AlbumsId, album.Album, true, DidlLite.AlbumClass, album.TrackCount, album.AlbumArtist, Artwork: album.CoverTrackPath is null ? null : new Uri(baseUri, "media/cover/" + PathCodec.Encode(album.CoverTrackPath)));

    private static DidlObject FolderObject(string path, string parentId)
    {
        var trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var title = Path.GetFileName(trimmed);
        return Container("fo:" + Pack(path), parentId, title.Length == 0 ? trimmed : title, null, DidlLite.StorageFolderClass);
    }

    private static DidlObject TrackObject(LibraryTrack track, string parentId, Uri baseUri) =>
        new(
            "tr:" + track.Id,
            parentId,
            track.Title,
            false,
            DidlLite.TrackClass,
            Artist: track.Artist ?? track.AlbumArtist,
            Album: track.Album,
            TrackNumber: track.TrackNumber,
            Resource: new Uri(baseUri, "media/music/" + PathCodec.Encode(track.Path)),
            MimeType: AudioFormats.ContentTypeFor(track.Path),
            Artwork: track.HasCover ? new Uri(baseUri, "media/cover/" + PathCodec.Encode(track.Path)) : null,
            Duration: track.Duration > TimeSpan.Zero ? track.Duration : null);

    public static string Pack(params string[] parts) => PathCodec.Encode(string.Join(Separator, parts));

    private static (string Kind, string[] Parts) Unpack(string objectId)
    {
        var colon = objectId.IndexOf(':');
        if (colon < 0)
        {
            throw new DlnaFaultException(701, "No such object");
        }
        var kind = objectId[..colon];
        var payload = objectId[(colon + 1)..];
        if (kind == "tr")
        {
            return (kind, [payload]);
        }
        if (!PathCodec.TryDecode(payload, out var decoded))
        {
            throw new DlnaFaultException(701, "No such object");
        }
        return (kind, decoded.Split(Separator));
    }
}
