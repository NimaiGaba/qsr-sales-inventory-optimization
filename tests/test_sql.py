"""
Unit Tests for SQLite Relational Database & SQL Queries
"""

import os
import sys
import sqlite3
import pytest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "qsr_analytics.db")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")


@pytest.fixture(scope="module")
def db_conn():
    """Establish connection to SQLite database."""
    if not os.path.exists(DB_PATH):
        pytest.skip("SQLite database not found. Run main.py first.")
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


def test_database_tables_exist(db_conn):
    """Verify all relational tables and analytical views exist."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
    objects = [r[0] for r in cursor.fetchall()]

    required_tables = [
        "orders",
        "order_details",
        "products",
        "locations",
        "inventory",
        "suppliers",
        "inventory_waste",
        "v_order_summary",
    ]
    for tbl in required_tables:
        assert tbl in objects, f"Expected table/view '{tbl}' missing from database"


def test_order_count_integrity(db_conn):
    """Verify orders table count and primary key uniqueness."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT OrderID) FROM orders")
    total, distinct = cursor.fetchone()
    assert total > 30000
    assert total == distinct


def test_kpi_metrics_sql_query(db_conn):
    """Verify that 01_kpi_metrics query executes and returns correct totals."""
    query = """
        SELECT 
            COUNT(DISTINCT o.OrderID) AS Total_Orders,
            ROUND(SUM(o.NetSales), 2) AS Net_Revenue,
            ROUND(SUM(o.GrossProfit), 2) AS Gross_Profit
        FROM orders o
    """
    df = pd.read_sql_query(query, db_conn)
    assert len(df) == 1
    assert df["Total_Orders"].iloc[0] > 30000
    assert df["Net_Revenue"].iloc[0] > 1000000
    assert df["Gross_Profit"].iloc[0] > 700000


def test_pareto_sql_query(db_conn):
    """Verify window functions and cumulative revenue calculation in SQL."""
    query = """
        WITH RankedProducts AS (
            SELECT 
                ProductID,
                ProductName,
                SUM(TotalPrice) AS Product_Revenue,
                ROW_NUMBER() OVER (ORDER BY SUM(TotalPrice) DESC) AS Sales_Rank
            FROM order_details
            GROUP BY ProductID, ProductName
        )
        SELECT 
            ProductID,
            ProductName,
            Product_Revenue,
            Sales_Rank,
            SUM(Product_Revenue) OVER (ORDER BY Sales_Rank) AS Running_Total
        FROM RankedProducts
        LIMIT 5;
    """
    df = pd.read_sql_query(query, db_conn)
    assert len(df) == 5
    assert df["Sales_Rank"].tolist() == [1, 2, 3, 4, 5]
    assert df["Running_Total"].iloc[0] == df["Product_Revenue"].iloc[0]
    assert df["Running_Total"].iloc[4] > df["Running_Total"].iloc[0]
