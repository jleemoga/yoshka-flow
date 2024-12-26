# Environmental Impact Data Collection

## Primary Objective
For the company Nestlé, retrieve and populate the **Environmental Impact** category in the hierarchical JSON structure below. Ensure all metrics are thoroughly populated using the provided scoring criteria, including confidence scores and data quality adjustments.

---

## Step-by-Step Instructions

### 1. Reference Identification
- Collect data from the most relevant, verifiable sources (e.g., sustainability reports, regulatory filings, verified third-party audits).
- Ensure sources meet the following criteria:
  - **Current**: Data < 12 months old.
  - **Diverse**: At least two independent sources per metric if possible.
  - **Reliable**: Prioritize sources with high credibility (e.g., peer-reviewed studies, government data).
  - **Verification**: Flag whether each data point is independently verified (third-party audit/certification).
- Populate the `references` array with objects containing:
  - `reference_id` (a local or numeric ID to be referenced by metrics).
  - `source_type` (e.g., "Sustainability Report").
  - `url` (if available).
  - `date_accessed` (YYYY-MM-DD).
  - `verified` (boolean).
  - `credibility` (0.0–1.0).
  - `notes` (additional context).

---

### 2. Metric-Specific Data Retrieval
Under the **Environmental Impact** category, retrieve or calculate the following metrics organized by section. For each metric:

- **`raw_data`**:  
  - **`value`**: The actual data point(s) (e.g., "3.16 MtCO2e", or a JSON object `{ "scope_1": "3.16" }`).  
  - **`unit`**: The units of measurement (e.g., "MtCO2e").  
  - **`reference_ids`**: An array of `reference_id` values that back up this metric.  
- **`assigned_points`**: Reflect compliance with scoring criteria.  
- **`confidence_score`**: A composite confidence rating (0.0–1.0), considering data quality, source diversity, and credibility.  
- **`explanation`**: A brief justification, referencing the data points and sources.

#### Sections & Metrics (Example)
- **Carbon & Energy**
  - GHG Emissions Reporting (Scope 1, 2, 3)
  - Emissions Trend & Intensity
  - Renewable Energy Use
  - ...
- **Waste Management**
  - Packaging Waste Reduction
  - Recycling & Diversion Rates
  - ...
- **Water & Resource Stewardship**
  - Water Usage Efficiency
  - ...
- **Biodiversity & Land Use**
  - Biodiversity Impact Assessment
  - ...

---

### 3. Cross-Metric Analysis
- Consider interactions across metrics (e.g., how Renewable Energy Use affects GHG Emissions).
- Summarize these insights in your explanations where appropriate.

---

### 4. Confidence Score Calculation
Each metric’s `confidence_score` can be based on:
- **Data recency and completeness** (did you find all required data?).
- **Source diversity** (multiple independent references).
- **Source credibility** (average credibility rating of each reference).
  
You may use an internal formula or the suggested weighting approach if needed.

---

### 5. Data Validation
- Check for recency (< 12 months).
- Ensure completeness for each metric; flag any missing fields.
- Aim for at least one high-credibility (≥ 0.8) source if possible.

---

### 6. Populate JSON
Use the structure below to generate your final JSON. **Do not** include a top-level `year` field.

```json
{
  "company_id": "<string or code>",
  "name": "Nestlé S.A.",
  "references": [
    {
      "reference_id": <integer or string>,
      "source_type": "<string>",
      "url": "<string>",
      "date_accessed": "<YYYY-MM-DD>",
      "verified": <boolean>,
      "credibility": <float>,
      "notes": "<string>"
    }
  ],
  "categories": [
    {
      "name": "Environmental Impact",
      "sections": [
        {
          "name": "<Section Name>",
          "metrics": [
            {
              "name": "<Metric Name>",
              "raw_data": {
                "value": "<string or object>",
                "unit": "<string>",
                "reference_ids": [<one or more reference_id>]
              },
              "assigned_points": <integer>,
              "confidence_score": <float>,
              "explanation": "<string>"
            }
          ]
        }
      ]
    }
  ]
}
