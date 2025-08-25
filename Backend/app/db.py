from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import asyncpg

_DB_POOL: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
	global _DB_POOL
	if _DB_POOL is None:
		_DB_POOL = await asyncpg.create_pool(dsn=_get_dsn(), min_size=1, max_size=5)
		await _init_schema(_DB_POOL)
	return _DB_POOL


def _get_dsn() -> str:
	host = os.getenv("POSTGRES_HOST", "db")
	port = os.getenv("POSTGRES_PORT", "5432")
	user = os.getenv("POSTGRES_USER", "postgres")
	password = os.getenv("POSTGRES_PASSWORD", "postgres")
	db = os.getenv("POSTGRES_DB", "crowd")
	return f"postgresql://{user}:{password}@{host}:{port}/{db}"


async def _init_schema(pool: asyncpg.Pool) -> None:
	async with pool.acquire() as conn:
		# Enable timescaledb extension and create hypertable
		await conn.execute(
			"""
			CREATE EXTENSION IF NOT EXISTS timescaledb;

			CREATE TABLE IF NOT EXISTS crowd_observations (
				id BIGSERIAL PRIMARY KEY,
				location_id TEXT NOT NULL,
				observed_at TIMESTAMPTZ NOT NULL,
				count INTEGER NOT NULL,
				density DOUBLE PRECISION NOT NULL
			);

			SELECT create_hypertable('crowd_observations', 'observed_at', if_not_exists => TRUE);
			"""
		)


async def insert_crowd_observation(
	db_pool: asyncpg.Pool,
	location_id: str,
	count: int,
	density: float,
	timestamp: datetime,
) -> None:
	async with db_pool.acquire() as conn:
		await conn.execute(
			"""
			INSERT INTO crowd_observations(location_id, observed_at, count, density)
			VALUES ($1, $2, $3, $4)
			""",
			location_id,
			timestamp,
			count,
			density,
		)

