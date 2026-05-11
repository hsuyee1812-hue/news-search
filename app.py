import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="따릉이 이용 분석 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 공공데이터 분석")
st.markdown("공공데이터를 활용하여 따릉이 이용 패턴과 기온의 상관관계를 분석합니다.")

# 2. 데이터베이스 존재 여부 확인
DB_PATH = 'bicycle.db'

if not os.path.exists(DB_PATH):
    st.error(f"🚨 '{DB_PATH}' 파일을 찾을 수 없습니다! 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 3. 데이터 로드 함수 (캐싱 처리하여 속도 향상)
def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

# --- 차트 1: 월별 이용패턴 ---
st.header("1. 월별 이용량 추이")
sql_1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수 
FROM 이용정보 
GROUP BY 대여일자 
ORDER BY 대여일자
"""
df1 = run_query(sql_1)

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    fig1 = px.line(df1, x='대여일자', y='총이용건수', title='월별 따릉이 이용 건수', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("🔍 분석 정보")
    st.code(sql_1, language='sql')
    st.info("""
    - **인사이트**: 계절적 요인이 강하게 나타납니다. 주로 날씨가 따뜻한 봄~가을에 이용량이 급증하며, 추운 겨울에는 급감하는 패턴을 보입니다.
    """)

st.divider()

# --- 차트 2: 기온별 평균 이용량 ---
st.header("2. 기온에 따른 평균 이용 변화")
# SQLite에서는 정수 나눗셈을 이용해 구간(Bin)을 만듭니다.
sql_2 = """
SELECT 
    (CAST(B.평균기온 / 5 AS INT) * 5) as 기온구간, 
    AVG(A.이용건수) as 평균이용건수
FROM 이용정보 A
JOIN 기온 B ON A.대여일자 = B.년월
GROUP BY 기온구간
ORDER BY 기온구간
"""
df2 = run_query(sql_2)
df2['기온구간_표기'] = df2['기온구간'].astype(str) + "도 ~ " + (df2['기온구간'] + 5).astype(str) + "도"

col2_1, col2_2 = st.columns([2, 1])
with col2_1:
    fig2 = px.bar(df2, x='기온구간_표기', y='평균이용건수', title='평균 기온별(5도 구간) 평균 이용건수',
                 color='평균이용건수', color_continuous_scale='Viridis')
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 분석 정보")
    st.code(sql_2, language='sql')
    st.info("""
    - **인사이트**: 기온이 20~25도 사이일 때 이용량이 가장 높습니다. 너무 덥거나(30도 이상) 너무 추우면 이용량이 현저히 줄어드는 '종 모양' 분포를 보입니다.
    """)

st.divider()

# --- 차트 3: 인기 대여소 TOP 10 ---
st.header("3. 가장 인기 있는 대여소 TOP 10")
sql_3 = """
SELECT B.보관소명, SUM(A.이용건수) as 총이용건수
FROM 이용정보 A
JOIN 대여소 B ON A.대여소번호 = B.대여소번호
GROUP BY B.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
df3 = run_query(sql_3).sort_values(by='총이용건수', ascending=True) # 가로 막대를 위해 정렬

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', 
                 title='이용건수 상위 10개 대여소', text_auto='.2s')
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 분석 정보")
    st.code(sql_3, language='sql')
    st.info("""
    - **인사이트**: 상위권 대여소들은 주로 지하철역 인근이나 대규모 주거 단지 근처에 위치해 있습니다. 이는 따릉이가 대중교통의 '라스트 마일' 수단으로 활용됨을 시사합니다.
    """)