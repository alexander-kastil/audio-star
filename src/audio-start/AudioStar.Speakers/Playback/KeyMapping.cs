using System.Globalization;

namespace AudioStar.Speakers.Playback;

internal sealed record KeyMappingList(int MaxNumber, IReadOnlyList<Preset> Presets);

internal static class KeyMapping
{
    private const string NameSuffixMarker = "_#~";

    public static KeyMappingList Parse(string? keyMappingXml)
    {
        if (string.IsNullOrWhiteSpace(keyMappingXml))
        {
            return new KeyMappingList(0, []);
        }
        XDocument document;
        try
        {
            document = XDocument.Parse(keyMappingXml);
        }
        catch (System.Xml.XmlException)
        {
            return new KeyMappingList(0, []);
        }
        var keyList = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "KeyList") ?? document.Root;
        var maxText = keyList?.Elements().FirstOrDefault(e => e.Name.LocalName == "MaxNumber")?.Value;
        if (!int.TryParse(maxText, NumberStyles.Integer, CultureInfo.InvariantCulture, out var max) || max <= 0)
        {
            return new KeyMappingList(0, []);
        }
        var presets = new List<Preset>();
        for (var number = 1; number <= max; number++)
        {
            var key = keyList!.Elements().FirstOrDefault(e => e.Name.LocalName == "Key" + number);
            presets.Add(ToPreset(number, key));
        }
        return new KeyMappingList(max, presets);
    }

    public static string Edit(string keyMappingXml, int number, IEnumerable<XElement> children)
    {
        var document = XDocument.Parse(keyMappingXml);
        var keyList = document.Descendants().First(e => e.Name.LocalName == "KeyList");
        var key = keyList.Elements().FirstOrDefault(e => e.Name.LocalName == "Key" + number);
        if (key is null)
        {
            key = new XElement("Key" + number);
            keyList.Add(key);
        }
        key.RemoveNodes();
        key.Add(children);
        return "<?xml version=\"1.0\"?>\n" + keyList.ToString(SaveOptions.DisableFormatting);
    }

    public static XElement[] EmptyKeyContent() => [new XElement("RoutineId", "Empty")];

    private static Preset ToPreset(int number, XElement? key)
    {
        if (key is null)
        {
            return new Preset(number, "", null, null, true);
        }
        string Child(string name) => key.Elements().FirstOrDefault(e => e.Name.LocalName == name)?.Value.Trim() ?? "";

        var routine = Child("RoutineId");
        var name = Child("Name");
        var markerAt = name.IndexOf(NameSuffixMarker, StringComparison.Ordinal);
        if (markerAt >= 0)
        {
            name = name[..markerAt];
        }
        if (routine.Equals("Empty", StringComparison.OrdinalIgnoreCase) || (name.Length == 0 && Child("Source").Length == 0 && Child("Url").Length == 0))
        {
            return new Preset(number, "", null, null, true);
        }
        Uri.TryCreate(Child("PicUrl"), UriKind.Absolute, out var picture);
        var source = Child("Source");
        return new Preset(number, name, source.Length == 0 ? null : source, picture, false);
    }
}
