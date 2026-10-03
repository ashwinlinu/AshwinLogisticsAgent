import asyncio

from pymongo import AsyncMongoClient

from app.config.settings import settings

_clients_by_loop: dict[asyncio.AbstractEventLoop, AsyncMongoClient] = {}
_dbs_by_loop: dict[asyncio.AbstractEventLoop, object] = {}


def get_db():
    loop = asyncio.get_running_loop()

    if loop not in _clients_by_loop:
        client = AsyncMongoClient(settings.mongodb_uri)
        _clients_by_loop[loop] = client
        _dbs_by_loop[loop] = client[settings.mongodb_database]

    return _dbs_by_loop[loop]


async def ping_mongodb():
    return await get_db().client.admin.command("ping")


async def close_mongodb():
    for client in list(_clients_by_loop.values()):
        await client.close()
    _clients_by_loop.clear()
    _dbs_by_loop.clear()