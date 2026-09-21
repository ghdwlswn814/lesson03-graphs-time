import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 10위권 데이터를 시간의 흐름에 따라 살펴봅니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜: 하이픈 없는 YYYYMMDD → 실제 날짜형
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d", errors="coerce")

    # 숫자형 열 정리
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 영화코드는 문자열로 유지
    df["영화코드"] = df["영화코드"].astype(str)

    return df.dropna(subset=["날짜"]).sort_values(["날짜", "순위"])

try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()

# ─────────────────────────────────────────────
# 그래프 1. 영화별 일관객 변화
# ─────────────────────────────────────────────
st.header("1. 영화별 일관객 변화")

movie_list = (
    df[["영화코드", "영화명"]]
    .drop_duplicates()
    .sort_values("영화명")
)

movie_options = movie_list["영화명"].tolist()

if not movie_options:
    st.warning("표시할 영화 데이터가 없습니다.")
    st.stop()

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_options,
    key="movie_selector",
)

selected_code = movie_list.loc[
    movie_list["영화명"] == selected_movie, "영화코드"
].iloc[0]

movie_df = (
    df[df["영화코드"] == selected_code]
    .sort_values("날짜")
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
    },
    custom_data=["영화명"],
)

fig.update_traces(
    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        title="일관객 수(명)",
        tickformat=",",
    ),
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.caption("선택한 영화의 일관객 수가 시간에 따라 어떻게 증가하거나 감소했는지 한눈에 볼 수 있습니다.")

# ─────────────────────────────────────────────
# 앞으로 추가할 그래프 구역
# ─────────────────────────────────────────────
st.divider()
st.header("2. 다음 그래프")
st.info("다음 시간 관련 그래프를 이 구역에 추가할 예정입니다.")

st.divider()
st.header("3. 다음 그래프")
st.info("추가 그래프를 이 구역에 이어서 구성할 수 있습니다.")
