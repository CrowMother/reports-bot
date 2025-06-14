import os
import sqlite3
import tempfile
import pytest
from Bot_App.core import position_tracker


def setup_db_with_open_positions():
    db_fd, db_path = tempfile.mkstemp()
    position_tracker.initialize_open_positions_table(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO open_positions (id, ticker, description, price, quantity, entered_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("id1", "AAPL", "AAPL 01/01/2025 $200 Call", 1.00, 1, "2024-01-01T10:00:00Z"),
        ("id2", "AAPL", "AAPL 01/01/2025 $200 Call", 2.00, 2, "2024-01-02T10:00:00Z"),
    ])
    conn.commit()
    conn.close()
    return db_path

def test_consume_partial_match():
    db_path = setup_db_with_open_positions()
    order = {
        "orderLegCollection": [{
            "instrument": {
                "symbol": "AAPL",
                "description": "AAPL 01/01/2025 $200 Call"
            }
        }],
        "quantity": 2,
        "price": 3.00
    }
    avg, used = position_tracker.consume_open_position(order, db_path)
    assert round(avg, 2) == 1.5
    assert used == 2
    os.remove(db_path)


def test_consume_full_match():
    db_path = setup_db_with_open_positions()
    order = {
        "orderLegCollection": [{
            "instrument": {
                "symbol": "AAPL",
                "description": "AAPL 01/01/2025 $200 Call"
            }
        }],
        "quantity": 3,
        "price": 3.00,
    }
    avg, used = position_tracker.consume_open_position(order, db_path)
    assert round(avg, 2) == 1.67
    assert used == 3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM open_positions")
    remaining = cursor.fetchone()[0]
    conn.close()
    assert remaining == 0
    os.remove(db_path)


def test_consume_no_match():
    db_path = setup_db_with_open_positions()
    order = {
        "orderLegCollection": [{
            "instrument": {
                "symbol": "MSFT",
                "description": "MSFT 01/01/2025 $200 Call"
            }
        }],
        "quantity": 1,
        "price": 3.00,
    }
    avg, used = position_tracker.consume_open_position(order, db_path)
    assert avg is None
    assert used == 0
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM open_positions")
    remaining = cursor.fetchone()[0]
    conn.close()
    assert remaining == 2
    os.remove(db_path)
