using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Api.Features.Research.Models;

namespace Api.Features.Products.Models;

public class Product
{
    [Key]
    [Column("product_id")]
    public int ProductId { get; set; }

    [Required]
    [Column("name")]
    [StringLength(255)]
    public string Name { get; set; } = string.Empty;

    [Column("industry")]
    [StringLength(255)]
    public string? Industry { get; set; }

    [Column("geographic_coverage")]
    [StringLength(255)]
    public string? GeographicCoverage { get; set; }

    [Column("time_horizon")]
    [StringLength(50)]
    public string? TimeHorizon { get; set; }

    [Column("analysis_date")]
    public DateTime? AnalysisDate { get; set; }

    // Navigation properties
    public virtual ICollection<ResearchTask> ResearchTasks { get; set; } = new List<ResearchTask>();
}
