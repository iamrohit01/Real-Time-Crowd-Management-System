from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone

# Placeholder for OpenCV/YOLO-based detection. For now, we simulate results.


@dataclass
class DetectionResult:
	location_id: str
	count: int
	density: float
	timestamp: datetime


class CrowdDetector:
	def __init__(self) -> None:
		# Initialize ML models/capture here in real implementation
		self._rng = random.Random()

	async def detect_once(self, location_id: str) -> DetectionResult:
		# Simulate a realistic count and derived density
		count = self._rng.randint(0, 120)
		density = round(min(1.0, count / 120.0), 3)
		return DetectionResult(
			location_id=location_id,
			count=count,
			density=density,
			timestamp=datetime.now(timezone.utc),
		)

