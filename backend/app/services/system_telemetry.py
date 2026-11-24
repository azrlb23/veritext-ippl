from __future__ import annotations

import asyncio
import os
import subprocess
import sys


def collect_host_cpu_memory() -> tuple[float, float]:
    """Mengambil persentase beban CPU & penggunaan memori aktual tanpa dependensi eksternal."""
    cpu_pct = 0.0
    try:
        load1 = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        cpu_pct = round(min(100.0, max(0.0, (load1 / cores) * 100.0)), 1)
    except (AttributeError, OSError):
        cpu_pct = 0.0

    mem_pct = 0.0
    try:
        if os.path.exists("/proc/meminfo"):
            info: dict[str, int] = {}
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        info[parts[0].rstrip(":")] = int(parts[1])
            total = info.get("MemTotal", 0)
            avail = info.get("MemAvailable", info.get("MemFree", 0))
            if total > 0:
                mem_pct = round(((total - avail) / total) * 100.0, 1)
        elif sys.platform == "darwin":
            total_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            out = subprocess.check_output(["vm_stat"], text=True, timeout=0.5)
            page_size = 4096
            free_pages = 0
            for line in out.splitlines():
                if "page size of" in line:
                    for tok in line.split():
                        if tok.isdigit():
                            page_size = int(tok)
                            break
                elif line.startswith(("Pages free:", "Pages inactive:", "Pages speculative:")):
                    val = line.split(":", 1)[1].strip().rstrip(".")
                    if val.isdigit():
                        free_pages += int(val)
            if total_bytes > 0:
                used = max(0, total_bytes - free_pages * page_size)
                mem_pct = round(min(100.0, (used / total_bytes) * 100.0), 1)
    except Exception:  # noqa: BLE001
        mem_pct = 0.0

    return cpu_pct, mem_pct


async def collect_redis_telemetry() -> tuple[str, float]:
    try:
        import redis.asyncio as aioredis
        from app.core.config import settings

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5, socket_timeout=0.5)
        try:
            if not await client.ping():
                return "DEGRADED", 0.0
            used_mb = 0.0
            try:
                mem_info = await client.info("memory")
                if isinstance(mem_info, dict):
                    used_mb = round(float(mem_info.get("used_memory", 0)) / (1024 * 1024), 2)
            except Exception:  # noqa: BLE001
                used_mb = 0.0
            return "HEALTHY", used_mb
        finally:
            await client.aclose()
    except Exception:  # noqa: BLE001
        return "DOWN", 0.0


def _inspect_celery_workers_sync() -> int:
    try:
        from app.workers.celery_app import celery_app

        insp = celery_app.control.inspect(timeout=0.4)
        ping = insp.ping() if insp else None
        return len(ping) if isinstance(ping, dict) else 0
    except Exception:  # noqa: BLE001
        return 0


async def collect_celery_workers_count() -> int:
    try:
        return await asyncio.wait_for(asyncio.to_thread(_inspect_celery_workers_sync), timeout=0.8)
    except Exception:  # noqa: BLE001
        return 0
