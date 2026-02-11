import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time
from datetime import datetime

# ==========================================
# [1] API 키 설정 (가장 확실한 방식)
# ==========================================
# 대표님의 API 키를 시스템에 직접 등록합니다.
MY_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"
genai.configure(api_key=MY_API_KEY)

# ==========================================
# [2] 기본 설정 및 디자인
# ==========================================
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

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

# ==========================================
# [3] AI 분석 함수
# ==========================================
def analyze_image_final(image, prompt_user):
    try:
        # 모델 설정 (최신 Flash 모델)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        규칙: 
        1. 취소선(가로줄) 항목은 절대 추출하지 마십시오. 
        2. 품목명, 규격, 수량, 비고를 추출하십시오. 
        3. 결과는 반드시 JSON 리스트로만 응답하십시오.
        """
        if prompt_user: 
            system_prompt += f"\n(참고 메모: {prompt_user})"

        with st.spinner("AI가 주문서를 판독하고 있습니다..."):
            # 이미지와 프롬프트 전송
            response = model.generate_content([system_prompt, image])
            
            # 응답 텍스트 추출
            text_res = response.text
            start = text_res.find('[')
            end = text_res.rfind(']') + 1
            
            if start != -1 and end != -1:
                return eval(text_res[start:end])
            return []
            
    except Exception as e:
        st.error(f"분석 중 오류 발생: {e}")
        return []

# ==========================================
# [4] 화면 로직
# ==========================================

# 로그인 체크
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 WOORI STEEL 접속")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if pw == "0723":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# 사이드바
with st.sidebar:
    st.title("WOORI STEEL")
    st.caption(f"🔧 AI 버전: v{genai.__version__}")
    menu = st.radio("메뉴", ["1. 수주/발주 관리 (AI)", "2. 생산 현황"])
    st.markdown("---")
    if st.button("🔄 작업 초기화"):
        for k in list(st.session_state.keys()):
            if k != 'logged_in': del st.session_state[k]
        st.rerun()

# 메인 기능
if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 판독 시스템")
    
    # 대표님 요청 경고 문구
    st.error("🚨 [필독] AI는 업무 보조 도구입니다. 인식 결과에 오류가 있을 수 있으므로, 담당자는 반드시 '2차 검수'를 진행하셔야 합니다.")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("1. 주문서 업로드")
        client = st.text_input("거래처/현장명")
        uploaded_file = st.file_uploader("📷 사진 선택 (JPG, PNG)", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("추가 요청 사항 (예: 취소선 제외해줘)")
        
        if st.button("🚀 분석 실행", type="primary"):
            if uploaded_file:
                img = Image.open(uploaded_file)
                result = analyze_image_final(img, memo)
                if result:
                    st.session_state['ai_result'] = result
                    st.session_state['analysis_done'] = True
            else:
                st.warning("사진을 먼저 올려주세요.")

    with col2:
        st.subheader("2. 검수 및 다운로드")
        if st.session_state.get('analysis_done'):
            df = pd.DataFrame(st.session_state['ai_result'])
            # 필요한 컬럼이 없을 경우 대비
            for c in ['품목명', '규격', '수량', '단가', '비고']:
                if c not in df.columns: df[c] = ""
            
            # 편집 가능한 표
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            
            # 엑셀 다운로드 버튼
            file_name = f"order_{datetime.now().strftime('%m%d_%H%M')}.csv"
            st.download_button(
                label="💾 엑셀(CSV) 저장",
                data=edited_df.to_csv(index=False).encode('utf-8-sig'),
                file_name=file_name,
                mime='text/csv'
            )
        else:
            st.info("왼쪽에서 분석을 시작하면 여기에 결과가 나타납니다.")
else:
    st.info("생산 현황 메뉴는 준비 중입니다.")
