using Microsoft.Extensions.DependencyInjection;
using MyApi.Features.Users.Repositories;
using MyApi.Features.Users.Services;

namespace MyApi.Features.Users.Extensions;

public static class UserFeatureExtensions
{
    public static IServiceCollection AddUserFeature(this IServiceCollection services)
    {
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IUserService, UserService>();
        return services;
    }
}
