# RTZR STT 강의/회의 요약 도구

## 프로젝트 소개

오디오 파일을 업로드하면 RTZR STT API로 전사하고, 전사문 기반 요약과 핵심 키워드를 생성하는 Streamlit 웹 데모입니다.

이 프로젝트는 RTZR STT API를 실제 호출해서 오디오 파일 전사 요청, 결과 조회, 전사문 저장, 요약 파일 생성을 수행합니다. 핵심은 RTZR STT API 호출과 결과 후처리 흐름을 재현 가능하게 보여주는 것입니다.

## 주요 기능

- 오디오 파일 업로드
- RTZR STT API 인증 토큰 발급
- RTZR STT API 파일 전사 요청
- 원본 전사 결과 JSON 저장
- `msg` 값만 추출한 전사문 저장
- 전사문 기반 요약 및 핵심 키워드 생성
- 전사문, 요약 결과, 원본 JSON 다운로드
- 영어/한국어 오디오 자동 감지 전사 설정

지원 파일 형식:

- `m4a`
- `mp3`
- `wav`
- `flac`
- `mp4`

## 기술 스택

- Python
- Streamlit
- requests
- python-dotenv
- RTZR STT API

## 실행 환경

- Python 3.9 이상 권장
- RTZR Developers 계정 필요
- `RTZR_CLIENT_ID`, `RTZR_CLIENT_SECRET` 필요

## 프로젝트 구조

```text
.
├── app.py
├── rtzr_client.py
├── summarizer.py
├── requirements.txt
├── .env.example
├── .gitignore
└── outputs/
```

- `app.py`: Streamlit 웹앱 화면과 실행 흐름을 연결합니다.
- `rtzr_client.py`: RTZR API 인증, 전사 요청, 결과 조회, 결과 저장을 담당합니다.
- `summarizer.py`: 전사문을 읽고 규칙 기반으로 요약과 핵심 키워드를 생성합니다.
- `requirements.txt`: 실행에 필요한 Python 패키지 목록입니다.
- `.env.example`: 필요한 환경변수 예시 파일입니다.
- `.gitignore`: `.env`, `outputs/` 등 GitHub에 올리지 않을 파일을 제외합니다.
- `outputs/`: 실행 시 생성되는 결과 파일 저장 폴더입니다. GitHub에는 커밋하지 않습니다.

## 사용한 RTZR API

인증 API:

- `POST https://openapi.vito.ai/v1/authenticate`
- `RTZR_CLIENT_ID`와 `RTZR_CLIENT_SECRET`을 사용해 access token을 발급받습니다.

파일 전사 요청 API:

- `POST https://openapi.vito.ai/v1/transcribe`
- `Authorization: Bearer {access_token}` 헤더를 넣고, 오디오 파일과 `config`를 `multipart/form-data`로 전송합니다.

전사 결과 조회 API:

- `GET https://openapi.vito.ai/v1/transcribe/{transcribe_id}`
- 전사 요청 후 발급받은 `transcribe_id`로 전사 완료 여부와 결과를 조회합니다.

본 프로젝트는 영어/한국어 오디오 처리를 위해 전사 요청 `config`에 언어 자동 감지 설정을 사용합니다. 실제 API 키는 코드에 직접 작성하지 않고 `.env`에서 불러옵니다.

## RTZR API 처리 흐름

1. `.env`에서 `RTZR_CLIENT_ID`, `RTZR_CLIENT_SECRET` 로드
2. `POST /v1/authenticate`로 access token 발급
3. `POST /v1/transcribe`로 오디오 파일 전사 요청
4. 응답으로 받은 `transcribe_id` 저장
5. `GET /v1/transcribe/{transcribe_id}`로 전사 결과 조회
6. 원본 JSON을 `outputs/result.json`에 저장
7. `result.json`에서 `msg` 값만 추출해 `outputs/transcript.txt`에 저장
8. `transcript.txt`를 기반으로 요약 및 핵심 키워드를 생성해 `outputs/summary.txt`에 저장

