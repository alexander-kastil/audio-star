using AudioStar.Core;
using AudioStar.Sources.Radio;
using AudioStar.Sources.SoundCloud;
using AudioStar.Sources.Spotify;
using AudioStar.Sources.YouTube;
using AudioStar.Sources.YtDlp;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources;

public static class SourcesServiceCollectionExtensions
{
    public static IServiceCollection AddAudioStarSources(this IServiceCollection services)
    {
        services.AddSingleton<IYtDlp, YtDlpProcess>();
        services.AddHostedService<YtDlpUpdater>();
        services.AddSingleton<IPlaylistCache>(provider => new JsonPlaylistCache(AppPaths.PlaylistCacheDirectory, provider.GetRequiredService<ILogger<JsonPlaylistCache>>()));
        services.AddSingleton<IMusicSource, YouTubeSource>();
        services.AddSingleton<SoundCloudSession>();
        services.AddSingleton<IMusicSource, SoundCloudSource>();
        services.AddSingleton<IStreamResolver, YouTubeStreamResolver>();
        services.AddSingleton<IStreamResolver, SoundCloudStreamResolver>();

        services.AddSingleton<SpotifyAuth>();
        services.AddSingleton<SpotifyApi>();
        services.AddSingleton<IMusicSource, SpotifySource>();

        services.AddSingleton<RadioBrowserClient>();
        services.AddSingleton<IRadioDirectory, RadioDirectory>();
        return services;
    }
}
