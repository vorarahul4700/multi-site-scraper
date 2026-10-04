-- ============================================================================
-- Enterprise PostgreSQL Schema for Millions of Competitor Product Records
-- Designed for Railway.com & Distributed Scraping Pipelines
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ----------------------------------------------------------------------------
-- Core Products Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitor_products (
    id BIGSERIAL PRIMARY KEY,
    store VARCHAR(100) NOT NULL,
    ref_product_url TEXT NOT NULL,
    ref_product_id VARCHAR(255),
    ref_variant_id VARCHAR(255),
    ref_variant_title VARCHAR(500),
    ref_category VARCHAR(500),
    ref_category_url TEXT,
    ref_brand_name VARCHAR(500),
    ref_product_name TEXT,
    ref_sku VARCHAR(255),
    ref_mpn VARCHAR(255),
    ref_gtin VARCHAR(100),
    ref_price NUMERIC(14, 2),
    ref_main_image TEXT,
    ref_quantity INTEGER DEFAULT 1,
    ref_group_attr_1 TEXT,
    ref_group_attr_2 TEXT,
    ref_status VARCHAR(50) DEFAULT 'active',
    raw_json JSONB,
    date_scraped TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Deduplication & High-Concurrency Upsert Index
-- Uses store + product_id + variant_id + MD5(url) to guarantee idempotency
-- ----------------------------------------------------------------------------
CREATE UNIQUE INDEX IF NOT EXISTS uq_competitor_product_variant
ON competitor_products (
    store,
    COALESCE(ref_product_id, ''),
    COALESCE(ref_variant_id, ''),
    md5(ref_product_url)
);

-- ----------------------------------------------------------------------------
-- Performance Indexes Engineered for Millions of Rows
-- ----------------------------------------------------------------------------
-- Fast filtering by store platform
CREATE INDEX IF NOT EXISTS idx_products_store 
ON competitor_products (store);

-- Partial indexes for SKU, GTIN/UPC, and MPN matching
CREATE INDEX IF NOT EXISTS idx_products_sku 
ON competitor_products (ref_sku) 
WHERE ref_sku IS NOT NULL AND ref_sku != '';

CREATE INDEX IF NOT EXISTS idx_products_gtin 
ON competitor_products (ref_gtin) 
WHERE ref_gtin IS NOT NULL AND ref_gtin != '';

CREATE INDEX IF NOT EXISTS idx_products_mpn 
ON competitor_products (ref_mpn) 
WHERE ref_mpn IS NOT NULL AND ref_mpn != '';

-- Brand & Price indexing for analytical queries
CREATE INDEX IF NOT EXISTS idx_products_brand 
ON competitor_products (ref_brand_name);

CREATE INDEX IF NOT EXISTS idx_products_price 
ON competitor_products (ref_price);

CREATE INDEX IF NOT EXISTS idx_products_status 
ON competitor_products (ref_status);

-- Recent scrapes sorting
CREATE INDEX IF NOT EXISTS idx_products_date_scraped 
ON competitor_products (date_scraped DESC);

-- Trigram fuzzy text index for rapid product search across millions of records
CREATE INDEX IF NOT EXISTS idx_products_name_trgm 
ON competitor_products USING gin (ref_product_name gin_trgm_ops);

-- ----------------------------------------------------------------------------
-- Automated updated_at Trigger
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_competitor_products_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_competitor_products_timestamp ON competitor_products;
CREATE TRIGGER trg_update_competitor_products_timestamp
BEFORE UPDATE ON competitor_products
FOR EACH ROW
EXECUTE FUNCTION update_competitor_products_timestamp();
