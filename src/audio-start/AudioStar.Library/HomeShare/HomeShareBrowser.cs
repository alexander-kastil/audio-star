using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Xml.Linq;
using AudioStar.Core;
using AudioStar.Library.Dlna;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.HomeShare;

internal sealed record DeviceDescription(string Udn, string FriendlyName, Uri ControlUri, string ServiceType);

internal static class DeviceDescriptionParser
{
    public static DeviceDescription? Parse(string xml, Uri location)
    {
        XDocument document;
        try
        {
            document = XDocument.Parse(xml);
        }
        catch (System.Xml.XmlException)
        {
            return null;
        }
        var device = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "device");
        if (device is null)
        {
            return null;
        }
        var udn = Child(device, "UDN");
        var name = Child(device, "friendlyName");
        var service = device.Descendants().FirstOrDefault(e => e.Name.LocalName == "service" && (Child(e, "serviceType") ?? "").StartsWith("urn:schemas-upnp-org:service:ContentDirectory:", StringComparison.OrdinalIgnoreCase));
        var control = service is null ? null : Child(service, "controlURL");
        if (udn is null || service is null || control is null)
        {
            return null;
        }
        var urlBase = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "URLBase")?.Value;
        var baseUri = Uri.TryCreate(urlBase, UriKind.Absolute, out var parsedBase) ? parsedBase : location;
        return new DeviceDescription(udn, string.IsNullOrWhiteSpace(name) ? udn : name, new Uri(baseUri, control), Child(service, "serviceType")!);
    }

    private static string? Child(XElement element, string localName) => element.Elements().FirstOrDefault(e => e.Name.LocalName == localName)?.Value.Trim();
}

internal sealed class HomeShareBrowser(DlnaHttp ownDevice, ILogger<HomeShareBrowser> logger) : IHomeShareBrowser, IAsyncDisposable
{
    private static readonly TimeSpan SearchInterval = TimeSpan.FromSeconds(60);
    private static readonly TimeSpan Retention = TimeSpan.FromMinutes(5);
    private const int PageSize = 100;

    private static readonly HttpClient Client = new() { Timeout = TimeSpan.FromSeconds(15) };

    private readonly object _lock = new();
    private readonly Dictionary<string, (DlnaServerInfo Info, DeviceDescription Description, DateTimeOffset LastSeen)> _devices = new(StringComparer.OrdinalIgnoreCase);
    private CancellationTokenSource? _cts;
    private Task? _loop;

    public IReadOnlyList<DlnaServerInfo> Servers
    {
        get
        {
            lock (_lock)
            {
                return _devices.Values.Select(d => d.Info).OrderBy(i => i.Name, StringComparer.OrdinalIgnoreCase).ToList();
            }
        }
    }

    public event EventHandler? ServersChanged;

    public Task StartAsync(CancellationToken cancellationToken)
    {
        if (_loop is not null)
        {
            return Task.CompletedTask;
        }
        _cts = new CancellationTokenSource();
        _loop = Task.Run(() => RunAsync(_cts.Token));
        return Task.CompletedTask;
    }

    public async ValueTask DisposeAsync()
    {
        _cts?.Cancel();
        if (_loop is not null)
        {
            try
            {
                await _loop;
            }
            catch (OperationCanceledException)
            {
            }
        }
        _cts?.Dispose();
    }

    public async Task<IReadOnlyList<DlnaItem>> BrowseAsync(DlnaServerInfo server, string objectId, CancellationToken cancellationToken = default)
    {
        var description = await DescribeAsync(server, cancellationToken);
        var items = new List<DlnaItem>();
        var start = 0;
        while (true)
        {
            using var request = new HttpRequestMessage(HttpMethod.Post, description.ControlUri)
            {
                Content = new StringContent(Soap.BrowseRequest(description.ServiceType, objectId, start, PageSize), Encoding.UTF8, "text/xml")
            };
            request.Headers.TryAddWithoutValidation("SOAPACTION", $"\"{description.ServiceType}#Browse\"");
            using var response = await Client.SendAsync(request, cancellationToken);
            response.EnsureSuccessStatusCode();
            var envelope = XDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
            var result = envelope.Descendants().FirstOrDefault(e => e.Name.LocalName == "Result")?.Value ?? "";
            var returned = int.TryParse(envelope.Descendants().FirstOrDefault(e => e.Name.LocalName == "NumberReturned")?.Value, out var n) ? n : 0;
            var total = int.TryParse(envelope.Descendants().FirstOrDefault(e => e.Name.LocalName == "TotalMatches")?.Value, out var t) ? t : 0;
            items.AddRange(DidlLite.Parse(result));
            start += returned;
            if (returned == 0 || (total > 0 && start >= total))
            {
                return items;
            }
        }
    }

