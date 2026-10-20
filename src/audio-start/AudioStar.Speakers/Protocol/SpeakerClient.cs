using System.Net.Http.Headers;

namespace AudioStar.Speakers.Protocol;

internal sealed class SpeakerClient(string ip, int upnpPort, IHttpClientFactory httpFactory)
{
    public const string SoapClientName = "speaker-soap";
    public const string HttpsClientName = "speaker-https";
    public const string EventClientName = "speaker-events";

    private static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(15);

    public string Ip { get; } = ip;

    public int UpnpPort { get; } = upnpPort;

    public async Task<IReadOnlyDictionary<string, string>> SoapAsync(
        SoapService service,
        string action,
        (string Name, string Value)[] args,
        CancellationToken cancellationToken,
        TimeSpan? timeout = null)
    {
        var body = SoapEnvelope.Build(service, action, args);
        using var request = new HttpRequestMessage(HttpMethod.Post, $"http://{Ip}:{UpnpPort}/upnp/control/{service.Endpoint}")
        {
            Content = new StringContent(body, new UTF8Encoding(false), "text/xml")
        };
        request.Content.Headers.ContentType = MediaTypeHeaderValue.Parse("text/xml; charset=\"utf-8\"");
        request.Headers.TryAddWithoutValidation("SOAPACTION", SoapEnvelope.SoapAction(service, action));
        var text = await SendAsync(httpFactory.CreateClient(SoapClientName), request, action, timeout, cancellationToken);
        return SoapEnvelope.ParseResponse(text);
    }

    public async Task<string> HttpGetAsync(string command, CancellationToken cancellationToken, TimeSpan? timeout = null)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, new Uri($"https://{Ip}/httpapi.asp?command={command}"));
        return await SendAsync(httpFactory.CreateClient(HttpsClientName), request, command, timeout, cancellationToken);
    }

    public async Task<string> HttpPostAsync(string command, string jsonPayload, CancellationToken cancellationToken, TimeSpan? timeout = null)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, new Uri($"https://{Ip}/httpapi.asp"))
        {
            Content = new ByteArrayContent(Encoding.UTF8.GetBytes($"command={command}:{jsonPayload}"))
        };
        return await SendAsync(httpFactory.CreateClient(HttpsClientName), request, command, timeout, cancellationToken);
    }

    public async Task<(string Sid, int TimeoutSeconds)> SubscribeAsync(string service, string callbackUrl, int timeoutSeconds, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(new HttpMethod("SUBSCRIBE"), EventUrl(service));
        request.Headers.TryAddWithoutValidation("NT", "upnp:event");
        request.Headers.TryAddWithoutValidation("CALLBACK", $"<{callbackUrl}>");
        request.Headers.TryAddWithoutValidation("TIMEOUT", $"Second-{timeoutSeconds}");
        return await SendSubscriptionAsync(request, "SUBSCRIBE " + service, timeoutSeconds, cancellationToken);
    }

    public async Task<(string Sid, int TimeoutSeconds)> RenewAsync(string service, string sid, int timeoutSeconds, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(new HttpMethod("SUBSCRIBE"), EventUrl(service));
        request.Headers.TryAddWithoutValidation("SID", sid);
        request.Headers.TryAddWithoutValidation("TIMEOUT", $"Second-{timeoutSeconds}");
        return await SendSubscriptionAsync(request, "RENEW " + service, timeoutSeconds, cancellationToken);
    }

    public async Task UnsubscribeAsync(string service, string sid, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(new HttpMethod("UNSUBSCRIBE"), EventUrl(service));
        request.Headers.TryAddWithoutValidation("SID", sid);
        await SendAsync(httpFactory.CreateClient(EventClientName), request, "UNSUBSCRIBE " + service, TimeSpan.FromSeconds(3), cancellationToken);
    }

    internal static int ParseTimeout(string? header, int fallbackSeconds)
    {
        if (string.IsNullOrWhiteSpace(header))
        {
            return fallbackSeconds;
        }
        var value = header.Trim();
        if (value.EndsWith("infinite", StringComparison.OrdinalIgnoreCase))
        {
            return 1800;
        }
        var dash = value.LastIndexOf('-');
        return dash >= 0 && int.TryParse(value[(dash + 1)..], out var seconds) && seconds > 0 ? seconds : fallbackSeconds;
    }

    private string EventUrl(string service) => $"http://{Ip}:{UpnpPort}/upnp/event/{service}";

    private async Task<(string Sid, int TimeoutSeconds)> SendSubscriptionAsync(HttpRequestMessage request, string operation, int requestedSeconds, CancellationToken cancellationToken)
    {
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        linked.CancelAfter(TimeSpan.FromSeconds(10));
        try
        {
            using var response = await httpFactory.CreateClient(EventClientName).SendAsync(request, linked.Token);
            if (!response.IsSuccessStatusCode)
            {
                throw new SpeakerRequestException(response.StatusCode, operation, "");
            }
            var sid = response.Headers.TryGetValues("SID", out var sids) ? sids.FirstOrDefault() : null;
            if (string.IsNullOrWhiteSpace(sid))
            {
                throw new SpeakerRequestException(response.StatusCode, operation + " without SID", "");
            }
            var timeout = response.Headers.TryGetValues("TIMEOUT", out var timeouts) ? ParseTimeout(timeouts.FirstOrDefault(), requestedSeconds) : requestedSeconds;
            return (sid, timeout);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"{operation} timed out");
        }
    }

    private static async Task<string> SendAsync(HttpClient client, HttpRequestMessage request, string operation, TimeSpan? timeout, CancellationToken cancellationToken)
    {
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        linked.CancelAfter(timeout ?? DefaultTimeout);
        try
        {
            using var response = await client.SendAsync(request, linked.Token);
            var text = await response.Content.ReadAsStringAsync(linked.Token);
            if (!response.IsSuccessStatusCode)
            {
                throw new SpeakerRequestException(response.StatusCode, operation, text);
            }
            return text;
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"{operation} timed out");
        }
    }
}
