# Configuration Guide

Create a `config/.env` file (not committed to version control) with the following keys. You can use `.env.example` as a starting point.

| Key | Description |
| --- | ----------- |
| `GSHEETS_CREDENTIALS` | Path to the Google service account JSON file used for Sheets access. |
| `GSHEETS_SHEET_ID` | ID of the spreadsheet where reports are written. |
| `GSHEETS_SHEET_NAME` | Worksheet name within the spreadsheet. |
| `SCHWAB_APP_KEY` | Schwab API application key. |
| `SCHWAB_APP_SECRET` | Schwab API secret. |
| `DATABASE_PATH` | Location of the SQLite database file. Defaults to `data/orders.db`. |
| `LOOP_TYPE` | `DAILY` to run once per day or `DEBUG` for a single run. Defaults to `DAILY`. |
| `HOUR_OF_DAY` | Hour (0-23) to trigger the daily run. Defaults to `17`. |
| `TIME_DELTA` | Number of past hours of orders to fetch from Schwab. Defaults to `24`. |
| `LOOP_FREQUENCY` | Interval in seconds between scheduler checks. Defaults to `60`. |

Copy `.env.example` to `config/.env` and update the values accordingly. The application loads this file at startup.

To use these variables securely in Codex, store the credentials as [secrets](https://docs.docker.com/engine/swarm/secrets/). When running the container, map the secrets or environment values rather than committing them to the repository.
