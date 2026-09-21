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

# ─────────────────────────────────────────────
# 그래프 2. 기간 내 일관객 합계 TOP 5 영화 비교
# ─────────────────────────────────────────────
st.header("2. 일관객 합계 TOP 5 영화의 날짜별 변화")

top5_codes = (
    df.groupby(["영화코드", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화코드"]
    .tolist()
)

top5_df = (
    df[df["영화코드"].isin(top5_codes)]
    .copy()
    .sort_values("날짜")
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=False,
    title="이 기간 일관객 합계가 가장 큰 5편의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화",
    },
)

fig2.update_traces(
    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>일관객: %{y:,}명<extra>%{fullData.name}</extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        title="일관객 수(명)",
        tickformat=",",
    ),
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    ),
    height=550,
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.caption("기간 전체에서 일관객 합계가 큰 5편이 날짜별로 어떤 관객 흐름을 보였는지 서로 비교할 수 있습니다.")

# ─────────────────────────────────────────────
# 그래프 3. 날짜별 10위권 일관객 합계
# ─────────────────────────────────────────────
st.divider()
st.header("3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total.nlargest(3, "일관객")
    .sort_values("일관객", ascending=False)
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계",
    },
)

fig3.update_traces(
    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>10위권 일관객 합계: %{y:,}명<extra></extra>"
)

# 합계가 가장 컸던 3일을 그래프 위에 표시
annotations = []
for _, row in top3_days.iterrows():
    annotations.append(
        dict(
            x=row["날짜"],
            y=row["일관객"],
            text=f"{row['날짜']:%Y-%m-%d}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-45,
            font=dict(size=12),
        )
    )

fig3.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        title="10위권 일관객 합계(명)",
        tickformat=",",
    ),
    annotations=annotations,
    height=550,
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.caption("날짜별로 영화 10위권 전체의 관객 규모가 어떻게 변했는지와 관객이 가장 많이 몰린 날을 확인할 수 있습니다.")

# ─────────────────────────────────────────────
# 그래프 4. 영화별 기간 일관객 TOP 10
# ─────────────────────────────────────────────
st.divider()
st.header("4. 영화별 기간 일관객 TOP 10")

movie_summary = (
    df.groupby(["영화코드", "영화명"], as_index=False)
    .agg(
        기간_일관객=("일관객", "sum"),
        일관객_10위권_등장일수=("날짜", "nunique"),
    )
    .sort_values("기간_일관객", ascending=False)
    .head(10)
    .sort_values("기간_일관객", ascending=True)
)

fig4 = px.bar(
    movie_summary,
    x="기간_일관객",
    y="영화명",
    orientation="h",
    title="이 기간 일관객 합계 TOP 10",
    labels={
        "기간_일관객": "기간 일관객 합계",
        "영화명": "영화",
    },
    custom_data=["일관객_10위권_등장일수"],
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{y}</b>"
        "<br>기간 일관객 합계: %{x:,}명"
        "<br>10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)

fig4.update_layout(
    xaxis=dict(
        title="기간 일관객 합계(명)",
        tickformat=",",
    ),
    yaxis=dict(
        title="",
        categoryorder="total ascending",
    ),
    height=600,
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.caption("이 기간 동안 누적된 일관객이 가장 많은 영화 10편과 각 영화가 박스오피스 10위권에 등장한 날수를 함께 비교할 수 있습니다.")

# ─────────────────────────────────────────────
# 앞으로 추가할 그래프 구역
# ─────────────────────────────────────────────
st.divider()
st.header("5. 다음 그래프")
st.info("추가 시간 관련 그래프를 이 구역에 이어서 구성할 수 있습니다.")
