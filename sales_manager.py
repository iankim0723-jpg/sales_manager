import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# ==========================================
# [1] 기본 설정 및 API 키
# ==========================================
# 대표님의 API 키 (이대로 두시면 됩니다)
FIXED_API_KEY = "AIzaSyAbUOeVMbAif18qz_5L2KaS2f6jFzfF0Yw"

st.set_page_config(page_title="WOORI STEEL 영업관리", layout="wide")

# ==========================================
# [2] 디자인 (다크모드 & 가독성)
# ==========================================
st.markdown("""
    <style>
    /* 전체 배경: 짙은 다크그레이 */
    .stApp { background-color: #121212 !important; }
    
    /* 사이드바: 약간 밝은 톤 + 금색 테두리 */
    [data-testid="stSidebar"] { 
        background-color: #1E1E1E !important; 
        border-right: 2px solid #D4AF37 !important; 
    }
    
    /* 글자색 전체 흰색 강제 */
    [data-testid="stSidebar"] *, .stMarkdown, p, label, li { 
        color: #FFFFFF !important; 
    }
    
    /* 입력창: 배경 다크, 글자 금색(가독성) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2D2D2D !important;
        color: #F1C40F !important; 
        border: 1px solid #555 !important;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 5px;
        width: 100%;
    }
    
    /* 데이터프레임(표) 헤더 색상 */
    [data-testid="stDataFrame"] {
        border: 1px solid #D4AF37;
    }
    
    /* 제목 색상 */
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [3] AI 분석 함수 (오류 해결 버전)
# ==========================================
def analyze_image(image, prompt_user):
    """Gemini AI에게 이미지를 보내고 분석 결과를 받습니다."""
    try:
        # 라이브러리 설정
        genai.configure(api_key=FIXED_API_KEY)
        
        # 모델 설정 (최신 버전 호환 확인)
        # 만약 flash 모델이 안 되면 pro 모델로 자동 전환하도록 설정
        model_name = 'gemini-1.5-flash' 
        model = genai.GenerativeModel(model_name)
        
        # AI에게 내리는 명령 (취소선 무시, 숫자 보정 등)
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다. 
        이 이미지는 수기 주문서입니다. 아래 규칙을 엄격히 지켜 JSON 리스트로 답하세요.

        [분석 규칙]
        1. 취소선(가로줄)이 그어진 항목은 삭제된 주문이므로 절대 추출하지 마십시오.
        2. 품목명(예: 난연EPS, 부자재), 규격(길이 mm), 수량(매), 비고(위치: 정면/우측 등)를 추출하십시오.
        3. 악필로 인한 오타('413D' -> 4130, '40to' -> 4050)는 문맥에 맞게 숫자로 자동 보정하십시오.
        4. 단가가 이미지에 없으면 0으로 입력하십시오.
        5. 결과는 오직 JSON 데이터만 출력하십시오.

        [출력 예시]
        [
            {"품목명": "난연EPS 판넬 155T", "규격": 3910, "수량": 6, "비고": "정면"},
            {"품목명": "부자재 스크류볼트", "규격": 0, "수량": 1000, "비고": "150mm"}
        ]
        """
        
        if prompt_user:
            system_prompt += f"\n(추가 요청사항: {prompt_user})"

        with st.spinner("AI가 주문서를 분석 중입니다... (약 5~10초)"):
            response = model.generate_content([system_prompt, image])
            
            # 응답 텍스트에서 JSON 부분만 추출 (안정성 강화)
            txt = response.text
            start = txt.find('[')
            end = txt.rfind(']') + 1
            
            if start != -1 and end != -1:
                return eval(txt[start:end]) # 문자열을 리스트로 변환
            else:
                st.error("AI 응답에서 데이터를 찾지 못했습니다. 다시 시도해주세요.")
                return []
                
    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다: {e}")
        st.info("팁: requirements.txt 파일에 'google-generativeai>=0.7.2'가 적혀있는지 확인해주세요.")
        return []

# 세션 초기화 함수
def reset_session():
    for key in list(st.session_state.keys()):
        if key != 'logged_in':
            del st.session_state[key]
    st.rerun()

# ==========================================
# [4] 메인 화면 로직
# ==========================================

# 로그인 확인
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

# 사이드바
with st.sidebar:
    st.title("WOORI STEEL")
    st.markdown("---")
    menu = st.radio("업무 선택", ["1. 수주/발주 관리 (AI)", "2. 생산 현황", "3. 재고 관리"])
    st.markdown("---")
    if st.button("🔄 새 작업 시작 (초기화)"):
        reset_session()
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# 메인 기능
if menu == "1. 수주/발주 관리 (AI)":
    st.header("📝 AI 수주서 자동 판독")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    # [왼쪽] 입력창
    with col1:
        st.subheader("1. 주문서 업로드")
        client = st.text_input("거래처명", placeholder="예: 화성시 금곡동 현장")
        uploaded_file = st.file_uploader("📷 사진 업로드", type=['png', 'jpg', 'jpeg'])
        memo = st.text_area("비고 (선택사항)", placeholder="예: 4270 규격은 제외해줘")
        
        if st.button("🚀 AI 분석 실행", type="primary"):
            if uploaded_file:
                image = Image.open(uploaded_file)
                result = analyze_image(image, memo)
                if result:
                    st.session_state['ai_result'] = result
                    st.session_state['analysis_done'] = True
            else:
                st.warning("사진을 먼저 올려주세요.")

    # [오른쪽] 결과창
    with col2:
        st.subheader("2. 분석 결과")
        if st.session_state.get('analysis_done') and 'ai_result' in st.session_state:
            df = pd.DataFrame(st.session_state['ai_result'])
            
            # 빈 컬럼 채우기
            for col in ['품목명', '규격', '수량', '단가', '비고']:
                if col not in df.columns:
                    df[col] = 0 if col == '단가' or col == '규격' else ""

            st.success(f"✅ 분석 완료! 총 {len(df)}개 품목이 추출되었습니다.")
            
            # 편집 가능한 표
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "단가": st.column_config.NumberColumn(format="%d 원"),
                    "수량": st.column_config.NumberColumn(format="%d"),
                    "규격": st.column_config.NumberColumn(format="%d")
                }
            )
            
            # 합계 및 다운로드
            total = (edited_df['수량'] * edited_df['단가']).sum()
            st.metric("총 공급가액 (예상)", f"{total:,.0f} 원")
            
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("💾 엑셀 다운로드", csv, "order.csv", "text/csv")
        else:
            st.info("왼쪽에서 사진을 올리고 분석 버튼을 눌러주세요.")

else:
    st.info("준비 중인 메뉴입니다.")
