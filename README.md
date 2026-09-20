# 🚀 Enterprise E-Commerce Distributed Scraping & Intelligence Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Dashboard-Flask%203.0-orange.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Databases-MySQL%20%7C%20PostgreSQL-4479A1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Cloud Orchestration](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20Matrix-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Anti-Bot Evasion](https://img.shields.io/badge/Evasion-Cloudflare%20%7C%20FlareSolverr%20%7C%20Undetected--Chrome-green.svg)](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

A distributed, high-throughput **Competitive Intelligence and Web Scraping Platform** engineered for large-scale furniture and home retail e-commerce catalogs.

The platform crawls millions of product variants across **40+ competitor storefronts**, bypasses complex anti-bot defenses (Cloudflare Turnstile/Interstitials, audio reCAPTCHAs, rate-limiting, TLS fingerprinting), normalizes catalog data into a unified schema, and syncs production datasets directly to database storage and remote FTP endpoints.

---

## 📑 Table of Contents

- [Architectural Overview](#-architectural-overview)
- [Key Capabilities](#-key-capabilities)
- [Repository Structure](#-repository-structure)
- [Competitor Scraper Matrix](#-competitor-scraper-matrix)
- [Standardized Data Schema](#-standardized-data-schema)
- [Distributed GitHub Actions Infrastructure](#-distributed-github-actions-infrastructure)
- [Google Shopping & SERP Subsystem](#-google-shopping--serp-subsystem)
- [Operations Dashboard (Web UI)](#-operations-dashboard-web-ui)
- [Installation & Quickstart](#-installation--quickstart)
- [CLI & Script Usage Guide](#-cli--script-usage-guide)
- [Environment Variables Reference](#-environment-variables-reference)
- [Production Best Practices & Troubleshooting](#-production-best-practices--troubleshooting)

---

## 🏗 Architectural Overview

```mermaid
flowchart TD
    subgraph Data Sources ["Target E-Commerce Retailers (40+ Competitors)"]
        S1["Shopify Stores (AFA, English Elm, Grayson...)"]
        S2["Magento / DataLayer Stores (Emma Mason, DRL, BFD...)"]
        S3["Enterprise APIs (Bloomingdale's, Overstock, BBB)"]
        S4["Protected Catalogs (Cymax, FurnitureCart, Walmart)"]
        S5["Search Engines (Google Shopping SERPs & Sellers)"]
    end

    subgraph Scraping Engines ["Anti-Bot & Extraction Engines"]
        E1["curl_cffi + cloudscraper (TLS & HTTP/2 Impersonation)"]
        E2["FlareSolverr Cluster (Turnstile / JS Challenge Evasion)"]
        E3["Selenium Undetected-Chromedriver + Audio CAPTCHA Bypass"]
        E4["Scrapy Framework + AutoThrottle"]
    end

    subgraph Orchestration ["Distributed Orchestration (GitHub Actions)"]
        O1["Sitemap Discovery & Dynamic Matrix Planner"]
        O2["Partition Balancer (NTILE on 30-Day Sales)"]
        O3["Parallel Worker Chunks (up to 40+ concurrent runners)"]
        O4["Automated Store-to-Store Chained Workflows"]
    end

    subgraph Storage ["Storage & Delivery Tier"]
        DB1[("MySQL: osb_products & Scraper Catalog")]
        DB2[("PostgreSQL + PgBouncer: Google Shopping Claims")]
        FTP[("Remote FTP Synchronization")]
        CSV[("Standardized CSV Chunks & Artifacts")]
    end

    subgraph Control ["Management & Operations"]
        CLI["Unified CLI Runner (scrape.py)"]
        DASH["Flask Web Dashboard (Port 5050)"]
    end

    Data Sources --> Scraping Engines
    Scraping Engines --> Orchestration
    Orchestration --> Storage
    Storage <--> Control
```

---

## ⚡ Key Capabilities

- **High-Concurrency Distributed Crawling**: Leverages GitHub Actions matrix builds to partition hundreds of XML sitemaps and hundreds of thousands of product URLs across dozens of simultaneous runners.
- **Advanced Anti-Bot Evasion**:
  - `curl_cffi` with TLS fingerprint impersonation to bypass Cloudflare protection without the overhead of headless browsers.
  - `FlareSolverr` microservice integration for automated JavaScript challenge and Turnstile resolution.
  - `undetected-chromedriver` with automated audio reCAPTCHA solving via Google Speech Recognition.
- **Smart Shopify Ingestion**: Queries native Shopify `.json` endpoints first for high-throughput extraction, falling back automatically to HTML scraping and JSON-LD schema parsing.
- **Sales-Weighted Crawl Balancing**: Partitions Google Shopping and retailer scraping tasks across runners using database window functions (`NTILE(4) OVER (ORDER BY mfr_sales_30d DESC)`) to prioritize high-revenue products.
- **Operations Dashboard**: Flask UI providing live process control, terminal log streaming (`deque`), and real-time worker monitoring.
- **Automated Artifact Delivery**: Chunks are merged, deduplicated, and synchronized directly to remote FTP servers and GitHub Actions workflow artifacts.

---

## 📂 Repository Structure

```text
.
├── scrape.py                            # Unified CLI runner for all competitors
├── competitors.json                     # Registry of 40+ competitor configs and scraper mappings
├── requirements.txt                     # Root dependency specifications
├── .env.example                         # Environment variable template
│
├── dashboard/                           # Flask-based web operations dashboard
│   ├── app.py                           # Dashboard server, process manager & workflow runner
│   ├── templates/                       # Jinja2 UI templates (index.html)
│   └── static/                          # UI assets (CSS, styling, JS)
│
├── resolve_redirects.py                 # Multi-threaded Google Shopping redirect cleaner
├── import_csv.py                        # Batch MySQL product importer with upsert logic
├── init_db.py                           # MySQL database schema initializer
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
│   └── bisonoffice.py                   # XML sitemap crawler and product extractor
│
├── blooming-dales/                      # Bloomingdale's digital XAPI product scraper
│   └── blooming_dales.py                # API-driven product data harvester
│
├── colemanfurniture_brand_file_scraper/ # Scrapy-based Coleman & Ashley Furniture brand scraper
│   ├── settings.py                      # Scrapy settings (AutoThrottle, FTP upload)
│   └── scripts/                         # Input URL fetcher & execution runners
│
├── luxedecor/                           # LuxeDecor curl_cffi scraper with rate-limit evasion
├── unlimited_furniture/                 # Unlimited Furniture Group scraper with PLP skip logic
├── walmart/                             # Walmart catalog crawler with CAPTCHA handling
│
├── scripts/
│   └── trigger_partitions.py            # Multi-account GitHub Action partition trigger
│
└── .github/workflows/                   # 20 GitHub Actions CI/CD workflows for cloud execution
```

---

## 🌐 Competitor Scraper Matrix

| Competitor Key | Store Name | Target Platform / Engine | Anti-Bot Bypass Strategy | Script Location |
|---|---|---|---|---|
| `afa-stores` | AFA Stores | Shopify (`.json` + HTML) | `curl_cffi` / `cloudscraper` | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| `english-elm` | English Elm | Shopify (`.json` + HTML) | `curl_cffi` / `cloudscraper` | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| `grayson-living` | Grayson Living | Shopify (`.json` + HTML) | `curl_cffi` / `cloudscraper` | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| `france-and-son` | France & Son | Shopify (`.json` + HTML) | `curl_cffi` / `cloudscraper` | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| `grayson-luxury` | Grayson Luxury | Shopify (`.json` + HTML) | `curl_cffi` / `cloudscraper` | `shopify-scrapper/shopifyscrap-cloudflare.py` |
| `cymax` | Cymax | Custom / Next.js | FlareSolverr + Sitemap Offset | `cymax/cymax.py` |
| `overstock` | Overstock | Internal REST API | Custom headers + session | `ovs-bbb/ovr.py` |
| `bed-bath-beyond` | Bed Bath & Beyond | Internal REST API | Direct SKU / model resolution | `ovs-bbb/bbb.py` |
| `emma-mason` | Emma Mason | Magento (`dataLayer`) | FlareSolverr + JS parsing | `drl/em_scraper_fast.py` |
| `discount-living-rooms`| Discount Living Rooms | Magento (`dataLayer`) | Fast HTTP session + regex | `drl/drl_scraper_fast.py` |
| `bedroom-furniture-discounts` | Bedroom Furniture Disc. | Magento (`dataLayer`) | Fast HTTP session + regex | `drl/drl_scraper_fast.py` |
| `dining-rooms-outlet` | Dining Rooms Outlet | Magento (`dataLayer`) | Fast HTTP session + regex | `drl/drl_scraper_fast.py` |
| `tv-stands-outlet` | TV Stands Outlet | Magento (`dataLayer`) | Fast HTTP session + regex | `drl/drl_scraper_fast.py` |
| `furniture-cart` | Furniture Cart | Custom bundle architecture | FlareSolverr session handling | `fpfc/fp_fc_scraper.py` |
| `bisonoffice` | BisonOffice | XML Sitemaps + HTML | `?bo=0` bypass parameter | `bisonoffice/bisonoffice.py` |
| `bloomingdales` | Bloomingdale's | Enterprise Digital XAPI | Direct API GET requests | `blooming-dales/blooming_dales.py` |
| `luxedecor` | LuxeDecor | Custom Catalog | `curl_cffi` TLS impersonation | `luxedecor/luxedecor.py` |
| `unlimited-furniture-group` | Unlimited Furniture | Custom / PLP Pagination | `curl_cffi` + PLP filter | `unlimited_furniture/unlimited_furniture.py` |
| `coleman-furniture` | Coleman Furniture | Brand Feeds / Scrapy | AutoThrottle + Crawl Matrix | `colemanfurniture_brand_file_scraper/` |
| `google-shopping` | Google Shopping | Search SERP & Sellers | Undetected-Chrome + Audio CAPTCHA | `gshopping/gscrapper.py` |
| `walmart` | Walmart | Custom Web | Rotating UA + Session retry | `walmart/walmart.py` |

---

## 📊 Standardized Data Schema

All scrapers output records following a standardized 17-column CSV schema, ensuring seamless downstream ingestion and analysis:

| Column Name | Type | Description | Example |
|---|---|---|---|
| `Ref Product URL` | String | Canonical URL of the product variant | `https://www.afastores.com/products/adant5750?variant=...` |
| `Ref Product ID` | String | Unique store product identifier | `9999104737580` |
| `Ref Variant ID` | String | Specific variant identifier | `51184242589996` |
| `Ref Category` | String | Breadcrumb or assigned collection name | `Nightstands` |
| `Ref Category URL` | String | Canonical URL of the category page | `https://www.afastores.com/collections/nightstands` |
| `Ref Brand Name` | String | Normalized manufacturer/vendor name | `A-America` |
| `Ref Product Name` | String | Full title of the product item | `A-America - Adamstown 3 Drawer Nightstand` |
| `Ref SKU` | String | Competitor SKU string | `ADANT5750` |
| `Ref MPN` | String | Manufacturer Part Number | `ADANT5750` |
| `Ref GTIN` | String | UPC / EAN barcode (digits only) | `767630060698` |
| `Ref Price` | Float | Variant current selling price | `870.00` |
| `Ref Main Image` | String | Primary high-resolution image URL | `https://cdn.shopify.com/.../adant5750-media-01.jpg` |
| `Ref Quantity` | Integer| Available inventory count or in-stock indicator | `1` |
| `Ref Group Attr 1` | String | Primary attribute option (e.g., Size, Color) | `Default Title` or `Queen` |
| `Ref Group Attr 2` | String | Secondary attribute option (e.g., Finish) | `Espresso` |
| `Ref Status` | String | Availability state (`active`, `out_of_stock`, `discontinued`) | `active` |
| `Date Scraped` | Datetime | UTC timestamp of ingestion (`YYYY-MM-DD HH:MM:SS`) | `2026-09-20 11:00:00` |

---

## ☁️ Distributed GitHub Actions Infrastructure

The `.github/workflows/` directory contains 20 production workflows that run scraping jobs across GitHub Actions virtual runners.

### Workflow Features
1. **Dynamic Matrix Generation**: Workflows parse target sitemaps in an initial `plan` job, split URLs into chunks (e.g., 2 sitemaps per chunk or 200 URLs per job), and generate a dynamic JSON matrix to spawn parallel runners.
2. **Sequential Store Chaining**: For Shopify stores, selecting `store: all` triggers an automated sequence:
   $$\text{AFA Stores} \longrightarrow \text{English Elm} \longrightarrow \text{Grayson Living} \longrightarrow \text{France \& Son} \longrightarrow \text{Grayson Luxury}$$
3. **Multi-Account Partition Balancing**: The `scripts/trigger_partitions.py` script divides the product catalog across multiple GitHub runner accounts using SQL sales volume quartiles:
   ```sql
   WITH partitioned_products AS (
       SELECT product_id, mfr_sales_30d,
              NTILE(4) OVER (ORDER BY COALESCE(mfr_sales_30d, 0) DESC, product_id ASC) as bucket
       FROM osb_products WHERE status = 1
   )
   ```
4. **Automated FTP & Artifact Delivery**: Completed worker CSV chunks are merged into a single archive and pushed directly to target FTP directories.

---

## 🔍 Google Shopping & SERP Subsystem

The `gshopping/` directory contains a specialized pipeline for competitive price extraction from Google Shopping:

1. **Undetected-Chromedriver Crawler (`gscrapper.py`)**: Automates Chrome sessions while bypassing automated bot detection.
2. **Audio reCAPTCHA Auto-Bypass (`solvecaptcha.py`)**: Downloads reCAPTCHA audio payloads, converts `.mp3` to `.wav` via `pydub`, and queries Google Speech Recognition to obtain the solved audio tokens automatically.
3. **Distributed Transactional Claiming (`gscraper_pg.py`)**: Uses PostgreSQL row-level locking (`SELECT ... FOR UPDATE SKIP LOCKED`) so dozens of parallel workers can claim product batches without collisions.
4. **Redirect Resolver (`resolve_redirects.py`)**: Multi-threaded utility that resolves Google Shopping click redirects, extracts clean search URLs, and discards `google.com/sorry` rate-limited endpoints.
5. **Pricing Reports (`export_reports.py`)**: Aggregates scraped seller prices across competitors to generate market pricing intelligence.

---

## 🖥 Operations Dashboard (Web UI)

A Flask operations dashboard (`dashboard/app.py`) provides an interactive interface for managing local and distributed scraping runs:

- **Process Manager**: Start, monitor, and terminate scrapers with live in-memory terminal streaming (`deque` retaining the last 200 log lines).
- **Environment Overrides**: Set custom concurrency (`MAX_WORKERS`), delays (`REQUEST_DELAY`), and sitemap limits on the fly.
- **Real-Time Statuses**: View active PIDs, start timestamps, execution durations, and exit codes.

To launch the dashboard:
```bash
python dashboard/app.py
```
Open **`http://localhost:5050`** in your browser.

---

## 🛠 Installation & Quickstart

### 1. Prerequisites
- Python **3.10+**
- Google Chrome & compatible ChromeDriver (for Selenium Google Shopping scraping)
- MySQL 8.0+ or PostgreSQL 14+ (optional for database-backed workflows)
- FlareSolverr (optional, for Cloudflare Turnstile bypass endpoints)

### 2. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/vorarahul4700/scraper.git
cd scraper

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
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=scraper_user
MYSQL_PASS=secretpassword
MYSQL_DB=scraping_db

# PostgreSQL Configuration (Google Shopping)
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASS=secretpassword
PG_DB=google_shopping

# Remote Storage / FTP
FTP_HOST=ftp.yourserver.com
FTP_PORT=21
FTP_USER=ftpuser
FTP_PASS=ftppassword
FTP_PATH=/uploads/
```

### 4. Database Initialization (Optional)

```bash
# Initialize MySQL tables
python init_db.py

# Import catalog CSV into MySQL
python import_csv.py products_chunk_1.csv
```

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

### Direct Scraper Invocations

Run Shopify scraper standalone:
```bash
export CURR_URL=https://www.afastores.com
export SITEMAP_OFFSET=0
export MAX_SITEMAPS=2
export MAX_WORKERS=4
python shopify-scrapper/shopifyscrap-cloudflare.py
```

Run Shopify concurrent local runner:
```bash
python shopify-scrapper/run_concurrent.py --store grayson-living --jobs 4 --workers 10
```

Run Google Shopping Scraper:
```bash
python gshopping/gscrapper.py
```

Clean Google Shopping redirect URLs:
```bash
python resolve_redirects.py
```

---

## ⚙️ Environment Variables Reference

| Variable | Scope / Script | Description | Default |
|---|---|---|---|
| `CURR_URL` | All scrapers | Base URL of the target store | Required |
| `API_BASE_URL` | API scrapers | Endpoint URL for internal store APIs | Varies |
| `SITEMAP_OFFSET` | Sitemaps | Zero-based index of sitemap chunk to process | `0` |
| `MAX_SITEMAPS` | Sitemaps | Total sitemaps to process (`0` = all discovered) | `0` |
| `MAX_URLS_PER_SITEMAP`| Sitemaps | Product URL limit per sitemap (`0` = unlimited) | `0` |
| `MAX_WORKERS` | Scrapers / Threading | Concurrency limit for parallel requests | `4` |
| `REQUEST_DELAY` | Scrapers | Base sleep delay between HTTP requests (seconds) | `1.0` |
| `FLARESOLVERR_URL` | Cloudflare scrapers | Endpoint of active FlareSolverr instance | `http://localhost:8191/v1` |
| `TARGET_STORE` | Multi-store scripts | Key of specific store to target (e.g. `afa-stores`) | `""` |
| `MYSQL_HOST` | Database | Host address for MySQL database | `localhost` |
| `PG_HOST` | Database | Host address for PostgreSQL database | `localhost` |
| `FTP_HOST` | Delivery | Target FTP server address for CSV uploads | `""` |

---

## 🛡 Production Best Practices & Troubleshooting

### 1. Cloudflare 403 Forbidden / Challenge Loops
- For Shopify sites, use `shopify-scrapper/shopifyscrap-cloudflare.py`. It uses `curl_cffi` to mimic Chrome TLS fingerprints without loading browser overhead.
- Ensure `FLARESOLVERR_URL` is active when running `cymax`, `fpfc`, or `em_scraper`.

### 2. Google Shopping CAPTCHAs
- If Google Shopping redirects to `google.com/sorry`:
  - `gshopping/solvecaptcha.py` will attempt an audio challenge bypass using Google Speech Recognition.
  - Run `resolve_redirects.py` to extract clean search URLs from Google redirect strings.
  - Implement residential proxies or decrease worker concurrency.

### 3. Memory Optimization on Large Datasets (500k+ URLs)
- Scrapers include periodic garbage collection (`gc.collect()`) and write output in streaming batches of 1,000 items to keep memory footprints low.

### 4. Database Deadlocks & Concurrency
- `import_csv.py` uses 5,000-row batch inserts with an automatic fallback to 1,000-row sub-batches upon collision.
- When running distributed Google Shopping scrapers with 40+ workers, route database connections through **PgBouncer** (`gshopping/pgbouncer.ini`) to prevent connection exhaustion.

---

## 📄 License & Terms

This repository is maintained for competitive intelligence and catalog monitoring. Ensure compliance with target site terms of service, robots.txt directives, and local data collection regulations.
