import gspread
from google.oauth2.service_account import Credentials
import logging
from Bot_App.config.secrets import get_date

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_gsheets_account(service_account_path):
    try:
        credentials = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Google Sheets: {e}")
        raise

def connect_to_sheet(client, spreadsheet_id, sheet_name):
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except Exception as e:
        logging.error(f"Failed to connect to sheet '{sheet_name}': {e}")
        raise

def get_next_empty_row(worksheet, column_index=1):
    try:
        values = worksheet.col_values(column_index)
        return len(values) + 1
    except Exception as e:
        logging.error(f"Failed to find next empty row: {e}")
        return 2

def insert_data(worksheet, cell, data):
    try:
        worksheet.update(cell, data, value_input_option='USER_ENTERED')
    except Exception as e:
        logging.error(f"Failed to insert data at {cell}: {e}")

def copy_headers(worksheet, location):
    try:
        worksheet.update(
            location,
            [[
                "=A1", "=B1", "=C1", "=D1", "=E1", "=F1", "=G1", "=H1", "=I1"
            ]],
            value_input_option="USER_ENTERED"
        )
    except Exception as e:
        logging.error(f"Failed to copy headers: {e}")

def format_data_row(closing_order, open_order):
    try:
        symbol = open_order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("symbol", "N/A")
        description = open_order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("description", "")
        date = parse_option_description(description, 2)
        strike = parse_option_description(description, 3)
        put_call = parse_option_description(description, 4)
        open_price = extract_execution_price(open_order)
        close_price = extract_execution_price(closing_order)

        return [
            str(get_date()),
            str(symbol.split(" ")[0]),
            str(date),
            f"{strike} {put_call}",
            str(open_price),
            str(close_price)
        ]
    except Exception as e:
        logging.error(f"Error formatting row data: {e}")
        return ["Error"] * 5

# Reuse helpers from Bot_App core
from Bot_App.core.order_utils import parse_option_description, extract_execution_price
