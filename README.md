# 🚀 Enterprise E-Commerce Distributed Scraping & Intelligence Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20(Millions%20Scale)-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Cloud Deployment](https://img.shields.io/badge/Deploy-Railway.com-0B0D0E.svg?logo=railway&logoColor=white)](https://railway.com/)
[![Dashboard](https://img.shields.io/badge/Orchestrator-Flask%203.0%20%2B%20Gunicorn-orange.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Cloud Orchestration](https://img.shields.io/badge/CI%2FCD-20%20GitHub%20Workflows-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Anti-Bot Evasion](https://img.shields.io/badge/Evasion-Cloudflare%20%7C%20FlareSolverr%20%7C%20Undetected--Chrome-green.svg)](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

A distributed, high-throughput **Competitive Intelligence, Web Scraping, and Cloud Orchestration Platform** engineered for enterprise furniture and home retail e-commerce catalogs.

The platform crawls millions of product variants across **40+ competitor storefronts**, bypasses complex anti-bot defenses (Cloudflare Turnstile/Interstitials, audio reCAPTCHAs, rate-limiting, TLS fingerprinting), normalizes catalog data into a unified schema, synchronizes directly into a high-performance **PostgreSQL database engineered for millions of records**, and provides an executive **Flask Operations Dashboard** deployable to **Railway.com** to dispatch, monitor, and stream live logs from **20 cloud workflows** running on GitHub Actions.

---

## 📑 Table of Contents

- [Architectural Overview](#-architectural-overview)
- [Key Capabilities](#-key-capabilities)
- [Repository Structure](#-repository-structure)
- [PostgreSQL Database Architecture (Millions of Records)](#-postgresql-database-architecture-millions-of-records)
- [Deploying to Railway.com](#-deploying-to-railwaycom)
- [Competitor Scraper & Workflow Matrix](#-competitor-scraper--workflow-matrix)
- [Standardized Data Schema](#-standardized-data-schema)
- [Distributed GitHub Actions Infrastructure](#-distributed-github-actions-infrastructure)
- [Google Shopping & SERP Subsystem](#-google-shopping--serp-subsystem)
- [Cloud Operations Orchestrator (Web UI)](#-cloud-operations-orchestrator-web-ui)
- [Installation & Quickstart](#-installation--quickstart)
- [CLI & Script Usage Guide](#-cli--script-usage-guide)
- [Environment Variables Reference](#-environment-variables-reference)
- [Production Best Practices & Troubleshooting](#-production-best-practices--troubleshooting)

---

## 🏗 Architectural Overview

```mermaid
flowchart TD
    subgraph Data Sources ["Target E-Commerce Retailers (40+ Competitors)"]
        S1["Shopify Stores (AFA, English Elm, Grayson Living, France & Son, Grayson Luxury)"]
        S2["Magento / DataLayer Stores (Emma Mason, DRL, BFD, DRO, TV Stands)"]
        S3["Enterprise APIs (Bloomingdale's, Overstock, Bed Bath & Beyond)"]
        S4["Protected Catalogs (Cymax, FurnitureCart, Walmart, Ashley)"]
        S5["Search Engines (Google Shopping SERPs & Merchant Sellers)"]
    end

    subgraph Scraping Engines ["Anti-Bot & Extraction Engines"]
        E1["curl_cffi + cloudscraper (TLS & HTTP/2 Fingerprint Impersonation)"]
        E2["FlareSolverr Cluster (Turnstile / JS Challenge Evasion)"]
        E3["Selenium Undetected-Chromedriver + Audio CAPTCHA Bypass"]
        E4["Scrapy Framework + AutoThrottle"]
    end

    subgraph Orchestration ["Distributed Cloud Orchestration (GitHub Actions)"]
        O1["Sitemap Discovery & Dynamic Matrix Planner"]
        O2["Partition Balancer (NTILE on 30-Day Sales Volume)"]
        O3["Parallel Worker Chunks (20 Standardized Workflows)"]
        O4["Automated Store-to-Store Chained Workflows (Shopify & DRL)"]
        O5["Automated PostgreSQL Bulk Ingestion (sync_to_postgres.py)"]
    end

    subgraph Storage ["Primary Storage Tier (Railway.com Managed)"]
        PG[("PostgreSQL Cluster: competitor_products (Millions of Records)")]
        PG_IDX["High-Speed B-Tree, BRIN & Trigram GIN Indexes"]
        FTP_BACKUP[("Optional Secondary FTP Backup Archive")]
    end

    subgraph Control ["Management & Operations (Railway Web Service)"]
        DASH["Flask GitHub Actions Orchestrator (Gunicorn on Railway $PORT)"]
        CLI["Unified CLI Runner (scrape.py)"]
        DB_SYNC["PostgreSQL Bulk Importer (sync_to_postgres.py)"]
    end

    Control <--> Orchestration
    Data Sources --> Scraping Engines
    Scraping Engines --> Orchestration
    Orchestration --> Storage
    Storage <--> Control
```

---

## ⚡ Key Capabilities

- **PostgreSQL Database Storage for Millions of Records**: High-scale catalog database replacing legacy FTP delivery. Engineered with unlogged staging tables, `COPY` streaming, and `ON CONFLICT DO UPDATE` upserts reaching speeds of **50,000–150,000 records/minute** with zero duplicate products.
- **Railway.com Native Deployment**: Ready-to-deploy specifications with `railway.json`, `Procfile`, production `Dockerfile`, dynamic `$PORT` binding, and automatic connection to Railway's managed PostgreSQL via `DATABASE_URL`.
- **Cloud Operations Orchestrator**: Interactive Flask Web Dashboard (`dashboard/app.py`) communicating with the GitHub REST API to trigger, monitor, configure parameters, and stream live terminal logs from all 20 cloud scraping workflows without requiring page reloads.
- **Automated Workflow Database Sync**: GitHub Actions scraping workflows automatically ingest their merged product CSV datasets directly into Railway PostgreSQL via `sync_to_postgres.py`.
- **Advanced Anti-Bot Evasion**:
  - `curl_cffi` with TLS fingerprint impersonation to bypass Cloudflare bot mitigation without browser overhead.
  - `FlareSolverr` microservice integration for automated JavaScript challenge and Turnstile resolution.
  - `undetected-chromedriver` with automated audio reCAPTCHA solving via Google Speech Recognition.
- **Multi-Store Sequential Chaining**:
  - **Shopify Multi-Store**: Automated chained crawl of 5 stores (`AFA Stores` → `English Elm` → `Grayson Living` → `France & Son` → `Grayson Luxury`).
  - **DRL Multi-Store**: Automated chained crawl of 4 stores (`Bedroom Furniture Discounts` → `Discount Living Rooms` → `Dining Rooms Outlet` → `TV Stands Outlet`).
- **Sales-Weighted Crawl Balancing**: Partitions Google Shopping and retailer scraping tasks across runners using database window functions (`NTILE(4) OVER (ORDER BY mfr_sales_30d DESC)`).

---

## 📂 Repository Structure

```text
.
├── scrape.py                            # Unified CLI runner for all competitors
├── sync_to_postgres.py                  # High-speed PostgreSQL bulk sync pipeline (Railway ready)
├── init_db.py                           # Universal database initializer (PostgreSQL / MySQL)
├── competitors.json                     # Registry of 40+ competitor configs and scraper mappings
├── requirements.txt                     # Root dependency specifications (psycopg2, gunicorn, etc.)
├── .env.example                         # Environment template with Railway & GitHub credentials
│
├── Procfile                             # Railway & Heroku WSGI entrypoint (gunicorn)
├── railway.json                         # Railway Nixpacks deployment configuration
├── Dockerfile                           # Multi-stage production container for Railway/Docker
├── .railwayignore                       # Excludes local artifacts & venv from Railway builds
│
├── db/                                  # Database DDL & Schema Management
│   └── schema.sql                       # PostgreSQL schema optimized for millions of records
│
├── dashboard/                           # Flask-based GitHub Actions Operations Orchestrator
│   ├── app.py                           # Orchestrator backend: REST API, workflow schema, DB stats
│   ├── templates/                       # Jinja2 UI templates (index.html with DB status badge)
│   └── static/                          # UI assets (style.css, design system)
│
├── resolve_redirects.py                 # Multi-threaded Google Shopping redirect cleaner
├── import_csv.py                        # Batch MySQL product importer with upsert logic
│
├── shopify-scrapper/                    # Cloudflare-resistant Shopify scraper
│   ├── shopifyscrap-cloudflare.py       # Multi-store crawler (AFA, English Elm, Grayson, etc.)
│   ├── run_concurrent.py                # Local concurrent multi-worker runner
│   └── readme.md                        # Component documentation
│
├── gshopping/                           # Google Shopping scraper subsystem
│   ├── gscrapper.py                     # Undetected-Chromedriver scraper with audio captcha solver
│   ├── gscraper_pg.py                   # High-scale PostgreSQL distributed claiming engine
│   ├── solvecaptcha.py                  # Google SpeechRecognition audio captcha bypass
│   ├── export_reports.py                # Competitive pricing report generator
│   └── scraper.sql                      # SQL diagnostic queries and table schemas
│
├── drl/                                 # Magento / DataLayer-based fast scrapers
│   ├── drl_scraper_fast.py              # Discount Living Rooms, BFD, Dining Rooms Outlet, TV Stands
│   └── em_scraper_fast.py               # Emma Mason scraper with FlareSolverr integration
│
├── cymax/ & cymax_scraper/              # Cymax 500k+ URL scraper with FlareSolverr bypass
│   ├── cymax.py                         # Core sitemap chunk & product detail crawler
│   └── cymaxv2.py                       # V2 streaming parser
│
├── ovs-bbb/                             # Overstock & Bed Bath & Beyond API scrapers
│   ├── ovr.py                           # Overstock product & variant scraper
│   └── bbb.py                           # Bed Bath & Beyond SKU extractor
│
├── fpfc/                                # FurnitureCart & FurniturePick scrapers
│   ├── fp_fc_scraper.py                 # Bundle variation & option extractor
│   └── generate_chunks.py               # Sitemap chunk generator for GitHub Actions
│
├── bisonoffice/                         # BisonOffice scraper with ?bo=0 parameter bypass
├── blooming-dales/                      # Bloomingdale's digital XAPI product scraper
├── colemanfurniture_brand_file_scraper/ # Scrapy-based Coleman & Ashley Furniture brand scraper
├── luxedecor/                           # LuxeDecor curl_cffi scraper with rate-limit evasion
├── unlimited_furniture/                 # Unlimited Furniture Group scraper with PLP skip logic
├── walmart/                             # Walmart catalog crawler with CAPTCHA handling
│
├── scripts/
│   └── trigger_partitions.py            # Multi-account GitHub Action partition trigger
│
└── .github/workflows/                   # 20 Standardized Platform GitHub Actions Workflows
```

---

## 🐘 PostgreSQL Database Architecture (Millions of Records)

To replace slow FTP file drops with an enterprise database that can store and query millions of competitor records without table locks or latency degradation, the platform uses **PostgreSQL 14+** (`db/schema.sql`).

### Database Table: `competitor_products`

```sql
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
```

### High-Throughput Scaling & Upsert Strategy

1. **Idempotent Composite Index**:
   ```sql
   CREATE UNIQUE INDEX uq_competitor_product_variant
   ON competitor_products (store, COALESCE(ref_product_id, ''), COALESCE(ref_variant_id, ''), md5(ref_product_url));
   ```
   Ensures that repeated crawls of the same store update existing records (price, inventory, status, date) instead of inserting duplicate rows.

2. **Ultra-Fast Staging COPY + UPSERT Pipeline (`sync_to_postgres.py`)**:
   - Rather than executing millions of individual `INSERT` queries (which bottleneck at ~500 rows/sec), `sync_to_postgres.py` streams CSV batches into an in-memory buffer, copies them into an unlogged temporary table via PostgreSQL binary `COPY`, and runs a set-based `INSERT ... ON CONFLICT DO UPDATE`.
   - **Throughput**: Easily sustains **50,000 to 150,000 rows per minute**.

3. **High-Speed Query Indexes**:
   - B-Tree indexes on `store`, `ref_brand_name`, `ref_price`, `date_scraped`.
   - Partial B-Tree indexes on `ref_sku`, `ref_gtin` (UPC/barcode), and `ref_mpn` (ignoring NULLs/empty strings to keep index size minimal).
   - PostgreSQL `pg_trgm` GIN index on `ref_product_name` for instant fuzzy title searches across millions of records:
     ```sql
     CREATE INDEX idx_products_name_trgm ON competitor_products USING gin (ref_product_name gin_trgm_ops);
     ```

4. **CLI Utilities**:
   ```bash
   # Initialize tables and indexes
   python sync_to_postgres.py --init-db

   # Check database status and record counts across all stores
   python sync_to_postgres.py --status

   # Manually sync any scraped CSV file
   python sync_to_postgres.py --csv cymax_full.csv --store cymax
   ```

---

## 🚂 Deploying to Railway.com

The platform is pre-configured for one-click deployment on **[Railway.com](https://railway.com/)** using either Nixpacks or Docker:

### Step 1: Create a Railway Project
1. Log in to [Railway.com](https://railway.com/) and click **New Project**.
2. Select **Deploy from GitHub repo** and choose `multi-site-scraper`.

### Step 2: Add a PostgreSQL Database Service
1. In your Railway Project canvas, click **+ New** → **Database** → **Add PostgreSQL**.
2. Railway will automatically provision a managed PostgreSQL instance and inject `DATABASE_URL` into your project environment.

### Step 3: Configure Environment Variables
In your Railway web service settings, add the following variables:

| Variable | Recommended Value / Description |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` *(Automatically linked by Railway)* |
| `GITHUB_TOKEN` | Your GitHub Personal Access Token (with `repo` & `actions:write` scope) |
| `GITHUB_REPO` | `vorarahul4700/multi-site-scraper` |
| `GITHUB_BRANCH` | `main` |
| `PORT` | *(Injected automatically by Railway, defaults to 5050)* |

### Step 4: Link GitHub Actions to Railway PostgreSQL
To allow cloud scraping workflows running in GitHub Actions to ingest data directly into your Railway PostgreSQL database:
1. Copy the **Public Connection URL** (or `DATABASE_URL`) from your Railway PostgreSQL service dashboard.
2. In your GitHub repository, navigate to **Settings** → **Secrets and variables** → **Actions**.
3. Create a secret named **`DATABASE_URL`** and paste your Railway PostgreSQL connection string.
4. *Now, whenever any scraping workflow finishes running, it will automatically stream all scraped records into your Railway database!*

### Deployment Specifications
- **Builder**: Nixpacks (default) configured via `railway.json` and `Procfile`.
- **WSGI Server**: Gunicorn running 2 worker processes with 4 threads each (`gunicorn dashboard.app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`).
- **Container Build**: Alternatively supported via multi-stage `Dockerfile`.

---

## 🌐 Competitor Scraper & Workflow Matrix

The platform maps each target store to both a dedicated local Python engine and a cloud-orchestrated GitHub Actions workflow:

| Platform / Store Name | Workflow Title | GitHub Actions File | Storage & Database Pipeline | Anti-Bot Strategy | Script Location |
|---|---|---|---|---|---|
| **Shopify Stores** (AFA, English Elm, Grayson Living, France & Son, Grayson Luxury) | `Shopify Stores (AFA, English Elm, Grayson Living, France & Son, Grayson Luxury)` | `shopifyscrapper-cloudflare.yml` | PostgreSQL Bulk Sync + FTP | `curl_cffi` / `cloudscraper` (TLS impersonation) | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| **DRL Multi-Store** (Bedroom Furniture Discounts, Discount Living Rooms, Dining Rooms Outlet, TV Stands Outlet) | `DRL Multi-Store (Bedroom Furniture, Discount Living, Dining Rooms, TV Stands)` | `drl-scrapper-fast.yml` | PostgreSQL Bulk Sync + FTP | FlareSolverr session pooling + regex | `drl/drl_scraper_fast.py` |
| **Emma Mason** | `Emma Mason` | `em-scrapper-fast.yml` | PostgreSQL Bulk Sync + FTP | FlareSolverr + JS `dataLayer` parsing | `drl/em_scraper_fast.py` |
| **Cymax (V2)** | `Cymax` | `cymaxv2.yml` | PostgreSQL Bulk Sync | FlareSolverr + Sitemap offset chunks | `cymax_scraper/cymaxv2.py` |
| **Cymax (Catalog)** | `Cymax (Catalog)` | `cymax-scraper.yml` | PostgreSQL Bulk Sync + FTP | Chunked XML pagination + proxying | `cymax/cymax.py` |
| **Cymax (Products)** | `Cymax (Products)` | `cymax-sitemap-products.yml` | PostgreSQL Bulk Sync + FTP | Granular URL chunk parser | `cymax/cymax.py` |
| **Ashley Furniture** | `Ashley Furniture` | `ashley_scraper.yml` | PostgreSQL Bulk Sync + FTP | Custom headers + chunk matrix | `colemanfurniture_brand_file_scraper/` |
| **Coleman Furniture** | `Coleman Furniture` | `colemanfurniture_brand_file.yml` | PostgreSQL Bulk Sync + FTP | Scrapy framework + AutoThrottle | `colemanfurniture_brand_file_scraper/` |
| **Bed Bath & Beyond** | `Bed Bath & Beyond` | `bbb-ovs-sku.yml` | PostgreSQL Bulk Sync | Direct REST SKU API requests | `ovs-bbb/bbb.py` |
| **Overstock & Bed Bath & Beyond** | `Overstock & Bed Bath & Beyond` | `ovs-bbb.yml` | PostgreSQL Bulk Sync + FTP | Internal REST API + session token | `ovs-bbb/ovr.py` |
| **Bison Office** | `Bison Office` | `bisonoffice.yml` | PostgreSQL Bulk Sync + FTP | `?bo=0` bypass query parameter | `bisonoffice/bisonoffice.py` |
| **Bloomingdale's** | `Bloomingdale's` | `blooming_dales.yml` | PostgreSQL Bulk Sync + FTP | Digital XAPI endpoint ingestion | `blooming-dales/blooming_dales.py` |
| **FurnitureCart & FurniturePick** | `FurnitureCart & FurniturePick` | `fp-fc-scrapper.yml` | PostgreSQL Bulk Sync + FTP | FlareSolverr session handling | `fpfc/fp_fc_scraper.py` |
| **Google Shopping** | `Google Shopping` | `gshopping_mysql.yml` | PostgreSQL Distributed Claims | Undetected-Chrome + Audio CAPTCHA solver | `gshopping/gscrapper.py` |
| **Google Shopping (Keywords)** | `Google Shopping (Keywords)` | `gshopping_keyword.yml` | PostgreSQL Bulk Sync | SERP keyword matrix crawlers | `gshopping/gscrapper.py` |
| **LuxeDecor** | `LuxeDecor` | `luxedecor.yml` | PostgreSQL Bulk Sync + FTP | `curl_cffi` TLS fingerprint impersonation | `luxedecor/luxedecor.py` |
| **Unlimited Furniture** | `Unlimited Furniture` | `unlimited_furniture.yml` | PostgreSQL Bulk Sync + FTP | `curl_cffi` + PLP skip filter | `unlimited_furniture/unlimited_furniture.py` |
| **Walmart** | `Walmart` | `walmart.yml` | PostgreSQL Bulk Sync + FTP | Rotating User-Agents & retry logic | `walmart/walmart.py` |
| **URL Redirect Resolver** | `URL Redirect Resolver` | `resolve_redirects.yml` | PostgreSQL Claims / URL Cleaner | Multi-threaded HTTP redirect cleaner | `resolve_redirects.py` |
| **GitHub Actions Cleanup** | `GitHub Actions Cleanup` | `cleanEverything.yml` | Log & Artifact Maintenance | *(GitHub API)* | *(GitHub API)* |

---

## 📊 Standardized Data Schema

All scrapers output records following a standardized 17-column CSV schema, ingested automatically into the PostgreSQL `competitor_products` table:

| Column Name | Database Field | Type | Description | Example |
|---|---|---|---|---|
| `Ref Product URL` | `ref_product_url` | TEXT | Canonical URL of the product variant | `https://www.afastores.com/products/adant5750?variant=...` |
| `Ref Product ID` | `ref_product_id` | VARCHAR(255) | Unique store product identifier | `9999104737580` |
| `Ref Variant ID` | `ref_variant_id` | VARCHAR(255) | Specific variant identifier | `51184242589996` |
| `Ref Variant Title`| `ref_variant_title`| VARCHAR(500) | Specific variant name / attributes | `Queen / Espresso` |
| `Ref Category` | `ref_category` | VARCHAR(500) | Breadcrumb or assigned collection name | `Nightstands` |
| `Ref Category URL` | `ref_category_url` | TEXT | Canonical URL of the category page | `https://www.afastores.com/collections/nightstands` |
| `Ref Brand Name` | `ref_brand_name` | VARCHAR(500) | Normalized manufacturer/vendor name | `A-America` |
| `Ref Product Name` | `ref_product_name` | TEXT | Full title of the product item | `A-America - Adamstown 3 Drawer Nightstand` |
| `Ref SKU` | `ref_sku` | VARCHAR(255) | Competitor SKU string | `ADANT5750` |
| `Ref MPN` | `ref_mpn` | VARCHAR(255) | Manufacturer Part Number | `ADANT5750` |
| `Ref GTIN` | `ref_gtin` | VARCHAR(100) | UPC / EAN barcode (digits only) | `767630060698` |
| `Ref Price` | `ref_price` | NUMERIC(14,2) | Variant current selling price | `870.00` |
| `Ref Main Image` | `ref_main_image` | TEXT | Primary high-resolution image URL | `https://cdn.shopify.com/.../adant5750-media-01.jpg` |
| `Ref Quantity` | `ref_quantity` | INTEGER | Available inventory count or indicator | `1` |
| `Ref Group Attr 1` | `ref_group_attr_1` | TEXT | Primary attribute option (e.g., Size) | `Default Title` or `Queen` |
| `Ref Group Attr 2` | `ref_group_attr_2` | TEXT | Secondary attribute option (e.g., Finish)| `Espresso` |
| `Ref Status` | `ref_status` | VARCHAR(50) | Availability state (`active`, `out_of_stock`)| `active` |
| `Date Scraped` | `date_scraped` | TIMESTAMPTZ | UTC timestamp of ingestion | `2026-09-20 11:00:00+00` |

---

## ☁️ Distributed GitHub Actions Infrastructure

The `.github/workflows/` directory contains 20 production workflows that run scraping jobs across GitHub Actions virtual runners:

### Workflow Features
1. **Dynamic Matrix Generation**: Workflows parse target sitemaps in an initial `plan` job, split URLs into chunks (e.g., 2 sitemaps per chunk or 200 URLs per job), and generate a dynamic JSON matrix to spawn parallel runners.
2. **Sequential Multi-Store Chaining**:
   - **Shopify Stores**: Selecting `store: all` automatically executes the sequence:
     $$\text{AFA Stores} \longrightarrow \text{English Elm} \longrightarrow \text{Grayson Living} \longrightarrow \text{France \& Son} \longrightarrow \text{Grayson Luxury}$$
   - **DRL Stores**: Selecting `store: all` automatically executes the sequence:
     $$\text{Bedroom Furniture Discounts} \longrightarrow \text{Discount Living Rooms} \longrightarrow \text{Dining Rooms Outlet} \longrightarrow \text{TV Stands Outlet}$$
3. **Automated Database Ingestion**: As soon as chunks are merged, the workflow invokes `sync_to_postgres.py` using `DATABASE_URL` to ingest tens of thousands of products directly into Railway PostgreSQL.
4. **Scheduled Maintenance & Purging**: `cleanEverything.yml` runs on schedule and on-demand to delete historical logs and expired workflow runs, preventing storage exhaustion.

---

## 🔍 Google Shopping & SERP Subsystem

The `gshopping/` directory contains a specialized pipeline for competitive price extraction from Google Shopping:

1. **Undetected-Chromedriver Crawler (`gscrapper.py`)**: Automates Chrome sessions while bypassing automated bot detection.
2. **Audio reCAPTCHA Auto-Bypass (`solvecaptcha.py`)**: Downloads reCAPTCHA audio payloads, converts `.mp3` to `.wav` via `pydub`, and queries Google Speech Recognition to obtain the solved audio tokens automatically.
3. **Distributed Transactional Claiming (`gscraper_pg.py`)**: Uses PostgreSQL row-level locking (`SELECT ... FOR UPDATE SKIP LOCKED`) so dozens of parallel workers can claim product batches without collisions.
4. **Redirect Resolver (`resolve_redirects.py`)**: Multi-threaded utility that resolves Google Shopping click redirects, extracts clean search URLs, and discards `google.com/sorry` rate-limited endpoints.
5. **Pricing Reports (`export_reports.py`)**: Aggregates scraped seller prices across competitors to generate market pricing intelligence.

---

## 🖥 Cloud Operations Orchestrator (Web UI)

The platform includes an **Executive Operations Dashboard** (`dashboard/app.py` & `dashboard/templates/index.html`) deployable on Railway or run locally:

### Key Capabilities & Interface Design
- **Direct GitHub REST API Orchestration**: Authenticates securely via `GITHUB_TOKEN` to communicate directly with GitHub Actions, eliminating the need to leave the dashboard.
- **Live PostgreSQL Database Badge**: Displays real-time database connectivity and live count of all scraped products stored across the database.
- **Dynamic Parameter Generation**: Automatically parses the `workflow_dispatch` inputs from all 20 YAML workflows with semantic input ordering (Target Store → Volume/Offsets → Concurrency → Anti-Bot / Delays → Delivery).
- **Single-Open Accordions**: Clean parameter panel with zero auto-collapse timeouts; opening another workflow’s parameters automatically collapses previously opened cards.
- **Instant Live Log Streaming**: Dynamic expandable log drawer that streams execution logs in real-time as jobs run without requiring a page refresh.
- **Single-Click Workflow Cancellation**: One-click stop button featuring a clean SVG cross (`✕`) to cancel errant jobs immediately via the GitHub API.
- **Fast Launcher Strip**: One-click quick-action bar to jump directly to or dispatch core high-frequency pipelines.
- **Executive Dark Design System**: Engineered in deep obsidian (`#0d1117`), jewel-toned accent borders, rich status badges, and card filtering by category.

### REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/overview` | `GET` | Fetches live metrics (Workflows, Active Runs, Completed, API Health, DB Status) and recent runs |
| `/api/db/stats` | `GET` | Returns live PostgreSQL connection metrics, total product counts, and store breakdown |
| `/api/workflows` | `GET` | Returns all 20 workflows with parsed metadata, inputs, and latest run states |
| `/api/workflows/<file>/schema` | `GET` | Returns input parameters and default values parsed from the workflow YAML |
| `/api/workflows/<file>/dispatch` | `POST` | Triggers a workflow execution on GitHub with custom parameter overrides |
| `/api/workflows/<id>/logs` | `GET` | Streams sanitized run logs for a specific run ID without page reloads |
| `/api/workflows/<id>/cancel` | `POST` | Cancels an in-progress workflow run on GitHub Actions |
| `/api/runs/recent` | `GET` | Returns the latest workflow execution runs across all pipelines |

---

## 🛠 Installation & Quickstart

### 1. Prerequisites
- Python **3.10+**
- PostgreSQL 14+ (or a Railway.com project with PostgreSQL attached)
- GitHub Personal Access Token (classic or fine-grained with `repo` and `actions:write` permissions)

### 2. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/vorarahul4700/multi-site-scraper.git
cd multi-site-scraper

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
# GitHub Actions Orchestrator
GITHUB_TOKEN=ghp_yourPersonalAccessTokenHere
GITHUB_REPO=vorarahul4700/multi-site-scraper
GITHUB_BRANCH=main
PORT=5050

# PostgreSQL Database (Railway / Production)
DATABASE_URL=postgresql://postgres:password@roundhouse.proxy.rlwy.net:12345/railway
```

### 4. Initialize Database & Launch Dashboard

```bash
# Initialize PostgreSQL schema & indexes
python init_db.py

# Launch the operations dashboard
python dashboard/app.py
```
Open **`http://localhost:5050`** in your browser.

---

## 💻 CLI & Script Usage Guide

### Unified Scraper CLI (`scrape.py`)

List all registered competitors:
```bash
python scrape.py --list
```

Run a specific competitor scraper:
```bash
# Run AFA Stores with 8 concurrent workers
python scrape.py -c afa-stores -w 8 -d 0.5

# Run Overstock
python scrape.py -c overstock -w 4

# Run Cymax
python scrape.py -c cymax -w 6
```

### Direct PostgreSQL Sync CLI (`sync_to_postgres.py`)

```bash
# Initialize schema and indexes
python sync_to_postgres.py --init-db

# Check record count and store breakdown in PostgreSQL
python sync_to_postgres.py --status

# Bulk sync a single CSV file
python sync_to_postgres.py --csv cymaxv2_products_full.csv --store cymax

# Bulk sync an entire directory of CSV chunks
python sync_to_postgres.py --dir ./output_chunks/ --store afa-stores
```

---

## ⚙️ Environment Variables Reference

| Variable | Scope / Component | Description | Default |
|---|---|---|---|
| `DATABASE_URL` | PostgreSQL / Railway | Full PostgreSQL connection URL (`postgresql://user:pass@host:port/db`) | Railway Linked |
| `PGHOST` / `PG_HOST` | PostgreSQL | Host address for PostgreSQL database | `localhost` |
| `PGPORT` / `PG_PORT` | PostgreSQL | Port for PostgreSQL database | `5432` |
| `PGUSER` / `PG_USER` | PostgreSQL | Username for PostgreSQL database | `postgres` |
| `PGPASSWORD` / `PG_PASS`| PostgreSQL | Password for PostgreSQL database | `""` |
| `PGDATABASE` / `PG_DB` | PostgreSQL | Database name for PostgreSQL | `railway` |
| `GITHUB_TOKEN` | Dashboard Orchestrator | GitHub PAT with `repo` and `actions:write` scopes | Required for Dashboard |
| `GITHUB_REPO` | Dashboard Orchestrator | Target GitHub repository (`owner/repo`) | Auto-detected / Required |
| `GITHUB_BRANCH` | Dashboard Orchestrator | Default branch to dispatch workflows against | `main` |
| `PORT` | Dashboard Orchestrator | HTTP port for the web dashboard (auto-injected by Railway) | `5050` |
| `CURR_URL` | Scrapers | Base URL of the target store | Required for CLI |
| `SITEMAP_OFFSET` | Sitemaps | Zero-based index of sitemap chunk to process | `0` |
| `MAX_SITEMAPS` | Sitemaps | Total sitemaps to process (`0` = all discovered) | `0` |
| `MAX_URLS_PER_SITEMAP`| Sitemaps | Product URL limit per sitemap (`0` = unlimited) | `0` |
| `MAX_WORKERS` | Scrapers / Threading | Concurrency limit for parallel requests | `4` |
| `REQUEST_DELAY` | Scrapers | Base sleep delay between HTTP requests (seconds) | `1.0` |
| `FLARESOLVERR_URL` | Cloudflare Evasion | Endpoint of active FlareSolverr instance | `http://localhost:8191/v1` |
| `FTP_HOST` | Optional Secondary Backup | Target FTP server address for CSV backup uploads | `""` |

---

## 🛡 Production Best Practices & Troubleshooting

### 1. PostgreSQL Performance with Millions of Records
- `sync_to_postgres.py` uses temporary unlogged staging tables with binary `COPY` to ingest tens of thousands of rows within seconds, bypassing individual SQL insert statement overhead.
- Indexes on `ref_sku`, `ref_gtin`, and `ref_mpn` use partial indexing (`WHERE ref_sku IS NOT NULL AND ref_sku != ''`) to ensure index trees remain compact and fit in RAM.
- Use `python sync_to_postgres.py --status` to monitor store distribution and scrape timestamps.

### 2. Cloudflare 403 Forbidden / Challenge Loops
- For Shopify sites, use `shopify-scrapper/shopifyscrap-cloudflare.py`. It uses `curl_cffi` to mimic Chrome TLS fingerprints without loading browser overhead.
- Ensure `FLARESOLVERR_URL` is active when running `cymax`, `fpfc`, or `em_scraper`.

### 3. Google Shopping CAPTCHAs
- If Google Shopping redirects to `google.com/sorry`:
  - `gshopping/solvecaptcha.py` will attempt an audio challenge bypass using Google Speech Recognition.
  - Run `resolve_redirects.py` to extract clean search URLs from Google redirect strings.

---

## 📄 License & Terms

This repository is maintained for competitive intelligence and catalog monitoring. Ensure compliance with target site terms of service, robots.txt directives, and local data collection regulations.
