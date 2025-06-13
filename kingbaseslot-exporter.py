import os
import asyncpg
from fastapi import FastAPI, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", 54321))  # Kingbase 默认端口通常是54321
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "test")

async def get_replication_slots():
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    rows = await conn.fetch("SELECT * FROM sys_replication_slots;")
    await conn.close()
    return rows

@app.get("/health")
async def health_check():
    return "ok"

@app.get("/metrics")
async def metrics():
    registry = CollectorRegistry()
    slot_active = Gauge(
        "kingbase_replication_slot_active",
        "Replication slot active status (1=active, 0=inactive)",
        ["slot_name", "plugin", "slot_type", "db_host", "db_port"],
        registry=registry,
    )
    slot_restart_lsn = Gauge(
        "kingbase_replication_slot_restart_lsn",
        "Replication slot restart_lsn (LSN as float for monitoring)",
        ["slot_name", "db_host", "db_port"],
        registry=registry,
    )

    rows = await get_replication_slots()
    for row in rows:
        slot_active.labels(
            slot_name=row["slot_name"],
            plugin=row.get("plugin", "none"),
            slot_type=row.get("slot_type", "none"),
            db_host=DB_HOST,
            db_port=str(DB_PORT),
        ).set(1 if row["active"] else 0)
        # LSN 不能直接转 float，这里仅做示例
        if row["restart_lsn"]:
            try:
                lsn_float = float(int(str(row["restart_lsn"]).split('/')[0], 16))
            except Exception:
                lsn_float = 0
            slot_restart_lsn.labels(slot_name=row["slot_name"], db_host=DB_HOST, db_port=str(DB_PORT)).set(lsn_float)

    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)