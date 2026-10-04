#!/usr/bin/env python3
"""
High-Throughput PostgreSQL Bulk Importer & Synchronizer
Optimized for Railway.com & Large-Scale Distributed E-Commerce Datasets (Millions of Rows)
"""

import os
import sys
import io
import csv
import re
import glob
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Optional psycopg2 import with helpful error
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

# Load environment
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


def get_db_connection():
    """
    Establish PostgreSQL connection using Railway DATABASE_URL or standard PG environment variables.
    """
    if psycopg2 is None:
        raise ImportError("psycopg2 is not installed. Run: pip install psycopg2-binary")

    db_url = os.getenv("DATABASE_URL", "").strip()

    # Railway / Heroku format compatibility
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(db_url)

    # Standard / individual environment parameters
    host = os.getenv("PGHOST") or os.getenv("PG_HOST", "localhost")
    port = os.getenv("PGPORT") or os.getenv("PG_PORT", "5432")
    user = os.getenv("PGUSER") or os.getenv("PG_USER", "postgres")
    password = os.getenv("PGPASSWORD") or os.getenv("PG_PASS", "")
    database = os.getenv("PGDATABASE") or os.getenv("PG_DB", "postgres")

    return psycopg2.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        connect_timeout=15,
    )


def init_database(conn=None):
    """
    Initialize tables, indexes, and triggers from schema.sql.
    """
    close_after = False
    if conn is None:
        conn = get_db_connection()
        close_after = True

    schema_path = PROJECT_ROOT / "db" / "schema.sql"
    if not schema_path.exists():
        print(f"[Error] Schema file not found at: {schema_path}")
        return False

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print("[PostgreSQL] Applying schema and high-performance indexes...")
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("[PostgreSQL] Database schema initialized successfully.")

    if close_after:
        conn.close()
    return True


def clean_price(val: Any) -> Optional[float]:
    """Parse monetary string to float safely."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        return None
    cleaned = re.sub(r"[^\d.]", "", s)
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def clean_int(val: Any, default: int = 1) -> int:
    """Parse integer value safely."""
    if val is None:
        return default
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        return default
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


def clean_str(val: Any, max_len: Optional[int] = None) -> Optional[str]:
    """Clean string, strip whitespace, map empty/null to None."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        return None
    if max_len and len(s) > max_len:
        s = s[:max_len]
    return s


def parse_timestamp(val: Any) -> str:
    """Standardize timestamp for PostgreSQL."""
    if val:
        s = str(val).strip()
        if s and s.lower() not in ("nan", "none", "null"):
            return s
    return datetime.now(timezone.utc).isoformat()


def detect_store_from_name(filename_or_site: str) -> str:
    """Infer clean store identifier from filename or site string."""
    name = Path(filename_or_site).name.lower()
    mapping = {
        "afa": "afa-stores",
        "english": "english-elm",
        "grayson": "grayson-living",
        "france": "france-and-son",
        "cymax": "cymax",
        "drl": "discount-living-rooms",
        "bfd": "bedroom-furniture-discounts",
        "dro": "dining-rooms-outlet",
        "tvs": "tv-stands-outlet",
        "emma": "emma-mason",
        "walmart": "walmart",
        "bison": "bisonoffice",
        "blooming": "bloomingdales",
        "ashley": "ashley-furniture",
        "coleman": "coleman-furniture",
        "overstock": "overstock",
        "bbb": "bed-bath-beyond",
        "fp": "furniture-cart",
        "fc": "furniture-pick",
        "luxe": "luxedecor",
        "unlimited": "unlimited-furniture",
        "google": "google-shopping",
        "gshopping": "google-shopping",
    }
    for key, val in mapping.items():
        if key in name:
            return val
    clean = re.sub(r"[_\-\.]+", "-", name)
    clean = re.sub(r"-(products|chunk|full|scraped|csv|gz).*", "", clean)
    return clean or "unknown-store"


