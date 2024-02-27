from langchain.schema import SystemMessage
import streamlit as st
import os
from typing import Type
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.agents import initialize_agent, AgentType

import pandas as pd
import sunung_calculate

openai_api_key = st.secrets["OPENAI_API_KEY"]
langchain_tracing_v2 = st.secrets["LANGCHAIN_TRACING_V2"]
langchain_api_key = st.secrets["LANGCHAIN_API_KEY"]
langchain_project = st.secrets["LANGCHAIN_PROJECT"]
langchain_endpoint = st.secrets["LANGCHAIN_ENDPOINT"]
langsmith_tenant_id = st.secrets["LANGSMITH_TENANT_ID"]



llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo-1106")

st.set_page_config(
    page_title="University Score Calulater",
    page_icon="📃",
)


@st.cache_data()
def read_file(file):
    file_content = file.read()
    file_path = f"./.cache/score_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    loader = pd.read_excel(file_path)
    doc_list = loader.values.tolist()
    return doc_list[0]

with st.sidebar:
    file = st.file_uploader(
        "Upload a .xlsx file",
        type=["xlsx"],
    )

@st.cache_data(show_spinner="Load file...")
def load_df():
    score_card = read_file(file)
    df = sunung_calculate.func_common(score_card)
    return df

def cut_the_university(symbol):
    df = load_df()
    df_uni = df.loc[df['대학명']==symbol]
    jss = df_uni.drop('대학명', axis=1).to_json(orient='records', force_ascii=False, indent=4)
    return {
                "symbol": symbol, 
                "annualReports": jss
            }


class NameOfUniversitySchema(BaseModel):
    symbol: str = Field(
        description="Name of the university in Korea.Example: 성균관대, 서울대",
    )


class InformationofUniversityTool(BaseTool):
    name = "InformationofUniversity"
    description = """
    Use this to retrieve information from universities. 
    Please show the all information.
    """
    args_schema: Type[NameOfUniversitySchema] = NameOfUniversitySchema

    def _run(self, symbol):
        data = cut_the_university(symbol)
        return data["annualReports"]


agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True,
    tools=[InformationofUniversityTool()],
    agent_kwargs={
        "system_message": SystemMessage(
            content="""
            You are a university admissions consultant in Korea.
                        
            It provides university scores and provides information about the university to users.
                        
            Please read the university's '학과명', '군', '환산점수', '커트라인'and advise whether or not to apply considering the difference in scores.
            
            You should display ‘humanities’ and ‘nature’ separately, all information in Korean and expose information about all departments of the university.
        """
        )
    },
)

st.title("수능 환산 점수 계산기")

st.markdown(
    """
수능 성적 엑셀 파일을 넣으시면 점수를 계산해 드립니다.
"""
)

if file:
    score_card = read_file(file)
    score = {
        '한국사등급' : [score_card[1]],
        '국어' : [score_card[2]],
        score_card[5] : [score_card[6]],
        '영어등급' : [score_card[9]],
        score_card[10] : [score_card[11]],
        score_card[14] : [score_card[15]],
        '제2외'+score_card[18] : [score_card[19]]
    }
    view_score = pd.DataFrame(score)
    st.markdown(view_score.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    

name_of_university = st.text_input("관심있는 대학 이름을 적어 주세요.")

if name_of_university:
    result = agent.invoke(name_of_university)
    st.write(result["output"].replace("$", "\$"))
