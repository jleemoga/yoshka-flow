using Microsoft.EntityFrameworkCore;
using Api.Features.Products.Models;
using Api.Features.Research.Models;
using Api.Features.Users.Models;
using Api.Features.Common.Data;
using System.Reflection;

namespace Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Product> Products { get; set; }
    public DbSet<ResearchTask> ResearchTasks { get; set; }
    public DbSet<Evidence> Evidence { get; set; }
    public DbSet<Metric> Metrics { get; set; }
    public DbSet<ConfidenceScore> ConfidenceScores { get; set; }
    public DbSet<PatternTracking> PatternTracking { get; set; }
    public DbSet<DataGap> DataGaps { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Dynamically apply all IEntityTypeConfiguration implementations
        var configurations = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(type => !type.IsAbstract && !type.IsInterface
                && type.GetInterfaces().Any(i => i == typeof(IEntityTypeConfiguration)))
            .Select(Activator.CreateInstance)
            .Cast<IEntityTypeConfiguration>();

        foreach (var configuration in configurations)
        {
            configuration.Configure(modelBuilder);
        }
    }
}
