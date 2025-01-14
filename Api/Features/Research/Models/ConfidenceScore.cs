using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Api.Features.Research.Models;

public class ConfidenceScore
{
    [Key]
    [Column("confidence_id")]
    public int ConfidenceId { get; set; }

    [Column("metric_id")]
    public int MetricId { get; set; }

    [Column("primary_data_availability")]
    public float? PrimaryDataAvailability { get; set; }

    [Column("alternative_data_quality")]
    public float? AlternativeDataQuality { get; set; }

    [Column("validation_comprehensiveness")]
    public float? ValidationComprehensiveness { get; set; }

    [Column("pattern_confirmation")]
    public float? PatternConfirmation { get; set; }

    [Column("overall_confidence_score")]
    public float? OverallConfidenceScore { get; set; }

    // Navigation properties
    [ForeignKey("MetricId")]
    public virtual Metric Metric { get; set; } = null!;
}
