Below is a high-level technical documentation that outlines the **flow and services** Yoshka requires for its AI-driven back end. This document is **database-agnostic** in terms of specific schema details—while still referencing the major entities (companies, products, references, metrics) as needed for context. The goal is to help an **AI developer** (or team) understand how the pieces fit together and what steps are necessary to implement the system.

---

# YoshkaFlow: Technical Architecture and Service Flow

## 1. Overview

**Yoshka** needs a back end that orchestrates:
1. **Entity Search & Creation**: Users can search for a company or product. If not found, they can create a new entry after AI validation.  
2. **AI Research & Reference Management**: Once an entity is confirmed, AI workflows gather references and produce metrics tied to that entity.  
3. **Indexing & Retrieval**: New entities are indexed in an external search system (e.g., Algolia).  
4. **Job Orchestration**: Multiple steps (validation, research, indexing) run asynchronously in a job queue.

### Primary Components

1. **Next.js Front End**  
   - User interface for searching, creating, and viewing companies/products.  
   - Initiates back-end requests via a REST (or GraphQL) API.

2. **Python API Layer** (e.g., FastAPI or Flask)  
   - Receives requests from the Next.js front end.  
   - Exposes routes such as `/search`, `/validate_query`, `/create_entity`, `/generate_metrics_json`, etc.  
   - Enqueues asynchronous tasks into an **Orchestrator** (job queue) for AI or referencing tasks.

3. **Orchestrator / Job Queue** (e.g., Celery, RQ, Airflow)  
   - Manages asynchronous jobs like:
     - **Query Validation** (check for profanity or nonsense).  
     - **AI Research** (using prompt templates, searching references, summarizing data).  
     - **Index in Algolia** (or another search engine) for findability.  
   - Supports retries, scheduling, and chaining of tasks.

4. **AI Services / Tools**  
   - Headless browser search or external API calls.  
   - Prompt-based LLM tasks for summarizing references.  
   - Additional data extraction or NLP tasks.

5. **External Search** (e.g., Algolia)  
   - Provides fast entity lookups by name, keywords, or attributes.  
   - Called by the orchestrator after a new company/product is created.

---

## 2. Typical Workflow

Below is the **end-to-end** flow from user interaction in the front end to the final AI outputs and indexing.

### 2.1. Entity Search & Potential Creation

1. **User Searches**:  
   - The front end calls `/api/search?query="Nestlé"`.  
   - The back end checks internal data (and/or Algolia) for matching entities.
2. **No Results → Prompt to Create**:  
   - If no match is found, the user is offered an option to “Create New Entity.”  
   - The front end calls `/api/validate_query` with the proposed name.

3. **Query Validation** (AI or rule-based):
   - The Python API enqueues a **validate_query** job in the orchestrator.  
   - A worker checks for profanity, nonsense, or duplication.  
   - If valid, the user can finalize creation; if not, it returns an error.

4. **Creation**:  
   - On success, the system calls `/api/create_entity` with the validated name, type (“company” or “product”), etc.  
   - The Python service creates the new entity record in the database (details are abstracted away here).  
   - Returns a new internal ID (e.g., a UUID) to the front end.

### 2.2. AI Research Pipeline

1. **Research Job**:  
   - The front end (or automatically) calls `/api/start_research` for the entity.  
   - The Python API enqueues a **research_entity** job in the orchestrator.  
2. **Gather References**:  
   - Worker tasks might do a **tool call** (e.g., a headless browser or web API) to locate references (reports, articles, official pages).  
   - The worker inserts or updates references for that entity, and logs them in the system (the DB details are out of scope, but each reference has `source_type`, `url`, etc.).
3. **Generate Metrics**:  
   - The AI calls a set of **prompt templates** to produce or refine metrics.  
   - Each metric can store `raw_data` (JSON structure from the LLM) plus fields like `name`, `confidence_score`, `assigned_points`, etc.  
   - References can be linked to metrics if the LLM cites them.

### 2.3. Indexing

1. **Index Job**:  
   - After the new entity is fully created, the system enqueues an **index_in_algolia** job.  
   - The worker fetches the entity’s essential fields (name, ID, etc.) and calls the Algolia Admin API to upsert the record.  
   - Subsequent user searches in the front end now surface the new entity.

---

## 3. Service & Endpoint Summary

Below is a **non-exhaustive** list of endpoints/services. The actual naming and structure might differ based on your conventions.

1. **Validation**  
   - **`POST /api/validate_query`**  
     - **Request**: `{ "query": "Nestlé" }`  
     - **Response**: `{ "valid": true, "sanitizedName": "Nestlé" }`  
     - Internally, enqueues a Celery/RQ task to check profanity or nonsense.

2. **Entity Creation**  
   - **`POST /api/create_entity`**  
     - **Request**: `{ "entity_type": "company", "name": "Nestlé S.A." }`  
     - **Response**: `{ "entity_id": "<UUID>", "created": true }`

