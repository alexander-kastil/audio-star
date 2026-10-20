using System.Globalization;
using System.Net;
using AudioStar.Speakers.Discovery;
using AudioStar.Speakers.Events;
using AudioStar.Speakers.Playback;
using AudioStar.Speakers.Protocol;

namespace AudioStar.Speakers;

internal sealed class SpeakerController(SpeakerSession session, SpeakerClient client, ILogger logger) : ISpeakerController
{
    private const string ControlSource = "WiiMApp";
    private const string CurrentQueue = "CurrentQueue";

    public Task PlayAsync(CancellationToken cancellationToken = default) => TransportAsync("Play", cancellationToken, ("Speed", "1"));

    public Task PauseAsync(CancellationToken cancellationToken = default) => TransportAsync("Pause", cancellationToken);

    public Task NextAsync(CancellationToken cancellationToken = default) => TransportAsync("Next", cancellationToken);

    public Task PreviousAsync(CancellationToken cancellationToken = default) => TransportAsync("Previous", cancellationToken);

    public async Task SeekAsync(TimeSpan position, CancellationToken cancellationToken = default)
    {
        await client.SoapAsync(
            SoapService.RenderTransport,
            "Seek",
            [("InstanceID", "0"), ("Unit", "REL_TIME"), ("Target", ClockText.Format(position))],
            cancellationToken);
        session.Apply(s => s with { Position = position < TimeSpan.Zero ? TimeSpan.Zero : position });
    }

    public async Task SetVolumeAsync(int volume, CancellationToken cancellationToken = default)
    {
        var clamped = Math.Clamp(volume, 0, 100);
        await client.SoapAsync(
            SoapService.RenderControl,
            "SetVolume",
            [("InstanceID", "0"), ("Channel", "Master"), ("DesiredVolume", clamped.ToString(CultureInfo.InvariantCulture))],
            cancellationToken);
        session.Apply(s => s with { Volume = clamped });
    }

    public async Task SetMuteAsync(bool muted, CancellationToken cancellationToken = default)
    {
        await client.SoapAsync(
            SoapService.RenderControl,
            "SetMute",
            [("InstanceID", "0"), ("Channel", "Master"), ("DesiredMute", muted ? "1" : "0")],
            cancellationToken);
        session.Apply(s => s with { Muted = muted });
    }

    public async Task SetLoopModeAsync(LoopMode mode, CancellationToken cancellationToken = default)
    {
        await client.SoapAsync(
            SoapService.PlayQueue,
            "SetQueueLoopMode",
            [("LoopMode", ((int)mode).ToString(CultureInfo.InvariantCulture))],
            cancellationToken);
        session.Apply(s => s with { LoopMode = mode });
    }

    public Task<PlaybackState> GetPlaybackStateAsync(CancellationToken cancellationToken = default) => session.RefreshStateAsync(cancellationToken);

    public async Task PlayAsync(PlayRequest request, CancellationToken cancellationToken = default)
    {
        if (request.Items.Count == 0)
        {
            return;
        }
        var plan = FastPlayPlanner.Plan(request.Items.Count, request.StartIndex);
        var pcUuid = PcIdentity.Value;

        string Xml(IEnumerable<int> indices) => PlayListBuilder.Build(
            request.ListName,
            request.SourceName,
            [.. indices.Select(i => request.Items[i])],
            request.ListArtworkUri,
            radio: false,
            pcUuid);

        await client.SoapAsync(
            SoapService.PlayQueue,
            "CreateQueue",
            CreateQueueArgs(Xml(plan.Initial)),
            cancellationToken);
        await client.SoapAsync(
            SoapService.PlayQueue,
            "PlayQueueWithIndex",
            PlayQueueWithIndexArgs(request.ListName, 1),
            cancellationToken);
        var appended = 0;
        try
        {
            foreach (var chunk in plan.TailChunks)
            {
                await AppendWithRetryAsync(AppendArgs(Xml(chunk), 1), cancellationToken);
                appended += chunk.Count;
            }
            foreach (var chunk in plan.HeadChunks)
            {
                await AppendWithRetryAsync(AppendArgs(Xml(chunk), 0), cancellationToken);
                appended += chunk.Count;
            }
        }
        catch (Exception ex) when (ex is HttpRequestException or IOException or TimeoutException)
        {
            logger.LogWarning(ex, "Queue for {List} stopped after {Count} appended tracks", request.ListName, appended + plan.Initial.Count);
        }
    }

