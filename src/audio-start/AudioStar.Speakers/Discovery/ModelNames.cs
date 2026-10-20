namespace AudioStar.Speakers.Discovery;

internal static class ModelNames
{
    private static readonly Dictionary<string, string> Known = new(StringComparer.OrdinalIgnoreCase)
    {
        ["WiiM_AMP"] = "WiiM Amp",
        ["WiiM_Amp_4layer"] = "WiiM Amp",
        ["WiiM_AMP_No_MFI"] = "WiiM Amp",
        ["WiiM_Amp_Pro"] = "WiiM Amp Pro",
        ["WiiM_Amp_Ultra"] = "WiiM Amp Ultra",
        ["WiiM_Pro_with_gc4a"] = "WiiM Pro",
        ["WiiM_Pro_AVS"] = "WiiM Pro",
        ["WiiM_Pro_Plus"] = "WiiM Pro Plus",
        ["WiiM_Ultra"] = "WiiM Ultra"
    };

    public static string Friendly(string project)
    {
        if (string.IsNullOrWhiteSpace(project))
        {
            return "WiiM";
        }
        return Known.TryGetValue(project, out var name) ? name : project.Replace('_', ' ');
    }
}