def sync_csv_to_postgres(
    csv_file: str,
    store_name: Optional[str] = None,
    batch_size: int = 15000,
    init_first: bool = True,
) -> Dict[str, Any]:
    """
    High-speed bulk sync of a CSV file into PostgreSQL using staging COPY + UPSERT.
    Scales effortlessly to millions of rows.
    """
    path = Path(csv_file)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    if not store_name:
        store_name = detect_store_from_name(path.stem)

    print(f"\n[PostgreSQL Sync] Starting ingestion for store: '{store_name}'")
    print(f"  Source file : {path} ({path.stat().st_size / (1024 * 1024):.2f} MB)")

    conn = get_db_connection()
    if init_first:
        init_database(conn)

    # Standard column aliases mapping
    col_mapping = {
        "ref_product_url": ["ref product url", "url", "product_url", "link"],
        "ref_product_id": ["ref product id", "product_id", "productid", "id"],
        "ref_variant_id": ["ref variant id", "variant_id", "variantid"],
        "ref_variant_title": ["ref variant title", "variant title", "variant"],
        "ref_category": ["ref category", "category", "collection"],
        "ref_category_url": ["ref category url", "category_url", "collection_url"],
        "ref_brand_name": ["ref brand name", "brand", "vendor", "manufacturer"],
        "ref_product_name": ["ref product name", "product_name", "title", "name"],
        "ref_sku": ["ref sku", "sku", "model"],
        "ref_mpn": ["ref mpn", "mpn"],
        "ref_gtin": ["ref gtin", "gtin", "upc", "ean", "barcode"],
        "ref_price": ["ref price", "price", "current_price", "sale_price"],
        "ref_main_image": ["ref main image", "main_image", "image", "image_url"],
        "ref_quantity": ["ref quantity", "quantity", "inventory", "stock"],
        "ref_group_attr_1": ["ref group attr 1", "group_attr_1", "attr_1", "option1"],
        "ref_group_attr_2": ["ref group attr 2", "group_attr_2", "attr_2", "option2"],
        "ref_status": ["ref status", "status", "availability"],
        "date_scraped": ["date scraped", "date_scraped", "scraped_at", "timestamp"],
        "raw_json": ["raw json", "raw_json", "json_data"],
        "store": ["store", "store_name", "retailer"],
    }

    total_rows = 0
    total_upserted = 0
    start_time = datetime.now()

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            print("[Warning] Empty CSV file.")
            conn.close()
            return {"status": "empty", "rows": 0}

        # Normalize header indices
        header_normalized = [h.strip().lower() for h in header]
        idx_map = {}
        for target_field, aliases in col_mapping.items():
            for alias in aliases:
                if alias in header_normalized:
                    idx_map[target_field] = header_normalized.index(alias)
                    break

        print(f"  Mapped {len(idx_map)} recognized columns from CSV header.")

        batch_rows: List[List[Any]] = []

        def flush_batch(batch: List[List[Any]]):
            nonlocal total_upserted
            if not batch:
                return

            with conn.cursor() as cur:
                # 1. Create temporary staging table
                cur.execute(
                    """
                    CREATE TEMP TABLE IF NOT EXISTS staging_competitor_products (
                        store VARCHAR(100),
                        ref_product_url TEXT,
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
                        ref_quantity INTEGER,
                        ref_group_attr_1 TEXT,
                        ref_group_attr_2 TEXT,
                        ref_status VARCHAR(50),
                        raw_json JSONB,
                        date_scraped TIMESTAMPTZ
                    ) ON COMMIT DROP;
                    TRUNCATE staging_competitor_products;
                    """
                )

                # 2. Ultra-fast COPY from memory buffer
                buffer = io.StringIO()
                writer = csv.writer(buffer, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
                for r in batch:
                    # Replace None with \N for PostgreSQL COPY null representation
                    writer.writerow(["\\N" if col is None else str(col).replace("\t", " ").replace("\n", " ") for col in r])
                buffer.seek(0)

                cur.copy_from(
                    buffer,
                    "staging_competitor_products",
                    sep="\t",
                    null="\\N",
                    columns=(
                        "store", "ref_product_url", "ref_product_id", "ref_variant_id",
                        "ref_variant_title", "ref_category", "ref_category_url", "ref_brand_name",
                        "ref_product_name", "ref_sku", "ref_mpn", "ref_gtin", "ref_price",
                        "ref_main_image", "ref_quantity", "ref_group_attr_1", "ref_group_attr_2",
                        "ref_status", "raw_json", "date_scraped"
                    ),
                )

                # 3. Fast set-based UPSERT into destination table
                cur.execute(
                    """
                    INSERT INTO competitor_products (
                        store, ref_product_url, ref_product_id, ref_variant_id, ref_variant_title,
                        ref_category, ref_category_url, ref_brand_name, ref_product_name,
                        ref_sku, ref_mpn, ref_gtin, ref_price, ref_main_image, ref_quantity,
                        ref_group_attr_1, ref_group_attr_2, ref_status, raw_json, date_scraped
                    )
                    SELECT
                        store, ref_product_url, ref_product_id, ref_variant_id, ref_variant_title,
                        ref_category, ref_category_url, ref_brand_name, ref_product_name,
                        ref_sku, ref_mpn, ref_gtin, ref_price, ref_main_image, ref_quantity,
                        ref_group_attr_1, ref_group_attr_2, ref_status, raw_json, date_scraped
                    FROM staging_competitor_products
                    ON CONFLICT (
                        store,
                        COALESCE(ref_product_id, ''),
                        COALESCE(ref_variant_id, ''),
                        md5(ref_product_url)
                    )
                    DO UPDATE SET
                        ref_price = EXCLUDED.ref_price,
                        ref_quantity = EXCLUDED.ref_quantity,
                        ref_status = EXCLUDED.ref_status,
                        ref_main_image = COALESCE(EXCLUDED.ref_main_image, competitor_products.ref_main_image),
                        ref_category = COALESCE(EXCLUDED.ref_category, competitor_products.ref_category),
                        ref_brand_name = COALESCE(EXCLUDED.ref_brand_name, competitor_products.ref_brand_name),
                        ref_product_name = COALESCE(EXCLUDED.ref_product_name, competitor_products.ref_product_name),
                        ref_sku = COALESCE(EXCLUDED.ref_sku, competitor_products.ref_sku),
                        ref_mpn = COALESCE(EXCLUDED.ref_mpn, competitor_products.ref_mpn),
                        ref_gtin = COALESCE(EXCLUDED.ref_gtin, competitor_products.ref_gtin),
                        date_scraped = EXCLUDED.date_scraped,
                        updated_at = CURRENT_TIMESTAMP;
                    """
                )
                total_upserted += len(batch)
            conn.commit()
            print(f"  -> Ingested {total_upserted:,} records...")

        for row in reader:
            if not row:
                continue
            total_rows += 1

            def get_val(f_name):
                idx = idx_map.get(f_name)
                if idx is not None and idx < len(row):
                    return row[idx]
                return None

            row_store = clean_str(get_val("store"), 100) or store_name
            url = clean_str(get_val("ref_product_url"))
            if not url:
                continue

            cleaned_row = [
                row_store,
                url,
                clean_str(get_val("ref_product_id"), 255),
                clean_str(get_val("ref_variant_id"), 255),
                clean_str(get_val("ref_variant_title"), 500),
                clean_str(get_val("ref_category"), 500),
                clean_str(get_val("ref_category_url")),
                clean_str(get_val("ref_brand_name"), 500),
                clean_str(get_val("ref_product_name")),
                clean_str(get_val("ref_sku"), 255),
                clean_str(get_val("ref_mpn"), 255),
                clean_str(get_val("ref_gtin"), 100),
                clean_price(get_val("ref_price")),
                clean_str(get_val("ref_main_image")),
                clean_int(get_val("ref_quantity"), 1),
                clean_str(get_val("ref_group_attr_1")),
                clean_str(get_val("ref_group_attr_2")),
                clean_str(get_val("ref_status"), 50) or "active",
                clean_str(get_val("raw_json")),
                parse_timestamp(get_val("date_scraped")),
            ]

            batch_rows.append(cleaned_row)
            if len(batch_rows) >= batch_size:
                flush_batch(batch_rows)
                batch_rows = []

        if batch_rows:
            flush_batch(batch_rows)

    duration = (datetime.now() - start_time).total_seconds()
    conn.close()

    rate = total_upserted / duration if duration > 0 else total_upserted
    print(f"\n[PostgreSQL Sync Complete] {total_upserted:,} records upserted in {duration:.2f}s ({rate:.0f} rows/sec)\n")
    return {
        "status": "success",
        "store": store_name,
        "rows_processed": total_rows,
        "rows_upserted": total_upserted,
        "duration_seconds": round(duration, 2),
    }


def get_db_stats() -> Dict[str, Any]:
    """Retrieve database metrics, total records, and per-store counts."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Check table existence
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'competitor_products'
                );
                """
            )
            exists = cur.fetchone()[0]
            if not exists:
                return {"connected": True, "initialized": False, "total_products": 0, "stores": []}

            # Total count
            cur.execute("SELECT COUNT(*) FROM competitor_products;")
            total = cur.fetchone()[0]

            # Store breakdown
            cur.execute(
                """
                SELECT store, COUNT(*) as count, MAX(date_scraped) as latest_scrape
                FROM competitor_products
                GROUP BY store
                ORDER BY count DESC;
                """
            )
            stores = [
                {
                    "store": r["store"],
                    "count": r["count"],
                    "latest_scrape": r["latest_scrape"].isoformat() if r["latest_scrape"] else None,
                }
                for r in cur.fetchall()
            ]

            return {
                "connected": True,
                "initialized": True,
                "total_products": total,
                "store_count": len(stores),
                "stores": stores,
            }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Synchronize scraper CSV chunks into PostgreSQL (Railway ready)")
    parser.add_argument("--csv", help="Path to input CSV file")
    parser.add_argument("--dir", help="Path to directory of CSV files to batch import")
    parser.add_argument("--store", help="Explicit store identifier (e.g. 'cymax', 'afa-stores')")
    parser.add_argument("--init-db", action="store_true", help="Initialize PostgreSQL schema and exit")
    parser.add_argument("--status", action="store_true", help="Print database record statistics and exit")
    parser.add_argument("--batch-size", type=int, default=15000, help="Batch chunk size for COPY (default: 15,000)")

    args = parser.parse_args()

    if args.init_db:
        init_database()
        return

    if args.status:
        try:
            stats = get_db_stats()
            print("\n================ PostgreSQL Database Status ================")
            print(f"  Connected      : {stats['connected']}")
            print(f"  Initialized    : {stats.get('initialized')}")
            print(f"  Total Products : {stats.get('total_products', 0):,}")
            print(f"  Stores Covered : {stats.get('store_count', 0)}")
            print("------------------------------------------------------------")
            for s in stats.get("stores", []):
                print(f"  • {s['store']:<28} : {s['count']:,} products (last: {s['latest_scrape'] or 'N/A'})")
            print("============================================================\n")
        except Exception as e:
            print(f"[Error] Failed to connect to database: {e}")
        return

    if args.csv:
        sync_csv_to_postgres(args.csv, store_name=args.store, batch_size=args.batch_size)
    elif args.dir:
        csv_files = glob.glob(os.path.join(args.dir, "*.csv"))
        if not csv_files:
            print(f"No CSV files found in: {args.dir}")
            return
        print(f"Found {len(csv_files)} CSV files to sync in {args.dir}")
        for f in csv_files:
            sync_csv_to_postgres(f, store_name=args.store, batch_size=args.batch_size)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
