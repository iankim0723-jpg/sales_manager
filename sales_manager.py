import streamlit as st
import pandas as pd
import time
from datetime import datetime
import google.generativeai as genai
from PIL import Image

# ==========================================
# [1] 시스템 설정 및 API 키 통합
# ==========================================
# 대표님이 제공해주신 Gemini API 키를 여기에 고정했습니다.
# ※ 주의: 이 코드가 포함된 파일은 타인에게 공유하지 마세요. (키 유출 위험)
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

# ==========================================
# [2] 디자인 (다크모드 & 가독성 최적화)
# ==========================================
st.markdown("""
    <style>
    /* 전체 테마: 짙은 다크그레이 배경 */
    .stApp { background-color: #121212 !important; }
    
    /* 사이드바: 약간 밝은 톤 + 금색 테두리 */
    [data-testid="stSidebar"] { 
        background-color: #1E1E1E !important; 
        border-right: 2px solid #D4AF37 !important; 
    }
    
    /* 글자색 전체 흰색 강제 */
    [data-testid="stSidebar"] *, .stMarkdown, p, label { 
        color: #FFFFFF !important; 
    }
    
    /* 입력창: 배경 다크, 글자 금색(잘 보이게) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important;
        color: #F1C40F !important; 
        border: 1px solid #555 !important;
    }
    
    /* 버튼: 금색 배경, 검은 글씨 */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 5px;
        width: 100%;
    }
    
    /* 구역 박스 디자인 */
    div.stColumn > div {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    
    /* 제목 스타일 */
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [3] 핵심 기능 함수 (AI 분석 & 초기화)
# ==========================================

def reset_session():
    """새 작업 시작 시 데이터 초기화"""
    for key in list(st.session_state.keys()):
        if key != 'logged_in': # 로그인 상태는 유지
            del st.session_state[key]
    st.rerun()

def analyze_image(image, prompt_text=""):
    """Gemini AI에게 이미지를 보내고 표 데이터를 받아오는 함수"""
    try:
        genai.configure(api_key=FIXED_API_KEY)
       # 추천 1: 버전 번호를 명시하기
model = genai.GenerativeModel('gemini-1.5-flash-001')
        
        # AI에게 주는 강력한 명령 (프롬프트)
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다. 이 이미지는 수기 주문서입니다.
        아래 규칙을 엄격히 준수하여 데이터를 추출하고 JSON 리스트 형식으로만 답하세요.

        [분석 규칙]
        1. **취소선 무시:** 글자 위에 가로줄(취소선)이 그어진 항목은 삭제된 주문이므로 절대 추출하지 마십시오. (가장 중요)
        2. **항목 추출:** 품목명(예: 난연EPS, 캐노피, 부자재), 규격(길이 mm), 수량(매), 비고(위치: 정면, 우측 등)를 추출하십시오.
        3. **규격 보정:** 악필로 인해 '413D', '40to', '4/30' 등으로 보이는 것은 문맥상 '4130', '4050', '4130' 같은 숫자로 자동 보정하십시오.
        4. **단가:** 이미지에 단가가 없으면 0으로 두십시오.
        
        [출력 포맷 예시 - 반드시 이 JSON 형태만 출력할 것]
        [
            {"품목명": "난연EPS 판넬 155T", "규격": 3910, "수량": 6, "비고": "정면"},
            {"품목명": "난연EPS 판넬 155T", "규격": 4050, "수량": 34, "비고": "정면/우측/좌측 합계"}
        ]
        """
        
        if prompt_text:
            system_prompt += f"\n(사용자 추가 메모: {prompt_text})"

        with st.spinner("AI가 주문서를 판독하고 있습니다... (약 5초)"):
            response = model.generate_content([system_prompt, image])
            
            # 응답 텍스트에서 JSON 부분만 추출
            txt = response.text
            start = txt.find('[')
            end = txt.rfind(']') + 1
            if start != -1 and end != -1:
                return eval(txt[start:end]) # 문자열을 파이썬 리스트로 변환
            else:
                return []
    except Exception as e:
        st.error(f"AI 분석 오류: {e}")
        return []

# ==========================================
# [4] 메인 로직 (로그인 & UI)
# ==========================================

# 로그인 체크
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
                st.error("비밀번호가 일치하지 않습니다.")
    st.stop()

# 사이드바 메뉴
with st.sidebar:
    st.title("WOORI STEEL")
    st.markdown("---")
    menu = st.radio("업무 선택", ["1. 수주/발주 관리 (AI)", "2. 생산 현황", "3. 재고 관리", "4. 출고/배차", "5. 미수금 관리"])
    st.markdown("---")
    
    # 기능 버튼들
    if st.button("🔄 새 작업 시작 (초기화)"):
        reset_session()
    
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# 메인 화면: 1. 수주 관리
if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 자동 등록")
    st.caption("수기 주문서나 카톡 캡처를 올리면 AI가 즉시 이카운트 업로드용 엑셀로 변환합니다.")

    # 2단 레이아웃
    c1, c2 = st.columns([1, 1.5], gap="large")

    # [왼쪽] 입력 및 업로드
    with c1:
        st.subheader("1. 주문서 업로드")
        client_name = st.text_input("거래처명", placeholder="예: 화성시 금곡동 현장")
        
        # 파일 업로더 (여러 장 가능하게 하려면 accept_multiple_files=True)
        uploaded_file = st.file_uploader("📷 이미지 파일 선택 (JPG, PNG)", type=['png', 'jpg', 'jpeg'])
        
        user_memo = st.text_area("비고/요청사항", placeholder="예: 단가는 155T 기준 21,000원으로 계산해줘", height=80)
        
        if st.button("🚀 AI 분석 실행", type="primary"):
            if uploaded_file:
                image = Image.open(uploaded_file)
                # AI 분석 호출
                result_data = analyze_image(image, user_memo)
                if result_data:
                    st.session_state['ai_data'] = result_data
                    st.session_state['analysis_done'] = True
            else:
                st.warning("먼저 이미지를 업로드해주세요.")

    # [오른쪽] 결과 확인 및 엑셀 다운로드
    with c2:
        st.subheader("2. 분석 결과 (편집 가능)")
        
        if st.session_state.get('analysis_done') and 'ai_data' in st.session_state:
            df = pd.DataFrame(st.session_state['ai_data'])
            
            # 빈 컬럼 채우기 (에러 방지)
            for col in ['품목명', '규격', '수량', '단가', '비고']:
                if col not in df.columns:
                    df[col] = 0 if col == '단가' else ""

            # 데이터 에디터 표시
            st.success(f"✅ 분석 완료! 총 {len(df)}개 행이 추출되었습니다.")
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "단가": st.column_config.NumberColumn(format="%d 원"),
                    "수량": st.column_config.NumberColumn(format="%d")
                }
            )
            
            # 합계 금액 자동 계산
            total_price = (edited_df['수량'] * edited_df['단가']).sum()
            st.metric("총 공급가액 (예상)", f"{total_price:,.0f} 원")

            # 엑셀 다운로드 버튼
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="💾 이카운트 엑셀 다운로드",
                data=csv,
                file_name=f"수주_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
        else:
            st.info("👈 왼쪽에서 주문서를 올리고 분석을 시작하세요.")
            st.markdown("""
            **[팁] AI가 잘 읽는 법**
            - 사진은 **밝은 곳**에서 찍어주세요.
            - **취소선(가로줄)**은 AI가 자동으로 제외합니다.
            - 글씨가 너무 흘려 써진 경우 '비고'란에 힌트를 적어주세요.
            """)

else:
    st.info(f"{menu} 메뉴는 현재 개발 중입니다.")

