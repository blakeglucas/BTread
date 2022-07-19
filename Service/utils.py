import asyncio

UUID_POSTFIX = '0000-1000-8000-00805f9b34fb'

def uuid_from_sid(sid: str, postfix=UUID_POSTFIX):
    return f'{sid.zfill(8)}-{postfix}'

def asyncio_threading_middleware(fn, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(fn(*args, **kwargs))
    loop.close()