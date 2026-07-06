import os
import re
import io
import sys
from datetime import datetime

from dotenv import load_dotenv
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import execute_values

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQmMlrXgRTZ01yVL7vn4EJ4sXKEeDl1LYXl6dgl0lmoEerG8860kpn6Vk70Yo5SJuOXIt7X822TsOFi/pub?output=csv"

load_dotenv()

PG_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}

TABLE_NAME = "public.gd_archives"
PRIMARY_KEY = "ID"

def fetch_sheet_csv(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text), dtype=str, keep_default_na=False)
 
 
def clean_yes_no_symbol(value: str) -> bool:
    return value.strip() in ("✔", "TRUE", "true", "1", "x", "X", "yes")
 
 
def clean_star_rating(value: str):
    value = value.strip()
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None
 
 
def clean_length_to_seconds(value: str):
    value = value.strip()
    if not value:
        return None
    parts = value.split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds
 
 
def clean_coins(value: str) -> int:
    value = value.strip()
    return len(value)
 
def clean_song_id(value: str):
    value = value.strip()
    if value == "Official":
        return -1
    return int(value) if value.isdigit() else None
 
def clean_links(value: str):
    if not value.strip():
        return []
    return [link.strip() for link in re.split(r"[,\s]+", value) if link.strip()]
 
 
def clean_upload_time(value: str):
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%m/%d/%Y %I:%M %p")
    except ValueError:
        return None
 
 
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
 
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
 
    df["ID"] = pd.to_numeric(df["ID"], errors="coerce").astype("Int64")
    df["Song ID"] = df["Song ID"].apply(clean_song_id)
    df["Length"] = df["Length"].apply(clean_length_to_seconds)
    df["Reward"] = df["Reward"].apply(clean_star_rating).astype("Int64")
    df["Rate"] = df["Rate"].apply(clean_yes_no_symbol)
    df["Coins"] = df["Coins"].apply(clean_coins)
    df["Recorded?"] = df["Recorded?"].apply(clean_yes_no_symbol)
    df["Uploaded?"] = df["Uploaded?"].apply(clean_yes_no_symbol)
    df["Thumbnail?"] = df["Thumbnail?"].apply(clean_yes_no_symbol)
    df["Link"] = df["Link"].apply(clean_links)
    df["Upload Time (EST)"] = df["Upload Time (EST)"].apply(clean_upload_time)
    df["As Of"] = datetime.now()
 
    df = df.dropna(subset=["ID"])
 
    return df
 
INSERT_COLUMNS = [
    "Level Name", "Creator", "ID", "Song", "Song ID", "Length",
    "Difficulty", "Reward", "Rate", "Coins", "Notable Info", "Recorder",
    "Recorded?", "Uploaded?", "Thumbnail?", "Link", "Upload Time (EST)", "As Of"
]
 
 
def upsert(df: pd.DataFrame):
    df = df.astype(object).where(pd.notnull(df), None)
 
    rows = [tuple(row[col] for col in INSERT_COLUMNS) for _, row in df.iterrows()]
 
    cols_sql = ", ".join(f'"{c}"' for c in INSERT_COLUMNS)
    update_sql = ", ".join(
        f'"{c}" = EXCLUDED."{c}"' for c in INSERT_COLUMNS if c != PRIMARY_KEY
    )
 
    query = f"""
        INSERT INTO {TABLE_NAME} ({cols_sql})
        VALUES %s
        ON CONFLICT ("{PRIMARY_KEY}") DO UPDATE SET
        {update_sql}
    """
 
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            execute_values(cur, query, rows)
        conn.commit()
        print(f"Upserted {len(rows)} rows into {TABLE_NAME}")
    except Exception as e:
        conn.rollback()
        print(f"Insert failed: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()
 
if __name__ == "__main__":
    raw_df = fetch_sheet_csv(SHEET_CSV_URL)
    clean_df = transform(raw_df)
    upsert(clean_df)
 