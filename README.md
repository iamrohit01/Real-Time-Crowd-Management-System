# Real-Time Crowd Management System

A full-stack system that estimates, monitors, and visualizes crowd density in real time using computer vision and time-series storage. It provides live dashboards, WebSocket updates, and persistence for analytics.

## Tech Stack
- Backend: FastAPI, WebSockets, OpenCV stubs, asyncpg
- ML: Placeholder detector 
- Database: TimescaleDB 
- Frontend: React, Leaflet.js, Recharts
- Containerization: Docker, docker-compose

## Features
- Real-time crowd count stream via WebSockets
- Threshold-based alerts exposed in the live payload
- Interactive map and time-series chart
- Time-series storage in TimescaleDB for future analysis

## Repository Layout
```
  Backend/
    app/
      db.py
      main.py
      services/
        detector.py
    Dockerfile
    requirements.txt
  Frontend/
    src/
      App.jsx
      main.jsx
    index.html
    vite.config.js
    package.json
    Dockerfile
  docker-compose.yml
  README.md
```

## Quick Start (Docker)
Prerequisites: Docker Desktop (with Compose)

```bash
# From repo root
docker compose up --build
```

- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:5173`

The frontend opens a WebSocket to the backend and displays a demo location marker with live counts and alerts.

## Backend
### Run locally (without Docker)
```bash
cd Backend
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set env vars if not using docker
export POSTGRES_HOST=localhost
export POSTGRES_DB=crowd
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API
- Health: `GET /health`
- Set threshold: `POST /config/threshold`
  - Body: `{ "location_id": "demo-square", "max_density": 60 }`
- Latest (placeholder): `GET /api/locations/{location_id}/latest`

### WebSocket
- `ws://localhost:8000/ws/stream/{location_id}`
- Example payload:
```json
{
  "location_id": "demo-square",
  "count": 42,
  "density": 0.35,
  "timestamp": "2024-01-01T00:00:00.000Z",
  "alert": false
}
```

### Database
- Image: `timescale/timescaledb:latest-pg15`
- Default credentials (docker-compose):
  - DB: `crowd`
  - User: `postgres`
  - Password: `postgres`

Schema is created automatically at startup:
- Table: `crowd_observations(location_id, observed_at, count, density)`
- Hypertable: `create_hypertable('crowd_observations', 'observed_at')`

## Frontend
### Run locally (without Docker)
```bash
cd Frontend
npm install
npm run dev
# Open http://localhost:5173
```

- The app opens a WebSocket to `ws://<host>:8000/ws/stream/demo-square`.
- Update the constant `LOCATION_ID` in `Frontend/src/App.jsx` as needed.

## Configuration
Backend environment variables (defaults used by docker-compose):
- `POSTGRES_HOST=db`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=crowd`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `PORT=8000`

Sample file: `Backend/.env.example`

## Replacing the Detector with a Real Model
- Implement loading a model in `Backend/app/services/detector.py`.
- Replace `detect_once` to read frames from a camera/RTSP and run inference.
- Optionally create a video capture service and a per-location pipeline with tracking to stabilize counts.

## Troubleshooting
- Port conflicts: ensure 8000 (backend), 5173 (frontend), and 5432 (db) are free.
- WebSocket not connecting: verify backend logs and that Docker network is up.
- Leaflet markers not visible: icon paths are fixed in `App.jsx` (vite build friendly).
- TimescaleDB extension: the container enables TimescaleDB; if running locally, ensure extension is installed and enabled.

## Roadmap / Extensions
- Predictive analytics using stored time-series
- IoT sensor integration via MQTT/Kafka
- Role-based views (admin/security/public)
- Edge deployment

