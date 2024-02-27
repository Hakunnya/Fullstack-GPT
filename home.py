import streamlit as st
from datetime import datetime

# set_page_config는 앱 페이지당 한 번만 호출 할 수 있으며 첫번째 streamlit명령으로 호출해야 함
st.set_page_config(
    page_title="Result study Home",
    page_icon="👀",
)
# 사이드바에 들어갈 카테고리는 home파일 동일 카테고리의 하위 카테로 pages라는 폴더명을 가져야 함

today = datetime.today().strftime("%H:%M:%S")
st.title("TEST PAGEs")
st.subheader(today)

st.markdown(
    """
# 테스트 중입니다.
            
이것저것 테스트 중...(2024-01-02)
            
Here are the apps I made:
            
- [ ] [Used Langchain Dataframe Agent Chatbot](/used_df_agent_bot)
- [ ] [Used Assistant api Chatbot](/used_assistant_api_bot)

"""
)
