"""CMP7227 Healthcare Analytics — interactive executive dashboard.
Run: python -m streamlit run app.py
"""
from pathlib import Path
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Healthcare Analytics | Executive Overview", page_icon="🫀", layout="wide", initial_sidebar_state="collapsed")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "Patients_Data_Cleaned.csv"
NAVY, BLUE, MUTED, GRID = "#082B50", "#2878B5", "#62748A", "#E6EDF4"
CONDITIONS = {
    "Heart attack": ("HadHeartAttack", "#E63946", "♥"),
    "Skin cancer": ("HadSkinCancer", "#8E44AD", "✿"),
    "Stroke": ("HadStroke", "#2878B5", "✚"),
    "COPD": ("HadCOPD", "#16A085", "◉"),
}
AGE_ORDER = ["Age 18 to 24", "Age 25 to 29", "Age 30 to 34", "Age 35 to 39", "Age 40 to 44", "Age 45 to 49", "Age 50 to 54", "Age 55 to 59", "Age 60 to 64", "Age 65 to 69", "Age 70 to 74", "Age 75 to 79", "Age 80 or older"]
HEALTH_ORDER = ["Excellent", "Very good", "Good", "Fair", "Poor"]
SMOKE_ORDER = ["Never smoked", "Former smoker", "Current smoker - now smokes some days", "Current smoker - now smokes every day"]

