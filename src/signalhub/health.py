import asyncio
from aiohttp import web

async def healthz(request):
    return web.Response(text="ok")

async def metrics(request):
    # These would be updated from Handler instance in real app
    counters = request.app["metrics"]
    return web.json_response(counters)

async def start_health_server(config):
    app = web.Application()
    app["metrics"] = {
        "emails_received": 0,
        "pushed_ok": 0,
        "pushed_failed": 0,
        "dedup_dropped": 0,
        "rate_limited": 0,
    }
    app.router.add_get("/healthz", healthz)
    app.router.add_get("/metrics", metrics)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.health_port)
    await site.start()
    while True:
        await asyncio.sleep(3600)
