# Send with FastAPI

Send email from a FastAPI endpoint with the uSend SDK, off the event loop.

Part of [usend examples](https://github.com/usend/usend-examples). Step-by-step guide: https://usend.et/docs/quickstarts/fastapi

You need a [verified domain](https://usend.et/docs/domains/verify) and an [API key](https://usend.et/docs/api-keys). The Python SDK is synchronous, so call it from a plain `def` endpoint or hand it to a background task, so it never blocks the event loop.

## 1. Install

```bash
pip install fastapi uvicorn usend
```

## 2. The app

`main.py`

```python
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from usend import Usend, UsendError

app = FastAPI()
usend = Usend()  # reads USEND_API_KEY

class Welcome(BaseModel):
    email: EmailStr

def send_welcome(email: str) -> None:
    usend.emails.send(
        {
            "from": "Acme <hello@acme.com>",
            "to": [email],
            "subject": "Welcome to Acme",
            "html": "<p>Thanks for signing up.</p>",
        },
        idempotency_key=f"welcome-{email}",
    )

@app.post("/send")
def send(body: Welcome):
    # A plain `def` runs in FastAPI's thread pool, so the blocking call is fine.
    try:
        result = usend.emails.send(
            {
                "from": "Acme <hello@acme.com>",
                "to": [body.email],
                "subject": "Welcome to Acme",
                "html": "<p>Thanks for signing up.</p>",
            }
        )
    except UsendError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"id": result["id"]}

@app.post("/signup")
def signup(body: Welcome, background: BackgroundTasks):
    background.add_task(send_welcome, body.email)  # reply first, send after
    return {"ok": True}
```

(`EmailStr` needs `pip install email-validator`, or use `str`.)

## 3. Run and test

```bash
export USEND_API_KEY="us_123456789"
uvicorn main:app --reload
curl -X POST localhost:8000/send -H 'Content-Type: application/json' -d '{"email":"you@example.com"}'
```

## Notes

- In background tasks, catch `UsendError` yourself: nobody sees the exception otherwise.
- The idempotency key makes a retried task safe. See [Idempotency](https://usend.et/docs/sending/idempotency).

Next: [Send emails](https://usend.et/docs/sending/emails).

## Environment

Create an [API key](https://usend.et/docs/api-keys) and a [verified domain](https://usend.et/docs/domains/verify), then set `USEND_API_KEY` (starts with `us_`); copy any `.env*.example` file to its real name first. Never put the key in browser code.

## License

MIT