st.markdown("""<style>
.stApp {background:#F5F8FC;color:#14243B}
.block-container {padding-top:1.3rem;padding-bottom:2.5rem;max-width:1580px}
h1,h2,h3 {color:#14243B}
.hero {background:linear-gradient(110deg,#06294D,#084578);padding:25px 30px;border-radius:16px;color:white;margin-bottom:16px;box-shadow:0 8px 24px #092C5015}
.hero .eyebrow {font-size:12px;letter-spacing:2px;font-weight:750;color:#C8E4F9}
.hero h1 {font-size:34px;line-height:1.16;color:white;margin:7px 0}
.hero .sub {color:#C9DCEE;font-size:14px}
.metric-card {border-radius:14px;background:white;padding:18px 20px 15px;border:1px solid #E4EBF3;min-height:138px;box-shadow:0 3px 12px #183D6010}
.metric-label {font-size:15px;font-weight:750;color:#24334A}
.metric-number {font-size:32px;font-weight:850;margin:8px 0 0;line-height:1.1}
.metric-foot {font-size:13px;color:#68788D;margin-top:4px}
.chart-heading {font-size:17px;font-weight:800;color:#1B2D43;margin:6px 0 0}
.chart-desc {font-size:12px;color:#65758A;margin-bottom:6px}
.section-heading {font-size:20px;font-weight:850;margin:12px 0}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px!important;background:white!important;border-color:#E5ECF3!important;box-shadow:0 3px 14px #1436530A}
div[data-testid="stMultiSelect"] label, div[data-testid="stSelectbox"] label {font-weight:700;color:#27394E}
.small-note {font-size:12px;color:#64748B}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading cleaned patient data…")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    required = {"State", "Sex", "AgeCategory", "GeneralHealth", "SmokerStatus", "BMI"} | {v[0] for v in CONDITIONS.values()}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Required columns missing: {', '.join(missing)}")
    for col, _, _ in CONDITIONS.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["BMI"] = pd.to_numeric(df["BMI"], errors="coerce")
    df["BMI category"] = pd.cut(df["BMI"], bins=[float("-inf"), 18.5, 25, 30, float("inf")], labels=["Underweight", "Healthy weight", "Overweight", "Obesity"], right=False)
    return df

if not DATA_PATH.exists():
    st.error("Dataset missing. Put **Patients_Data_Cleaned.csv** in the **data** folder, then refresh this page.")
    st.code("healthcare-dashboard/\n  app.py\n  requirements.txt\n  data/\n    Patients_Data_Cleaned.csv", language="text")
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

st.markdown('<div class="hero"><div class="eyebrow">HEALTHCARE ANALYTICS · CMP7227</div><h1>Executive Overview <span style="color:#17D6E5">Dashboard</span></h1><div class="sub">Explore patient records, reported health conditions and demographic patterns · Interactive exploratory analysis</div></div>', unsafe_allow_html=True)

# Widgets use stable keys so the reset button clears every filter in one rerun.
filter_keys = ["age_filter", "sex_filter", "state_filter", "health_filter", "smoke_filter", "bmi_filter"]
def reset_filters():
    for key in filter_keys:
        st.session_state[key] = []

with st.container(border=True):
    f1, f2, f3, f4, f5, f6, f7 = st.columns([1.1, .85, 1.25, 1.1, 1.25, 1.1, .75], vertical_alignment="bottom")
    with f1: ages = st.multiselect("Age category", [a for a in AGE_ORDER if a in set(df["AgeCategory"].dropna())], key="age_filter", placeholder="All ages")
    with f2: sexes = st.multiselect("Sex", sorted(df["Sex"].dropna().unique().tolist()), key="sex_filter", placeholder="All sexes")
    with f3: states = st.multiselect("State", sorted(df["State"].dropna().unique().tolist()), key="state_filter", placeholder="All states")
    with f4: healths = st.multiselect("General health", [h for h in HEALTH_ORDER if h in set(df["GeneralHealth"].dropna())], key="health_filter", placeholder="All levels")
    with f5: smokers = st.multiselect("Smoking status", sorted(df["SmokerStatus"].dropna().unique().tolist()), key="smoke_filter", placeholder="All statuses")
    with f6: bmis = st.multiselect("BMI category", ["Underweight", "Healthy weight", "Overweight", "Obesity"], key="bmi_filter", placeholder="All categories")
    with f7: st.button("↻ Reset", on_click=reset_filters, use_container_width=True)

filtered = df
for column, selected in [("AgeCategory", ages), ("Sex", sexes), ("State", states), ("GeneralHealth", healths), ("SmokerStatus", smokers), ("BMI category", bmis)]:
    if selected:
        filtered = filtered[filtered[column].isin(selected)]
n = len(filtered)
st.caption(f"**{n:,}** of **{len(df):,}** records selected ({n / len(df):.1%}). All charts and cards use the same filtered records. Blank filters mean ‘all’. ")
if n == 0:
    st.warning("No records match these filters. Select broader categories or click Reset.")
    st.stop()

# Condition counts use valid 0/1 answers as denominators, not silently treating missing as 'No'.
def condition_stats(frame: pd.DataFrame, column: str) -> tuple[int, int, float]:
    valid = frame[column].isin([0, 1])
    denom = int(valid.sum())
    cases = int((frame[column] == 1).sum())
    return cases, denom, 100 * cases / denom if denom else 0.0

cards = st.columns(4)
for box, (label, (column, color, symbol)) in zip(cards, CONDITIONS.items()):
    count, denominator, pct = condition_stats(filtered, column)
    with box:
        st.markdown(f'<div class="metric-card" style="border-top:5px solid {color}"><div class="metric-label"><span style="color:{color};font-size:19px">{symbol}</span> &nbsp;{html.escape(label)}</div><div class="metric-number" style="color:{color}">{count:,}</div><div class="metric-foot"><b>{pct:.2f}%</b> of {denominator:,} valid responses</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-heading">Population and condition overview</div>', unsafe_allow_html=True)
focus = st.selectbox("Condition for demographic comparison", list(CONDITIONS), index=0, help="Changes the condition-by-sex chart. All other charts continue to reflect shared filters.")
focus_col, focus_color, _ = CONDITIONS[focus]

def style_chart(fig: go.Figure, height=315, percent=False):
    fig.update_layout(height=height, margin=dict(l=8, r=10, t=15, b=22), paper_bgcolor="white", plot_bgcolor="white", font=dict(family="Arial, sans-serif", color="#334155", size=12), showlegend=False, hoverlabel=dict(bgcolor="white", font_size=12))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#D7E2EC")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    if percent:
        fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    return fig

def chart_card(title, desc, fig):
    with st.container(border=True):
        st.markdown(f'<div class="chart-heading">{html.escape(title)}</div><div class="chart-desc">{html.escape(desc)}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False, "responsive":True})

left, mid, right = st.columns(3, gap="medium")
with left:
    records = []
    for label, (column, color, _) in CONDITIONS.items():
        count, den, rate = condition_stats(filtered, column)
        records.append({"Condition":label, "Percentage":rate, "Cases":count, "Valid":den, "Colour":color})
    summary = pd.DataFrame(records)
    fig = px.bar(summary, x="Condition", y="Percentage", color="Condition", color_discrete_map={k:v[1] for k,v in CONDITIONS.items()}, custom_data=["Cases", "Valid"], text="Percentage")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", hovertemplate="%{x}<br>Reported: %{customdata[0]:,}<br>Valid responses: %{customdata[1]:,}<br>Percentage: %{y:.2f}%<extra></extra>")
    style_chart(fig, percent=True)
    fig.update_yaxes(range=[0, max(5, summary["Percentage"].max()*1.28)])
    chart_card("Reported conditions", "Percentage of valid responses for each condition", fig)
with mid:
    age = filtered.groupby("AgeCategory", observed=True).size().reindex(AGE_ORDER, fill_value=0).reset_index(name="Records")
    age["Age label"] = age["AgeCategory"].str.replace("Age ", "", regex=False).str.replace(" or older", "+", regex=False)
    fig = px.bar(age, x="Age label", y="Records", color_discrete_sequence=[BLUE], custom_data=["AgeCategory"], text="Records")
    fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside", hovertemplate="%{customdata[0]}<br>Records: %{y:,}<extra></extra>")
    style_chart(fig)
    fig.update_xaxes(tickangle=-45)
    chart_card("Age distribution", "Number of selected records in each age group", fig)
with right:
    valid = filtered[filtered[focus_col].isin([0,1])]
    grouped = valid.groupby("Sex", dropna=False).agg(Valid=(focus_col,"size"), Cases=(focus_col,"sum")).reset_index()
    grouped["Rate"] = grouped["Cases"].div(grouped["Valid"]).mul(100)
    fig = px.bar(grouped, x="Sex", y="Rate", color="Sex", color_discrete_map={"Male":"#2878B5", "Female":"#E781AF"}, custom_data=["Cases","Valid"], text="Rate")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", hovertemplate="%{x}<br>Reported: %{customdata[0]:,}<br>Valid: %{customdata[1]:,}<br>Percentage: %{y:.2f}%<extra></extra>")
    style_chart(fig, percent=True)
    fig.update_yaxes(range=[0, max(5, grouped["Rate"].max()*1.28)] if not grouped.empty else [0,5])
    chart_card(f"{focus} by sex", "Within-sex percentage (not share of total cases)", fig)

left, mid, right = st.columns(3, gap="medium")
with left:
    top = filtered["State"].value_counts().head(10).sort_values().rename_axis("State").reset_index(name="Records")
    fig = px.bar(top, x="Records", y="State", orientation="h", color_discrete_sequence=[BLUE], text="Records")
    fig.update_traces(texttemplate="%{x:,}", textposition="outside", hovertemplate="%{y}<br>Records: %{x:,}<extra></extra>")
    style_chart(fig)
    fig.update_xaxes(range=[0, max(1, top["Records"].max()*1.22)])
    fig.update_yaxes(showgrid=False)
    chart_card("Top 10 states", "Record counts, not population-adjusted rates", fig)
with mid:
    counts = filtered["GeneralHealth"].value_counts().reindex(HEALTH_ORDER, fill_value=0).rename_axis("Health").reset_index(name="Records")
    counts["Percentage"] = counts["Records"] / n * 100
    fig = px.bar(counts, x="Health", y="Percentage", color="Health", color_discrete_map={"Excellent":"#0F9B8E","Very good":"#50B99E","Good":"#E8BE5C","Fair":"#F09C59","Poor":"#E45B64"}, custom_data=["Records"], text="Percentage")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", hovertemplate="%{x}<br>Records: %{customdata[0]:,}<br>Share: %{y:.2f}%<extra></extra>")
    style_chart(fig, percent=True)
    fig.update_yaxes(range=[0,max(5,counts["Percentage"].max()*1.26)])
    fig.update_xaxes(tickangle=-25)
    chart_card("General health status", "Percentage of selected records", fig)
with right:
    smoke = filtered["SmokerStatus"].value_counts().reindex(SMOKE_ORDER, fill_value=0).rename_axis("Smoking").reset_index(name="Records")
    smoke["Percentage"] = smoke["Records"] / n * 100
    smoke["Short"] = ["Never", "Former", "Some days", "Every day"]
    fig = px.bar(smoke, x="Short", y="Percentage", color="Short", color_discrete_map={"Never":"#16A085","Former":"#66BFC4","Some days":"#F3AA66","Every day":"#E76F73"}, custom_data=["Smoking","Records"], text="Percentage")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", hovertemplate="%{customdata[0]}<br>Records: %{customdata[1]:,}<br>Share: %{y:.2f}%<extra></extra>")
    style_chart(fig, percent=True)
    fig.update_yaxes(range=[0,max(5,smoke["Percentage"].max()*1.26)])
    chart_card("Smoking status", "Percentage of selected records", fig)

with st.expander("Data definitions, quality and limitations", expanded=False):
    st.markdown("""
    **Source:** `Patients_Data_Cleaned.csv` (user-provided cleaned dataset). Original survey publisher, sampling weights and collection year have not been independently verified.

    **Condition percentages:** number of rows coded `1` divided by rows coded `0` or `1` for that condition. Conditions can overlap; percentages need not sum to 100%.

    **Age, health and smoking charts:** record distributions, not longitudinal trends. **State chart:** number of records, not a disease-risk ranking. **Sex comparison:** percentage within each sex, not percentage of all cases.

    **BMI categories:** underweight <18.5; healthy 18.5–<25; overweight 25–<30; obesity ≥30. BMI is a screening measure, not a diagnosis.

    **Interpretation:** descriptive, unweighted, observational data. Filters change the analysis population; associations are not causal. Small filtered subgroups can produce unstable percentages. Do not infer representativeness of a state or the country.
    """)
    st.dataframe(pd.DataFrame({"Field":list(CONDITIONS),"Dataset column":[x[0] for x in CONDITIONS.values()]}), hide_index=True, use_container_width=True)
    st.write(f"Selected records: **{n:,}** | Total records: **{len(df):,}** | Dataset columns: **{df.shape[1] - 1}** (plus derived BMI category)")

st.download_button("⬇ Download filtered data (CSV)", data=filtered.to_csv(index=False).encode("utf-8"), file_name="healthcare_filtered_records.csv", mime="text/csv")
st.caption("CMP7227 · Interactive exploratory dashboard · Charts powered by Plotly and Streamlit")
