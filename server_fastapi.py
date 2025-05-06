from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

TELEGRAM_TOKEN = "7747140572:AAECbzwVlIINXQITvB32Vef-_lHx1h_-cbw"  # вставь новый токен
CHAT_ID = 494063094  # оставить как есть

@app.post("/send")
async def send_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(None)
):
    text = f"📬 Новая заявка:\n\n👤 Имя: {name}\n📧 Email: {email}\n📝 Сообщение:\n{message}"

    async with httpx.AsyncClient() as client:
        # Отправка текста
        await client.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text
        })

        # Отправка файла
        if file:
            file_bytes = await file.read()
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID},
                files={"document": (file.filename, file_bytes)}
            )

    return JSONResponse(
        content={"status": "ok"},
        status_code=200,
        media_type="application/json"
    )
