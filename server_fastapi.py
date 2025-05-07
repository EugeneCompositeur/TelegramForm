from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import csv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_TOKEN = "YOUR_ACTUAL_TOKEN_HERE"
CHAT_ID = 494063094
SPREADSHEET_ID = "1w7u3_x_8mV3qB8J1_0zBGCV90DxmXOL652WIxx0ylz8"

def write_to_gsheets(name, email, message, filename):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("theorders-fac8c8cbb228.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([now, name, email, message, filename])

def write_to_csv(name, email, message, filename):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [now, name, email, message, filename]
    file_exists = os.path.isfile("leads.csv")
    with open("leads.csv", "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Дата", "Имя", "Email", "Сообщение", "Файл"])
        writer.writerow(row)

@app.post("/send")
async def send_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(None)
):
    filename = file.filename if file else "—"
    text = f"📬 Новая заявка:\n\n👤 Имя: {name}\n📧 Email: {email}\n📝 Сообщение:\n{message}"

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )

        if file:
            file_bytes = await file.read()
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID},
                files={"document": (file.filename, file_bytes)}
            )

    write_to_gsheets(name, email, message, filename)
    write_to_csv(name, email, message, filename)

    return JSONResponse(
        content={"status": "ok"},
        status_code=200,
        media_type="application/json"
    )
