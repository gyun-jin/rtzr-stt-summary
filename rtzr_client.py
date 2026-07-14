import os

import requests
from dotenv import load_dotenv


AUTH_URL = "https://openapi.vito.ai/v1/authenticate"


def get_auth_token():
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


if __name__ == "__main__":
    get_auth_token()
