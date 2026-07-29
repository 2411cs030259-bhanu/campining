"""
services/report_service.py
Builds downloadable analytics reports from processed data and
records report metadata in the database for future retrieval
(Version 2.0 will add a "report history" view on top of this table).
"""

import os
import uuid
from datetime import datetime

import pandas as pd

from database import get_db_cursor
from config import get_config

config = get_config()


def build_report_csv(analysis: dict, user_id: int) -> str:
    """
    Write a CSV report file to the reports folder and return its
    filename (not full path - callers should join with REPORT_FOLDER).
    """
    os.makedirs(config.REPORT_FOLDER, exist_ok=True)

    filename = f"report_{user_id}_{uuid.uuid4().hex[:8]}.csv"
    full_path = os.path.join(config.REPORT_FOLDER, filename)

    kpis = analysis["kpis"]
    campaigns_df = pd.DataFrame(analysis["campaigns"])
    platforms_df = pd.DataFrame(analysis["platforms"])

    with open(full_path, "w", newline="", encoding="utf-8") as f:
        f.write("Marketing Analytics Report\n")
        f.write(f"Generated At,{datetime.utcnow().isoformat()}\n\n")

        f.write("Performance Overview\n")
        f.write("Metric,Value\n")
        f.write(f"Total Spend,{kpis['total_spend']}\n")
        f.write(f"Total Revenue,{kpis['total_revenue']}\n")
        f.write(f"CTR (%),{kpis['ctr']}\n")
        f.write(f"CPC,{kpis['cpc']}\n")
        f.write(f"CPA,{kpis['cpa']}\n")
        f.write(f"ROAS,{kpis['roas']}\n\n")

        f.write("Campaign Breakdown\n")
        campaigns_df.to_csv(f, index=False)
        f.write("\n")

        f.write("Platform Breakdown\n")
        platforms_df.to_csv(f, index=False)
        f.write("\n")

        f.write("Insights\n")
        for insight in analysis["insights"]:
            f.write(f"- {insight}\n")

    return filename


def save_report_record(user_id: int, dataset_id, report_filename: str, kpis: dict) -> int:
    """Persist report metadata so it can be listed/retrieved later."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO reports
                (user_id, dataset_id, report_filename, total_spend, total_revenue, ctr, cpc, cpa, roas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                dataset_id,
                report_filename,
                kpis["total_spend"],
                kpis["total_revenue"],
                kpis["ctr"],
                kpis["cpc"],
                kpis["cpa"],
                kpis["roas"],
            ),
        )
        return cursor.lastrowid


def save_dataset_record(user_id: int, original_filename: str, stored_filename: str, row_count: int) -> int:
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO datasets (user_id, original_filename, stored_filename, row_count)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, original_filename, stored_filename, row_count),
        )
        return cursor.lastrowid


def list_reports_for_user(user_id: int) -> list:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, report_filename, total_spend, total_revenue, ctr, cpc, cpa, roas, created_at
            FROM reports
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
