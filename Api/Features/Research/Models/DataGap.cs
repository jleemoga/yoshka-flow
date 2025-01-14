using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Api.Features.Research.Models;

public class DataGap
{
    [Key]
    [Column("gap_id")]
    public int GapId { get; set; }

    [Column("task_id")]
    public int TaskId { get; set; }

    [Column("gap_description")]
    public string? GapDescription { get; set; }

    [Column("impact_on_confidence_score")]
    public float? ImpactOnConfidenceScore { get; set; }

    [Column("alternative_metrics_used", TypeName = "jsonb")]
    public string? AlternativeMetricsUsed { get; set; }

    // Navigation properties
    [ForeignKey("TaskId")]
    public virtual ResearchTask ResearchTask { get; set; } = null!;
}
