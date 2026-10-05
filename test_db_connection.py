import os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    print("FAIL: DATABASE_URL not set in .env")
    sys.exit(1)

print("URL:", DATABASE_URL[:55] + "...")

try:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("OK: Connected -", cur.fetchone()[0][:60])
    cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'competitor_products')")
    exists = cur.fetchone()[0]
    print("Table exists:", exists)
    if exists:
        cur.execute("SELECT COUNT(*) FROM competitor_products")
        print("Records:", cur.fetchone()[0])
    else:
        print("NOTE: Run init_db.py to create tables")
    conn.close()
    print("RESULT: Database is working correctly!")
except Exception as e:
    print("FAIL:", e)
