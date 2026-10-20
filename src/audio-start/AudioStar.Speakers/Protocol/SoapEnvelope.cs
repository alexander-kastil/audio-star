namespace AudioStar.Speakers.Protocol;

internal readonly record struct SoapService(string Endpoint, string ServiceId, string Urn)
{
    public static SoapService RenderControl { get; } = Create("rendercontrol1", "RenderingControl:1");
    public static SoapService RenderTransport { get; } = Create("rendertransport1", "AVTransport:1");
    public static SoapService PlayQueue { get; } = Create("PlayQueue1", "PlayQueue:1");

    private static SoapService Create(string endpoint, string serviceId)
    {
        var urn = serviceId == "PlayQueue:1"
            ? $"urn:schemas-wiimu-com:service:{serviceId}"
            : $"urn:schemas-upnp-org:service:{serviceId}";
        return new SoapService(endpoint, serviceId, urn);
    }
}

internal static class SoapEnvelope
{
    public static string Build(SoapService service, string action, params (string Name, string Value)[] args)
    {
        var parameters = new StringBuilder();
        foreach (var (name, value) in args)
        {
            parameters.Append('<').Append(name).Append('>').Append(XmlText.Escape(value)).Append("</").Append(name).Append('>');
        }
        return $"<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:{action} xmlns:u=\"{service.Urn}\">{parameters}</u:{action}></s:Body></s:Envelope>";
    }

    public static string SoapAction(SoapService service, string action) => $"\"{service.Urn}#{action}\"";

    public static IReadOnlyDictionary<string, string> ParseResponse(string xml)
    {
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        var document = XDocument.Parse(xml);
        var body = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "Body");
        var response = body?.Elements().FirstOrDefault();
        if (response is null)
        {
            return result;
        }
        foreach (var element in response.Elements())
        {
            result.TryAdd(element.Name.LocalName, element.Value);
        }
        return result;
    }
}

internal static class XmlText
{
    public static string Escape(string? value)
    {
        return string.IsNullOrEmpty(value)
            ? ""
            : value.Replace("&", "&amp;", StringComparison.Ordinal).Replace("<", "&lt;", StringComparison.Ordinal).Replace(">", "&gt;", StringComparison.Ordinal);
    }
}
