from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime, timezone
import random

router = APIRouter()

@router.websocket("/threat-feed")
async def websocket_threat_feed(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate a live transaction event
            await asyncio.sleep(random.randint(3, 10))
            
            src = f"SBIN{random.randint(1000, 9999)}"
            tgt = f"HDFC{random.randint(1000, 9999)}"
            amt = round(random.uniform(5000, 500000), 2)
            
            event = {
                "event_type": "CRITICAL_FUND_TRANSFER",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "source_account": src,
                    "target_account": tgt,
                    "amount": amt,
                    "risk_trigger": "RAPID_MULE_HOP",
                    "cytoscape_edge": {
                        "data": {
                            "id": f"live_edge_{random.randint(10000, 99999)}",
                            "source": f"BankAccount_{src}",
                            "target": f"BankAccount_{tgt}",
                            "label": "TRANSFERRED_FUNDS",
                            "details": {"amount": amt, "flagged": True}
                        }
                    }
                }
            }
            
            await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
