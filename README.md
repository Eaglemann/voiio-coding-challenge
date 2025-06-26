# Train Reminder Script

This script monitors train departures between specified stations and sends a notification
to remind you when it's time to leave to catch your train.

Requirements:

- Python 3.13+
- Dependencies are managed via pyproject.toml

## How to run:

1. Initialize and install dependencies:
   ```bash
   uv install
   ```
2. Run the script:
   `bash
   uv run main.py
    `
   The script will then run continuously and notify you when it's time to leave. The script is assumming the trains are only every 1h.
