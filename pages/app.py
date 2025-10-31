import pandas as pd
import streamlit as st
import plotly.express as px

# 파일 읽기 (euc-kr 인코딩)
df = pd.read_csv("202509_202509_jumindeungrogingumicsedaehyeonhwang_weolgan.csv", encoding="euc-kr")
df = df.dropna()  # 결측치 제거

# Streamlit 앱
st.title("2025년 9월 주민등록 인구 및 세대 현황 시각화")

# 주요 컬럼 숫자형 변환
cols_to_numeric = [
    "2025년09월_총인구수", 
    "2025년09월_세대수", 
    "2025년09월_세대당 인구", 
    "2025년09월_남자 인구수", 
    "2025년09월_여자 인구수", 
    "2025년09월_남여 비율"
]
for col in cols_to_numeric:
    df[col] = df[col].astype(str).str.replace(",", "").astype(float)

# 행정구역 선택
area = st.selectbox("행정구역 선택", df["행정구역"].unique())
filtered = df[df["행정구역"] == area]

# 바 차트: 남녀 인구 비교
st.subheader(f"{area} 남녀 인구 비교")
bar = px.bar(
    filtered.melt(id_vars=["행정구역"], 
                  value_vars=["2025년09월_남자 인구수", "2025년09월_여자 인구수"],
                  var_name="성별", value_name="인구수"),
    x="성별", y="인구수", color="성별", title=f"{area} 남녀 인구수"
)
st.plotly_chart(bar)

# 전체 행정구역: 총인구수 TOP 10
st.subheader("행정구역별 총인구수 TOP 10")
top10 = df.sort_values("2025년09월_총인구수", ascending=False).head(10)
fig_top10 = px.bar(top10, x="행정구역", y="2025년09월_총인구수", title="총인구수 TOP 10")
st.plotly_chart(fig_top10)

# 전체 행정구역: 남여 비율 시각화
st.subheader("행정구역별 남여 비율 분포")
fig_ratio = px.scatter(
    df, x="행정구역", y="2025년09월_남여 비율",
    size="2025년09월_총인구수", title="남여 비율 분포 (버블 크기: 총인구수)"
)
st.plotly_chart(fig_ratio)

