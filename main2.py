from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import qrcode
import os
import time  # To simulate waiting for payment confirmation
import random  # To simulate payment success or failure

upi_id="9724696358q-2@oksbi"
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Predefined payment amount
FIXED_AMOUNT = 1.00  # Set a fixed amount for the payment (in INR)

# Generate QR code based on UPI ID, name, and a fixed amount
def generate_upi_qr(upi_id, name: str):
    upi_string = f"upi://pay?pa={upi_id}&pn={name}&am={FIXED_AMOUNT}&cu=INR"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save("static/upi_qr.png")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_qr", response_class=HTMLResponse)
async def generate_qr(request: Request, name: str = Form(...)):
    generate_upi_qr(upi_id, name)
    
    # Simulate waiting for the payment confirmation (replace this with real UPI API call)
    time.sleep(5)  # Simulates time taken for payment to be made (e.g., waiting for 5 seconds)

    # Simulate payment status (replace this logic with actual payment gateway integration)
    # payment_success = random.choice([True, False])  # Simulating payment success/failure randomly

    # Return success or failure based on payment confirmation
    # payment_status = "success" if payment_success else "failed"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "qr_code": "/static/upi_qr.png",
            # "payment_status": payment_status,
        }
    )


@app.get("/static/upi_qr.png")
def get_qr_code():
    file_path = "static/upi_qr.png"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "QR code not found!"}