3. **Search**  
   - **`GET /api/search?query=XYZ`**  
     - **Response**: 
       ```json
       {
         "results": [
           { "company_id": "<UUID>", "name": "Nestlé S.A." },
           ...
         ]
       }
       ```
     - If empty, the front end prompts creation.

4. **Start Research**  
   - **`POST /api/start_research`**  
     - **Request**: `{ "entity_id": "<UUID>" }`  
     - **Response**: `{ "job_id": "<UUID of the queued job>" }`  
     - Worker fetches references, runs AI tasks, populates metrics.

5. **Generate Final JSON** (Optional)  
   - **`GET /api/generate_metrics_json?entity_id=<UUID>`**  
     - Returns a consolidated JSON with references, categories, sections, metrics, etc.

6. **Index in Algolia** (Internally triggered)  
   - Worker function that calls the Algolia Admin API:  
     - **`algoliaClient.saveObject(...)`** with the entity’s name, ID, etc.

---

## 4. Orchestrator / Job Queue Details

While the exact implementation can vary (Celery, RQ, Airflow, etc.), the overall pattern is:

1. **API Layer** receives a request.  
2. **Enqueue Job**: e.g., `research_entity.delay(entity_id=...)`.  
3. **Worker** picks up the job:  
   1. Fetch relevant data (like the new entity’s name).  
   2. Call external tools (e.g., search plugin, LLM prompts).  
   3. Store references, produce metrics.  
   4. Optionally enqueue **index_in_algolia** as a follow-up job.  

### Common Task Types

- **`validate_query`**  
  - Checks user-submitted names for profanity or invalid content.  
- **`research_entity`**  
  - Gathers references, runs AI prompt templates, inserts new metrics.  
- **`index_in_algolia`**  
  - Publishes the entity to Algolia.  
- **`generate_summary_json`** (if you do it asynchronously)  
  - Joins references and metrics data into a final structure.

---

## 5. AI Services & Tools

**Your AI developer** will focus on these tasks:

1. **Query Validation**  
   - Possibly uses a small LLM or a rule-based approach to see if the text is real, non-profane, and not nonsense.  
   - Could be integrated with a profanity library or an external classification API.

2. **Browser Search or API Calls**  
   - Headless browser (Playwright/Selenium) or direct web requests to gather references.  
   - Summaries or extraction might be done with an LLM (OpenAI, local model, etc.).

3. **Prompt Templates** for Metrics  
   - For each category or research domain, define a custom prompt.  
   - The AI developer sets up a pipeline so that once references are found, the system calls the right prompts to produce metrics.  
   - The output is stored in the `raw_data` field for each metric.

4. **Indexing**  
   - Typically simpler: the worker just calls `algoliaClient.saveObject({ ... })`.  
   - The AI developer ensures the payload is consistent (unique ID, name, etc.).

---

## 6. Error Handling & Retries

1. **Validation Errors**  
   - If `validate_query` fails, the front end is informed. The user can’t create the entity.  
2. **AI Request Failures**  
   - The orchestrator can retry tasks on network or timeouts (configurable in Celery/RQ).  
3. **Partial Data**  
   - If an AI step fails mid-way, references might already be inserted. Logging partial results is recommended so the process can resume.

---

## 7. Security & Authorization

- You can add **authentication** tokens (JWT, OAuth) if needed.  
- Some endpoints (like entity creation or research) should require elevated privileges or be admin-only to prevent spamming or malicious input.  
- External search tools (Algolia, etc.) require secure API keys.

---

## 8. Summary of the Implementation Steps

1. **Set Up Python API**:  
   - Use a framework like **FastAPI** or **Flask**.  
   - Expose endpoints: `/search`, `/validate_query`, `/create_entity`, `/start_research`, `/generate_metrics_json`, etc.

2. **Integrate Orchestrator**:  
   - Choose **Celery + Redis** or **RQ + Redis**, or a similar approach.  
   - Write tasks such as `validate_query_task`, `research_entity_task`, `index_in_algolia_task`.

3. **AI/LLM Integration**:  
   - Decide how you’ll call the LLM (OpenAI, local model, etc.).  
   - Implement logic to gather references, parse them, and store them as needed.  
   - Create prompt templates for metrics.

4. **Algolia Indexing**:  
   - Write a function that receives an entity’s data, calls `saveObject` on Algolia’s Admin API.  
   - Enqueue it after the entity or product is fully created.

5. **Front-End Hooks**:  
   - Next.js calls these endpoints, shows job statuses to users (via polling or websockets), displays final metrics JSON or newly indexed results.

By following this **high-level plan**, the AI developer can easily grasp how to integrate their tasks into the broader YoshkaFlow system—without diving into the underlying database schema (which is managed, but not deeply detailed here). The main focus is on orchestrating AI-based processes (validation, reference gathering, metric generation) and hooking them up to the external search indexing flow.