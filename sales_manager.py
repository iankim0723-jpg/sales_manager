# 2. 스타일 설정 (다크모드 가독성 최적화)
st.markdown("""
    <style>
    /* 전체 배경색 및 기본 글자색 강제 지정 */
    .stApp { 
        background-color: #1E1E1E; 
    }
    
    /* 모든 일반 텍스트 및 라벨 글자색을 흰색으로 */
    .stApp, .stMarkdown, p, label, .stSelectbox, .stTextInput, .stTextArea, .stButton {
        color: #FFFFFF !important;
    }
    
    /* 사이드바 배경 및 글자색 */
    [data-testid="stSidebar"] { 
        background-color: #2B2B2B !important; 
        border-right: 1px solid #444; 
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* 제목(Heading) 색상 - 금색 포인트 */
    h1, h2, h3, h4, h5, h6 { 
        color: #D4AF37 !important; 
    }

    /* 데이터프레임 가독성 조절 (배경은 어둡게, 글자는 밝게) */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #2D2D2D !important;
    }
    
    /* 입력창 배경색 조절 (글자가 잘 보이도록) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #333333 !important;
        color: white !important;
        border: 1px solid #555 !important;
    }

    /* 경고/정보 박스 내 글자색 유지 */
    .stAlert p {
        color: white !important;
    }
    
    /* 에디터(Data Editor) 글자색 보정 */
    div[data-testid="stDataEditor"] div {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
