from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .services.detector import CrowdDetector, DetectionResult
from .db import get_db_pool, insert_crowd_observation

app = FastAPI(title="Real-Time Crowd Management System", version="0.1.0")

# CORS for local dev
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class HealthResponse(BaseModel):
	status: str
	time: datetime


class ThresholdConfig(BaseModel):
	location_id: str
	max_density: int


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
	return HealthResponse(status="ok", time=datetime.now(timezone.utc))


@app.post("/config/threshold")
async def set_threshold(config: ThresholdConfig) -> dict[str, Any]:
	# For now store in memory; could persist to DB/config service later
	app.state.thresholds = getattr(app.state, "thresholds", {})
	app.state.thresholds[config.location_id] = config.max_density
	return {"ok": True}


@app.websocket("/ws/stream/{location_id}")
async def ws_stream(websocket: WebSocket, location_id: str, db_pool=Depends(get_db_pool)) -> None:
	await websocket.accept()

	# Initialize detector per connection
	detector = CrowdDetector()

	try:
		async for result in _generate_results(detector, location_id):
			# Persist to DB (fire-and-forget)
			asyncio.create_task(
				insert_crowd_observation(
					db_pool=db_pool,
					location_id=location_id,
					count=result.count,
					density=result.density,
					timestamp=result.timestamp,
				)
			)

			payload = {
				"location_id": location_id,
				"count": result.count,
				"density": result.density,
				"timestamp": result.timestamp.isoformat(),
				"alert": _should_alert(location_id, result.count),
			}
			await websocket.send_text(json.dumps(payload))
	except WebSocketDisconnect:
		return


async def _generate_results(detector: CrowdDetector, location_id: str) -> AsyncIterator[DetectionResult]:
	# In a real impl, we would read frames from a camera/RTSP. Here we simulate.
	while True:
		yield await detector.detect_once(location_id)
		await asyncio.sleep(1.0)


def _should_alert(location_id: str, count: int) -> bool:
	thresholds: dict[str, int] = getattr(app.state, "thresholds", {})
	max_density = thresholds.get(location_id)
	if max_density is None:
		return False
	return count >= max_density


# Simple REST access to latest aggregates (placeholder)
@app.get("/api/locations/{location_id}/latest")
async def latest(location_id: str, db_pool=Depends(get_db_pool)) -> dict[str, Any]:
	# Return a minimal shape for the dashboard to consume
	return {"location_id": location_id, "count": 0, "density": 0.0, "timestamp": datetime.now(timezone.utc).isoformat()}


# Uvicorn entrypoint: `python -m app.main`
if __name__ == "__main__":
	import uvicorn

	uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)

