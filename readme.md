# Reports bot
## General Outline
### One Liner
- Once triggered, pull Schwab account data and place data into a google sheets page.

### Goals / Requirements 
1. Formatting data, combine same trades to single lines for automatic percentage gain/loss calculations
2. Formatting data, for optimal graphing of data with google sheets
3. Creation of new data page for each report? 
4. Automatic date range from last trigger to current trigger

## Configuration
Copy `.env.example` to `config/.env` and adjust the values to match your environment. See `config/config.md` for a detailed description of each key.

When running inside Codex, provide secrets as environment variables instead of editing the file directly. This keeps credentials out of source control and build logs.
