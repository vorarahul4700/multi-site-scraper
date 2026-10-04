#!/usr/bin/env python3
"""
Universal Database Initializer (PostgreSQL & MySQL)
Automatically applies the appropriate schema based on configured environment variables.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


def init_postgres():
    from sync_to_postgres import init_database
    print("Initializing PostgreSQL database...")
    init_database()


def init_mysql():
    import pymysql
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user = os.getenv("MYSQL_USER")
    mysql_pass = os.getenv("MYSQL_PASS")
    mysql_db = os.getenv("MYSQL_DB")

    print("Connecting to MySQL...")
    conn = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_pass,
        database=mysql_db
    )
    cursor = conn.cursor()
    schema_path = PROJECT_ROOT / "data" / "sql" / "new_scraping_schema_mysql.sql"
    if schema_path.exists():
        print(f"Executing MySQL schema from {schema_path}...")
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        for stmt in sql.split(";"):
            clean_stmt = "\n".join(
                line for line in stmt.split("\n") if not line.strip().startswith("--")
            ).strip()
            if clean_stmt:
                cursor.execute(clean_stmt)
        conn.commit()
    cursor.close()
    conn.close()
    print("✓ MySQL database tables initialized successfully.")


def main():
    has_pg = bool(os.getenv("DATABASE_URL") or os.getenv("PG_HOST") or os.getenv("PGHOST"))
    has_mysql = bool(os.getenv("MYSQL_HOST") and os.getenv("MYSQL_USER"))

    if has_pg:
        init_postgres()
    elif has_mysql:
        init_mysql()
    else:
        print("[Notice] Neither DATABASE_URL / PG_HOST nor MYSQL_HOST found in environment.")
        print("To initialize PostgreSQL on Railway or locally, set DATABASE_URL or PG_HOST in .env.")


if __name__ == "__main__":
    main()
