import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket):
    # 누군가 서버에 접속하면 명단에 추가
    connected_clients.add(websocket)
    print(f"🟢 연결 성공! (현재 접속: {len(connected_clients)}명)")
    
    try:
        async for message in websocket:
            # 한 명이 그린 그림 좌표를 나머지 모두(OBS 포함)에게 뿌려줌
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"🔴 연결 종료. (현재 접속: {len(connected_clients)}명)")

async def main():
    # 내 컴퓨터의 8765번 포트에서 서버 오픈
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("🚀 코스노우 드로잉 중계 서버가 가동되었습니다! (대기 중...)")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())