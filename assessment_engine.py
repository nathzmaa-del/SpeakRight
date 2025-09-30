import azure.cognitiveservices.speech as speechsdk
import json
import os
from dotenv import load_dotenv

load_dotenv() # โหลดค่าจากไฟล์ .env

# --- อ่านค่าการเชื่อมต่อทั้งหมด ---
speech_key = os.environ.get('AZURE_SPEECH_KEY')
service_region = os.environ.get('AZURE_SERVICE_REGION')
endpoint = os.environ.get('AZURE_SPEECH_ENDPOINT') # <-- ตัวแปรใหม่

def assess_pronunciation(language_code, reference_text, audio_file_path):
    """ฟังก์ชันหลักสำหรับประเมินผล"""
    if not speech_key or (not service_region and not endpoint):
        return {"error": "Azure Speech credentials are not fully configured."}
    
    try:
        # --- อัปเกรด Logic การเชื่อมต่อ ---
        if endpoint:
            # ใช้วิธีเชื่อมต่อผ่าน Endpoint โดยตรง (เสถียรกว่า)
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=endpoint)
        else:
            # ใช้วิธีเชื่อมต่อผ่าน Region (วิธีเดิม)
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        # --- สิ้นสุดส่วนอัปเกรด ---

        speech_config.speech_recognition_language = language_code

        audio_config = speechsdk.AudioConfig(filename=audio_file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=True
        )
        pronunciation_config.apply_to(speech_recognizer)

        result = speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            pronunciation_result_json = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
            return json.loads(pronunciation_result_json)
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {"error": "No speech could be recognized."}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            # ให้ข้อมูล Error ที่ละเอียดขึ้น
            return {"error": f"Canceled: {cancellation_details.reason}", "details": f"ErrorCode={cancellation_details.error_code}, ErrorDetails={cancellation_details.error_details}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

