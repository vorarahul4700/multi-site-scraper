"""
Concurrent Full Store Scraper Orchestrator.

Splits a store's total sitemaps across multiple parallel worker processes
on your local machine so you can scrape 100% of the store concurrently.

Usage:
    python shopify-scrapper/run_concurrent.py --store grayson-living --jobs 4 --workers 10
"""

import os
import sys
import glob
import math
import time
import argparse
import subprocess
import xml.etree.ElementTree as ET
import cloudscraper
import pandas as pd

STORE_REGISTRY = {
    "afa-stores": {
        "domain": "afastores.com",
        "url": "https://www.afastores.com",
        "sitemap": "https://www.afastores.com/sitemap.xml",
    },
    "english-elm": {
        "domain": "englishelm.com",
        "url": "https://englishelm.com",
        "sitemap": "https://englishelm.com/sitemap.xml",
    },
    "grayson-living": {
        "domain": "graysonliving.com",
        "url": "https://www.graysonliving.com",
        "sitemap": "https://www.graysonliving.com/sitemap.xml",
    },
    "france-and-son": {
        "domain": "franceandson.com",
        "url": "https://www.franceandson.com",
        "sitemap": "https://www.franceandson.com/sitemap.xml",
    },
    "grayson-luxury": {
        "domain": "graysonluxury.com",
        "url": "https://www.graysonluxury.com",
        "sitemap": "https://www.graysonluxury.com/sitemap.xml",
    },
}

STORE_ALIASES = {
    "afa": "afa-stores",
    "ee": "english-elm",
    "gl": "grayson-living",
    "fas": "france-and-son",
    "glx": "grayson-luxury",
}


def log(msg: str):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] [Orchestrator] {msg}\n")
    sys.stderr.flush()


def discover_total_sitemaps(store_key: str, cookie: str = "") -> int:
    """Discovers the total number of sitemaps in the store's sitemap index."""
    cfg = STORE_REGISTRY.get(store_key, {})
    base_url = cfg.get("url", f"https://www.{store_key}.com").rstrip("/")
    sitemap_url = cfg.get("sitemap", f"{base_url}/sitemap.xml")

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False},
        delay=10,
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    if cookie:
        headers["Cookie"] = cookie

    scraper.headers.update(headers)

    candidates = [
        sitemap_url,
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/sitemaps/sitemap.xml",
    ]

    for target_url in candidates:
        log(f"Checking sitemap index at: {target_url}")
        try:
            resp = scraper.get(target_url, timeout=30)
            if resp.status_code == 200 and resp.text:
                root = ET.fromstring(resp.text)
                locs = root.findall(".//{*}loc")
                if not locs:
                    locs = root.findall(".//loc")
                if locs:
                    log(f"Found {len(locs)} sitemaps!")
                    return len(locs)
        except Exception as e:
            log(f"Discovery check failed for {target_url}: {e}")

    log("Could not auto-detect sitemaps; defaulting to 20.")
    return 20


def merge_chunks(output_dir: str, store_key: str):
    """Merges all products_chunk_*.csv files in output_dir into products_full.csv."""
    chunk_pattern = os.path.join(output_dir, "products_chunk_*.csv")
    csv_files = sorted(glob.glob(chunk_pattern))

    if not csv_files:
        log("No chunk CSV files found to merge.")
        return

    full_output = os.path.join(output_dir, "products_full.csv")
    log(f"Merging {len(csv_files)} chunk CSV files into: {full_output}")

    dfs = []
    total_rows = 0
    for f in csv_files:
        try:
            df = pd.read_csv(f, dtype=str)
            dfs.append(df)
            total_rows += len(df)
            log(f"  Loaded {os.path.basename(f)}: {len(df)} variants")
        except Exception as e:
            log(f"  Error reading {f}: {e}")

    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        # Deduplicate on Ref Variant ID if present
        if "Ref Variant ID" in merged_df.columns:
            before_dedup = len(merged_df)
            merged_df.drop_duplicates(subset=["Ref Variant ID"], inplace=True)
            log(f"Deduplicated {before_dedup - len(merged_df)} duplicate rows")

        merged_df.to_csv(full_output, index=False, encoding="utf-8")
        log(f"SUCCESS! Merged {len(merged_df)} total unique variants into {full_output}")


