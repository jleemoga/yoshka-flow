using Api.Features.Common.Data;
using Api.Features.Research.Models;
using Microsoft.EntityFrameworkCore;

namespace Api.Features.Research.Data;

public class ResearchConfiguration : IEntityTypeConfiguration
{
    public void Configure(ModelBuilder modelBuilder)
    {
        // ResearchTask configuration
        modelBuilder.Entity<ResearchTask>(entity =>
        {
            entity.HasKey(e => e.TaskId);
            entity.HasIndex(e => e.Category);
            entity.HasOne(e => e.Product)
                  .WithMany(p => p.ResearchTasks)
                  .HasForeignKey(e => e.ProductId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // Evidence configuration
        modelBuilder.Entity<Evidence>(entity =>
        {
            entity.HasKey(e => e.EvidenceId);
            entity.HasIndex(e => e.SourceType);
            entity.HasOne(e => e.ResearchTask)
                  .WithMany(r => r.Evidence)
                  .HasForeignKey(e => e.TaskId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // Metric configuration
        modelBuilder.Entity<Metric>(entity =>
        {
            entity.HasKey(e => e.MetricId);
            entity.HasIndex(e => e.MetricName);
            entity.HasIndex(e => e.RawData).HasMethod("GIN");
            entity.HasIndex(e => e.PatternAnalysis).HasMethod("GIN");
            entity.HasOne(e => e.ResearchTask)
                  .WithMany(r => r.Metrics)
                  .HasForeignKey(e => e.TaskId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // ConfidenceScore configuration
        modelBuilder.Entity<ConfidenceScore>(entity =>
        {
            entity.HasKey(e => e.ConfidenceId);
            entity.HasIndex(e => e.OverallConfidenceScore);
            entity.HasOne(e => e.Metric)
                  .WithOne(m => m.MetricConfidenceScore)
                  .HasForeignKey<ConfidenceScore>(e => e.MetricId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // PatternTracking configuration
        modelBuilder.Entity<PatternTracking>(entity =>
        {
            entity.HasKey(e => e.PatternId);
            entity.HasIndex(e => e.PerformancePatterns).HasMethod("GIN");
            entity.HasIndex(e => e.InnovationPatterns).HasMethod("GIN");
            entity.HasIndex(e => e.MarketPatterns).HasMethod("GIN");
            entity.HasOne(e => e.Metric)
                  .WithOne(m => m.PatternTracking)
                  .HasForeignKey<PatternTracking>(e => e.MetricId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // DataGap configuration
        modelBuilder.Entity<DataGap>(entity =>
        {
            entity.HasKey(e => e.GapId);
            entity.HasIndex(e => e.GapDescription);
            entity.HasOne(e => e.ResearchTask)
                  .WithMany(r => r.DataGaps)
                  .HasForeignKey(e => e.TaskId)
                  .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
