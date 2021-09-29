import asyncio
import websockets


async def echo(websocket, path):
    while True:
        websocket.send('some other messages')
        try:
            recv_text=await asyncio.wait_for(websocket.recv(), timeout=0)
        except (asyncio.TimeoutError, ConnectionRefusedError):
            print('timeout')
        websocket.send('some other messages')

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, 'localhost', 8765))
asyncio.get_event_loop().run_forever()