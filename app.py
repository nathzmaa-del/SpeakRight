from flask import Flask, render_template, request, jsonify
import base64
import os
import wave # <-- เพิ่ม Library สำหรับจัดการไฟล์ WAV
from assessment_engine import assess_pronunciation
from dotenv import load_dotenv # <-- ตรวจสอบว่ามีบรรทัดนี้
load_dotenv() # <-- และบรรทัดนี้

app = Flask(__name__)

@app.route('/')
def index():
    """แสดงหน้าเว็บหลัก (index.html)"""
    return render_template('index.html')

@app.route('/assess', methods=['POST'])
def assess():
    """API Endpoint สำหรับรับเสียงและประเมินผล"""
    data = request.get_json()
    
    # 1. รับข้อมูลจาก Front-End
    language = data['language']
    reference_text = data['word']
    audio_base64 = data['audioBase64']

    # 2. แปลงข้อมูลเสียง Base64 กลับเป็นข้อมูลเสียงดิบ
    audio_data = base64.b64decode(audio_base64)
    temp_audio_path = "temp_audio.wav"

    # --- ส่วนที่อัปเดต: เขียนไฟล์ WAV พร้อม Header ที่ถูกต้อง ---
    # ตั้งค่ามาตรฐานสำหรับเสียงคุณภาพสูงที่ Azure ต้องการ
    # (Mono, 16-bit, 16kHz sample rate)
    n_channels = 1
    samp_width = 2
    frame_rate = 16000

    with wave.open(temp_audio_path, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(samp_width)
        wf.setframerate(frame_rate)
        wf.writeframes(audio_data)
    # --- สิ้นสุดส่วนที่อัปเดต ---

    # 3. เรียกใช้งานเครื่องยนต์ AI (ส่วนนี้เหมือนเดิม)
    result = assess_pronunciation(language, reference_text, temp_audio_path)

    # 4. ลบไฟล์เสียงชั่วคราว
    os.remove(temp_audio_path)

    # 5. ส่งผลลัพธ์กลับไปให้ Front-End
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)