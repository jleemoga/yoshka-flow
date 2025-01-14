using Microsoft.Extensions.DependencyInjection;
using Api.Features.Users.Repositories;
using Api.Features.Users.Services;

namespace Api.Features.Users.Extensions;

public static class UserFeatureExtensions
{
    public static IServiceCollection AddUserFeature(this IServiceCollection services)
    {
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IUserService, UserService>();
        return services;
    }
}
