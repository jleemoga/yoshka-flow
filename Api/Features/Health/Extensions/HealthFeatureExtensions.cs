using Microsoft.Extensions.DependencyInjection;
using MyApi.Features.Health.Controllers;

namespace MyApi.Features.Health.Extensions;

public static class HealthFeatureExtensions
{
    public static IServiceCollection AddHealthFeature(this IServiceCollection services)
    {
        services.AddControllers().AddApplicationPart(typeof(HealthController).Assembly);
        return services;
    }
}
