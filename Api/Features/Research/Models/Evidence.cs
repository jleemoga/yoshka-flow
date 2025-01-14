using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Api.Features.Research.Models;

public class Evidence
{
    [Key]
    [Column("evidence_id")]
    public int EvidenceId { get; set; }

    [Column("task_id")]
    public int TaskId { get; set; }

    [Required]
    [Column("source_type")]
    [StringLength(255)]
    public string SourceType { get; set; } = string.Empty;

    [Column("validation_method")]
    [StringLength(255)]
    public string? ValidationMethod { get; set; }

    [Column("date_accessed")]
    public DateTime? DateAccessed { get; set; }

    [Column("verified")]
    public bool Verified { get; set; }

    [Column("credibility")]
    public float? Credibility { get; set; }

    [Column("source_url")]
    public string? SourceUrl { get; set; }

    [Column("notes")]
    public string? Notes { get; set; }

    // Navigation properties
    [ForeignKey("TaskId")]
    public virtual ResearchTask ResearchTask { get; set; } = null!;
}
