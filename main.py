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
