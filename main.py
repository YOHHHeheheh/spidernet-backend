import sys
import traceback

try:
    from app.main import app
except Exception as e:
    err_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print("FATAL STARTUP ERROR:", err_msg)
    
    # Fallback ASGI app to show the error on the screen
    async def app(scope, receive, send):
        assert scope['type'] == 'http'
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [
                (b'content-type', b'text/plain'),
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': err_msg.encode('utf-8'),
        })
