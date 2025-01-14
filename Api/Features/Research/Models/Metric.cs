using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Api.Features.Research.Models;

public class Metric
{
    [Key]
    [Column("metric_id")]
    public int MetricId { get; set; }

    [Column("task_id")]
    public int TaskId { get; set; }

    [Required]
    [Column("metric_name")]
    [StringLength(255)]
    public string MetricName { get; set; } = string.Empty;

    [Column("raw_data", TypeName = "jsonb")]
    public string? RawData { get; set; }

    [Column("pattern_analysis", TypeName = "jsonb")]
    public string? PatternAnalysis { get; set; }

    [Column("confidence_score")]
    public float? ConfidenceScore { get; set; }

    [Column("evidence_quality")]
    public float? EvidenceQuality { get; set; }

    // Navigation properties
    [ForeignKey("TaskId")]
    public virtual ResearchTask ResearchTask { get; set; } = null!;
    public virtual ConfidenceScore? MetricConfidenceScore { get; set; }
    public virtual PatternTracking? PatternTracking { get; set; }
}
