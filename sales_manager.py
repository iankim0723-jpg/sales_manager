import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import time

# ==========================================
# [1] 필수 설정
# ==========================================
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

# API 키 (고정)
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

# ==========================================
# [2] 스타일(CSS) - 가독성 & 경고창 강화
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
    /* [중요] 경고 문구 스타일 강조 */
    .stAlert {
        background-color: #330000 !important;
        border: 1px solid #FF0000 !important;
        color: #FFCCCC !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [3] 핵심 기능 함수
# ==========================================
def reset_session():
    """새 작업 시작 (초기화)"""
    for key in list(st.session_state.keys()):
        if key != 'logged_in': 
            del st.session_state[key]
    st.rerun()

def analyze_image(image, prompt_user):
    """AI에게 이미지를 보내고 표 데이터를 받아옴"""
    try:
        genai.configure(api_key=FIXED_API_KEY)
        
        # [수정됨] 최신 Flash 모델 대신, 구형 버전에서도 100% 작동하는 'pro-vision' 모델 사용
        # 이 모델은 업데이트를 안 해도 작동합니다.
        model = genai.GenerativeModel('gemini-pro-vision')

        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다.
        이 수기 주문서 이미지를 보고 아래 규칙에 따라 JSON 데이터만 출력하세요.
        
        1. 취소선(가로줄)이 그어진 항목은 삭제된 것이므로 절대 추출하지 마십시오.
        2. 품목명, 규격(길이), 수량, 비고를 추출하십시오.
        3. 악필로 인한 오타(413D -> 4130)는 문맥에 맞춰 숫자로 보정하십시오.
        4. 출력 형식은 오직 JSON 리스트여야 합니다. 예: [{"품목명": "EPS", "규격": 3000, "수량": 10, "비고": ""}]
        """
        
        if prompt_user:
            system_prompt += f"\n(사용자 메모: {prompt_user})"

        with st.spinner("AI가 주문서를 분석 중입니다..."):
            response = model.generate_content([system_prompt, image])
            text = response.text
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                return eval(text[start:end])
            return []
            
    except Exception as e:
        # 에러 발생 시 사용자에게 친절하게 안내
        st.error(f"분석 오류: {e}")
        st.warning("팁: 만약 '404 model not found'가 계속 뜨면 requirements.txt 파일을 확인해주세요.")
        return []

# ==========================================
# [4] 메인 화면 로직
# ==========================================

# 1. 로그인 화면
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
            else:
                st.error("비밀번호가 틀렸습니다.")
    st.stop()

# 2. 사이드바 메뉴
with st.sidebar:
    st.title("WOORI STEEL")
    st.markdown("---")
    menu = st.radio("메뉴", ["1. 수주/발주 관리 (AI)", "2. 생산 현황", "3. 재고 관리"])
    st.markdown("---")
    if st.button("🔄 새 작업 시작 (초기화)"):
        reset_session()
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# 3. 메인 기능 화면
if menu == "1. 수주/발주 관리 (AI)":
    # 상단 헤더 & 새로고침 버튼
    c_head, c_btn = st.columns([5, 1])
    with c_head:
        st.header("📝 AI 수주서 자동 판독")
    with c_btn:
        if st.button("➕ 초기화"):
            reset_session()
            
    # [중요] 경고 문구 (요청하신 내용 반영)
    st.error("🚨 [필독] AI는 업무 보조 도구입니다. 결과에 오류가 있을 수 있으므로, 담당자는 반드시 '2차 검수'를 진행하셔야 합니다.")

    # 본문
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("1. 주문서 업로드")
        client = st.text_input("거래처명", placeholder="예: 화성 금곡동")
        
        uploaded_file = st.file_uploader("📷 주문서 사진 (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("비고 (선택사항)", height=100)
        
        if st.button("🚀 AI 분석 실행", type="primary"):
            if uploaded_file:
                img = Image.open(uploaded_file)
                result = analyze_image(img, memo)
                if result:
                    st.session_state['ai_result'] = result
                    st.session_state['analysis_done'] = True
            else:
                st.warning("사진을 먼저 올려주세요!")

    with col2:
        st.subheader("2. 분석 결과 (검수 필수)")
        if st.session_state.get('analysis_done') and 'ai_result' in st.session_state:
            df = pd.DataFrame(st.session_state['ai_result'])
            
            # 컬럼 보정
            for c in ['품목명', '규격', '수량', '단가', '비고']:
                if c not in df.columns: df[c] = ""
            
            st.success(f"✅ 분석 완료! ({len(df)}건)")
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("💾 엑셀 다운로드", csv, "order.csv", "text/csv")
        else:
            st.info("👈 왼쪽에서 사진을 올리면 여기에 결과가 나옵니다.")

else:
    st.header(f"{menu}")
    st.info("준비 중입니다.")
