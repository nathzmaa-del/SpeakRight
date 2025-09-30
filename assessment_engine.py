import azure.cognitiveservices.speech as speechsdk
import json
import os
from dotenv import load_dotenv

load_dotenv() # โหลดค่าจากไฟล์ .env

speech_key = os.environ.get('AZURE_SPEECH_KEY')
service_region = os.environ.get('AZURE_SERVICE_REGION')

def assess_pronunciation(language_code, reference_text, audio_file_path):
    """
    ฟังก์ชันแกนหลักสำหรับประเมินผล รับค่า 3 อย่างและคืนค่าผลลัพธ์เป็น JSON
    """
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
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
            return {"error": f"Canceled: {cancellation_details.reason}", "details": cancellation_details.error_details}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
