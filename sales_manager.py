import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. 페이지 설정 (최상단 고정)
st.set_page_config(page_title="WOORI STEEL 영업관리 시스템", layout="wide", initial_sidebar_state="expanded")

# 2. 스타일 설정 (다크모드 가독성 & 가시성 100% 확보)
st.markdown("""
    <style>
    /* 전체 배경 및 글자색 */
    .stApp { background-color: #1E1E1E !important; }
    
    /* 모든 텍스트 요소를 흰색으로 강제 */
    .stApp, .stMarkdown, p, label, .stSelectbox, .stTextInput, .stTextArea, .stButton, .stMetric, [data-testid="stHeader"] {
        color: #FFFFFF !important;
    }
    
    /* 제목(Heading) 색상 - 금색 */
    h1, h2, h3, h4, h5, h6 { color: #D4AF37 !important; }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #2B2B2B !important; border-right: 1px solid #444; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }

    /* 입력창(Input) 가시성 확보: 배경은 어둡게, 테두리는 밝게 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #333333 !important;
        color: white !important;
        border: 1px solid #D4AF37 !important;
    }

    /* 데이터프레임/에디터 글자색 강제 (흰색) */
    div[data-testid="stDataEditor"] div, .stDataFrame div {
        color: white !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #1E1E1E !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------
# [함수 정의] (에러 방지를 위해 메인 로직 전 선언)
# ------------------------------------------
def calculate_price(mat, thick):
    base_eps, base_gw, base_ure = 11500, 13800, 24500
    gap_eps, gap_gw, gap_ure = 800, 2400, 4000
    
    price = 0
    if mat == "EPS": price = base_eps + (int(thick/25)*gap_eps)
    elif mat == "GW": price = base_gw + (int(thick/25)*gap_gw)
    elif mat == "URE": price = base_ure + (int(thick/25)*gap_ure)
    return price

# ------------------------------------------
# [로그인 로직]
# ------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 WOORI STEEL 접속")
    col1, _ = st.columns([1, 2])
    with col1:
        pw = st.text_input("비밀번호 (0723)", type="password")
        if st.button("로그인"):
            if pw == "0723":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    st.stop()

# ------------------------------------------
# [사이드바 메뉴]
# ------------------------------------------
with st.sidebar:
    st.title("WOORI STEEL\nManager System")
    st.markdown("---")
    menu = st.radio("업무 선택", [
        "1. 수주/발주 관리 (AI)", 
        "2. 생산 관리", 
        "3. 재고 관리", 
        "4. 출고/배차 관리",
        "5. 수금/미수 관리"
    ])
    st.markdown("---")
    # datetime 에러 방지를 위해 변수에 미리 담기
    current_date = datetime.now().strftime('%Y-%m-%d')
    st.info(f"접속자: 관리자\n날짜: {current_date}")
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# ------------------------------------------
# [메인 화면]
# ------------------------------------------
if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주 등록")
    st.write("주문서 텍스트나 파일을 올리면 분석을 시작합니다.")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        client_name = st.text_input("거래처명", "주식회사 대성플러스")
        raw_text = st.text_area("주문 내용 입력", height=150)
        btn_analyze = st.button("🚀 AI 분석 실행")

    with c2:
        if btn_analyze:
            with st.spinner("분석 중..."):
                time.sleep(1)
                data = {
                    '품목명': ['GW판넬 벽체 125T (48K)', '선홈통 (Gutter)'],
                    '규격': [2.900, 3.000],
                    '수량': [6, 20],
                    '단가': [25500, 12000]
                }
                df = pd.DataFrame(data)
                st.success("분석 완료!")
                st.data_editor(df, use_container_width=True)

else:
    st.header(f"{menu}")
    st.write("상세 내용을 준비 중입니다.")