    private async Task AppendWithRetryAsync((string, string)[] args, CancellationToken cancellationToken)
    {
        await Task.Delay(TimeSpan.FromMilliseconds(400), cancellationToken);
        try
        {
            await client.SoapAsync(SoapService.PlayQueue, "AppendTracksInQueueEx", args, cancellationToken);
        }
        catch (Exception ex) when (ex is HttpRequestException or IOException)
        {
            logger.LogDebug("Append failed once, retrying: {Message}", ex.Message);
            await Task.Delay(TimeSpan.FromSeconds(2), cancellationToken);
            await client.SoapAsync(SoapService.PlayQueue, "AppendTracksInQueueEx", args, cancellationToken);
        }
    }

    public async Task PlayUrlAsync(string title, Uri streamUri, Uri? artworkUri, string sourceName, CancellationToken cancellationToken = default)
    {
        var item = new PlayItem(streamUri.ToString(), title, null, null, streamUri, artworkUri, null);
        var xml = PlayListBuilder.Build(title, sourceName, [item], artworkUri, radio: true, PcIdentity.Value);
        await client.SoapAsync(SoapService.PlayQueue, "CreateQueue", CreateQueueArgs(xml), cancellationToken);
        await client.SoapAsync(SoapService.PlayQueue, "PlayQueueWithIndex", PlayQueueWithIndexArgs(title, 1), cancellationToken);
    }

    public async Task<SpeakerQueue?> GetQueueAsync(CancellationToken cancellationToken = default)
    {
        var xml = await BrowseQueueXmlAsync(cancellationToken);
        return QueueParser.Parse(xml, client.Ip);
    }

    public async Task PlayQueueIndexAsync(int index, CancellationToken cancellationToken = default)
    {
        await client.SoapAsync(SoapService.PlayQueue, "PlayQueueWithIndex", PlayQueueWithIndexArgs(CurrentQueue, Math.Max(0, index) + 1), cancellationToken);
    }

    public async Task RemoveQueueIndexAsync(int index, CancellationToken cancellationToken = default)
    {
        var position = (Math.Max(0, index) + 1).ToString(CultureInfo.InvariantCulture);
        await client.SoapAsync(
            SoapService.PlayQueue,
            "RemoveTracksInQueue",
            [("QueueName", CurrentQueue), ("RangStart", position), ("RangEnd", position)],
            cancellationToken);
    }

    public async Task<IReadOnlyList<Preset>> GetPresetsAsync(CancellationToken cancellationToken = default)
    {
        var xml = await GetKeyMappingXmlAsync(cancellationToken);
        return KeyMapping.Parse(xml).Presets;
    }

    public async Task PlayPresetAsync(int number, CancellationToken cancellationToken = default)
    {
        await client.HttpGetAsync($"MCUKeyShortClick:{number}", cancellationToken);
    }

    public async Task SaveCurrentAsPresetAsync(int number, CancellationToken cancellationToken = default)
    {
        var keyMappingXml = await GetKeyMappingXmlAsync(cancellationToken);
        var mapping = KeyMapping.Parse(keyMappingXml);
        if (mapping.MaxNumber == 0 || number < 1 || number > mapping.MaxNumber)
        {
            throw new NotSupportedException("This speaker has no preset slot " + number);
        }
        var queueXml = await BrowseQueueXmlAsync(cancellationToken)
            ?? throw new InvalidOperationException("The speaker has no current queue to save");
        await client.SoapAsync(SoapService.PlayQueue, "BackUpQueue", [("QueueContext", queueXml)], cancellationToken);
        var updated = KeyMapping.Edit(keyMappingXml!, number, PresetContent(queueXml));
        await client.SoapAsync(SoapService.PlayQueue, "SetKeyMapping", [("QueueContext", updated)], cancellationToken);
    }

