using Api.Features.Common.Data;
using Api.Features.Users.Models;
using Microsoft.EntityFrameworkCore;

namespace Api.Features.Users.Data;

public class UserConfiguration : IEntityTypeConfiguration
{
    public void Configure(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired();
            entity.Property(e => e.Email).IsRequired();
        });
    }
}
