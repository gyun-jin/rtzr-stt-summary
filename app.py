import os

import streamlit as st

from rtzr_client import (
    extract_messages,
    get_access_token,
    request_transcription,
    save_json_result,
    save_transcript,
    wait_for_result,
)
from summarizer import extract_keywords, read_transcript, save_summary, summarize_text


OUTPUT_DIR = "outputs"
RESULT_JSON_PATH = "outputs/result.json"
TRANSCRIPT_PATH = "outputs/transcript.txt"
SUMMARY_PATH = "outputs/summary.txt"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_uploaded_audio(uploaded_file):
    ensure_output_dir()
    extension = os.path.splitext(uploaded_file.name)[1].lower()
    output_path = os.path.join(OUTPUT_DIR, f"uploaded_audio{extension}")

    with open(output_path, "wb") as output_file:
        output_file.write(uploaded_file.getbuffer())

    return output_path


def read_file(path, mode="r"):
    if "b" in mode:
        with open(path, mode) as input_file:
            return input_file.read()

    with open(path, mode, encoding="utf-8") as input_file:
        return input_file.read()


def show_download_button(label, path, mime):
    if not os.path.exists(path):
        st.info(f"{path} 파일이 아직 생성되지 않았습니다.")
        return

    data = read_file(path, "rb")
    st.download_button(
        label=label,
        data=data,
        file_name=os.path.basename(path),
        mime=mime,
    )


st.set_page_config(page_title="RTZR STT 강의/회의 요약 도구", layout="wide")

st.title("RTZR STT 강의/회의 요약 도구")
st.write(
    "오디오 파일을 업로드하면 RTZR STT API로 전사하고, 전사문 기반 요약과 핵심 키워드를 생성합니다."
)

uploaded_file = st.file_uploader(
    "오디오 파일 업로드",
    type=["m4a", "mp3", "wav", "flac", "mp4"],
)

uploaded_audio_path = None
if uploaded_file:
    try:
        uploaded_audio_path = save_uploaded_audio(uploaded_file)
        st.success("오디오 파일이 저장되었습니다.")
        st.write(f"업로드된 파일명: `{uploaded_file.name}`")
    except Exception as error:
        st.error(f"업로드 파일 저장 중 오류가 발생했습니다: {error}")


if st.button("전사 및 요약 실행"):
    if not uploaded_audio_path:
        st.warning("먼저 오디오 파일을 업로드해 주세요.")
    else:
        try:
            # RTZR API 실행 결과는 README에서 재현 가능한 고정 경로에 저장한다.
            with st.spinner("RTZR STT API로 전사 중입니다. 파일 길이에 따라 시간이 걸릴 수 있습니다."):
                access_token = get_access_token()
                if not access_token:
                    st.error(".env의 RTZR_CLIENT_ID 또는 RTZR_CLIENT_SECRET을 확인해 주세요.")
                    st.stop()

                transcribe_id = request_transcription(uploaded_audio_path, access_token)
                if not transcribe_id:
                    st.error("RTZR STT API 전사 요청에 실패했습니다.")
                    st.stop()

                transcription_result = wait_for_result(transcribe_id, access_token)
                if not transcription_result:
                    st.error("전사 결과 조회에 실패했습니다.")
                    st.stop()

                save_json_result(transcription_result, RESULT_JSON_PATH)
                transcript_text = extract_messages(transcription_result)
                save_transcript(transcript_text, TRANSCRIPT_PATH)

            with st.spinner("전사문 기반 요약을 생성 중입니다."):
                transcript = read_transcript(TRANSCRIPT_PATH)
                summary = summarize_text(transcript)
                keywords = extract_keywords(transcript)
                save_summary(summary, keywords, SUMMARY_PATH)

            st.success("전사 및 요약이 완료되었습니다.")
        except Exception as error:
            st.error(f"처리 중 오류가 발생했습니다: {error}")


st.subheader("결과")

with st.expander("전사 결과", expanded=False):
    if os.path.exists(TRANSCRIPT_PATH):
        transcript_text = read_file(TRANSCRIPT_PATH)
        st.text_area("outputs/transcript.txt", transcript_text, height=300)
    else:
        st.info("전사문 파일이 아직 생성되지 않았습니다. 전사 및 요약 실행 후 확인해 주세요.")

with st.expander("요약 결과", expanded=True):
    if os.path.exists(SUMMARY_PATH):
        summary_text = read_file(SUMMARY_PATH)
        st.text_area("outputs/summary.txt", summary_text, height=260)
    else:
        st.info("요약 파일이 아직 생성되지 않았습니다. 전사 및 요약 실행 후 확인해 주세요.")

st.subheader("다운로드")
col1, col2, col3 = st.columns(3)

with col1:
    show_download_button("전사문 다운로드 (.txt)", TRANSCRIPT_PATH, "text/plain")

with col2:
    show_download_button("요약 결과 다운로드 (.txt)", SUMMARY_PATH, "text/plain")

with col3:
    show_download_button("원본 JSON 다운로드 (.json)", RESULT_JSON_PATH, "application/json")
