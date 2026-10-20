using AudioStar.Speakers.Discovery;
using AudioStar.Speakers.Events;
using AudioStar.Speakers.Protocol;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace AudioStar.Speakers;

public static class SpeakersServiceCollectionExtensions
{
    public static IServiceCollection AddAudioStarSpeakers(this IServiceCollection services)
    {
        services.AddHttpClient(SpeakerClient.SoapClientName);
        services.AddHttpClient(SpeakerClient.EventClientName);
        services.AddHttpClient(SpeakerClient.HttpsClientName)
            .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
            {
                SslOptions = { RemoteCertificateValidationCallback = (_, _, _, _) => true }
            });

        services.AddSingleton<SpeakerEventRouter>();
        services.AddSingleton<SpeakerEventListener>();
        services.AddSingleton<SpeakerProber>();
        services.AddSingleton<SsdpDiscovery>();
        services.AddSingleton<MdnsDiscovery>();
        services.AddSingleton(sp => new SpeakerCache(sp.GetRequiredService<ILogger<SpeakerCache>>()));
        services.AddSingleton<SpeakerHub>();
        services.AddSingleton<ISpeakerHub>(sp => sp.GetRequiredService<SpeakerHub>());
        services.AddHostedService<SpeakerHubHostedService>();
        return services;
    }
}
