import os
from aiohttp import web

# 접속한 시청자와 OBS를 기억할 명단
connected_clients = set()

async def websocket_handler(request):
    # 1. 웹소켓 통신이 아닌 경우 (Render의 생존 확인 인사)
    if request.headers.get('Upgrade', '').lower() != 'websocket':
        return web.Response(text="Render Health Check OK - Server is Alive!")

    # 2. 웹소켓 통신인 경우 (그림 데이터 중계)
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    connected_clients.add(ws)
    print(f"🟢 연결 성공! (현재 접속: {len(connected_clients)}명)")
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # 받은 그림 데이터를 나를 제외한 모두에게 뿌림
                for client in connected_clients:
                    if client != ws:
                        await client.send_str(msg.data)
    finally:
        connected_clients.remove(ws)
        print(f"🔴 연결 종료. (현재 접속: {len(connected_clients)}명)")
    
    return ws

# 서버 설정 및 실행
app = web.Application()
app.router.add_get('/', websocket_handler)

if __name__ == '__main__':
    # Render가 부여하는 동적 포트를 자동으로 찾아냅니다. (로컬 테스트 시 8765)
    port = int(os.environ.get("PORT", 8765))
    print(f"🚀 서버가 포트 {port}에서 가동됩니다...")
    web.run_app(app, port=port)