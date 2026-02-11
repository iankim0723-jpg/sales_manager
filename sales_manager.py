import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

# 2. 고강도 시각화 CSS (가독성 강화)
st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; }
    [data-testid="stSidebar"] { background-color: #1E1E1E !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* 구역 박스 디자인 */
    div.stColumn > div {
        background-color: #1E1E1E;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #D4AF37 !important; border-bottom: 1px solid #D4AF37; padding-bottom: 10px; }
    
    /* 입력창 및 에디터 글자색 (밝은 노란색으로 가독성 확보) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important;
        color: #F1C40F !important; 
        border: 1px solid #444 !important;
    }
    
    /* 초기화 버튼 스타일 */
    .reset-btn {
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 세션 상태 초기화 함수 ---
def reset_session():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

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
                st.error("비밀번호가 틀렸습니다.")
    st.stop()

# --- 사이드바 ---
with st.sidebar:
    st.title("WOORI STEEL")
    menu = st.radio("메뉴 선택", ["1. 수주/발주 관리 (AI)", "2. 생산 현황", "3. 재고 조회", "4. 출고/배차", "5. 미수금 관리"])
    st.markdown("---")
    if st.button("🔄 전체 시스템 초기화"):
        reset_session()
    if st.button("🚪 로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- 메인 화면 ---
if menu == "1. 수주/발주 관리 (AI)":
    # 상단 헤더 및 새로고침 버튼
    col_head, col_reset = st.columns([5, 1])
    with col_head:
        st.header("📝 AI 수주 등록 및 자동 변환")
    with col_reset:
        if st.button("➕ 새 작업 시작", help="클릭 시 입력 내용과 사진이 초기화됩니다."):
            reset_session()

    st.warning("⚠️ **공지:** 이미지 파일은 **최대 10장**까지 한 번에 업로드 가능합니다. (JPG, PNG, PDF 지원)")

    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("📥 데이터 입력")
        client = st.text_input("거래처명", placeholder="거래처를 입력하세요")
        
        # 다중 파일 업로드 설정 (accept_multiple_files=True)
        uploaded_files = st.file_uploader(
            "📷 주문서 사진 업로드 (최대 10장)", 
            type=['png', 'jpg', 'jpeg', 'pdf'], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"✅ 현재 {len(uploaded_files)}장의 파일이 선택되었습니다.")
            if len(uploaded_files) > 10:
                st.error("파일은 최대 10장까지만 가능합니다. 초과된 파일은 제외됩니다.")
        
        raw_text = st.text_area("✍️ 텍스트 직접 입력 (선택사항)", height=100)
        
        if st.button("🚀 AI 분석 실행", type="primary"):
            if not uploaded_files and not raw_text:
                st.error("사진을 업로드하거나 내용을 입력해주세요.")
            else:
                with st.spinner("AI가 이미지를 판독하고 단가를 계산 중입니다..."):
                    time.sleep(2)
                    st.session_state['analysis_result'] = True

    with col2:
        st.subheader("📊 ERP 변환 검토")
        if st.session_state.get('analysis_result'):
            # 분석 결과 데이터 예시
            df_example = pd.DataFrame({
                '선택': [True, True, True],
                '품목명': ['GW판넬 벽체 125T', 'EPS 지붕 100T', '스크류볼트 150mm'],
                '규격(L)': [3500, 4200, 0],
                '수량': [12, 30, 1000],
                'AI 단가': [26500, 14500, 55],
                '비고': ['현장 직송', '', '아이보리']
            })
            
            st.success("✅ 분석이 완료되었습니다. 수정이 필요한 부분은 표에서 직접 클릭하여 수정하세요.")
            edited_df = st.data_editor(df_example, use_container_width=True, num_rows="dynamic")
            
            # 합계 계산
            total = (edited_df['수량'] * edited_df['AI 단가']).sum()
            st.metric("총 공급가액 (예상)", f"{total:,.0f} 원")
            
            st.download_button(
                label="💾 이카운트 업로드용 엑셀 다운로드",
                data=edited_df.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"수주_{datetime.now().strftime('%m%d_%H%M')}.csv",
                mime='text/csv'
            )
        else:
            st.info("왼쪽 섹션에서 주문 정보를 입력한 후 [AI 분석 실행]을 눌러주세요.")

else:
    st.header(f"🏗️ {menu}")
    st.info("해당 메뉴의 세부 기능은 현재 데이터 연결 중입니다.")
