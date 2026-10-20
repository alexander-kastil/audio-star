using System.Xml.Linq;

namespace AudioStar.Library.Dlna;

internal sealed record SoapRequest(string Action, IReadOnlyDictionary<string, string> Arguments)
{
    public string Get(string name, string fallback = "") => Arguments.GetValueOrDefault(name, fallback);

    public int GetInt(string name, int fallback = 0) => int.TryParse(Get(name), out var value) ? value : fallback;
}

internal static class Soap
{
    public const string ContentDirectoryType = "urn:schemas-upnp-org:service:ContentDirectory:1";

    private static readonly XNamespace Envelope = "http://schemas.xmlsoap.org/soap/envelope/";

    public static SoapRequest? ParseRequest(string xml)
    {
        try
        {
            var body = XDocument.Parse(xml).Descendants(Envelope + "Body").FirstOrDefault();
            var action = body?.Elements().FirstOrDefault();
            if (action is null)
            {
                return null;
            }
            var arguments = action.Elements().ToDictionary(e => e.Name.LocalName, e => e.Value, StringComparer.OrdinalIgnoreCase);
            return new SoapRequest(action.Name.LocalName, arguments);
        }
        catch (System.Xml.XmlException)
        {
            return null;
        }
    }

    public static string Response(string action, string serviceType, IEnumerable<KeyValuePair<string, string>> values)
    {
        XNamespace service = serviceType;
        var response = new XElement(
            service + action + "Response",
            new XAttribute(XNamespace.Xmlns + "u", serviceType),
            values.Select(v => new XElement(v.Key, v.Value)));
        return Wrap(response);
    }

    public static string Fault(int code, string description)
    {
        XNamespace control = "urn:schemas-upnp-org:control-1-0";
        var fault = new XElement(
            Envelope + "Fault",
            new XElement("faultcode", "s:Client"),
            new XElement("faultstring", "UPnPError"),
            new XElement("detail", new XElement(control + "UPnPError", new XElement(control + "errorCode", code), new XElement(control + "errorDescription", description))));
        return Wrap(fault);
    }

    public static string BrowseRequest(string serviceType, string objectId, int startingIndex, int requestedCount)
    {
        XNamespace service = serviceType;
        var browse = new XElement(
            service + "Browse",
            new XAttribute(XNamespace.Xmlns + "u", serviceType),
            new XElement("ObjectID", objectId),
            new XElement("BrowseFlag", "BrowseDirectChildren"),
            new XElement("Filter", "*"),
            new XElement("StartingIndex", startingIndex),
            new XElement("RequestedCount", requestedCount),
            new XElement("SortCriteria", ""));
        return Wrap(browse);
    }

    private static string Wrap(XElement content)
    {
        var document = new XDocument(
            new XDeclaration("1.0", "utf-8", null),
            new XElement(
                Envelope + "Envelope",
                new XAttribute(XNamespace.Xmlns + "s", Envelope.NamespaceName),
                new XAttribute(Envelope + "encodingStyle", "http://schemas.xmlsoap.org/soap/encoding/"),
                new XElement(Envelope + "Body", content)));
        return document.Declaration + document.ToString(SaveOptions.DisableFormatting);
    }
}
