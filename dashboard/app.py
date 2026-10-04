#!/usr/bin/env python3
"""
Scraper Workflow Dashboard (GitHub Actions Connected)
Fully featured web UI to monitor, configure, and trigger GitHub Actions scraping workflows.
Run: python dashboard/app.py
Open: http://localhost:5050
"""

import os
import sys
import re
import json
import time
import yaml
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Project setup & Environment loading
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file from project root
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "vorarahul4700/multi-site-scraper").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()
PORT = int(os.getenv("PORT", "5050"))

WORKFLOWS_DIR = PROJECT_ROOT / ".github" / "workflows"

# Category metadata mapping
WORKFLOW_METADATA = {
    "ashley_scraper.yml": {
        "category": "Retailers",
        "color": "#EC4899",
        "store": "Ashley Furniture",
        "description": "Ashley Furniture product catalog, pricing, variations, and inventory crawler."
    },
    "bbb-ovs-sku.yml": {
        "category": "Retailers",
        "color": "#F97316",
        "store": "Bed Bath & Beyond",
        "description": "Bed Bath & Beyond catalog product details and model SKU data extractor."
    },
    "bisonoffice.yml": {
        "category": "Retailers",
        "color": "#3B82F6",
        "store": "Bison Office",
        "description": "Bison Office store catalog, office furniture, and equipment product crawler."
    },
    "blooming_dales.yml": {
        "category": "Retailers",
        "color": "#14B8A6",
        "store": "Bloomingdale's",
        "description": "Bloomingdale's designer home furnishings, luxury decor, and catalog product crawler."
    },
    "cleanEverything.yml": {
        "category": "Utilities",
        "color": "#64748B",
        "store": "GitHub Actions",
        "description": "Automated workflow run logs and build artifact maintenance cleanup utility."
    },
    "colemanfurniture_brand_file.yml": {
        "category": "Retailers",
        "color": "#F59E0B",
        "store": "Coleman Furniture",
        "description": "Coleman Furniture brand catalog, pricing, and product inventory crawler."
    },
    "cymax-scraper.yml": {
        "category": "Retailers",
        "color": "#9333EA",
        "store": "Cymax",
        "description": "Cymax home and office furniture catalog crawler."
    },
    "cymax-sitemap-products.yml": {
        "category": "Retailers",
        "color": "#A855F7",
        "store": "Cymax",
        "description": "Cymax product inventory and specifications crawler."
    },
    "cymaxv2.yml": {
        "category": "Retailers",
        "color": "#8B5CF6",
        "store": "Cymax",
        "description": "Cymax comprehensive online store catalog crawler."
    },
    "drl-scrapper-fast.yml": {
        "category": "Retailers",
        "color": "#6366F1",
        "store": "DRL / BFD / DRO / TVS",
        "description": "Multi-store network supporting Bedroom Furniture Discounts, Discount Living Rooms, Dining Rooms Outlet, and TV Stands Outlet."
    },
    "em-scrapper-fast.yml": {
        "category": "Retailers",
        "color": "#06B6D4",
        "store": "Emma Mason",
        "description": "Emma Mason furniture collection and product inventory crawler."
    },
    "fp-fc-scrapper.yml": {
        "category": "Retailers",
        "color": "#10B981",
        "store": "FurnitureCart & FurniturePick",
        "description": "FurnitureCart and FurniturePick complete furniture product catalog crawler."
    },
    "gshopping_keyword.yml": {
        "category": "Marketplaces",
        "color": "#4285F4",
        "store": "Google Shopping",
        "description": "Google Shopping marketplace keyword search and competitor rankings crawler."
    },
    "gshopping_mysql.yml": {
        "category": "Marketplaces",
        "color": "#EA4335",
        "store": "Google Shopping",
        "description": "Google Shopping marketplace seller pricing and product catalog pipeline."
    },
    "luxedecor.yml": {
        "category": "Retailers",
        "color": "#E11D48",
        "store": "LuxeDecor",
        "description": "LuxeDecor luxury outdoor and designer indoor furniture product crawler."
    },
    "ovs-bbb.yml": {
        "category": "Retailers",
        "color": "#D97706",
        "store": "Overstock / BBB",
        "description": "Overstock and Bed Bath & Beyond unified store catalog crawler."
    },
    "resolve_redirects.yml": {
        "category": "Utilities",
        "color": "#475569",
        "store": "Redirect Resolver",
        "description": "HTTP redirect and canonical landing URL resolver utility."
    },
    "shopifyscrapper-cloudflare.yml": {
        "category": "Marketplaces",
        "color": "#059669",
        "store": "Shopify Multi-Store",
        "description": "Multi-store network supporting AFA Stores, English Elm, Grayson Living, France & Son, and Grayson Luxury."
    },
    "unlimited_furniture.yml": {
        "category": "Retailers",
        "color": "#0D9488",
        "store": "Unlimited Furniture",
        "description": "Unlimited Furniture designer home decor and product catalog crawler."
    },
    "walmart.yml": {
        "category": "Marketplaces",
        "color": "#0284C7",
        "store": "Walmart",
        "description": "Walmart marketplace furniture and home goods catalog crawler."
    },
}

