using Microsoft.EntityFrameworkCore;

namespace Api.Features.Common.Data;

public interface IEntityTypeConfiguration
{
    void Configure(ModelBuilder modelBuilder);
}
