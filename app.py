from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()

import base64
import os
import io
from pydub import AudioSegment
from assessment_engine import assess_pronunciation

# --- ส่วนที่เพิ่มเข้ามาเพื่อแก้ปัญหา ---
# บังคับให้ Pydub รู้จักที่อยู่ของ FFmpeg ที่ติดตั้งบนเซิร์ฟเวอร์ Render
AudioSegment.converter = "/usr/bin/ffmpeg"
# ------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assess', methods=['POST'])
def assess():
    data = request.get_json()
    
    language = data['language']
    reference_text = data['word']
    audio_base64 = data['audioBase64']

    audio_data = base64.b64decode(audio_base64)
    temp_audio_path = "temp_audio.wav"

    try:
        audio_stream = io.BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(audio_stream)
        
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_sample_width(2)
        
        audio_segment.export(temp_audio_path, format="wav")

    except Exception as e:
        print(f"Error processing audio file: {e}")
        return jsonify({"error": "ไม่สามารถประมวลผลไฟล์เสียงที่ได้รับมา"}), 400

    result = assess_pronunciation(language, reference_text, temp_audio_path)
    os.remove(temp_audio_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

