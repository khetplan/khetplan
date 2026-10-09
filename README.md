# KhetPlan — Flask backend

This package keeps the existing KhetPlan HTML/CSS/JavaScript frontend and serves it through Flask. It adds a SQLite-backed API for saving the planner state and recording rainfall entries.

## Run on Windows

1. Install Python 3.10 or newer from https://www.python.org/downloads/ (enable **Add Python to PATH** during setup).
2. Extract this folder somewhere convenient.
3. Open Command Prompt in the `KhetPlan_Flask` folder.
4. Create and activate a virtual environment (recommended):
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```
5. Install Flask:
   ```bat
   pip install -r requirements.txt
   ```
6. Start the server:
   ```bat
   python app.py
   ```
7. Open http://127.0.0.1:5000 in your browser.

## API endpoints

- `GET /api/health` — checks the server.
- `GET /api/state` — reads the saved planner state.
- `POST /api/state` — saves planner settings, completed tasks and the active plan as JSON.
- `GET /api/rain-logs` — returns recent rainfall entries.
- `POST /api/rain-logs` — records a rainfall entry. JSON example: `{"rain_type":"good","note":"Rain after sowing"}`. `rain_type` must be `light`, `good`, or `heavy`.

The database `khetplan.db` is created automatically beside `app.py`. Keep the server running while using the app. The planner still keeps a browser-local copy as a fallback.

## Notes

- This is a local development setup, not a public production deployment.
- The app currently has one shared saved planner state. Before hosting it for multiple users, add user accounts and per-user state separation, CSRF/security controls, and production server configuration.
- Crop costs, yields, and profit values are estimates from the original frontend, not live market or agricultural advice. Confirm decisions with local agriculture experts.
