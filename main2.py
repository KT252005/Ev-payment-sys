from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import qrcode
import os
import time  # To simulate waiting for payment confirmation
import random  # To simulate payment success or failure
import uvicorn

# UPI ID and fixed payment amount
upi_id = "9724696358q-2@oksbi"
FIXED_AMOUNT = 1.00  # Set a fixed amount for the payment (in INR)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_temp_dir():
    """Get the appropriate temp directory based on the environment."""
    if os.getenv("AWS_EXECUTION_ENV") or os.getenv("VERCEL_ENV"):  # Check for AWS Lambda or Vercel
        return "/tmp"  # Use /tmp for AWS Lambda and Vercel
    else:
        return os.getcwd()  # Use current working directory locally

def generate_upi_qr(upi_id, name: str):
    """Generate a UPI QR code and save it to a temp directory."""
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

    # Save the image to the temp directory
    tmp_file_path = os.path.join(get_temp_dir(), "upi_qr.png")
    img.save(tmp_file_path)

    return tmp_file_path  # Return the path to the saved QR code

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    """Render the HTML form for UPI payment."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_qr", response_class=HTMLResponse)
async def generate_qr(request: Request, name: str = Form(...)):
    """Generate QR code for UPI payment and simulate payment confirmation."""
    qr_file_path = generate_upi_qr(upi_id, name)  # Generate QR code and get the path

    # Simulate waiting for the payment confirmation
    time.sleep(5)  # Simulates time taken for payment (e.g., waiting for 5 seconds)

    # Simulate payment status
    payment_success = random.choice([True, False])  # Simulating payment success/failure randomly
    payment_status = "success" if payment_success else "failed"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "qr_code": "/static/upi_qr.png",
            "payment_status": payment_status,
        }
    )

@app.get("/static/upi_qr.png")
def get_qr_code():
    """Serve the generated QR code."""
    file_path = os.path.join(get_temp_dir(), "upi_qr.png")  # Check the temp directory for the QR code
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "QR code not found!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 4000))  
    uvicorn.run(app, host="0.0.0.0", port=port)
