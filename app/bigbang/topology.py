"""Warp topology generation: random warps, BFS connectivity, bridge insertion."""

import random
from collections import defaultdict, deque


def generate_warps(
    sector_count: int,
    fedspace_count: int = 10,
    min_warps: int = 1,
    max_warps: int = 6,
    bidirectional_chance: float = 0.95,
    rng: random.Random | None = None,
) -> list[tuple[int, int]]:
    """Generate random warp connections for non-FedSpace sectors.

    Returns list of (from_sector_id, to_sector_id) pairs.
    FedSpace sectors (1..fedspace_count) are excluded — they get canonical warps.
    """
    r = rng or random
    warps: set[tuple[int, int]] = set()
    all_sectors = list(range(1, sector_count + 1))
    non_fed = list(range(fedspace_count + 1, sector_count + 1))

    for sector_id in non_fed:
        num_warps = r.randint(min_warps, max_warps)
        # Pick targets from all sectors (can warp into FedSpace edge sectors)
        targets = r.sample(
            [s for s in all_sectors if s != sector_id],
            min(num_warps, len(all_sectors) - 1),
        )
        for target in targets:
            warps.add((sector_id, target))
            if r.random() < bidirectional_chance:
                warps.add((target, sector_id))

    # Also connect FedSpace border sectors to some non-fed sectors
    for border in [6, 10]:  # Dead-end FedSpace sectors
        if non_fed:
            target = r.choice(non_fed)
            warps.add((border, target))
            warps.add((target, border))

    return list(warps)


def build_adjacency(warps: list[tuple[int, int]], sector_count: int) -> dict[int, set[int]]:
    """Build adjacency list from warp pairs."""
    adj: dict[int, set[int]] = defaultdict(set)
    for a, b in warps:
        adj[a].add(b)
    # Ensure all sectors exist in the map
    for i in range(1, sector_count + 1):
        if i not in adj:
            adj[i] = set()
    return dict(adj)


def bfs_reachable(adj: dict[int, set[int]], start: int) -> set[int]:
    """BFS from start, returns all reachable sector IDs."""
    visited: set[int] = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor in adj.get(current, set()):
            if neighbor not in visited:
                queue.append(neighbor)
    return visited


def find_components(adj: dict[int, set[int]], sector_count: int) -> list[set[int]]:
    """Find all connected components."""
    visited: set[int] = set()
    components: list[set[int]] = []
    for sector_id in range(1, sector_count + 1):
        if sector_id not in visited:
            component = bfs_reachable(adj, sector_id)
            components.append(component)
            visited.update(component)
    return components


def bridge_components(
    adj: dict[int, set[int]],
    sector_count: int,
    rng: random.Random | None = None,
) -> list[tuple[int, int]]:
    """Find disconnected components and add bridge warps to connect them.

    Returns list of new (from, to) pairs to add.
    """
    r = rng or random
    components = find_components(adj, sector_count)

    if len(components) <= 1:
        return []

    # Sort components by size descending — merge smaller into the main component
    components.sort(key=len, reverse=True)
    main_component = components[0]
    bridges: list[tuple[int, int]] = []

    for component in components[1:]:
        a = r.choice(list(main_component))
        b = r.choice(list(component))
        bridges.append((a, b))
        bridges.append((b, a))
        # Merge into main
        main_component = main_component | component
        # Update adjacency
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    return bridges


def bfs_shortest_path(
    adj: dict[int, set[int]], start: int, end: int
) -> list[int] | None:
    """BFS shortest path from start to end. Returns list of sector IDs or None."""
    if start == end:
        return [start]
    visited: set[int] = set()
    queue: deque[list[int]] = deque([[start]])
    while queue:
        path = queue.popleft()
        current = path[-1]
        if current in visited:
            continue
        visited.add(current)
        for neighbor in adj.get(current, set()):
            new_path = path + [neighbor]
            if neighbor == end:
                return new_path
            if neighbor not in visited:
                queue.append(new_path)
    return None
