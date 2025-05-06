
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

TELEGRAM_TOKEN = "7747140572:AAFa_2UhUYJ8R44XdHN9F5UkWhyPF59gkxY"
CHAT_ID = None  # можно заменить на свой ID, иначе бот возьмёт из первого сообщения

@app.post("/send")
async def send_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(None)
):
    text = f"📥 Новая заявка:

👤 Имя: {name}
📧 Email: {email}
📝 Сообщение:
{message}"
    async with httpx.AsyncClient() as client:
        # Отправка текстового сообщения
        await client.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID or "",
            "text": text
        })

        # Отправка файла, если есть
        if file:
            file_bytes = await file.read()
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID or ""},
                files={"document": (file.filename, file_bytes)}
            )

    return JSONResponse(content={"status": "ok"})
