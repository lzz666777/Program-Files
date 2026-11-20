"""
“桩”尽其用 · 项目初始框架
四个模块：价格地图 / 站点账单 / 治理沙盘 / 反馈中心

运行：
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="桩尽其用 · 价格与车位治理",
    page_icon=":material/ev_station:",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "stations.csv"

GLASS_CSS = """
<style>
:root {
  --glass-bg: rgba(255, 255, 255, 0.82);
  --glass-border: rgba(255, 255, 255, 0.92);
  --ink: #122a26;
}
html, body, .stApp { background: #dce8e4; }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  backdrop-filter: none !important;
}
[data-testid="stMainBlockContainer"] {
  max-width: 680px;
  margin: 18px 22px 18px auto;
  padding: 20px 22px 64px;
  min-height: calc(100vh - 36px);
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  position: relative;
  z-index: 3;
}
[data-testid="stMainBlockContainer"]::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(135deg, rgba(255,255,255,0.90), rgba(255,255,255,0.78));
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.92);
  border-radius: 30px;
  box-shadow: 0 30px 80px rgba(12, 40, 34, 0.22);
}
.st-key-map_bg {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: -2 !important;
}
.st-key-map_bg > div { height: 100vh !important; padding: 0 !important; }
.st-key-map_bg iframe, .st-key-map_bg canvas {
  width: 100vw !important;
  height: 100vh !important;
}
section[data-testid="stSidebar"] {
  background: rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(36px) saturate(180%);
  -webkit-backdrop-filter: blur(36px) saturate(180%);
  border-right: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: 0 26px 26px 0;
  box-shadow: 18px 0 60px rgba(12, 40, 34, 0.12);
}
section[data-testid="stSidebar"] > div { background: transparent !important; }
[data-testid="stMetric"] {
  background: rgba(255, 255, 255, 0.74) !important;
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.88) !important;
  border-radius: 20px !important;
  padding: 14px 16px !important;
  box-shadow: 0 12px 30px rgba(15, 40, 35, 0.08);
}
[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255, 255, 255, 0.62) !important;
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.80) !important;
  border-radius: 22px !important;
}
div[data-testid="stDataFrame"] {
  background: transparent !important;
  border-radius: 16px;
  overflow: hidden;
}
h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.02em; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--ink) !important; }
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"] {
    max-width: calc(100vw - 24px);
    margin: 12px;
    padding: 16px 16px 48px;
    border-radius: 24px;
  }
}
</style>
"""
REQUIRED = {
    "station_id",
    "station_name",
    "district",
    "grid_company",
    "operator",
    "lng",
    "lat",
    "piles",
    "price_elec",
    "price_service",
    "price_parking",
    "platform_price",
    "field_price",
    "occupancy",
    "queue",
    "fake_idle",
    "feedback_count",
    "evidence",
}


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    return prepare_data(pd.read_csv(path))


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """统一计算派生指标，上传自己的 CSV 也会走这里。"""
    out = df.copy()
    out["price_deviation"] = (
        (out["field_price"] - out["platform_price"]) / out["platform_price"] * 100
    ).round(1)
    # 按“充 60 度 + 停车 1 小时”估算一次全成本，便于横向比较
    out["full_cost_60"] = (out["field_price"] * 60 + out["price_parking"]).round(1)
    out["effective_supply"] = (out["piles"] * (1 - out["fake_idle"])).round(1)
    return out


def price_color(value: float) -> list[int]:
    if value >= 20:
        return [200, 45, 60, 210]
    if value >= 10:
        return [240, 165, 40, 210]
    return [35, 145, 95, 210]


def make_map(data: pd.DataFrame) -> pdk.Deck:
    map_df = data.copy()
    map_df["color"] = map_df["price_deviation"].apply(price_color)
    map_df["radius"] = (map_df["piles"] * 12).clip(lower=90)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lng, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=float(map_df["lat"].mean()),
            longitude=float(map_df["lng"].mean()),
            zoom=10.3,
            pitch=0,
        ),
        map_style="light",
        tooltip={
            "text": "{station_name}\n电网：{grid_company}\n"
            "平台价：{platform_price} 元/度\n实付价：{field_price} 元/度"
        },
    )


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("### 筛选")
        districts = st.multiselect("区域", sorted(df["district"].unique()), default=None, placeholder="全部")
        grids = st.multiselect("电网", sorted(df["grid_company"].unique()), default=None, placeholder="全部")
        operators = st.multiselect("运营商", sorted(df["operator"].unique()), default=None, placeholder="全部")
        min_dev = st.slider("最低价格偏差（%）", 0, 30, 0, 5)

    view = df.copy()
    if districts:
        view = view[view["district"].isin(districts)]
    if grids:
        view = view[view["grid_company"].isin(grids)]
    if operators:
        view = view[view["operator"].isin(operators)]
    view = view[view["price_deviation"] >= min_dev]
    return view


def page_price_map() -> None:
    df = st.session_state["df"]
    st.title("价格地图")
    st.caption("先看哪里贵、哪里平台价与实付价不一致；点开站点账单看证据。")

    view = st.session_state.get("view", df)
    if view.empty:
        st.warning("当前筛选没有站点，放宽条件再试。")
        return

    st.caption("全屏地图在背景，可拖动/缩放；左侧筛选会同时更新地图和下方清单。")

    row1 = st.columns(2)
    with row1[0]:
        st.metric("站点数", len(view), border=True)
    with row1[1]:
        st.metric("平均价格偏差", f"{view['price_deviation'].mean():.1f}%", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.metric("平均全成本", f"¥{view['full_cost_60'].mean():.0f}", border=True)
    with row2[1]:
        st.metric("平均假空闲率", f"{view['fake_idle'].mean():.1%}", border=True)

    with st.container(border=True):
        st.subheader("差价最大的站点")
        top = (
            view.nlargest(8, "price_deviation")[["station_name", "price_deviation"]]
            .set_index("station_name")
        )
        st.bar_chart(top, horizontal=True, alt="价格偏差最大的站点")

    with st.container(border=True):
        st.subheader("怎么读")
        st.markdown(
            "- 平台价是平台展示价；实付价是现场账单。\n"
            "- 偏差 >0 表示现场更贵。\n"
            "- 核验时间与证据等级见站点账单。\n"
            "- 地图气泡：红 ≥20%，黄 10%—20%，绿 <10%。"
        )

    with st.container(border=True):
        st.subheader("站点价格清单")
        show = view[
            [
                "station_name",
                "district",
                "grid_company",
                "operator",
                "platform_price",
                "field_price",
                "price_deviation",
                "full_cost_60",
                "fake_idle",
            ]
        ].sort_values("price_deviation", ascending=False)
        show = show.assign(fake_idle_pct=(show["fake_idle"] * 100).round(0)).drop(columns=["fake_idle"])
        show = show.reset_index(drop=True)
        st.dataframe(
            show,
            hide_index=True,
            alt="站点平台价、实付价与价格偏差清单",
            column_config={
                "platform_price": st.column_config.NumberColumn("平台价（元/度）", format="%.2f"),
                "field_price": st.column_config.NumberColumn("实付价（元/度）", format="%.2f"),
                "price_deviation": st.column_config.NumberColumn("价格偏差", format="%.1f%%"),
                "full_cost_60": st.column_config.NumberColumn("全成本（60度+停车）", format="¥%.0f"),
                "fake_idle_pct": st.column_config.NumberColumn("假空闲率", format="%.0f%%"),
            },
        )

    st.info(
        "结论：低价不等于低全成本；先看价格偏差大的站，再看它是否还排长队。",
        title="一句话",
    )


def page_station_bill() -> None:
    df = st.session_state["df"]
    st.title("站点账单")
    st.caption("把平台价、现场价、电费/服务费/停车费拆开；价格旁边必须有证据。")

    station = st.selectbox("选择站点", sorted(df["station_name"].unique()))
    row = df.loc[df["station_name"] == station].iloc[0]

    st.subheader(row["station_name"])
    st.caption(f"{row['district']} · {row['operator']} · 桩数 {int(row['piles'])}")
    with st.container(horizontal=True):
        st.badge(f"电网：{row['grid_company']}", color="blue")
        st.badge(f"证据等级：{row['evidence']}", color="green" if row["evidence"] == "A" else "orange")
        st.badge("核验：2026-11-18", color="gray")

    row1 = st.columns(2)
    with row1[0]:
        st.metric("平台价", f"¥{row['platform_price']:.2f}/度", border=True)
    with row1[1]:
        st.metric("实地实付", f"¥{row['field_price']:.2f}/度", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.metric("价格偏差", f"{row['price_deviation']:+.1f}%", border=True)
    with row2[1]:
        st.metric("全成本", f"¥{row['full_cost_60']:.0f}", border=True)

    with st.container(border=True):
        st.subheader("一次充电的钱花在哪")
        bill = pd.DataFrame(
            {
                "项目": ["电费", "服务费", "停车费"],
                "金额": [
                    row["price_elec"] * 60,
                    row["price_service"] * 60,
                    row["price_parking"],
                ],
            }
        )
        st.bar_chart(bill, x="项目", y="金额", alt="电费、服务费、停车费构成")
        st.caption("按充 60 度、停车 1 小时估算；实际以账单为准。")

    with st.container(border=True):
        st.subheader("价格核对")
        check = pd.DataFrame(
            {
                "项目": ["电费（元/度）", "服务费（元/度）", "停车费（元/小时）"],
                "平台展示": [row["price_elec"], row["price_service"], row["price_parking"]],
                "现场实付": [
                    row["price_elec"] * row["field_price"] / row["platform_price"],
                    row["price_service"] * row["field_price"] / row["platform_price"],
                    row["price_parking"],
                ],
            }
        )
        st.dataframe(check, hide_index=True, alt="平台展示与现场实付价格核对")
        st.caption("示例：按总价差等比拆分电费/服务费；真实项目以账单分项为准。")

    st.info(
        f"平台标价 ¥{row['platform_price']:.2f}/度，现场实付 ¥{row['field_price']:.2f}/度，"
        f"偏差 {row['price_deviation']:+.1f}%。证据等级 {row['evidence']}，核验时间 2026-11-18。",
        title="价格结论",
    )

    with st.container(border=True):
        st.subheader(f"最近反馈（{int(row['feedback_count'])} 条）")
        feedback = pd.DataFrame(
            [
                ["价格不符", "平台显示 1.20，现场扫小程序变成 1.65", "A"],
                ["占位", "晚高峰有车充满不走，等了 20 分钟", "B"],
                ["坏桩", "3 号枪无法启动，现场没人处理", "B"],
            ],
            columns=["类型", "内容", "证据"],
        )
        st.dataframe(feedback, hide_index=True, alt="站点最近用户反馈")


def page_sandbox() -> None:
    df = st.session_state["df"]
    st.title("治理沙盘")
    st.caption("调免费宽限、占用费、预约，观察等待、假空闲、有效供给的变化。")

    with st.sidebar:
        st.markdown("### 占位费参数")
        grace = st.slider("免费宽限（分钟）", 0, 60, 30, 5)
        fee = st.slider("超时占用费（元/10分钟）", 1, 10, 3, 1)
        cap = st.slider("单次封顶（元）", 10, 100, 50, 10)
        reservation = st.toggle("启用预约锁位", value=True)

    base_wait = float(df["queue"].mean())
    base_fake = float(df["fake_idle"].mean())
    total_piles = float(df["piles"].sum())

    # 仅用于框架演示的简化公式，后续替换为排队/仿真模型
    grace_effect = max(0, 30 - grace) * 0.0008
    new_fake = max(
        0.02,
        base_fake - fee * 0.012 - (0.04 if reservation else 0) - grace_effect,
    )
    new_wait = max(
        2.0,
        base_wait * (1 - fee * 0.03) - (3 if reservation else 0) - max(0, 30 - grace) * 0.03,
    )
    new_eff = total_piles * (1 - new_fake)
    events = max(0.0, (base_fake - new_fake) * total_piles * 8)
    revenue = min(cap, fee * 6) * events

    row1 = st.columns(2)
    with row1[0]:
        st.metric("平均等待（现状）", f"{base_wait:.1f} 分钟", border=True)
    with row1[1]:
        st.metric("平均等待（方案）", f"{new_wait:.1f} 分钟", f"{new_wait - base_wait:+.1f}", border=True)
    row2 = st.columns(2)
    with row2[0]:
        st.metric("假空闲率", f"{new_fake:.1%}", f"{(new_fake - base_fake) * 100:+.1f}pp", border=True)
    with row2[1]:
        st.metric("有效桩数", f"{new_eff:.0f}", border=True)

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("等待时间对比")
            compare_wait = pd.DataFrame(
                {"方案": ["现状", "方案"], "平均等待": [base_wait, new_wait]}
            )
            st.bar_chart(compare_wait, x="方案", y="平均等待", alt="现状与方案平均等待对比")
    with right:
        with st.container(border=True):
            st.subheader("假空闲率对比")
            compare_idle = pd.DataFrame(
                {"方案": ["现状", "方案"], "假空闲率": [base_fake, new_fake]}
            )
            st.bar_chart(compare_idle, x="方案", y="假空闲率", alt="现状与方案假空闲率对比")

    with st.container(border=True):
        st.subheader("当前假设")
        st.dataframe(
            pd.DataFrame(
                {
                    "参数": ["免费宽限", "占用费", "封顶", "预约", "估算占用费收入/日"],
                    "取值": [f"{grace} 分钟", f"¥{fee}/10分钟", f"¥{cap}", "开" if reservation else "关", f"¥{revenue:.0f}"],
                }
            ),
            hide_index=True,
            alt="占位治理参数与假设",
        )
        st.caption("这是框架演示公式，不是实证结论；真实项目要用到达率、服务时长、占位时长做仿真。")

    st.info(
        f"当前方案：等待从 {base_wait:.1f} 分钟降到 {new_wait:.1f} 分钟，"
        f"假空闲率从 {base_fake:.1%} 降到 {new_fake:.1%}；需用真实数据校准费率和误伤率。",
        title="沙盘结论",
    )


def page_feedback() -> None:
    df = st.session_state["df"]
    st.title("反馈中心")
    st.caption("用户上报价格不符、占位、坏桩、排队；带证据、可审核，才能修正数据。")

    if "feedback" not in st.session_state:
        st.session_state.feedback = [
            ["长沙南站充电站", "价格不符", "平台 1.20，现场小程序 1.65", "A", "2026-11-18"],
            ["五一广场充电站", "占位", "有车充满不走，排队 20 分钟", "B", "2026-11-18"],
            ["星沙服务区充电站", "坏桩", "2 号枪无法启动", "B", "2026-11-17"],
        ]

    rows = st.session_state.feedback
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("反馈总数", len(rows), border=True)
    with c2:
        st.metric("价格类", sum(1 for r in rows if r[1] == "价格不符"), border=True)
    with c3:
        st.metric("待核验", sum(1 for r in rows if r[3] != "A"), border=True)

    with st.form("feedback_form", border=True):
        st.subheader("提交一条反馈")
        c1, c2, c3 = st.columns(3)
        station = c1.selectbox("站点", sorted(df["station_name"].unique()), key="fb_station")
        kind = c2.selectbox("类型", ["价格不符", "占位", "坏桩", "排队", "环境/服务"], key="fb_kind")
        evidence = c3.selectbox("证据", ["A 实地+账单", "B 现场照片", "C 仅文字"], key="fb_evidence")
        content = st.text_area(
            "具体问题",
            placeholder="例如：平台显示 1.20，现场扫码变成 1.65，服务费多 0.4",
            key="fb_content",
        )
        submitted = st.form_submit_button("提交反馈", width="stretch", key="fb_submit")

    if submitted:
        if not content.strip():
            st.error("写点具体问题，别只提交空内容。")
        else:
            rows.append([station, kind, content.strip(), evidence[0], "2026-11-20"])
            st.success("已加入当前会话；接后端后可持久化并进入审核。")

    with st.container(border=True):
        st.subheader("反馈列表")
        st.dataframe(
            pd.DataFrame(rows, columns=["站点", "类型", "内容", "证据", "时间"]),
            hide_index=True,
            alt="用户反馈列表",
        )
        st.caption("演示：反馈只存在当前浏览器会话；刷新页面会回到示例数据。")


def main() -> None:
    st.html(GLASS_CSS)

    st.sidebar.markdown("### 数据")
    uploaded = st.sidebar.file_uploader(
        "上传站点 CSV",
        type=["csv"],
        help="不传就用 20 个长沙示例站点；字段见 README。",
    )
    if uploaded is not None:
        try:
            candidate = pd.read_csv(uploaded)
        except Exception as exc:
            st.sidebar.error(f"读取失败：{exc}")
            candidate = load_data(DATA_PATH)
        missing = REQUIRED - set(candidate.columns)
        if missing:
            st.sidebar.error(f"缺少字段：{', '.join(sorted(missing))}")
            candidate = load_data(DATA_PATH)
        else:
            candidate = prepare_data(candidate)
    else:
        candidate = load_data(DATA_PATH)

    st.session_state["df"] = candidate
    view = sidebar_filters(candidate)
    st.session_state["view"] = view

    map_data = view if not view.empty else candidate
    with st.container(key="map_bg"):
        st.pydeck_chart(
            make_map(map_data),
            height=1000,
            alt="全屏站点价格偏差地图",
        )

    st.sidebar.caption(
        f"当前：{len(candidate)} 个站点 · 示例数据"
        if uploaded is None
        else f"当前：{len(candidate)} 个站点 · 已上传"
    )
    st.sidebar.markdown("---")

    pages = [
        st.Page(page_price_map, title="价格地图", icon=":material/map:", default=True),
        st.Page(page_station_bill, title="站点账单", icon=":material/receipt_long:"),
        st.Page(page_sandbox, title="治理沙盘", icon=":material/tune:"),
        st.Page(page_feedback, title="反馈中心", icon=":material/forum:"),
    ]
    nav = st.navigation(pages, position="sidebar")
    nav.run()


if __name__ == "__main__":
    main()
