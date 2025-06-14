import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import types

# stub modules so importing functions works without external package
Bot_App = types.ModuleType("Bot_App")
core = types.ModuleType("Bot_App.core")
order_utils = types.ModuleType("Bot_App.core.order_utils")
order_utils.parse_option_description = lambda d, p: ""
order_utils.extract_execution_price = lambda o: 0
order_utils.generate_order_id = lambda order: 'id'
order_utils.find_matching_open_order = lambda order, db: {'open':'order'}
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
secrets.get_secret = lambda *a, **k: 'x'
secrets.get_date = lambda: '01/01'

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

import functions

class DummySheet:
    def __init__(self):
        self.inserted = []
        self.headers = []


def test_send_to_gsheet(monkeypatch):
    sheet = DummySheet()
    monkeypatch.setattr(functions, 'connect_gsheets_account', lambda path: 'client')
    monkeypatch.setattr(functions, 'connect_to_sheet', lambda client, sid, name: sheet)
    monkeypatch.setattr(functions, 'copy_headers', lambda s, loc: sheet.headers.append(loc))
    counter = {'c':0}
    def next_row(s, col=1):
        counter['c'] += 1
        return 2 if counter['c'] == 1 else 3
    monkeypatch.setattr(functions, 'get_next_empty_row', next_row)
    monkeypatch.setattr(functions, 'insert_data', lambda s, cell, data: sheet.inserted.append((cell, data)))
    monkeypatch.setattr(functions, '_get_already_posted_ids', lambda db: set())
    posted = []
    monkeypatch.setattr(functions, '_mark_posted', lambda oid, db: posted.append(oid))
    monkeypatch.setattr(functions, 'generate_order_id', lambda order: 'id1')
    monkeypatch.setattr(functions, 'format_data_row', lambda close, open_: ['row'])

    closing_order = {
        'enteredTime': '2024-01-02T00:00:00Z',
        'orderLegCollection':[{'positionEffect':'CLOSING','instrument':{'symbol':'AAPL','description':'AAPL 01/01/2025 $200 Call'}}]
    }

    functions.send_to_gsheet([closing_order], db_path=':memory:')

    assert sheet.headers == ['A2']
    assert sheet.inserted == [('A3', [['row']])]
    assert posted == ['id1']

