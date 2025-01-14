using Microsoft.AspNetCore.Mvc;

namespace Api.Features.Health.Controllers;

[ApiController]
[Route("")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            Status = "Online",
            Timestamp = DateTime.UtcNow,
            Version = "1.0.0"
        });
    }
}
