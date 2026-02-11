import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

# 2. 고강도 시각화 CSS (가독성 문제 해결 핵심)
st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp { background-color: #121212 !important; }

    /* [좌측 사이드바] 글자색과 배경색 대비 강화 */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E !important;
        border-right: 2px solid #D4AF37 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important; /* 모든 글자 흰색 고정 */
        font-weight: 500;
    }
    /* 사이드바 라디오 버튼(메뉴) 선택 시 강조 */
    div[data-testid="stSidebarUserContent"] .st-emotion-cache-17l69e0 {
        background-color: #333333 !important;
        border-radius: 10px;
        padding: 5px;
    }

    /* [메인 화면] 템플릿 구분을 위한 박스 디자인 */
    div.stColumn > div {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }

    /* 제목 및 강조 텍스트 */
    h1, h2, h3 { color: #D4AF37 !important; border-bottom: 1px solid #D4AF37; padding-bottom: 10px; }
    
    /* 입력창 및 에디터 가시성 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important;
        color: #00FF00 !important; /* 입력 글자는 녹색으로 눈에 띄게 */
        border: 1px solid #444 !important;
    }
    
    /* 데이터프레임 헤더와 본문 구분 */
    .stDataFrame {
        border: 1px solid #D4AF37 !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background-color: #D4AF37 !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 로그인 로직 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 WOORI STEEL SYSTEM")
    with st.container():
        pw = st.text_input("비밀번호 입력", type="password")
        if st.button("접속하기"):
            if pw == "0723":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("접근 권한이 없습니다.")
    st.stop()

# --- 사이드바 메뉴 ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/D4AF37/000000?text=WOORI+STEEL", use_container_width=True)
    st.markdown("### 📋 핵심 업무 메뉴")
    menu = st.radio("", [
        "1. 수주/발주 관리 (AI)", 
        "2. 생산 현황", 
        "3. 재고 조회", 
        "4. 출고/배차",
        "5. 미수금 관리"
    ])
    st.markdown("---")
    st.write(f"📅 **일자:** {datetime.now().strftime('%Y-%m-%d')}")
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- 메인 컨텐츠 ---
if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 변환 자동화")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("📥 데이터 입력")
        client = st.text_input("거래처명", placeholder="거래처를 입력하세요")
        # 파일 업로드 양식 부활
        img_file = st.file_uploader("📷 주문서 사진/파일 업로드", type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'])
        raw_text = st.text_area("✍️ 수동 입력 (카톡 복사 등)", height=150)
        
        if st.button("🚀 데이터 분석 시작"):
            with st.spinner("AI가 규격과 단가를 매칭하는 중..."):
                time.sleep(1.5)
                st.session_state['analysis_done'] = True

    with col2:
        st.subheader("📊 ERP 변환 결과")
        if st.session_state.get('analysis_done'):
            # 예시 데이터 (실제 업무 양식 반영)
            df_example = pd.DataFrame({
                '품목명': ['GW판넬 벽체 125T', 'EPS 지붕 100T', '스크류볼트'],
                '규격(L)': [3500, 4200, 150],
                '수량': [10, 25, 500],
                '단가': [26500, 14500, 60],
                '공급가액': [927500, 1522500, 30000]
            })
            st.success("✅ 분석 완료! 아래 표를 검토 후 다운로드하세요.")
            edited_df = st.data_editor(df_example, use_container_width=True, num_rows="dynamic")
            
            st.markdown("---")
            st.download_button("💾 이카운트 엑셀 양식 다운로드", data=edited_df.to_csv().encode('utf-8-sig'), file_name="order.csv")
        else:
            st.info("왼쪽에서 주문서를 업로드하거나 내용을 입력하면 분석 결과가 여기에 표시됩니다.")

else:
    st.header(f"🏗️ {menu} 섹션")
    st.info("해당 메뉴의 세부 기능은 현재 준비 중입니다.")
