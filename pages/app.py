import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# 페이지 설정
st.set_page_config(
    page_title="인구 통계 대시보드",
    page_icon="📊",
    layout="wide"
)

# 캐싱으로 데이터 로드 최적화
@st.cache_data
def load_data():
    # 현재 스크립트 디렉토리 기준
    script_dir = Path(__file__).parent
    
    # 가능한 경로들
    possible_paths = [
        script_dir / "data" / "202509_202509_jumindeungrogingumicsedaehyeonhwang_weolgan.csv",
        script_dir / "202509_202509_jumindeungrogingumicsedaehyeonhwang_weolgan.csv",
        Path("data/202509_202509_jumindeungrogingumicsedaehyeonhwang_weolgan.csv"),
        Path("202509_202509_jumindeungrogingumicsedaehyeonhwang_weolgan.csv"),
    ]
    
    file_path = None
    for path in possible_paths:
        if path.exists():
            file_path = path
            st.write(f"✅ 파일 발견: {file_path}")
            break
    
    if file_path is None:
        st.error("❌ CSV 파일을 찾을 수 없습니다!")
        st.write("현재 작업 디렉토리:", os.getcwd())
        st.write("시도한 경로들:")
        for path in possible_paths:
            st.write(f"  - {path} (존재: {path.exists()})")
        st.stop()
    
    df = pd.read_csv(file_path, encoding="euc-kr")
    df = df.dropna()
    return df

# 데이터 로드
df = load_data()

# 숫자형 변환
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

# 제목
st.title("📊 2025년 9월 주민등록 인구 및 세대 현황")

# 사이드바 필터
st.sidebar.header("필터 설정")
selected_area = st.sidebar.selectbox("행정구역 선택", df["행정구역"].unique())

# 전체 통계
st.sidebar.markdown("---")
st.sidebar.subheader("📈 전체 통계")
total_pop = df["2025년09월_총인구수"].sum()
total_household = df["2025년09월_세대수"].sum()
st.sidebar.metric("총 인구", f"{total_pop:,.0f}")
st.sidebar.metric("총 세대수", f"{total_household:,.0f}")

# 메인 대시보드
col1, col2, col3 = st.columns(3)

filtered = df[df["행정구역"] == selected_area]
if len(filtered) > 0:
    area_data = filtered.iloc[0]
    with col1:
        st.metric("총 인구수", f"{area_data['2025년09월_총인구수']:,.0f}")
    with col2:
        st.metric("세대수", f"{area_data['2025년09월_세대수']:,.0f}")
    with col3:
        st.metric("세대당 인구", f"{area_data['2025년09월_세대당 인구']:.2f}")

st.markdown("---")

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["📊 남녀 비교", "📈 TOP 10", "📉 비율 분석", "📋 데이터 조회"])

# 탭 1: 남녀 비교
with tab1:
    st.subheader(f"{selected_area} - 남녀 인구 비교")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bar_data = filtered.melt(
            id_vars=["행정구역"],
            value_vars=["2025년09월_남자 인구수", "2025년09월_여자 인구수"],
            var_name="성별", value_name="인구수"
        )
        fig_bar = px.bar(
            bar_data,
            x="성별", y="인구수",
            color="성별",
            title=f"{selected_area} 남녀 인구수 비교",
            labels={"인구수": "인구 수", "성별": "성별"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        pie_data = filtered.melt(
            id_vars=["행정구역"],
            value_vars=["2025년09월_남자 인구수", "2025년09월_여자 인구수"],
            var_name="성별", value_name="인구수"
        )
        fig_pie = px.pie(
            pie_data,
            values="인구수", names="성별",
            title=f"{selected_area} 남녀 인구 비율"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# 탭 2: TOP 10
with tab2:
    st.subheader("행정구역별 통계 TOP 10")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top10_pop = df.sort_values("2025년09월_총인구수", ascending=False).head(10)
        fig_top_pop = px.bar(
            top10_pop,
            x="행정구역", y="2025년09월_총인구수",
            title="총인구수 TOP 10",
            labels={"2025년09월_총인구수": "인구수"}
        )
        st.plotly_chart(fig_top_pop, use_container_width=True)
    
    with col2:
        top10_household = df.sort_values("2025년09월_세대수", ascending=False).head(10)
        fig_top_household = px.bar(
            top10_household,
            x="행정구역", y="2025년09월_세대수",
            title="세대수 TOP 10",
            labels={"2025년09월_세대수": "세대수"}
        )
        st.plotly_chart(fig_top_household, use_container_width=True)

# 탭 3: 비율 분석
with tab3:
    st.subheader("남여 비율(성비) 분석")
    
    fig_scatter = px.scatter(
        df,
        x="2025년09월_총인구수",
        y="2025년09월_남여 비율",
        size="2025년09월_세대수",
        hover_name="행정구역",
        title="인구수 vs 남여 비율",
        labels={
            "2025년09월_총인구수": "총인구수",
            "2025년09월_남여 비율": "남여 비율"
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.subheader("남여 비율 분포")
    fig_hist = px.histogram(
        df,
        x="2025년09월_남여 비율",
        nbins=20,
        title="남여 비율 히스토그램"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# 탭 4: 데이터 조회
with tab4:
    st.subheader("원본 데이터 조회")
    
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("정렬 기준", cols_to_numeric)
    with col2:
        ascending = st.checkbox("오름차순", value=False)
    
    sorted_df = df.sort_values(by=sort_by, ascending=ascending)
    st.dataframe(sorted_df, use_container_width=True)
    
    # CSV 다운로드
    csv = sorted_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 CSV로 다운로드",
        data=csv,
        file_name="population_data.csv",
        mime="text/csv"
    )
