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
# [3] AI 자동 연결 함수 (여기가 핵심!)
# ==========================================
def analyze_image_auto(image, prompt_user):
    genai.configure(api_key=FIXED_API_KEY)
    
    # [전략] 서버가 무슨 버전을 쓰는지 모르니, 
    # 다 준비해놓고 될 때까지 순서대로 시도합니다.
    model_candidates = [
        "gemini-1.5-flash",       # 1순위: 최신 (빠름)
        "gemini-1.5-flash-001",   # 1.5버전 다른 이름
        "gemini-1.5-flash-latest",# 1.5버전 다른 이름 2
        "gemini-1.5-pro",         # 2순위: 고성능
        "gemini-1.5-pro-001",     # 2순위 다른 이름
        "gemini-1.5-pro-latest",  # 2순위 다른 이름 2
        "gemini-pro-vision",      # 3순위: 구형 (호환성 최강)
    ]
    
    system_prompt = """
    당신은 샌드위치 판넬 발주서 분석 전문가입니다.
    규칙:
    1. 취소선(가로줄) 항목은 절대 추출하지 마십시오.
    2. 품목명, 규격(숫자만), 수량, 비고를 추출하십시오.
    3. 결과는 오직 JSON 리스트 형식으로만 출력하십시오.
    """
    if prompt_user:
        system_prompt += f"\n(메모: {prompt_user})"

    last_error = ""
    
    # 후보 모델들을 하나씩 순회하며 시도
    for model_name in model_candidates:
        try:
            # 모델 생성 시도
            model = genai.GenerativeModel(model_name)
            
            # 실제 호출 시도 (여기서 에러 안 나면 성공)
            with st.spinner(f"AI 모델({model_name})로 접속 시도 중..."):
                response = model.generate_content([system_prompt, image])
                text = response.text
                
                # 성공하면 즉시 결과 처리 후 리턴
                start = text.find('[')
                end = text.rfind(']') + 1
                if start != -1 and end != -1:
                    st.toast(f"✅ {model_name} 모델로 연결 성공!", icon="🎉") # 성공 알림
                    return eval(text[start:end])
                
        except Exception as e:
            # 실패하면 다음 모델로 넘어감
            last_error = str(e)
            continue
            
    # 모든 모델이 다 실패했을 때만 에러 출력
    st.error("🚨 모든 AI 모델 연결에 실패했습니다.")
    st.error(f"마지막 오류 메시지: {last_error}")
    st.warning("팁: requirements.txt 가 업데이트 되지 않은 것 같습니다. 잠시 후 다시 시도해보세요.")
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
    
    # 현재 라이브러리 버전 확인용 (디버깅)
    st.caption(f"🔧 라이브러리 버전: {genai.__version__}")
    
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
                # 자동 연결 함수 호출
                result = analyze_image_auto(img, memo)
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