    public async Task DeletePresetAsync(int number, CancellationToken cancellationToken = default)
    {
        var keyMappingXml = await GetKeyMappingXmlAsync(cancellationToken);
        var mapping = KeyMapping.Parse(keyMappingXml);
        if (mapping.MaxNumber == 0 || number < 1 || number > mapping.MaxNumber)
        {
            throw new NotSupportedException("This speaker has no preset slot " + number);
        }
        var updated = KeyMapping.Edit(keyMappingXml!, number, KeyMapping.EmptyKeyContent());
        await client.SoapAsync(SoapService.PlayQueue, "SetKeyMapping", [("QueueContext", updated)], cancellationToken);
    }

    public async Task<IReadOnlyList<AudioInput>> GetInputsAsync(CancellationToken cancellationToken = default)
    {
        string? renames = null;
        try
        {
            renames = await client.HttpGetAsync("getModeRename", cancellationToken, TimeSpan.FromSeconds(5));
        }
        catch (Exception ex) when (ex is SpeakerRequestException or HttpRequestException or TimeoutException)
        {
            logger.LogDebug("getModeRename on {Speaker} failed: {Message}", session.Info.Id, ex.Message);
        }
        return InputCatalog.Build(session.Status.Project, session.Status.PlmSupport, session.Status.HasUsbDisk, renames);
    }

    public async Task SwitchInputAsync(string mode, CancellationToken cancellationToken = default)
    {
        await client.HttpGetAsync($"setPlayerCmd:switchmode:{mode}", cancellationToken);
    }

    public Task<string> SendCommandAsync(string command, CancellationToken cancellationToken = default) => client.HttpGetAsync(command, cancellationToken);

    public Task<string> PostCommandAsync(string command, string jsonPayload, CancellationToken cancellationToken = default) => client.HttpPostAsync(command, jsonPayload, cancellationToken);

    internal static (string, string)[] CreateQueueArgs(string queueContext) => [("QueueContext", queueContext), ("QueuePolicy", "0")];

    internal static (string, string)[] PlayQueueWithIndexArgs(string queueName, int index) =>
        [("QueueName", queueName), ("Index", index.ToString(CultureInfo.InvariantCulture))];

    internal static (string, string)[] AppendArgs(string queueContext, int direction) =>
        [("QueueContext", queueContext), ("Direction", direction.ToString(CultureInfo.InvariantCulture)), ("StartIndex", "0"), ("QueuePolicy", "0")];

    private async Task TransportAsync(string action, CancellationToken cancellationToken, params (string, string)[] extra)
    {
        (string, string)[] args = [("InstanceID", "0"), .. extra, ("ControlSource", ControlSource)];
        await client.SoapAsync(SoapService.RenderTransport, action, args, cancellationToken);
    }

    private async Task<string?> BrowseQueueXmlAsync(CancellationToken cancellationToken)
    {
        try
        {
            var reply = await client.SoapAsync(SoapService.PlayQueue, "BrowseQueue", [("QueueName", CurrentQueue)], cancellationToken);
            return reply.TryGetValue("QueueContext", out var xml) ? xml : null;
        }
        catch (SpeakerRequestException ex) when (ex.StatusCode == HttpStatusCode.InternalServerError)
        {
            return null;
        }
    }

    private async Task<string?> GetKeyMappingXmlAsync(CancellationToken cancellationToken)
    {
        var reply = await client.SoapAsync(SoapService.PlayQueue, "GetKeyMapping", [], cancellationToken);
        return reply.TryGetValue("QueueContext", out var xml) ? xml : null;
    }

    private static IEnumerable<XElement> PresetContent(string queueXml)
    {
        var document = XDocument.Parse(queueXml);
        string Text(string name) => document.Descendants().FirstOrDefault(e => e.Name.LocalName == name)?.Value.Trim() ?? "";

        var firstTrack = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "Tracks")?.Elements().FirstOrDefault();
        string TrackText(string name) => firstTrack?.Elements().FirstOrDefault(e => e.Name.LocalName == name)?.Value ?? "";

        return
        [
            new XElement("Name", Text("ListName")),
            new XElement("Source", Text("SourceName")),
            new XElement("PicUrl", Text("PicUrl")),
            new XElement("SearchUrl", Text("SearchUrl")),
            new XElement("Url", TrackText("URL")),
            new XElement("Id", TrackText("Id")),
            new XElement("Metadata", TrackText("Metadata"))
        ];
    }
}
