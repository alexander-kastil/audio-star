using Microsoft.Extensions.DependencyInjection;

namespace AudioStar.Core;

public static class CoreServiceCollectionExtensions
{
    public static IServiceCollection AddAudioStarCore(this IServiceCollection services)
    {
        services.AddSingleton<ISettingsStore, JsonSettingsStore>();
        return services;
    }
}
