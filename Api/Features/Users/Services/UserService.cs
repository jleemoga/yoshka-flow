using MyApi.Features.Users.Models;
using MyApi.Features.Users.Repositories;

namespace MyApi.Features.Users.Services;

public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;

    public UserService(IUserRepository userRepository)
    {
        _userRepository = userRepository;
    }

    public async Task<User> GetUserByIdAsync(int id)
    {
        return await _userRepository.GetUserByIdAsync(id);
    }

    public async Task<IEnumerable<User>> GetAllUsersAsync()
    {
        return await _userRepository.GetAllUsersAsync();
    }

    public async Task AddUserAsync(User user)
    {
        await _userRepository.AddUserAsync(user);
    }

    public async Task UpdateUserAsync(User user)
    {
        await _userRepository.UpdateUserAsync(user);
    }

    public async Task DeleteUserAsync(int id)
    {
        await _userRepository.DeleteUserAsync(id);
    }
}