    private async Task<DeviceDescription> DescribeAsync(DlnaServerInfo server, CancellationToken cancellationToken)
    {
        lock (_lock)
        {
            if (_devices.TryGetValue(server.Id, out var known))
            {
                return known.Description;
            }
        }
        var xml = await Client.GetStringAsync(server.DescriptionUri, cancellationToken);
        return DeviceDescriptionParser.Parse(xml, server.DescriptionUri) ?? throw new InvalidOperationException($"{server.Name} does not offer a ContentDirectory service.");
    }

    private async Task RunAsync(CancellationToken cancellationToken)
    {
        using var timer = new PeriodicTimer(SearchInterval);
        do
        {
            try
            {
                var locations = await SearchAsync(cancellationToken);
                var changed = false;
                foreach (var location in locations)
                {
                    changed |= await RegisterAsync(location, cancellationToken);
                }
                changed |= Expire();
                if (changed)
                {
                    ServersChanged?.Invoke(this, EventArgs.Empty);
                }
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogWarning(ex, "Home Share search failed");
            }
        }
        while (await WaitAsync(timer, cancellationToken));
    }

    private static async Task<bool> WaitAsync(PeriodicTimer timer, CancellationToken cancellationToken)
    {
        try
        {
            return await timer.WaitForNextTickAsync(cancellationToken);
        }
        catch (OperationCanceledException)
        {
            return false;
        }
    }

    private async Task<IReadOnlyCollection<Uri>> SearchAsync(CancellationToken cancellationToken)
    {
        var found = new HashSet<Uri>();
        using var client = new UdpClient(new IPEndPoint(IPAddress.Any, 0));
        var payload = SsdpMessages.BuildSearch(SsdpMessages.MediaServerType, 2);
        var target = new IPEndPoint(SsdpMessages.MulticastAddress, SsdpMessages.Port);
        await client.SendAsync(payload, target, cancellationToken);
        await client.SendAsync(payload, target, cancellationToken);
        using var window = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        window.CancelAfter(TimeSpan.FromSeconds(3));
        try
        {
            while (true)
            {
                var received = await client.ReceiveAsync(window.Token);
                var message = SsdpMessages.Parse(Encoding.UTF8.GetString(received.Buffer));
                if (message is not null && Uri.TryCreate(message.Get("LOCATION"), UriKind.Absolute, out var location))
                {
                    found.Add(location);
                }
            }
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
        }
        return found;
    }

    private async Task<bool> RegisterAsync(Uri location, CancellationToken cancellationToken)
    {
        DeviceDescription? description;
        try
        {
            description = DeviceDescriptionParser.Parse(await Client.GetStringAsync(location, cancellationToken), location);
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
        {
            return false;
        }
        if (description is null || description.Udn.Equals(ownDevice.Udn, StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }
        lock (_lock)
        {
            var isNew = !_devices.ContainsKey(description.Udn);
            _devices[description.Udn] = (new DlnaServerInfo(description.Udn, description.FriendlyName, location), description, DateTimeOffset.UtcNow);
            return isNew;
        }
    }

    private bool Expire()
    {
        lock (_lock)
        {
            var stale = _devices.Where(d => DateTimeOffset.UtcNow - d.Value.LastSeen > Retention).Select(d => d.Key).ToList();
            foreach (var key in stale)
            {
                _devices.Remove(key);
            }
            return stale.Count > 0;
        }
    }
}
