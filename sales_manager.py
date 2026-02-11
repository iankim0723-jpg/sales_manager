import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time

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

# [3] AI 분석 함수 (최신 호출 규격 적용)
def analyze_image_final(image, prompt_user):
    try:
        # API 설정
        genai.configure(api_key=FIXED_API_KEY)
        
        # 최신 모델 생성 방식 (모델 이름을 리스트가 아닌 단일 문자열로 전달)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        규칙: 
        1. 취소선(가로줄) 항목은 절대 추출하지 마십시오. 
        2. 품목명, 규격, 수량, 비고를 추출하십시오. 
        3. 결과는 반드시 JSON 리스트로만 응답하십시오. (예: [{"품목명": "EPS", "규격": 3000, "수량": 10, "비고": ""}])
        """
        if prompt_user: 
            system_prompt += f"\n(참고 메모: {prompt_user})"

        with st.spinner("AI가 주문서를 판독하고 있습니다..."):
            # 이미지 데이터와 프롬프트를 함께 전송
            response = model.generate_content([system_prompt, image])
            
            # 응답 텍스트 추출 및 정제
            text_res = response.text
            start = text_res.find('[')
            end = text_res.rfind(']') + 1
            
            if start != -1 and end != -1:
                return eval(text_res[start:end])
            else:
                st.warning("데이터 추출 실패: 사진이 흐리거나 양식이 다를 수 있습니다.")
                return []
                
    except Exception as e:
        st.error(f"분석 오류 발생: {e}")
        st.info(f"현재 시스템 라이브러리 버전: {genai.__version__}")
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
    st.error("🚨 [주의] AI 결과는 보조용입니다. 담당자는 반드시 직접 2차 검수하셔야 합니다.")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("1. 주문서 업로드")
        client = st.text_input("거래처/현장명")
        uploaded_file = st.file_uploader("📷 사진 선택 (최대 10장 지원 예정)", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("추가 요청 사항")
        if st.button("🚀 분석 실행", type="primary") and uploaded_file:
            st.session_state['ai_result'] = analyze_image_final(Image.open(uploaded_file), memo)
            st.session_state['analysis_done'] = True
            
    with col2:
        st.subheader("2. 검수 및 다운로드")
        if st.session_state.get('analysis_done'):
            df = pd.DataFrame(st.session_state['ai_result'])
            # 필수 열 자동 생성
            for col in ['품목명', '규격', '수량', '단가', '비고']:
                if col not in df.columns: df[col] = ""
            
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.download_button("💾 엑셀(CSV) 저장", edited_df.to_csv(index=False).encode('utf-8-sig'), f"order_{datetime.now().strftime('%m%d')}.csv")
        else:
            st.info("왼쪽에서 사진을 업로드하고 분석을 시작하세요.")