def main():
    parser = argparse.ArgumentParser(description="Concurrent Full Store Scraper Orchestrator")
    parser.add_argument("--store", default="grayson-living", help="Store key (e.g. grayson-living, france-and-son, etc.)")
    parser.add_argument("--jobs", type=int, default=3, help="Number of concurrent worker processes (default: 3)")
    parser.add_argument("--workers", type=int, default=10, help="Threads per worker process (default: 10)")
    parser.add_argument("--delay", type=float, default=0.3, help="Crawl delay in seconds (default: 0.3)")
    parser.add_argument("--cookie", default="", help="Shopify Cloudflare cookie string")
    parser.add_argument("--total-sitemaps", type=int, default=0, help="Override total sitemaps if known")

    args = parser.parse_args()

    store_key = STORE_ALIASES.get(args.store.lower(), args.store.lower())
    if store_key not in STORE_REGISTRY:
        log(f"Unknown store '{args.store}'. Available stores: {list(STORE_REGISTRY.keys())}")
        sys.exit(1)

    cookie = args.cookie or os.getenv("SHOPIFY_COOKIE", "")

    # 1. Determine total sitemaps
    if args.total_sitemaps > 0:
        total_sitemaps = args.total_sitemaps
    else:
        total_sitemaps = discover_total_sitemaps(store_key, cookie)

    log(f"Target Store:    {store_key}")
    log(f"Total Sitemaps:  {total_sitemaps}")
    log(f"Concurrent Jobs: {args.jobs}")
    log(f"Threads Per Job: {args.workers}")

    # 2. Divide into job slices
    chunk_size = math.ceil(total_sitemaps / args.jobs)
    job_slices = []
    for i in range(args.jobs):
        offset = i * chunk_size
        remaining = total_sitemaps - offset
        if remaining <= 0:
            break
        limit = min(chunk_size, remaining)
        job_slices.append((offset, limit))

    log(f"Planned {len(job_slices)} parallel jobs:")
    for idx, (off, lim) in enumerate(job_slices):
        log(f"  Job {idx + 1}: Sitemaps [{off} to {off + lim - 1}] (offset={off}, limit={lim})")

    # 3. Launch subprocesses concurrently
    script_path = os.path.join(os.path.dirname(__file__), "shopifyscrap-cloudflare.py")
    output_dir = os.path.join("output", store_key)
    os.makedirs(output_dir, exist_ok=True)

    processes = []
    log("=" * 60)
    log("LAUNCHING ALL JOBS CONCURRENTLY...")
    log("=" * 60)

    for idx, (off, lim) in enumerate(job_slices):
        env = os.environ.copy()
        env["TARGET_STORE"] = store_key
        env["SITEMAP_OFFSET"] = str(off)
        env["MAX_SITEMAPS"] = str(lim)
        env["MAX_URLS_PER_SITEMAP"] = "0"  # Full scrape: all URLs
        env["MAX_WORKERS"] = str(args.workers)
        env["REQUEST_DELAY"] = str(args.delay)
        if cookie:
            env["SHOPIFY_COOKIE"] = cookie

        p = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            cwd=os.getcwd(),
        )
        processes.append((idx + 1, off, lim, p))
        log(f"  Started Job {idx + 1} (PID: {p.pid}) -> Offset: {off}, Limit: {lim}")

    # 4. Wait for all jobs to complete
    log("Waiting for all jobs to complete...")
    for idx, off, lim, p in processes:
        p.wait()
        log(f"Job {idx} (offset={off}, limit={lim}) finished with exit code {p.returncode}")

    # 5. Automatically merge chunk files
    log("All concurrent scraper jobs finished! Merging outputs...")
    merge_chunks(output_dir, store_key)
    log("FULL SCRAPE COMPLETE!")


if __name__ == "__main__":
    main()
