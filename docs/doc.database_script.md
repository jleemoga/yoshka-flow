-- 0) Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) Create job_status_enum if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_status_enum') THEN
        CREATE TYPE job_status_enum AS ENUM ('pending', 'in_progress', 'completed', 'failed');
    END IF;
END$$;

-- 2) Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id      UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    description      TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 3) Companies
CREATE TABLE IF NOT EXISTS companies (
    company_id       UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name             TEXT NOT NULL,
    stock_ticker     TEXT,
    headquarters     TEXT,
    validated        BOOLEAN NOT NULL DEFAULT FALSE,
    algolia_object_id TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 4) Products
CREATE TABLE IF NOT EXISTS products (
    product_id       UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id       UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    name             TEXT NOT NULL,
    sku              TEXT,
    validated        BOOLEAN NOT NULL DEFAULT FALSE,
    algolia_object_id TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 5) Sources
CREATE TABLE IF NOT EXISTS sources (
    source_id        UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id       UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    product_id       UUID REFERENCES products(product_id) ON DELETE CASCADE,
    source_type      TEXT NOT NULL,
    url              TEXT,
    date_accessed    DATE,
    verified         BOOLEAN NOT NULL DEFAULT FALSE,
    credibility      NUMERIC(3,2) CHECK (credibility >= 0 AND credibility <= 1),
    notes            TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 6) Metrics
CREATE TABLE IF NOT EXISTS metrics (
    metric_id        UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id       UUID REFERENCES companies(company_id) ON DELETE CASCADE,
    product_id       UUID REFERENCES products(product_id) ON DELETE CASCADE,
    category_id      UUID REFERENCES categories(category_id) ON DELETE SET NULL,
    section_name     TEXT,  -- store your "Carbon & Energy" label here
    name             TEXT NOT NULL,
    description      TEXT,
    raw_data         JSONB,
    assigned_points  INTEGER,
    confidence_score NUMERIC(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    explanation      TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 7) metric_sources bridging (many-to-many)
CREATE TABLE IF NOT EXISTS metric_sources (
    metric_id    UUID NOT NULL REFERENCES metrics(metric_id) ON DELETE CASCADE,
    source_id    UUID NOT NULL REFERENCES sources(source_id) ON DELETE CASCADE,
    PRIMARY KEY (metric_id, source_id)
);

-- 8) AI Jobs
CREATE TABLE IF NOT EXISTS ai_jobs (
    job_id        UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_type      TEXT NOT NULL,
    company_id    UUID REFERENCES companies(company_id) ON DELETE SET NULL,
    product_id    UUID REFERENCES products(product_id) ON DELETE SET NULL,
    status        job_status_enum NOT NULL DEFAULT 'pending',
    result_data   JSONB,
    started_at    TIMESTAMP WITH TIME ZONE,
    completed_at  TIMESTAMP WITH TIME ZONE,
    created_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 9) Search Queries (optional)
CREATE TABLE IF NOT EXISTS search_queries (
    search_id            UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id              UUID,
    query_text           TEXT NOT NULL,
    filters              JSONB,
    result_count         INTEGER,
    execution_time_ms    INTEGER,
    created_at           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for foreign keys and commonly queried fields
CREATE INDEX IF NOT EXISTS idx_products_company_id    ON products(company_id);
CREATE INDEX IF NOT EXISTS idx_sources_company_id     ON sources(company_id);
CREATE INDEX IF NOT EXISTS idx_sources_product_id     ON sources(product_id);
CREATE INDEX IF NOT EXISTS idx_metrics_company_id     ON metrics(company_id);
CREATE INDEX IF NOT EXISTS idx_metrics_product_id     ON metrics(product_id);
CREATE INDEX IF NOT EXISTS idx_metrics_category_id    ON metrics(category_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_company_id     ON ai_jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_product_id     ON ai_jobs(product_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_status         ON ai_jobs(status);
