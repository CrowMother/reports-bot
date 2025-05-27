import logging
import sqlite3

from Bot_App.core.order_utils import generate_order_id, find_matching_open_order
from Bot_App.config.secrets import get_secret
from gsheet import (
    connect_gsheets_account,
    connect_to_sheet,
    copy_headers,
    get_next_empty_row,
    insert_data,
    format_data_row,
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def send_to_gsheet(all_orders, db_path="data/orders.db"):
    try:
        creds = get_secret("GSHEETS_CREDENTIALS", "config/.env")
        sheet_id = get_secret("GSHEETS_SHEET_ID", "config/.env")
        sheet_name = get_secret("GSHEETS_SHEET_NAME", "config/.env")

        client = connect_gsheets_account(creds)
        sheet = connect_to_sheet(client, sheet_id, sheet_name)
        copy_headers(sheet, f"A{get_next_empty_row(sheet, 2)}")

        closed_orders = [o for o in all_orders if _is_closing_order(o)]
        posted_ids = _get_already_posted_ids(db_path)

        for order in closed_orders:
            open_order = find_matching_open_order(order, db_path)
            if not open_order:
                logging.debug("No matching open order found for this closing order.")
                continue

            row_data = format_data_row(order, open_order)
            order_id = generate_order_id(order)

            if order_id not in posted_ids:
                row = get_next_empty_row(sheet, 2)
                insert_data(sheet, f"A{row}", [row_data])
                _mark_posted(order_id, db_path)

    except Exception as e:
        logging.error(f"Error sending data to GSheet: {e}")


def _is_closing_order(order):
    try:
        return order.get("orderLegCollection", [{}])[0].get("positionEffect") == "CLOSING"
    except Exception:
        return False


def _get_already_posted_ids(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM schwab_orders WHERE posted_to_discord = TRUE")
        ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return ids
    except Exception as e:
        logging.error(f"Failed to read posted IDs: {e}")
        return set()


def _mark_posted(order_id, db_path):
    try:
        from Bot_App.core.database import mark_as_posted
        mark_as_posted(order_id, db_path)
    except Exception as e:
        logging.error(f"Failed to mark order as posted: {e}")
