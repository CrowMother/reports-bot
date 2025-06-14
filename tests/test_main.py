import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import types

# create stub modules so importing main works without external package
Bot_App = types.ModuleType("Bot_App")
core = types.ModuleType("Bot_App.core")
order_utils = types.ModuleType("Bot_App.core.order_utils")
order_utils.parse_option_description = lambda d, p: ""
order_utils.extract_execution_price = lambda o: 0
database = types.ModuleType("Bot_App.core.database")
database.store_orders = lambda *a, **k: None
database.initialize_db = lambda *a, **k: None
position_tracker = types.ModuleType("Bot_App.core.position_tracker")
position_tracker.initialize_open_positions_table = lambda *a, **k: None
schwab_client = types.ModuleType("Bot_App.core.schwab_client")
class SchwabClient: pass
schwab_client.SchwabClient = SchwabClient
config = types.ModuleType("Bot_App.config")
secrets = types.ModuleType("Bot_App.config.secrets")
secrets.get_secret = lambda *a, **k: "0"
secrets.check_time_of_day = lambda *a, **k: True
secrets.str_to_bool = lambda *a, **k: False

sys.modules.update({
    'Bot_App': Bot_App,
    'Bot_App.core': core,
    'Bot_App.core.order_utils': order_utils,
    'Bot_App.core.database': database,
    'Bot_App.core.position_tracker': position_tracker,
    'Bot_App.core.schwab_client': schwab_client,
    'Bot_App.config': config,
    'Bot_App.config.secrets': secrets,
})

import main

class DummyClient:
    def __init__(self, orders):
        self.orders = orders
    def get_account_positions(self, status_filter="FILLED", hours=1):
        return self.orders

def test_loop_work_processes_orders(monkeypatch):
    calls = {}
    monkeypatch.setattr(main, 'initialize_db', lambda p, drop_table=False: calls.setdefault('init_db', True))
    monkeypatch.setattr(main, 'initialize_open_positions_table', lambda p: calls.setdefault('init_open', True))
    monkeypatch.setattr(main, 'store_orders', lambda orders, db_path=None: calls.setdefault('store', orders))
    monkeypatch.setattr(main, 'send_to_gsheet', lambda orders, db_path=None: calls.setdefault('send', orders))

    client = DummyClient(['order'])
    main.loop_work(client)

    assert calls['store'] == ['order']
    assert calls['send'] == ['order']

def test_loop_work_no_orders(monkeypatch):
    monkeypatch.setattr(main, 'store_orders', lambda *a, **k: (_ for _ in ()).throw(AssertionError('store_orders should not be called')))
    monkeypatch.setattr(main, 'send_to_gsheet', lambda *a, **k: (_ for _ in ()).throw(AssertionError('send_to_gsheet should not be called')))
    monkeypatch.setattr(main, 'initialize_db', lambda *a, **k: None)
    monkeypatch.setattr(main, 'initialize_open_positions_table', lambda *a, **k: None)

    client = DummyClient([])
    main.loop_work(client)


