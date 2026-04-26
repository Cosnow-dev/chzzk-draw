import os
from aiohttp import web

# ★ 변경점: 접속자 명단을 '방(채널 ID)' 별로 관리하는 딕셔너리로 변경
rooms = {}

async def websocket_handler(request):
    # 1. Render 생존 확인 인사 (웹소켓이 아닐 때)
    if request.headers.get('Upgrade', '').lower() != 'websocket':
        return web.Response(text="Render Health Check OK - Server is Alive!")

    # ★ 접속 시 요청한 URL 주소 끝에서 '방 번호(채널 ID)'를 빼옵니다.
    room_id = request.match_info.get('room_id')
    if not room_id:
        return web.Response(status=400, text="Room ID is required")

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # 해당 방이 없으면 새로 만들고, 내 접속 정보를 그 방에 넣습니다.
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(ws)
    
    print(f"🟢 [{room_id}] 방에 접속! (현재 인원: {len(rooms[room_id])}명)")
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # ★ 내가 속한 방(room_id)에 있는 사람들에게만 데이터를 뿌려줍니다!
                for client in rooms[room_id]:
                    if client != ws:
                        await client.send_str(msg.data)
    finally:
        # 접속 종료 시 내 정보를 방에서 뺍니다.
        rooms[room_id].remove(ws)
        print(f"🔴 [{room_id}] 방에서 퇴장. (남은 인원: {len(rooms[room_id])}명)")
        # 방에 아무도 없으면 방 자체를 폭파(메모리 절약)
        if len(rooms[room_id]) == 0:
            del rooms[room_id]
    
    return ws

app = web.Application()
# ★ 접속 주소 뒤에 방 번호(/{room_id})를 받을 수 있도록 라우터 수정
app.router.add_get('/{room_id}', websocket_handler)
app.router.add_get('/', websocket_handler) # 기본 주소 예외 처리

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8765))
    print(f"🚀 멀티룸 서버가 포트 {port}에서 가동됩니다...")
    web.run_app(app, port=port)