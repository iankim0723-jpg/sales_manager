import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time

# ==========================================
# [1] 기본 설정
# ==========================================
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

# ==========================================
# [2] 스타일(CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #1E1E1E !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important;
        color: #F1C40F !important; 
        border: 1px solid #555 !important;
    }
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #000000 !important;
        font-weight: bold;
        width: 100%;
    }
    .stAlert {
        background-color: #330000 !important;
        border: 1px solid #FF0000 !important;
        color: #FFCCCC !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [3] AI 분석 함수 (Pro 모델 사용)
# ==========================================
def analyze_image_pro(image, prompt_user):
    genai.configure(api_key=FIXED_API_KEY)
    
    # [전략 변경] Flash가 자꾸 404가 뜨므로, 'Pro' 모델로 변경
    # Pro 모델은 더 무겁지만 성능이 좋고 인식이 잘 됩니다.
    target_model = 'gemini-1.5-pro' 
    
    try:
        model = genai.GenerativeModel(target_model)
        
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        규칙:
        1. 취소선(가로줄) 항목은 절대 추출하지 마십시오.
        2. 품목명, 규격(숫자만), 수량, 비고를 추출하십시오.
        3. 결과는 오직 JSON 리스트 형식으로만 출력하십시오.
        """
        
        if prompt_user:
            system_prompt += f"\n(메모: {prompt_user})"

        with st.spinner(f"AI({target_model})가 정밀 분석 중입니다..."):
            response = model.generate_content([system_prompt, image])
            text = response.text
            
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                return eval(text[start:end])
            return []
            
    except Exception as e:
        st.error(f"🚨 분석 실패: {e}")
        # 여기에 버전 정보를 띄워서 원인을 파악합니다.
        st.warning(f"현재 시스템의 AI 도구 버전: {genai.__version__}")
        st.info("만약 버전이 0.8.3 미만이라면 requirements.txt 업데이트가 아직 반영되지 않은 것입니다.")
        return []

def reset_session():
    for key in list(st.session_state.keys()):
        if key != 'logged_in': 
            del st.session_state[key]
    st.rerun()

# ==========================================
# [4] 메인 화면
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 WOORI STEEL 접속")
    col1, _ = st.columns([1, 2])
    with col1:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "0723":
                st.session_state['logged_in'] = True
                st.rerun()
    st.stop()

with st.sidebar:
    st.title("WOORI STEEL")
    st.markdown("---")
    
    # [진단 기능] 여기에 현재 버전이 표시됩니다.
    st.caption(f"🔧 시스템 버전: v{genai.__version__}")
    
    menu = st.radio("메뉴", ["1. 수주/발주 관리 (AI)", "2. 생산 현황"])
    st.markdown("---")
    if st.button("🔄 작업 초기화"):
        reset_session()
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

if menu == "1. 수주/발주 관리 (AI)":
    c1, c2 = st.columns([5, 1])
    with c1: st.header("📝 AI 수주서 판독")
    with c2: 
        if st.button("➕ 초기화"): reset_session()

    st.error("🚨 [필독] AI 결과는 반드시 담당자가 2차 검수를 해야 합니다.")

    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("1. 업로드")
        client = st.text_input("거래처명", placeholder="현장명")
        uploaded_file = st.file_uploader("📷 주문서 (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("비고", height=100)
        
        if st.button("🚀 AI 분석 실행", type="primary"):
            if uploaded_file:
                img = Image.open(uploaded_file)
                # Pro 모델 함수 호출
                result = analyze_image_pro(img, memo)
                if result:
                    st.session_state['ai_result'] = result
                    st.session_state['analysis_done'] = True
            else:
                st.warning("사진을 올려주세요.")

    with col2:
        st.subheader("2. 결과 확인")
        if st.session_state.get('analysis_done') and 'ai_result' in st.session_state:
            df = pd.DataFrame(st.session_state['ai_result'])
            for c in ['품목명', '규격', '수량', '단가', '비고']:
                if c not in df.columns: df[c] = ""
            
            st.success(f"✅ 분석 완료! ({len(df)}건)")
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("💾 엑셀 다운로드", csv, "order.csv", "text/csv")
        else:
            st.info("왼쪽에서 분석을 시작하세요.")
else:
    st.info("준비 중")
