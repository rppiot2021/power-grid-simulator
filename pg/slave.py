import asyncio
import websockets


async def hello(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello world!")
        t = await websocket.recv()
        print(t)
        print()

        await websocket.send("init_data")
        t = await websocket.recv()
        print(t)
        print()

        await websocket.send("curr_data")
        t = await websocket.recv()
        print(t)
        print()

asyncio.get_event_loop().run_until_complete(
    hello('ws://localhost:8765'))