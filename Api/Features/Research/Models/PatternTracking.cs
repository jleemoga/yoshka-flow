using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Api.Features.Research.Models;

public class PatternTracking
{
    [Key]
    [Column("pattern_id")]
    public int PatternId { get; set; }

    [Column("metric_id")]
    public int MetricId { get; set; }

    [Column("performance_patterns", TypeName = "jsonb")]
    public string? PerformancePatterns { get; set; }

    [Column("innovation_patterns", TypeName = "jsonb")]
    public string? InnovationPatterns { get; set; }

    [Column("market_patterns", TypeName = "jsonb")]
    public string? MarketPatterns { get; set; }

    // Navigation properties
    [ForeignKey("MetricId")]
    public virtual Metric Metric { get; set; } = null!;
}