# ---------------------------------------------------------------------------
# Semantic Parameter Order Ranking (Target -> Volume -> Concurrency -> Anti-Bot -> Advanced)
# ---------------------------------------------------------------------------
PARAM_ORDER_WEIGHTS = {
    # 1. Target Scope / Source
    "store": 10,
    "url": 11,
    "base_url": 12,
    "api_url": 13,
    "bbb_api_url": 14,
    "base_api": 15,
    "keyword": 16,
    "manufacturer_id": 17,
    "source_type": 18,
    "ftp_filename": 19,
    "input_filename": 20,
    "sitemap_url": 21,
    "direct_urls": 22,
    "product_ids": 23,

    # 2. Volume & Paging
    "total_sitemaps": 30,
    "total_pages": 31,
    "start_page": 32,
    "end_page": 33,
    "total_chunks": 34,
    "urls_per_sitemap": 35,
    "urls_per_job": 36,
    "chunk_size": 37,
    "max_products": 38,
    "total_products_limit": 39,
    "limit": 40,
    "sample_size": 41,
    "claim_limit": 42,
    "total_accounts": 43,

    # 3. Concurrency & Workers
    "sitemaps_per_job": 50,
    "pages_per_job": 51,
    "max_parallel_jobs": 52,
    "max_workers": 53,
    "url_concurrency": 54,
    "product_concurrency": 55,
    "product_chunks": 56,

    # 4. Anti-bot & Throttling
    "request_delay": 70,
    "flaresolverr_instances": 71,
    "products_per_hour": 72,
    "max_runtime_hours": 73,
    "use_free_proxies": 74,

    # 5. Overrides & Advanced
    "specific_offsets": 90,
    "sitemap_urls_override": 91,
    "is_chained": 92,
    "scrape_only": 93,
    "urls_file": 94,
    "run_resolve_redirects": 95,
    "reset_errors": 96,
    "ftp_file_name": 97,
    "run_depth": 98,
    "max_depth": 99,
    "max_rounds": 100,
    "current_round": 101,
    "remaining_run_id": 102,
}

