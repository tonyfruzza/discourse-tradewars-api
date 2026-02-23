"""Pathfinding service: BFS shortest path through warp graph."""

from collections import defaultdict, deque

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sector import SectorWarp


async def find_path(db: AsyncSession, from_sector: int, to_sector: int) -> dict:
    """Find shortest path from from_sector to to_sector via BFS."""
    if from_sector == to_sector:
        return {"path": [from_sector], "hops": 0}

    # Load full warp graph
    result = await db.execute(select(SectorWarp.from_sector_id, SectorWarp.to_sector_id))
    adj: dict[int, set[int]] = defaultdict(set)
    for row in result.all():
        adj[row[0]].add(row[1])

    # BFS
    visited: set[int] = set()
    queue: deque[list[int]] = deque([[from_sector]])

    while queue:
        path = queue.popleft()
        current = path[-1]
        if current in visited:
            continue
        visited.add(current)

        for neighbor in adj.get(current, set()):
            new_path = path + [neighbor]
            if neighbor == to_sector:
                return {"path": new_path, "hops": len(new_path) - 1}
            if neighbor not in visited:
                queue.append(new_path)

    return {"path": [], "hops": -1, "error": "No path found"}
