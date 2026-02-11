import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time
from datetime import datetime # 시간 도구 추가

# [1] 필수 설정
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

# [2] 스타일 설정
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        규칙: 
        1. 취소선(가로줄) 항목은 절대 추출하지 마십시오. 
        2. 품목명, 규격, 수량, 비고를 추출하십시오. 
        3. 결과는 반드시 JSON 리스트로만 응답하십시오.
        """
        if prompt_user: system_prompt += f"\n(참고 메모: {prompt_user})"

        with st.spinner("AI가 주문서를 판독하고 있습니다..."):
            response = model.generate_content([system_prompt, image])
            text_res = response.text
            start = text_res.find('[')
            end = text_res.rfind(']') + 1
            if start != -1 and end != -1:
                return eval(text_res[start:end])
            return []
    except Exception as e:
        st.error(f"분석 오류 발생: {e}")
        return []

# [4] 화면 로직
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
    st.caption(f"🔧 AI 도구 버전: v{genai.__version__}")
    menu = st.radio("메뉴", ["1. 수주/발주 관리 (AI)", "2. 생산 현황"])
    if st.button("🔄 작업 초기화"):
        for k in list(st.session_state.keys()):
            if k != 'logged_in': del st.session_state[k]
        st.rerun()

if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 판독 시스템")
    # 대표님이 강조하신 경고 문구
    st.error("🚨 [필독] AI는 업무 보조 도구입니다. 인식 결과에 오류가 있을 수 있으므로, 담당자는 반드시 '2차 검수'를 진행하셔야 합니다.")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("1. 주문서 업로드")
        client = st.text_input("거래처/현장명")
        uploaded_file = st.file_uploader("📷 사진 선택", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("추가 요청 사항")
        if st.button("🚀 분석 실행", type="primary") and uploaded_file:
            st.session_state['ai_result'] = analyze_image_final(Image.open(uploaded_file), memo)
            st.session_state['analysis_done'] = True
            
    with col2:
        st.subheader("2. 검수 및 다운로드")
        if st.session_state.get('analysis_done'):
            df = pd.DataFrame(st.session_state['ai_result'])
            for col in ['품목명', '규격', '수량', '단가', '비고']:
                if col not in df.columns: df[col] = ""
            
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            # 에러가 났던 저장 버튼 부분 (이제 정상 작동함)
            st.download_button(
                "💾 엑셀(CSV) 저장", 
                edited_df.to_csv(index=False).encode('utf-8-sig'), 
                f"order_{datetime.now().strftime('%m%d')}.csv"
            )
        else:
            st.info("왼쪽에서 사진을 업로드하고 분석을 시작하세요.")
else:
    st.info("준비 중입니다.")
