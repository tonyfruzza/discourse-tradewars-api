from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, health, player, port, sector, ship, tick


def _run_migrations() -> None:
    """Run Alembic migrations synchronously (called from a worker thread)."""
    from alembic.config import Config

    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import anyio

    await anyio.to_thread.run_sync(_run_migrations)
    yield


app = FastAPI(title="TradeWars API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(player.router)
app.include_router(sector.router)
app.include_router(port.router)
app.include_router(ship.router)
app.include_router(admin.router)
app.include_router(tick.router)
