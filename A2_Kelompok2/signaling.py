from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()
rooms = {}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    room_id = None
    try:
        while True:
            data = await ws.receive_json()
            typ = data.get("type")
            room = data.get("room")

            if typ == "join":
                room_id = room
                rooms.setdefault(room_id, set()).add(ws)
                for peer in rooms[room_id]:
                    if peer is not ws:
                        await peer.send_json({"type": "new-peer"})

            elif typ in ("offer", "answer", "candidate"):
                for peer in rooms.get(room, []):
                    if peer is not ws:
                        await peer.send_json({
                            "type": typ,
                            "sdp": data.get("sdp"),
                            "candidate": data.get("candidate")
                        })

            elif typ == "leave":
                if room_id in rooms and ws in rooms[room_id]:
                    rooms[room_id].remove(ws)
                    for peer in rooms[room_id]:
                        await peer.send_json({"type": "peer-left"})
                break

    except WebSocketDisconnect:
        pass
    finally:
        if room_id and room_id in rooms and ws in rooms[room_id]:
            rooms[room_id].remove(ws)
            for peer in rooms[room_id]:
                try:
                    await peer.send_json({"type": "peer-left"})
                except:
                    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)