# Reports bot
## General Outline
### One Liner
- Once triggered, pull Schwab account data and place data into a google sheets page.

### Goals / Requirements
1. Formatting data, combine same trades to single lines for automatic percentage gain/loss calculations
2. Formatting data, for optimal graphing of data with google sheets
3. Creation of new data page for each report?
4. Automatic date range from last trigger to current trigger

### Running Tests
1. Install dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```
2. Run the tests with:
   ```bash
   pytest
   ```
## Configuration
Copy `.env.example` to `config/.env` and adjust the values to match your environment. See `config/config.md` for a detailed description of each key.

