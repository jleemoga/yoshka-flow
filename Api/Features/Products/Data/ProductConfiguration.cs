using Api.Features.Common.Data;
using Api.Features.Products.Models;
using Microsoft.EntityFrameworkCore;

namespace Api.Features.Products.Data;

public class ProductConfiguration : IEntityTypeConfiguration
{
    public void Configure(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Product>(entity =>
        {
            entity.HasKey(e => e.ProductId);
            entity.HasIndex(e => e.Name);
        });
    }
}
