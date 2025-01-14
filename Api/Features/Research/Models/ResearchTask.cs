using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Api.Features.Products.Models;

namespace Api.Features.Research.Models;

public class ResearchTask
{
    [Key]
    [Column("task_id")]
    public int TaskId { get; set; }

    [Column("product_id")]
    public int ProductId { get; set; }

    [Required]
    [Column("category")]
    [StringLength(255)]
    public string Category { get; set; } = string.Empty;

    [Required]
    [Column("subtask")]
    [StringLength(255)]
    public string Subtask { get; set; } = string.Empty;

    [Column("status")]
    [StringLength(50)]
    public string Status { get; set; } = "pending";

    [Column("assigned_agent")]
    [StringLength(255)]
    public string? AssignedAgent { get; set; }

    // Navigation properties
    [ForeignKey("ProductId")]
    public virtual Product Product { get; set; } = null!;
    public virtual ICollection<Evidence> Evidence { get; set; } = new List<Evidence>();
    public virtual ICollection<Metric> Metrics { get; set; } = new List<Metric>();
    public virtual ICollection<DataGap> DataGaps { get; set; } = new List<DataGap>();
}
