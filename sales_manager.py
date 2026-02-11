import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time

# [1] 기본 설정
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

# [2] 스타일(CSS)
st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E1E1E !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important; color: #F1C40F !important; border: 1px solid #555 !important;
    }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold; width: 100%; }
    .stAlert { background-color: #330000 !important; border: 1px solid #FF0000 !important; color: #FFCCCC !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# [3] AI 분석 함수
def analyze_image_final(image, prompt_user):
    try:
        genai.configure(api_key=FIXED_API_KEY)
        # 최신 라이브러리 설치 시 무조건 작동하는 모델
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        규칙: 1. 취소선 항목 제외. 2. 품목명, 규격, 수량, 비고 추출. 3. JSON 리스트로만 응답.
        """
        if prompt_user: system_prompt += f"\n(메모: {prompt_user})"

        with st.spinner("AI 분석 중..."):
            response = model.generate_content([system_prompt, image])
            text = response.text
            start, end = text.find('['), text.rfind(']') + 1
            return eval(text[start:end]) if start != -1 else []
    except Exception as e:
        st.error(f"분석 실패: {e}")
        st.info(f"설치된 버전: {genai.__version__}")
        return []

# [4] 화면 로직 (로그인/사이드바/메인)
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']:
    st.title("🔒 WOORI STEEL 접속")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인") and pw == "0723":
        st.session_state['logged_in'] = True
        st.rerun()
    st.stop()

with st.sidebar:
    st.title("WOORI STEEL")
    st.caption(f"🔧 버전: v{genai.__version__}")
    menu = st.radio("메뉴", ["1. 수주/발주 관리 (AI)", "2. 생산 현황"])
    if st.button("🔄 작업 초기화"):
        for k in list(st.session_state.keys()):
            if k != 'logged_in': del st.session_state[k]
        st.rerun()

if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 판독")
    st.error("🚨 [주의] AI 결과는 반드시 담당자가 2차 검수해야 합니다.")
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("1. 업로드")
        client = st.text_input("거래처명", placeholder="현장명")
        uploaded_file = st.file_uploader("📷 사진 선택", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("비고")
        if st.button("🚀 분석 실행", type="primary") and uploaded_file:
            st.session_state['ai_result'] = analyze_image_final(Image.open(uploaded_file), memo)
            st.session_state['analysis_done'] = True
    with col2:
        st.subheader("2. 결과")
        if st.session_state.get('analysis_done'):
            df = pd.DataFrame(st.session_state['ai_result'])
            for c in ['품목명', '규격', '수량', '단가', '비고']:
                if c not in df.columns: df[c] = ""
            st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.download_button("💾 엑셀 저장", df.to_csv(index=False).encode('utf-8-sig'), "order.csv")
