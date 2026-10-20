using AudioStar.Core;
using AudioStar.Library.Data;
using AudioStar.Library.Dlna;
using AudioStar.Library.HomeShare;
using AudioStar.Library.Media;
using AudioStar.Library.Music;
using AudioStar.Library.Recent;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Hosting;

namespace AudioStar.Library;

public static class LibraryServiceCollectionExtensions
{
    public static IServiceCollection AddAudioStarLibrary(this IServiceCollection services)
    {
        services.AddSingleton(_ => new Database(AppPaths.DatabaseFile));
        services.AddSingleton<TrackStore>();
        services.AddSingleton<ITrackCatalog>(sp => sp.GetRequiredService<TrackStore>());
        services.AddSingleton<CoverService>();
        services.AddSingleton<StreamEndpoint>();
        services.AddSingleton<DlnaHttp>();
        services.AddSingleton<MediaServer>();
        services.AddSingleton<IMediaServer>(sp => sp.GetRequiredService<MediaServer>());
        services.AddSingleton<MusicLibrary>();
        services.AddSingleton<IMusicLibrary>(sp => sp.GetRequiredService<MusicLibrary>());
        services.AddSingleton<IDlnaServer, DlnaServer>();
        services.AddSingleton<IHomeShareBrowser, HomeShareBrowser>();
        services.AddSingleton<IRecentlyPlayed, RecentlyPlayed>();
        services.AddSingleton<IHostedService, LibraryHostedService>();
        return services;
    }
}
