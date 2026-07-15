import os
import json
import time

import requests
from dotenv import load_dotenv


AUTH_URL = "https://openapi.vito.ai/v1/authenticate"
TRANSCRIBE_URL = "https://openapi.vito.ai/v1/transcribe"


def get_access_token():
    load_dotenv()

    client_id = os.getenv("RTZR_CLIENT_ID")
    client_secret = os.getenv("RTZR_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("에러: RTZR_CLIENT_ID 또는 RTZR_CLIENT_SECRET이 설정되지 않았습니다.")
        return None

    response = requests.post(
        AUTH_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    if response.ok:
        token = response.json().get("access_token") or response.json().get("token")
        print("토큰 발급 성공")
        if token:
            print(f"토큰 일부: {token[:10]}...")
        return token

    print(f"토큰 발급 실패: {response.status_code}")
    print(response.text)
    return None


def get_auth_token():
    return get_access_token()


def request_transcription(file_path, access_token):
    if not access_token:
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    config = {
        "model_name": "whisper",
        "language": "detect",
        "language_candidates": ["ko", "en"],
        "use_diarization": True,
        "diarization": {
            "spk_count": 1,
        },
        "use_itn": True,
        "use_disfluency_filter": True,
        "use_profanity_filter": False,
    }

    with open(file_path, "rb") as audio_file:
        response = requests.post(
            TRANSCRIBE_URL,
            headers=headers,
            files={
                "file": audio_file,
                "config": (None, json.dumps(config), "application/json"),
            },
        )

    if response.ok:
        result = response.json()
        return result.get("id") or result.get("transcribe_id")

    print(f"전사 요청 실패: {response.status_code}")
    print(response.text)
    return None


def get_transcription_result(transcribe_id, access_token):
    if not access_token:
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(
        f"{TRANSCRIBE_URL}/{transcribe_id}",
        headers=headers,
    )

    if response.ok:
        return response.json()

    print(f"전사 결과 조회 실패: {response.status_code}")
    print(response.text)
    return None


def wait_for_result(transcribe_id, access_token, interval=5):
    is_processing_printed = False

    while True:
        result = get_transcription_result(transcribe_id, access_token)
        if not result:
            return None

        status = result.get("status")

        if status == "completed":
            return result

        if status == "failed":
            raise RuntimeError(f"전사 실패: {result}")

        if not is_processing_printed:
            print("전사 처리 중...")
            is_processing_printed = True

        time.sleep(interval)


def extract_messages(transcription_result):
    messages = []

    def collect_messages(value):
        if isinstance(value, dict):
            message = value.get("msg")
            if isinstance(message, str) and message.strip():
                messages.append(message.strip())

            for item in value.values():
                collect_messages(item)
        elif isinstance(value, list):
            for item in value:
                collect_messages(item)

    collect_messages(transcription_result)
    return "\n".join(messages)


def save_transcript(text, output_path="outputs/transcript.txt"):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)

    return output_path


def save_json_result(result, output_path="outputs/result.json"):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=2)

    return output_path


if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        transcribe_id = request_transcription("test_audio.m4a", access_token)
        if transcribe_id:
            print(f"transcribe_id: {transcribe_id}")
            transcription_result = wait_for_result(transcribe_id, access_token)
            if transcription_result:
                json_path = save_json_result(transcription_result)
                transcript = extract_messages(transcription_result)
                transcript_path = save_transcript(transcript)
                print("전사 완료")
                print(f"원본 JSON 저장 완료: {json_path}")
                print(f"전사문 저장 완료: {transcript_path}")
