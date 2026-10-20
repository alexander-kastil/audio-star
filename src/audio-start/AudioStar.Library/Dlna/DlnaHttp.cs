using System.Text;
using System.Text.RegularExpressions;
using AudioStar.Core;
using AudioStar.Library.Data;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.Dlna;

internal static class DeviceIdentity
{
    public static string LoadOrCreateUdn(string path)
    {
        if (File.Exists(path))
        {
            var existing = File.ReadAllText(path).Trim();
            if (existing.StartsWith("uuid:", StringComparison.OrdinalIgnoreCase))
            {
                return existing;
            }
        }
        var udn = "uuid:" + Guid.NewGuid();
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path, udn);
        return udn;
    }
}

internal sealed partial class DlnaHttp(ITrackCatalog catalog, ISettingsStore settings, ILogger<DlnaHttp> logger)
{
    private const string XmlType = "text/xml; charset=\"utf-8\"";

    private readonly Lazy<string> _udn = new(() => DeviceIdentity.LoadOrCreateUdn(Path.Combine(AppPaths.DataDirectory, "dlna-uuid.txt")));
    private readonly DlnaBrowser _browser = new(catalog, () => settings.Current.MusicFolders.ToArray());

    public volatile bool Enabled;

    public string Udn => _udn.Value;

    public string FriendlyName => string.IsNullOrWhiteSpace(settings.Current.DlnaServerName) ? "Audio Star" : settings.Current.DlnaServerName;

    public void Map(IEndpointRouteBuilder app)
    {
        app.MapGet(DlnaDescriptions.DescriptionPath, (HttpContext context) => Guard(context, () => Results.Text(DlnaDescriptions.Device(FriendlyName, Udn), XmlType, Encoding.UTF8)));
        app.MapGet(DlnaDescriptions.ScpdPath, (HttpContext context) => Guard(context, () => Results.Text(DlnaDescriptions.ContentDirectoryScpd, XmlType, Encoding.UTF8)));
        Delegate control = ControlAsync;
        app.MapPost(DlnaDescriptions.ControlPath, control);
        app.MapMethods(DlnaDescriptions.EventPath, ["SUBSCRIBE", "UNSUBSCRIBE"], (HttpContext context) => Guard(context, () =>
        {
            context.Response.Headers["SID"] = "uuid:" + Guid.NewGuid();
            context.Response.Headers["TIMEOUT"] = "Second-1800";
            return Results.Ok();
        }));
    }

    private IResult Guard(HttpContext context, Func<IResult> result) => Enabled ? result() : Results.NotFound();

    private async Task<IResult> ControlAsync(HttpContext context)
    {
        if (!Enabled)
        {
            return Results.NotFound();
        }
        using var reader = new StreamReader(context.Request.Body, Encoding.UTF8);
        var request = Soap.ParseRequest(await reader.ReadToEndAsync(context.RequestAborted));
        if (request is null)
        {
            return Results.Text(Soap.Fault(401, "Invalid Action"), XmlType, Encoding.UTF8, StatusCodes.Status500InternalServerError);
        }
        context.Response.Headers["EXT"] = "";
        try
        {
            var values = await HandleAsync(request, new Uri($"{context.Request.Scheme}://{context.Request.Host}/"), context.RequestAborted);
            return Results.Text(Soap.Response(request.Action, Soap.ContentDirectoryType, values), XmlType, Encoding.UTF8);
        }
        catch (DlnaFaultException ex)
        {
            return Results.Text(Soap.Fault(ex.Code, ex.Message), XmlType, Encoding.UTF8, StatusCodes.Status500InternalServerError);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            logger.LogWarning(ex, "DLNA action {Action} failed", request.Action);
            return Results.Text(Soap.Fault(501, "Action Failed"), XmlType, Encoding.UTF8, StatusCodes.Status500InternalServerError);
        }
    }

    internal async Task<IReadOnlyList<KeyValuePair<string, string>>> HandleAsync(SoapRequest request, Uri baseUri, CancellationToken cancellationToken)
    {
        switch (request.Action)
        {
            case "Browse":
                {
                    var metadata = request.Get("BrowseFlag").Equals("BrowseMetadata", StringComparison.OrdinalIgnoreCase);
                    var result = await _browser.BrowseAsync(request.Get("ObjectID", DlnaBrowser.RootId), metadata, request.GetInt("StartingIndex"), request.GetInt("RequestedCount"), baseUri, FriendlyName, cancellationToken);
                    return BrowseValues(result);
                }
            case "Search":
                {
                    var result = await _browser.SearchAsync(ExtractSearchText(request.Get("SearchCriteria")), request.GetInt("StartingIndex"), request.GetInt("RequestedCount"), baseUri, cancellationToken);
                    return BrowseValues(result);
                }
            case "GetSortCapabilities":
                return [new("SortCaps", "")];
            case "GetSearchCapabilities":
                return [new("SearchCaps", "dc:title,upnp:artist,upnp:album")];
            case "GetSystemUpdateID":
                return [new("Id", "1")];
            default:
                throw new DlnaFaultException(401, "Invalid Action");
        }
    }

    internal static string ExtractSearchText(string criteria)
    {
        var match = SearchTextPattern().Match(criteria);
        return match.Success ? match.Groups[1].Value : "";
    }

    private static IReadOnlyList<KeyValuePair<string, string>> BrowseValues(BrowseResult result) =>
    [
        new("Result", DidlLite.Build(result.Objects)),
        new("NumberReturned", result.NumberReturned.ToString()),
        new("TotalMatches", result.TotalMatches.ToString()),
        new("UpdateID", "1")
    ];

    [GeneratedRegex("contains\\s+\"([^\"]*)\"", RegexOptions.IgnoreCase)]
    private static partial Regex SearchTextPattern();
}
