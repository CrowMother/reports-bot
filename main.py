import time
import logging

from Bot_App.core.schwab_client import SchwabClient
from Bot_App.core.database import store_orders, initialize_db
from Bot_App.core.position_tracker import initialize_open_positions_table
from Bot_App.config.secrets import get_secret, check_time_of_day, str_to_bool
from functions import send_to_gsheet

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Config
LOOP_TYPE = get_secret("LOOP_TYPE", "config/.env", "DAILY")
HOUR_OF_DAY = int(get_secret("HOUR_OF_DAY", "config/.env", 17))
DATABASE_PATH = get_secret("DATABASE_PATH", "config/.env", "data/orders.db")
TIME_DELTA = int(get_secret("TIME_DELTA", "config/.env", 24))
SCHWAB_APP_KEY = get_secret("SCHWAB_APP_KEY", "config/.env")
SCHWAB_APP_SECRET = get_secret("SCHWAB_APP_SECRET", "config/.env")
LOOP_FREQUENCY = int(get_secret("LOOP_FREQUENCY", "config/.env", 60))

ISREPORTGEN = False

def loop_work():
    logging.info("Running loop_work()")
    client = SchwabClient(SCHWAB_APP_KEY, SCHWAB_APP_SECRET)
    initialize_db(DATABASE_PATH, drop_table= False)
    initialize_open_positions_table(DATABASE_PATH)

    # Fetch Schwab orders
    raw_orders = client.get_account_positions("FILLED", hours=TIME_DELTA)
    if not raw_orders:
        logging.info("No orders returned from Schwab.")
        return

    # Store new orders and match/process closures
    store_orders(raw_orders, db_path=DATABASE_PATH)

    # Push closed positions to GSheet
    send_to_gsheet(raw_orders, db_path=DATABASE_PATH)

def main():
    global ISREPORTGEN
    logging.info("Starting Schwab GSheet Tracker...")

    while True:
        if LOOP_TYPE == "DEBUG":
            loop_work()
            break

        elif LOOP_TYPE == "DAILY":
            if check_time_of_day(HOUR_OF_DAY):
                if not ISREPORTGEN:
                    loop_work()
                    ISREPORTGEN = True
            else:
                ISREPORTGEN = False

        time.sleep(LOOP_FREQUENCY)

if __name__ == "__main__":
    main()
