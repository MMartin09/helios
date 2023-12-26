from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def scheduler_context():
    try:
        print("STARTING THE SCHEDULER")
        scheduler.start()
        yield
    finally:
        print("SHUTTING DOWN THE SCHEDULER")
        scheduler.shutdown()
