from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import io
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import zxingcpp

app = FastAPI(title="EasyOCR & Robust QR/Barcode API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("EasyOCR Model Loading... Please wait.")
reader = easyocr.Reader(['en', 'bn'], gpu=False)
print("EasyOCR Model Loaded Successfully!")

# OpenCV QR Detector setup
opencv_qr_detector = cv2.QRCodeDetector()

@app.get("/")
def home():
    return {"message": "OCR API Server is Running!"}


# ==========================================
# আপনার আগের অবিকল আসল কোড (একটুও চেঞ্জ করা হয়নি)
# ==========================================
@app.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    try:
       
        image_bytes = await file.read()
        
      
        results = reader.readtext(image_bytes)
        
        # ৩. শুধু টেক্সটগুলো বের করে অ্যারেই (List)-এ নেওয়া
        extracted_texts = []
        for result in results:
            extracted_texts.append(result[1]) # result[1]-এ মূল স্ক্যান হওয়া টেক্সট থাকে
            
        # ৪. ডাটাবেজে না রেখে সরাসরি JSON রিটার্ন করবে
        return {
            "success": True,
            "filename": file.filename,
            "scanned_data": extracted_texts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Universal / Super Robust QR Code Scanner
# ==========================================
def extract_qr_from_pil(img: Image.Image) -> list:
    """বিভিন্ন ইমেজ ফিল্টার ব্যবহার করে zxingcpp দিয়ে চেষ্টা করবে"""
    found_texts = set()
    
    # টেস্ট ভার্সন ১: অরিজিনাল ছবি
    results = zxingcpp.read_barcodes(img)
    for r in results:
        if r.text:
            found_texts.add(r.text)
            
    if found_texts:
        return list(found_texts)

    # টেস্ট ভার্সন ২: চারপাশে বর্ডার (Quiet Zone) দেওয়া
    w, h = img.size
    padded_img = Image.new(img.mode, (w + 60, h + 60), (255, 255, 255))
    padded_img.paste(img, (30, 30))
    results = zxingcpp.read_barcodes(padded_img)
    for r in results:
        if r.text:
            found_texts.add(r.text)

    if found_texts:
        return list(found_texts)

    # টেস্ট ভার্সন ৩: গ্রে-স্কেল ও হাই-কনট্রাস্ট (ইনভার্টেড/ঝাপসা ছবির জন্য)
    gray_img = ImageOps.grayscale(padded_img)
    enhancer = ImageEnhance.Contrast(gray_img)
    high_contrast_img = enhancer.enhance(2.0)
    
    results = zxingcpp.read_barcodes(high_contrast_img)
    for r in results:
        if r.text:
            found_texts.add(r.text)

    return list(found_texts)


@app.post("/scan/qr")
async def scan_qr(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # ১. zxing-cpp দিয়ে মাল্টি-লেয়ার ফিল্টারিং করে স্ক্যান
        qr_results = extract_qr_from_pil(pil_image)

        # ২. ব্যাকআপ ইঞ্জিন: OpenCV QR Detector (যদি ১ কাজ না করে)
        if not qr_results:
            nparr = np.frombuffer(image_bytes, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Multi-QR Detection
            retval, decoded_info, _, _ = opencv_qr_detector.detectAndDecodeMulti(cv_img)
            if retval:
                for info in decoded_info:
                    if info:
                        qr_results.append(info)
            else:
                # Single QR Fallback
                data, _, _ = opencv_qr_detector.detectAndDecode(cv_img)
                if data:
                    qr_results.append(data)

        # ডুপ্লিকেট রিমুভ করা
        unique_qr_data = list(set(qr_results))

        return {
            "success": True,
            "filename": file.filename,
            "qr_data": unique_qr_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# ২. Barcode (ওষুধ/পণ্য) স্ক্যান করার এপিআই
# ==========================================
@app.post("/scan/barcode")
async def scan_barcode(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        results = zxingcpp.read_barcodes(image)

        barcode_data = []
        for result in results:
            if result.text and "QRCode" not in str(result.format):
                barcode_data.append({
                    "code_type": str(result.format),
                    "code_number": result.text
                })

        return {
            "success": True,
            "filename": file.filename,
            "barcode_data": barcode_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))