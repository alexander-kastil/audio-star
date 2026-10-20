using AudioStar.Core;
using AudioStar.Devices.Groups;
using AudioStar.Devices.Settings;
using Microsoft.Extensions.DependencyInjection;

namespace AudioStar.Devices;

public static class DevicesServiceCollectionExtensions
{
    public static IServiceCollection AddAudioStarDevices(this IServiceCollection services)
    {
        services.AddSingleton<IGroupService, GroupService>();
        services.AddSingleton<IDeviceSettingsService, DeviceSettingsService>();
        return services;
    }
}
