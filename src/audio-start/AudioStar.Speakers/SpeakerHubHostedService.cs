using Microsoft.Extensions.Hosting;

namespace AudioStar.Speakers;

internal sealed class SpeakerHubHostedService(ISpeakerHub hub) : IHostedService
{
    public Task StartAsync(CancellationToken cancellationToken) => hub.StartAsync(cancellationToken);

    public Task StopAsync(CancellationToken cancellationToken) => hub.StopAsync(cancellationToken);
}