## 환경변수 설정

`.env.example` 파일을 복사해서 `.env` 파일을 만듭니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 본인의 RTZR Developers 콘솔에서 발급받은 값을 입력합니다.

```env
RTZR_CLIENT_ID=your_client_id_here
RTZR_CLIENT_SECRET=your_client_secret_here
```

주의:

- 실제 `.env` 파일은 GitHub에 커밋하지 않습니다.
- API 키와 시크릿은 코드에 직접 작성하지 않습니다.
- 실제 `CLIENT_ID`나 `CLIENT_SECRET` 값은 README에 작성하지 않습니다.

## 설치 방법

```bash
git clone <repository-url>
cd <repository-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows 사용자는 필요하면 아래 명령어로 가상환경을 활성화합니다.

```bash
venv\Scripts\activate
```

## 실행 방법

```bash
streamlit run app.py
```

실행 후 예상 흐름:

- 브라우저에서 Streamlit 화면이 열립니다.
- 오디오 파일을 업로드합니다.
- **전사 및 요약 실행** 버튼을 클릭합니다.
- 전사 결과와 요약 결과를 확인합니다.
- 필요한 결과 파일을 다운로드합니다.

## 사용 방법

1. RTZR Developers에서 `CLIENT_ID`와 `CLIENT_SECRET`을 발급받습니다.
2. `.env.example`을 복사해 `.env` 파일을 작성합니다.
3. 패키지를 설치합니다.
4. `streamlit run app.py`를 실행합니다.
5. 오디오 파일을 업로드합니다.
6. **전사 및 요약 실행** 버튼을 누릅니다.
7. 전사 결과, 요약 결과를 확인하고 필요한 파일을 다운로드합니다.

## 결과 파일

- `outputs/result.json`: RTZR STT API에서 반환한 원본 JSON
- `outputs/transcript.txt`: 원본 JSON에서 `msg` 값만 추출한 전사문
- `outputs/summary.txt`: 전사문 기반 규칙 기반 요약과 핵심 키워드

## 요약 기능 설명

요약 기능은 외부 LLM API를 사용하지 않습니다.

전사문에서 핵심 키워드와 중요 문장을 추출하는 규칙 기반 요약 방식입니다. STT 결과에 오인식이 포함되면 요약 결과에도 일부 부정확한 표현이 반영될 수 있습니다.

이 프로젝트의 핵심은 RTZR STT API 호출과 전사 결과 후처리 흐름을 보여주는 것입니다.

## 보안 및 주의사항

- `.env` 파일은 절대 커밋하지 않습니다.
- `outputs/` 폴더는 실행 결과물이므로 커밋하지 않습니다.
- 테스트 오디오는 직접 녹음했거나 사용 권한이 있는 파일만 사용합니다.
- 실제 `RTZR_CLIENT_ID` 값과 `RTZR_CLIENT_SECRET` 값은 README에 작성하지 않습니다.
- `RTZR_CLIENT_SECRET`은 외부에 공개하지 않습니다.

## 문제 해결

- `ModuleNotFoundError`가 발생하면 `pip install -r requirements.txt`를 실행합니다.
- 인증 오류가 발생하면 `.env`의 `RTZR_CLIENT_ID`, `RTZR_CLIENT_SECRET` 값을 확인합니다.
- 전사 결과가 비어 있으면 지원 파일 형식과 오디오 길이를 확인합니다.
- Streamlit이 실행되지 않으면 가상환경 활성화 여부를 확인합니다.
- API 사용량이 부족하면 RTZR Developers 콘솔의 사용량을 확인합니다.

## 참고 문서

- RTZR Developers: https://developers.rtzr.ai/
- RTZR Docs: https://developers.rtzr.ai/docs/

## AI 코딩 에이전트 활용

Codex를 사용해 API 호출 흐름 구현, 오류 수정, Streamlit 화면 구성, README 구조화에 활용했습니다.

API 키 관리, 실제 실행, 결과 검증, 최종 커밋 관리는 직접 수행했습니다.