# ---------------------------------------------------------------------------
# GitHub Actions API Client
# ---------------------------------------------------------------------------
class GitHubActionsClient:
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}

    def update_config(self, token: Optional[str] = None, repo: Optional[str] = None):
        if token is not None:
            self.token = token.strip()
        if repo is not None:
            self.repo = repo.strip()
        self._cache.clear()
        self._cache_time.clear()

    @property
    def headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Scraper-Dashboard",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_rate_limit(self) -> Dict[str, Any]:
        try:
            r = requests.get("https://api.github.com/rate_limit", headers=self.headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return {"valid": True, **data.get("rate", {})}
            return {"valid": False, "error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def get_repo_info(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"https://api.github.com/repos/{self.repo}", headers=self.headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return {
                    "valid": True,
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "private": data.get("private"),
                    "html_url": data.get("html_url"),
                    "default_branch": data.get("default_branch", "main"),
                    "owner": data.get("owner", {}).get("login"),
                    "owner_avatar": data.get("owner", {}).get("avatar_url"),
                }
            return {"valid": False, "error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def get_all_runs(self, limit: int = 50, force: bool = False) -> List[Dict[str, Any]]:
        cache_key = f"all_runs_{limit}"
        now = time.time()
        if not force and cache_key in self._cache and (now - self._cache_time.get(cache_key, 0)) < 3.0:
            return self._cache[cache_key]

        try:
            r = requests.get(
                f"https://api.github.com/repos/{self.repo}/actions/runs?per_page={limit}",
                headers=self.headers,
                timeout=7,
            )
            if r.status_code == 200:
                runs = r.json().get("workflow_runs", [])
                self._cache[cache_key] = runs
                self._cache_time[cache_key] = now
                return runs
        except Exception as e:
            print(f"Error fetching runs: {e}")
        return self._cache.get(cache_key, [])

    def get_workflow_runs(self, workflow_file: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{self.repo}/actions/workflows/{workflow_file}/runs?per_page={limit}",
                headers=self.headers,
                timeout=6,
            )
            if r.status_code == 200:
                return r.json().get("workflow_runs", [])
        except Exception as e:
            print(f"Error fetching workflow runs for {workflow_file}: {e}")
        return []

    def dispatch(self, workflow_file: str, inputs: Optional[Dict[str, Any]] = None, ref: str = "main") -> Dict[str, Any]:
        """Trigger a workflow_dispatch event."""
        # Convert all inputs to strings as required by GitHub Actions API
        formatted_inputs = {}
        if inputs:
            for k, v in inputs.items():
                if isinstance(v, bool):
                    formatted_inputs[k] = "true" if v else "false"
                elif v is None:
                    formatted_inputs[k] = ""
                else:
                    formatted_inputs[k] = str(v)

        payload = {"ref": ref or GITHUB_BRANCH or "main"}
        if formatted_inputs:
            payload["inputs"] = formatted_inputs

        url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{workflow_file}/dispatches"
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if r.status_code in (204, 200, 201):
                # Clear runs cache so fresh runs are pulled
                self._cache.clear()
                self._cache_time.clear()
                return {"success": True, "message": f"Workflow {workflow_file} successfully dispatched on GitHub!"}
            else:
                error_msg = r.text
                try:
                    err_json = r.json()
                    error_msg = err_json.get("message", error_msg)
                except Exception:
                    pass
                return {"success": False, "error": f"GitHub API {r.status_code}: {error_msg}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_run(self, run_id: int) -> Dict[str, Any]:
        """Cancel a running workflow."""
        url = f"https://api.github.com/repos/{self.repo}/actions/runs/{run_id}/cancel"
        try:
            r = requests.post(url, headers=self.headers, timeout=8)
            if r.status_code in (202, 200):
                self._cache.clear()
                return {"success": True, "message": f"Run #{run_id} cancellation requested."}
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_run_jobs(self, run_id: int) -> List[Dict[str, Any]]:
        """Get jobs and steps for a specific run."""
        url = f"https://api.github.com/repos/{self.repo}/actions/runs/{run_id}/jobs"
        try:
            r = requests.get(url, headers=self.headers, timeout=6)
            if r.status_code == 200:
                return r.json().get("jobs", [])
        except Exception as e:
            print(f"Error fetching jobs for run {run_id}: {e}")
        return []

    def get_run_logs(self, run_id: int, max_lines: int = 100) -> Dict[str, Any]:
        """
        Fetch execution logs for a workflow run.
        Uses job logs endpoint and handles Azure storage redirection cleanly.
        """
        jobs = self.get_run_jobs(run_id)
        if not jobs:
            return {"logs": ["No jobs found for this run or logs are not ready yet."]}

        # Find latest failed job, or in-progress job, or first completed job
        target_job = None
        for j in jobs:
            if j.get("conclusion") == "failure":
                target_job = j
                break
            if j.get("status") in ("in_progress", "queued"):
                target_job = j
        if not target_job and jobs:
            target_job = jobs[0]

        job_id = target_job.get("id")
        job_name = target_job.get("name", "Job")
        job_status = target_job.get("status")
        job_conclusion = target_job.get("conclusion")

        # Step summary
        steps_summary = []
        for s in target_job.get("steps", []):
            steps_summary.append({
                "name": s.get("name"),
                "status": s.get("status"),
                "conclusion": s.get("conclusion"),
                "number": s.get("number"),
            })

        # Fetch job log text
        logs_text = []
        try:
            url = f"https://api.github.com/repos/{self.repo}/actions/jobs/{job_id}/logs"
            # GitHub redirects with 302 to Azure Blob SAS URL.
            # Stripping Authorization header on redirect prevents 401 Server failed to authenticate error.
            r = requests.get(url, headers=self.headers, allow_redirects=False, timeout=8)
            if r.status_code == 302:
                redirect_url = r.headers.get("Location")
                if redirect_url:
                    log_resp = requests.get(redirect_url, timeout=10)
                    if log_resp.status_code == 200:
                        all_lines = log_resp.text.strip().splitlines()
                        logs_text = all_lines[-max_lines:] if len(all_lines) > max_lines else all_lines
            elif r.status_code == 200:
                all_lines = r.text.strip().splitlines()
                logs_text = all_lines[-max_lines:] if len(all_lines) > max_lines else all_lines
        except Exception as e:
            logs_text.append(f"Log retrieval error: {str(e)}")

        if not logs_text:
            logs_text = [f"Job '{job_name}' status: {job_status} ({job_conclusion or 'running'}).", "Log output is either pending or archived by GitHub."]

        return {
            "job_id": job_id,
            "job_name": job_name,
            "job_status": job_status,
            "job_conclusion": job_conclusion,
            "steps": steps_summary,
            "logs": logs_text,
        }


gh_client = GitHubActionsClient(GITHUB_TOKEN, GITHUB_REPO)

# ---------------------------------------------------------------------------
# Workflow Files Parser
# ---------------------------------------------------------------------------
def parse_workflow_files() -> List[Dict[str, Any]]:
    """Scan and parse all workflow YAML files in .github/workflows."""
    workflows = []
    if not WORKFLOWS_DIR.exists():
        return workflows

    for yaml_path in sorted(WORKFLOWS_DIR.glob("*.y*ml")):
        filename = yaml_path.name
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f)
                if not isinstance(doc, dict):
                    continue

                name = doc.get("name", filename.replace(".yml", "").replace(".yaml", "").replace("-", " ").title())
                
                # YAML 1.1 quirk: 'on' parses as boolean True
                on_block = doc.get(True) or doc.get("on") or {}
                dispatch = None
                if isinstance(on_block, dict):
                    dispatch = on_block.get("workflow_dispatch")
                elif isinstance(on_block, list) and "workflow_dispatch" in on_block:
                    dispatch = {}
                elif "workflow_dispatch" in str(on_block):
                    dispatch = {}

                inputs_dict = {}
                if isinstance(dispatch, dict) and dispatch.get("inputs"):
                    raw_inputs = dispatch["inputs"]
                    for k, v in raw_inputs.items():
                        if isinstance(v, dict):
                            inputs_dict[k] = {
                                "name": k,
                                "description": v.get("description", ""),
                                "required": bool(v.get("required", False)),
                                "default": v.get("default", ""),
                                "type": v.get("type", "string"),
                                "options": v.get("options", []),
                            }
                    # Order parameters logically: Target -> Volume -> Concurrency -> Anti-Bot -> Advanced
                    sorted_keys = sorted(inputs_dict.keys(), key=lambda k: PARAM_ORDER_WEIGHTS.get(k, 60))
                    inputs_dict = {k: inputs_dict[k] for k in sorted_keys}

                meta = WORKFLOW_METADATA.get(filename, {
                    "category": "Retailers",
                    "color": "#6366F1",
                    "store": name,
                    "description": f"Workflow scraper definition for {filename}",
                })

                workflows.append({
                    "file": filename,
                    "name": name,
                    "category": meta.get("category", "Retailers"),
                    "color": meta.get("color", "#6366F1"),
                    "store": meta.get("store", name),
                    "description": meta.get("description", ""),
                    "inputs": inputs_dict,
                    "inputs_list": list(inputs_dict.values()),
                    "inputs_count": len(inputs_dict),
                    "github_path": f".github/workflows/{filename}",
                })
        except Exception as e:
            print(f"Error parsing {yaml_path}: {e}")

    return workflows


def map_run_status(status: Optional[str], conclusion: Optional[str]) -> str:
    """
    Standardize GitHub run statuses to user-requested states:
    - running
    - pending
    - completed
    - failed
    - cancelled
    - idle
    """
    if not status:
        return "idle"
    status_lower = status.lower()
    conclusion_lower = (conclusion or "").lower()

    if status_lower in ("queued", "waiting", "requested"):
        return "pending"
    if status_lower == "in_progress":
        return "running"
    if status_lower == "completed":
        if conclusion_lower == "success":
            return "completed"
        if conclusion_lower in ("failure", "timed_out", "action_required"):
            return "failed"
        if conclusion_lower in ("cancelled", "skipped"):
            return "cancelled"
        return "completed"
    return status_lower


def format_relative_time(timestamp_str: Optional[str]) -> str:
    if not timestamp_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
    except Exception:
        return timestamp_str[:10]


# ---------------------------------------------------------------------------
# Flask Application
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
if hasattr(app, "json"):
    app.json.sort_keys = False

@app.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/overview")
def api_overview():
    """Returns overview statistics, repo details, token health, and recent runs."""
    rate = gh_client.get_rate_limit()
    repo_info = gh_client.get_repo_info()
    runs = gh_client.get_all_runs(limit=25)

    workflows = parse_workflow_files()
    total_workflows = len(workflows)

    # Calculate status counts across latest runs
    running_count = 0
    pending_count = 0
    completed_count = 0
    failed_count = 0

    formatted_runs = []
    workflow_latest_runs = {}

    for r in runs:
        wf_path = r.get("path", "")
        wf_file = wf_path.split("/")[-1] if "/" in wf_path else wf_path
        st = map_run_status(r.get("status"), r.get("conclusion"))

        if wf_file and wf_file not in workflow_latest_runs:
            workflow_latest_runs[wf_file] = st

        run_item = {
            "id": r.get("id"),
            "run_number": r.get("run_number"),
            "name": r.get("name"),
            "workflow_file": wf_file,
            "status": r.get("status"),
            "conclusion": r.get("conclusion"),
            "unified_status": st,
            "html_url": r.get("html_url"),
            "event": r.get("event"),
            "branch": r.get("head_branch"),
            "created_at": r.get("created_at"),
            "created_at_relative": format_relative_time(r.get("created_at")),
            "actor": r.get("actor", {}).get("login"),
            "actor_avatar": r.get("actor", {}).get("avatar_url"),
        }
        formatted_runs.append(run_item)

    running_count = sum(1 for r in formatted_runs if r["unified_status"] == "running")
    pending_count = sum(1 for r in formatted_runs if r["unified_status"] == "pending")
    completed_count = sum(1 for r in formatted_runs if r["unified_status"] == "completed")
    failed_count = sum(1 for r in formatted_runs if r["unified_status"] == "failed")

    # Database metrics check
    has_pg = bool(os.getenv("DATABASE_URL") or os.getenv("PG_HOST") or os.getenv("PGHOST"))
    db_info = {"configured": has_pg, "connected": False, "total_products": 0}
    if has_pg:
        try:
            from sync_to_postgres import get_db_stats
            db_stats = get_db_stats()
            db_info = {
                "configured": True,
                "connected": db_stats.get("connected", False),
                "initialized": db_stats.get("initialized", False),
                "total_products": db_stats.get("total_products", 0),
                "store_count": db_stats.get("store_count", 0),
                "stores": db_stats.get("stores", []),
            }
        except Exception as e:
            db_info = {"configured": True, "connected": False, "error": str(e), "total_products": 0}


    return jsonify({
        "repo": repo_info,
        "token_rate": rate,
        "current_token_masked": (GITHUB_TOKEN[:12] + "..." + GITHUB_TOKEN[-4:]) if GITHUB_TOKEN else "Not configured",
        "current_repo": GITHUB_REPO,
        "database": db_info,
        "counts": {
            "total_workflows": total_workflows,
            "running": running_count,
            "pending": pending_count,
            "completed": completed_count,
            "failed": failed_count,
        },
        "recent_runs": formatted_runs[:15],
    })



@app.route("/api/workflows")
def api_workflows():
    """
    Returns all 20 workflows with:
    - metadata, category, color, store
    - original dispatch inputs schema & defaults
    - latest run info (id, status, conclusion, unified_status, html_url)
    - direct link to last run or workflow on GitHub
    """
    workflows = parse_workflow_files()
    runs = gh_client.get_all_runs(limit=60)

    # Map runs by workflow file name
    runs_by_file: Dict[str, List[Dict[str, Any]]] = {}
    for r in runs:
        wf_path = r.get("path", "")
        wf_file = wf_path.split("/")[-1] if "/" in wf_path else wf_path
        if wf_file:
            runs_by_file.setdefault(wf_file, []).append(r)

    enriched_workflows = []
    for wf in workflows:
        filename = wf["file"]
        file_runs = runs_by_file.get(filename, [])
        last_run_data = None
        unified_status = "idle"

        # GitHub URL fallbacks
        workflow_github_url = f"https://github.com/{GITHUB_REPO}/actions/workflows/{filename}"
        last_run_url = workflow_github_url

        if file_runs:
            latest_run = file_runs[0]
            unified_status = map_run_status(latest_run.get("status"), latest_run.get("conclusion"))
            last_run_url = latest_run.get("html_url", workflow_github_url)

            created_at = latest_run.get("created_at")
            updated_at = latest_run.get("updated_at")
            duration_str = None
            if created_at and updated_at:
                try:
                    c_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    u_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    dur_secs = int((u_dt - c_dt).total_seconds())
                    duration_str = f"{dur_secs}s" if dur_secs < 60 else f"{dur_secs // 60}m {dur_secs % 60}s"
                except Exception:
                    pass

            last_run_data = {
                "id": latest_run.get("id"),
                "run_number": latest_run.get("run_number"),
                "status": latest_run.get("status"),
                "conclusion": latest_run.get("conclusion"),
                "unified_status": unified_status,
                "html_url": last_run_url,
                "event": latest_run.get("event"),
                "created_at": created_at,
                "created_at_relative": format_relative_time(created_at),
                "duration": duration_str,
                "actor": latest_run.get("triggering_actor", {}).get("login") or latest_run.get("actor", {}).get("login"),
            }

        enriched_workflows.append({
            **wf,
            "unified_status": unified_status,
            "last_run": last_run_data,
            "github_run_url": last_run_url,
            "github_workflow_url": workflow_github_url,
        })

    return jsonify(enriched_workflows)


@app.route("/api/workflows/<filename>/dispatch", methods=["POST"])
def api_dispatch_workflow(filename):
    """Trigger a workflow dispatch on GitHub."""
    body = request.get_json(silent=True) or {}
    inputs = body.get("inputs", {})
    ref = body.get("ref", GITHUB_BRANCH or "main")

    result = gh_client.dispatch(filename, inputs=inputs, ref=ref)
    code = 200 if result.get("success") else 400
    return jsonify(result), code


@app.route("/api/runs/<int:run_id>/cancel", methods=["POST"])
def api_cancel_run(run_id):
    """Cancel a running workflow on GitHub."""
    result = gh_client.cancel_run(run_id)
    code = 200 if result.get("success") else 400
    return jsonify(result), code


@app.route("/api/runs/<int:run_id>/jobs")
def api_run_jobs(run_id):
    """Get jobs and steps breakdown for a run."""
    jobs = gh_client.get_run_jobs(run_id)
    return jsonify({"jobs": jobs})


@app.route("/api/runs/<int:run_id>/logs")
def api_run_logs(run_id):
    """Get minimal execution logs for a run."""
    max_lines = request.args.get("lines", 100, type=int)
    log_data = gh_client.get_run_logs(run_id, max_lines=max_lines)
    return jsonify(log_data)





@app.route("/api/rate-limit")
def api_rate_limit():
    return jsonify(gh_client.get_rate_limit())


@app.route("/api/db/stats")
def api_db_stats():
    """Get live PostgreSQL database connection metrics and record counts."""
    try:
        from sync_to_postgres import get_db_stats
        return jsonify(get_db_stats())
    except Exception as e:
        has_pg = bool(os.getenv("DATABASE_URL") or os.getenv("PG_HOST") or os.getenv("PGHOST"))
        return jsonify({
            "configured": has_pg,
            "connected": False,
            "error": str(e),
            "total_products": 0,
            "stores": []
        })



# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("================================================================")
    print("  SCRAPER WORKFLOW DASHBOARD (GitHub Connected)")
    print(f"  Repository : https://github.com/{GITHUB_REPO}")
    print(f"  Token      : {'Configured (' + GITHUB_TOKEN[:10] + '...)' if GITHUB_TOKEN else 'MISSING'}")
    print(f"  Local URL  : http://localhost:{PORT}")
    print("================================================================")
    app.run(host="0.0.0.0", port=PORT, debug=False)
