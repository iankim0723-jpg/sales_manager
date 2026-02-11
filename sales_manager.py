def analyze_image(image, prompt_user):
    """Gemini AI에게 이미지를 보내고 분석 결과를 받습니다."""
    try:
        # 라이브러리 설정
        genai.configure(api_key=FIXED_API_KEY)
        
        # [수정] 모델 자동 선택 로직
        # 1순위: 최신 플래시 모델 (속도 빠름)
        # 2순위: 프로 비전 모델 (구형이지만 안정적)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest') # latest 태그 추가
        except:
            st.warning("⚠️ 최신 모델을 찾을 수 없어 구형 모델(gemini-pro-vision)로 전환합니다.")
            model = genai.GenerativeModel('gemini-pro-vision')
        
        # AI에게 내리는 명령
        system_prompt = """
        당신은 샌드위치 판넬 발주서 분석 전문가입니다. 
        이 이미지는 수기 주문서입니다. 아래 규칙을 엄격히 지켜 JSON 리스트로 답하세요.

        [분석 규칙]
        1. 취소선(가로줄)이 그어진 항목은 삭제된 주문이므로 절대 추출하지 마십시오.
        2. 품목명, 규격(길이 mm), 수량(매), 비고를 추출하십시오.
        3. 결과는 오직 JSON 데이터만 출력하십시오.
        """
        
        if prompt_user:
            system_prompt += f"\n(추가 요청사항: {prompt_user})"

        with st.spinner("AI가 주문서를 분석 중입니다..."):
            response = model.generate_content([system_prompt, image])
            
            # 응답 텍스트에서 JSON 부분만 추출
            txt = response.text
            start = txt.find('[')
            end = txt.rfind(']') + 1
            
            if start != -1 and end != -1:
                return eval(txt[start:end])
            else:
                return []
                
    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다: {e}")
        st.info("팁: 오른쪽 하단 Manage app -> Reboot app을 꼭 눌러주세요!")
        return []
