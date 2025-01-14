using Microsoft.Extensions.DependencyInjection;
using Api.Features.Health.Controllers;

namespace Api.Features.Health.Extensions;

public static class HealthFeatureExtensions
{
    public static IServiceCollection AddHealthFeature(this IServiceCollection services)
    {
        services.AddControllers().AddApplicationPart(typeof(HealthController).Assembly);
        return services;
    }
}
