from __future__ import annotations

import json
import os
from typing import Dict, List
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from vitaledge_core import estimate_risk, infer_conflict, load_output_data, load_raw_data, risk_color

st.set_page_config(page_title="VitalEdge+ Command Center", layout="wide", initial_sidebar_state="expanded")


@st.cache_data(show_spinner=False)
def load_raw() -> Dict[str, pd.DataFrame]:
    return load_raw_data()


@st.cache_data(show_spinner=False)
def load_outputs() -> Dict[str, pd.DataFrame]:
    return load_output_data()


def _api_base_url() -> str:
    # Streamlit Community Cloud secrets take priority, then env var, then localhost.
    try:
        url = st.secrets.get("VITALEDGE_API_BASE_URL", None)
        if url:
            return str(url).rstrip("/")
    except Exception:
        pass
    return os.getenv("VITALEDGE_API_BASE_URL", "http://localhost:8000").rstrip("/")


@st.cache_data(show_spinner=False, ttl=30)
def get_api_health() -> Dict[str, str]:
    base_url = _api_base_url()
    try:
        with urlopen(f"{base_url}/health", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {"label": "Online", "detail": payload.get("status", "ok"), "url": base_url}
    except (URLError, TimeoutError, ValueError):
        return {"label": "Offline", "detail": "unreachable", "url": base_url}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
            --bg: #f4efe7;
            --surface: rgba(255,255,255,0.72);
            --surface-strong: rgba(255,255,255,0.92);
            --ink: #14213d;
            --muted: #5c677d;
            --accent: #0f766e;
            --accent-soft: #d8f3dc;
            --shadow: 0 24px 60px rgba(20, 33, 61, 0.10);
            --border: rgba(20, 33, 61, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15,118,110,0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(196,69,54,0.12), transparent 24%),
                linear-gradient(180deg, #f8f4ee 0%, #efe7da 100%);
            color: var(--ink);
            font-family: 'IBM Plex Sans', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.03em;
        }

        [data-testid="stSidebar"] {
            background: rgba(20, 33, 61, 0.94);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        .hero-shell {
            background: linear-gradient(135deg, rgba(20,33,61,0.96), rgba(15,118,110,0.92));
            border-radius: 28px;
            padding: 2.4rem 2.6rem;
            box-shadow: var(--shadow);
            color: #f8fafc;
            overflow: hidden;
            position: relative;
            margin-bottom: 1.25rem;
        }

        .hero-shell::after {
            content: '';
            position: absolute;
            width: 320px;
            height: 320px;
            right: -100px;
            top: -120px;
            border-radius: 999px;
            background: rgba(255,255,255,0.09);
        }

        .hero-kicker {
            text-transform: uppercase;
            font-size: 0.76rem;
            letter-spacing: 0.2em;
            opacity: 0.76;
            margin-bottom: 0.7rem;
        }

        .hero-title {
            font-size: 3rem;
            line-height: 0.96;
            margin: 0;
            max-width: 9ch;
        }

        .hero-copy {
            max-width: 58ch;
            margin-top: 1rem;
            font-size: 1rem;
            color: rgba(248,250,252,0.82);
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.5rem;
        }

        .glass-card {
            background: var(--surface);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            border-radius: 22px;
            padding: 1.2rem 1.25rem;
            backdrop-filter: blur(14px);
        }

        .metric-card {
            background: var(--surface-strong);
            border-radius: 20px;
            padding: 1.1rem 1.2rem;
            border: 1px solid var(--border);
            box-shadow: 0 18px 42px rgba(20, 33, 61, 0.06);
        }

        .metric-label {
            font-size: 0.78rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .metric-value {
            font-size: 2rem;
            font-family: 'Space Grotesk', sans-serif;
            margin-top: 0.4rem;
            color: var(--ink);
        }

        .metric-delta {
            color: var(--accent);
            font-size: 0.9rem;
            margin-top: 0.3rem;
        }

        .section-title {
            font-size: 1.35rem;
            margin-top: 0.3rem;
            margin-bottom: 0.9rem;
        }

        .signal-pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #d8f3dc;
            color: #0f766e;
            font-size: 0.82rem;
            font-weight: 600;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .status-banner {
            border-radius: 20px;
            padding: 1rem 1.1rem;
            color: white;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 2.2rem;
            }
            .hero-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: List[dict]) -> None:
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        column.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{metric['label']}</div>
                <div class="metric-value">{metric['value']}</div>
                <div class="metric-delta">{metric['delta']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def style_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color="#14213d"),
        margin=dict(l=12, r=12, t=48, b=12),
    )
    return fig


def render_hero(outputs: Dict[str, pd.DataFrame]) -> None:
    kpis = outputs["kpis"]
    model = outputs["model"].iloc[0]
    quality = outputs["quality"].iloc[0]
    patient_count = len(outputs["patients"])
    pass_rate = int(kpis["Pass"].sum()) / max(1, len(kpis))

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">Clinical Risk Intelligence</div>
            <h1 class="hero-title">VitalEdge+ Command Center</h1>
            <div class="hero-copy">
                A deployable decision-support frontend for allergy risk surveillance, model monitoring, and prescribing simulation.
                This version turns the project outputs into an operational console instead of a default analytics page.
            </div>
            <div class="hero-grid">
                <div class="glass-card"><strong>{patient_count}</strong><br/>patients across the current synthetic cohort</div>
                <div class="glass-card"><strong>{model['Model_AUC_ROC']:.3f}</strong><br/>AUC-ROC on the current benchmark</div>
                <div class="glass-card"><strong>{quality['Data_Quality_Score']:.1f}</strong><br/>data quality score with monitored KPI coverage</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(
        [
            {"label": "KPI pass rate", "value": f"{pass_rate * 100:.0f}%", "delta": f"{int(kpis['Pass'].sum())} of {len(kpis)} KPIs on target"},
            {"label": "Model F1", "value": f"{model['Model_F1']:.3f}", "delta": f"threshold {model['Decision_Threshold']:.2f}"},
            {"label": "Explainability", "value": f"{model['Explanation_Coverage_High_Risk'] * 100:.0f}%", "delta": "coverage on high-risk outcomes"},
            {"label": "Data quality", "value": f"{quality['Data_Quality_Score']:.1f}", "delta": "completeness, consistency, referential integrity"},
        ]
    )


def draw_overview(outputs: Dict[str, pd.DataFrame]) -> None:
    render_hero(outputs)

    kpis = outputs["kpis"].copy()
    doctors = outputs["doctors"].copy()
    patients = outputs["patients"].copy()

    left, right = st.columns((1.3, 1))
    with left:
        st.markdown('<div class="section-title">Performance against PRD targets</div>', unsafe_allow_html=True)
        kpi_fig = px.bar(
            kpis,
            x="Value",
            y="KPI",
            color="Pass",
            orientation="h",
            text="Target",
            color_discrete_map={True: "#0f766e", False: "#c44536"},
        )
        kpi_fig.update_traces(texttemplate="Target %{text}", textposition="outside")
        kpi_fig.update_layout(showlegend=False, xaxis_title="Measured value", yaxis_title="")
        st.plotly_chart(style_figure(kpi_fig), use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Current risk mix</div>', unsafe_allow_html=True)
        band_counts = patients["ABS_Risk_Band"].value_counts().rename_axis("Risk Band").reset_index(name="Patients")
        donut = px.pie(
            band_counts,
            names="Risk Band",
            values="Patients",
            hole=0.62,
            color="Risk Band",
            color_discrete_map={"LOW": "#2f855a", "MODERATE": "#ba8f2a", "HIGH": "#dd6b20", "CRITICAL": "#c44536"},
        )
        donut.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_figure(donut), use_container_width=True)

    left, right = st.columns((1.1, 1.2))
    with left:
        st.markdown('<div class="section-title">Highest exposure clinicians</div>', unsafe_allow_html=True)
        top_doctors = doctors.sort_values("Composite_Risk_Score", ascending=False).head(8)
        doctor_fig = px.bar(
            top_doctors,
            x="Composite_Risk_Score",
            y="Doctor_ID",
            color="Risk_Tier",
            orientation="h",
            color_discrete_map={"GREEN": "#2f855a", "AMBER": "#dd6b20", "RED": "#c44536"},
        )
        doctor_fig.update_layout(showlegend=False, xaxis_title="Composite risk score", yaxis_title="")
        st.plotly_chart(style_figure(doctor_fig), use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Patient signal landscape</div>', unsafe_allow_html=True)
        scatter = px.scatter(
            patients,
            x="IgE_Level_Avg",
            y="Allergy_Burden_Score",
            color="Cluster_Label",
            size="Active_Allergen_Class_Count",
            hover_data=["Patient_ID", "Age", "Comorbidity_Count", "ABS_Risk_Band"],
        )
        scatter.update_layout(xaxis_title="Average IgE", yaxis_title="Allergy burden score")
        st.plotly_chart(style_figure(scatter), use_container_width=True)


def draw_patient_console(raw: Dict[str, pd.DataFrame], outputs: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">Patient Safety Console</div>', unsafe_allow_html=True)
    intel = outputs["patients"].copy()
    patient_ids = sorted(intel["Patient_ID"].astype(str).unique())
    patient_id = st.selectbox("Select patient", patient_ids)

    patient_row = intel[intel["Patient_ID"].astype(str) == patient_id].iloc[0]
    allergies = raw["allergies"][raw["allergies"]["Patient_ID"].astype(str) == patient_id].copy()
    prescriptions = raw["prescriptions"][raw["prescriptions"]["Patient_ID"].astype(str) == patient_id].copy()

    banner_color = {
        "LOW": "linear-gradient(135deg, #2f855a, #38a169)",
        "MODERATE": "linear-gradient(135deg, #ba8f2a, #dd6b20)",
        "HIGH": "linear-gradient(135deg, #dd6b20, #c05621)",
        "CRITICAL": "linear-gradient(135deg, #9b2c2c, #c44536)",
    }.get(str(patient_row.get("ABS_Risk_Band", "LOW")), "linear-gradient(135deg, #0f766e, #2563eb)")

    st.markdown(
        f"""
        <div class="status-banner" style="background: {banner_color};">
            {patient_id} is classified as {patient_row['ABS_Risk_Band']} risk with ABS {patient_row['Allergy_Burden_Score']:.1f}. Cluster: {patient_row['Cluster_Label']}.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(
        [
            {"label": "ABS score", "value": f"{patient_row['Allergy_Burden_Score']:.1f}", "delta": f"band {patient_row['ABS_Risk_Band']}"},
            {"label": "IgE average", "value": f"{patient_row['IgE_Level_Avg']:.1f}", "delta": "lab-derived immunology signal"},
            {"label": "Active allergen classes", "value": f"{int(patient_row['Active_Allergen_Class_Count'])}", "delta": f"reaction rate {patient_row['Reaction_Rate']:.2f}"},
            {"label": "Comorbidities", "value": f"{int(patient_row['Comorbidity_Count'])}", "delta": f"cluster {int(patient_row['Cluster_ID'])}"},
        ]
    )

    left, right = st.columns((1.1, 0.9))
    with left:
        st.markdown('<div class="section-title">Allergy profile</div>', unsafe_allow_html=True)
        allergy_view = allergies[["Allergen_Name", "Allergen_Class", "Severity", "Is_Current", "Reaction_Type"]].copy()
        allergy_view = allergy_view.sort_values(["Is_Current", "Severity"], ascending=[False, False])
        st.dataframe(allergy_view, use_container_width=True, hide_index=True)

    with right:
        st.markdown('<div class="section-title">Risk component balance</div>', unsafe_allow_html=True)
        component_frame = pd.DataFrame(
            {
                "Component": ["Severity", "Allergen count", "Reaction history", "Lab marker"],
                "Score": [
                    patient_row["Severity_Component"],
                    patient_row["Allergen_Count_Component"],
                    patient_row["Reaction_History_Component"],
                    patient_row["Lab_Marker_Component"],
                ],
            }
        )
        radar = go.Figure()
        radar.add_trace(
            go.Scatterpolar(
                r=component_frame["Score"],
                theta=component_frame["Component"],
                fill="toself",
                line=dict(color="#0f766e", width=3),
                fillcolor="rgba(15, 118, 110, 0.24)",
                name="Patient profile",
            )
        )
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(style_figure(radar), use_container_width=True)

    st.markdown('<div class="section-title">Recent prescriptions</div>', unsafe_allow_html=True)
    rx_view = prescriptions[["Prescription_ID", "Medicine_Name", "Allergen_Class", "Conflict_Detected", "Override_Issued", "Prescription_Date"]].copy()
    rx_view = rx_view.sort_values("Prescription_Date", ascending=False).head(20)
    st.dataframe(rx_view, use_container_width=True, hide_index=True)


def draw_simulator(raw: Dict[str, pd.DataFrame], outputs: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">Prescribing What-If Simulator</div>', unsafe_allow_html=True)
    intel = outputs["patients"].copy()
    medicines = raw["medicines"].copy()

    left, right = st.columns(2)
    patient_id = left.selectbox("Patient", sorted(intel["Patient_ID"].astype(str).unique()), key="sim_patient")
    medicine_choice = right.selectbox(
        "Medicine",
        medicines.apply(lambda row: f"{row['Medicine_ID']} | {row['Medicine_Name']} | {row['Allergen_Class']}", axis=1).tolist(),
    )
    medicine_id = medicine_choice.split("|")[0].strip()
    medicine_row = medicines[medicines["Medicine_ID"].astype(str) == medicine_id].iloc[0]

    if st.button("Run safety simulation", type="primary", use_container_width=True):
        patient_row = intel[intel["Patient_ID"].astype(str) == patient_id].iloc[0]
        conflict, reason = infer_conflict(patient_id, medicine_id, raw)
        requires_check = str(medicine_row.get("Requires_Allergy_Check", "")).strip().lower() in ["true", "1", "yes"]
        risk = estimate_risk(float(patient_row["Allergy_Burden_Score"]), conflict, requires_check)

        alternative_pool = medicines[
            (medicines["Allergen_Class"].astype(str) != str(medicine_row.get("Allergen_Class", "")))
            & (medicines["Requires_Allergy_Check"].astype(str).str.lower().isin(["false", "0", "no"]))
        ]
        alternative = alternative_pool.sample(1, random_state=42).iloc[0] if not alternative_pool.empty else None

        result_left, result_right = st.columns((1, 1))
        with result_left:
            st.markdown(
                f"""
                <div class="glass-card">
                    <span class="signal-pill">Conflict: {conflict}</span>
                    <span class="signal-pill">Requires allergy check: {'Yes' if requires_check else 'No'}</span>
                    <h3 style="margin-top: 0.9rem;">{medicine_row['Medicine_Name']}</h3>
                    <p style="color:#5c677d; margin-bottom:0.6rem;">{reason}</p>
                    <p style="font-size:2.4rem; font-family:'Space Grotesk', sans-serif; color:{risk_color(conflict)}; margin:0;">{risk * 100:.1f}%</p>
                    <p style="margin-top:0.4rem; color:#5c677d;">Estimated medication risk score for the selected patient.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with result_right:
            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=risk * 100,
                    number={"suffix": "%", "font": {"size": 38}},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": risk_color(conflict)},
                        "steps": [
                            {"range": [0, 25], "color": "#d8f3dc"},
                            {"range": [25, 50], "color": "#f6e7b0"},
                            {"range": [50, 75], "color": "#f7c59f"},
                            {"range": [75, 100], "color": "#f3b0a9"},
                        ],
                    },
                    title={"text": "Simulation risk gauge"},
                )
            )
            st.plotly_chart(style_figure(gauge), use_container_width=True)

        explanation_col, alternative_col = st.columns((1.1, 0.9))
        with explanation_col:
            st.markdown('<div class="section-title">Representative explanation drivers</div>', unsafe_allow_html=True)
            explanation_rows = outputs["explanations"].head(6).copy()
            feature_fig = px.bar(
                explanation_rows,
                x="Contribution",
                y="Feature",
                color="Contribution",
                color_continuous_scale=["#c44536", "#f4efe7", "#0f766e"],
                orientation="h",
            )
            feature_fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Contribution")
            st.plotly_chart(style_figure(feature_fig), use_container_width=True)

        with alternative_col:
            st.markdown('<div class="section-title">Suggested alternative</div>', unsafe_allow_html=True)
            if alternative is None:
                st.warning("No low-check alternative exists in the current medicine catalog.")
            else:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div class="metric-label">Recommended swap</div>
                        <div class="metric-value" style="font-size:1.5rem;">{alternative['Medicine_Name']}</div>
                        <p style="margin-top:0.6rem; color:#5c677d;">Medicine ID: {alternative['Medicine_ID']}</p>
                        <p style="margin-top:0.2rem; color:#5c677d;">Class: {alternative['Allergen_Class']}</p>
                        <p style="margin-top:0.2rem; color:#5c677d;">Requires allergy check: {alternative['Requires_Allergy_Check']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def draw_doctor_profile(outputs: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">Doctor Risk Profile</div>', unsafe_allow_html=True)
    doctors = outputs["doctors"].copy().sort_values("Composite_Risk_Score", ascending=False)

    top = doctors.head(3)
    render_metric_cards(
        [
            {"label": "Highest risk clinician", "value": str(top.iloc[0]["Doctor_ID"]), "delta": f"score {top.iloc[0]['Composite_Risk_Score']:.2f}"},
            {"label": "Mean override rate", "value": f"{doctors['Override_Rate_Pct'].mean():.1f}%", "delta": "across monitored prescribers"},
            {"label": "Mean reaction rate", "value": f"{doctors['Reaction_Rate_Pct'].mean():.1f}%", "delta": "post-override outcomes"},
            {"label": "Amber tier share", "value": f"{doctors['Risk_Tier'].eq('AMBER').mean() * 100:.0f}%", "delta": "current profile distribution"},
        ]
    )

    left, right = st.columns((1.1, 0.9))
    with left:
        scatter = px.scatter(
            doctors,
            x="Conflict_Rate_Pct",
            y="Override_Rate_Pct",
            size="Composite_Risk_Score",
            color="Risk_Tier",
            hover_data=["Doctor_ID", "Reaction_Rate_Pct", "high_risk_count"],
            color_discrete_map={"GREEN": "#2f855a", "AMBER": "#dd6b20", "RED": "#c44536"},
        )
        scatter.update_layout(xaxis_title="Conflict rate %", yaxis_title="Override rate %")
        st.plotly_chart(style_figure(scatter), use_container_width=True)

    with right:
        bar = px.bar(
            doctors.head(12),
            x="Doctor_ID",
            y="Composite_Risk_Score",
            color="Risk_Tier",
            color_discrete_map={"GREEN": "#2f855a", "AMBER": "#dd6b20", "RED": "#c44536"},
        )
        bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Composite score")
        st.plotly_chart(style_figure(bar), use_container_width=True)

    st.dataframe(
        doctors[["Doctor_ID", "total_prescriptions", "Conflict_Rate_Pct", "Override_Rate_Pct", "Reaction_Rate_Pct", "high_risk_count", "Composite_Risk_Score", "Risk_Tier"]],
        use_container_width=True,
        hide_index=True,
    )


def draw_cluster_analytics(outputs: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">Cluster Analytics</div>', unsafe_allow_html=True)
    patients = outputs["patients"].copy()
    clusters = outputs["clusters"].copy()

    left, right = st.columns((1.15, 0.85))
    with left:
        scatter = px.scatter(
            patients,
            x="Age",
            y="Allergy_Burden_Score",
            color="Cluster_Label",
            size="IgE_Level_Avg",
            hover_data=["Patient_ID", "Comorbidity_Count", "ABS_Risk_Band"],
        )
        scatter.update_layout(xaxis_title="Age", yaxis_title="Allergy burden score")
        st.plotly_chart(style_figure(scatter), use_container_width=True)

    with right:
        cluster_bar = px.bar(
            clusters.sort_values("Avg_ABS", ascending=False),
            x="Cluster_Label",
            y="Avg_ABS",
            color="Avg_Allergen_Count",
            color_continuous_scale=["#d8f3dc", "#0f766e"],
        )
        cluster_bar.update_layout(xaxis_title="", yaxis_title="Average ABS", coloraxis_showscale=False)
        st.plotly_chart(style_figure(cluster_bar), use_container_width=True)

    st.dataframe(clusters, use_container_width=True, hide_index=True)


def draw_quality_monitor(outputs: Dict[str, pd.DataFrame]) -> None:
    st.plotly_chart(style_figure(line), use_container_width=True)
    quality = outputs["quality"].iloc[0]
    model = outputs["model"].iloc[0]
    kpis = outputs["kpis"].copy()

    render_metric_cards(
        [
            {"label": "Completeness", "value": f"{quality['Completeness_Score']:.1f}", "delta": "source table coverage"},
            {"label": "Consistency", "value": f"{quality['Consistency_Score']:.1f}", "delta": "duplicate and schema checks"},
            {"label": "Referential integrity", "value": f"{quality['Referential_Integrity_Score']:.1f}", "delta": "cross-table ID validation"},
            {"label": "AUC-ROC", "value": f"{model['Model_AUC_ROC']:.3f}", "delta": f"{model['Model_Name']} benchmark"},
        ]
    )

    left, right = st.columns(2)
    with left:
        metric_series = pd.DataFrame(
            {
                "Metric": ["F1", "Precision", "Recall", "AUC-ROC"],
                "Value": [model["Model_F1"], model["Model_Precision"], model["Model_Recall"], model["Model_AUC_ROC"]],
            }
        )
        line = px.line(metric_series, x="Metric", y="Value", markers=True)
        line.update_traces(line=dict(color="#0f766e", width=4), marker=dict(size=12))
        line.update_layout(yaxis_range=[0, 1.05], xaxis_title="", yaxis_title="Score")
        st.plotly_chart(style_figure(line), width="stretch")

    with right:
        pass_mix = kpis["Pass"].value_counts().rename_axis("Pass").reset_index(name="Count")
        mix = px.bar(pass_mix, x="Pass", y="Count", color="Pass", color_discrete_map={True: "#0f766e", False: "#c44536"})
        mix.update_layout(showlegend=False, xaxis_title="KPI status", yaxis_title="Count")
        st.plotly_chart(style_figure(mix), use_container_width=True)

    st.dataframe(kpis, use_container_width=True, hide_index=True)


inject_styles()

try:
    raw_data = load_raw()
    output_data = load_outputs()
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.sidebar.markdown("## VitalEdge+")
st.sidebar.caption("Clinical allergy intelligence workspace")
api_health = get_api_health()
st.sidebar.markdown(f"API status: **{api_health['label']}**")
st.sidebar.caption(f"{api_health['url']} · {api_health['detail']}")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Patient Safety Console",
        "Prescribing Simulator",
        "Doctor Risk Profile",
        "Cluster Analytics",
        "Quality Monitor",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("Deploy target: Streamlit frontend + FastAPI backend")
st.sidebar.markdown("Recommended runtime: Docker Compose")

if page == "Overview":
    draw_overview(output_data)
elif page == "Patient Safety Console":
    draw_patient_console(raw_data, output_data)
elif page == "Prescribing Simulator":
    draw_simulator(raw_data, output_data)
elif page == "Doctor Risk Profile":
    draw_doctor_profile(output_data)
elif page == "Cluster Analytics":
    draw_cluster_analytics(output_data)
else:
    draw_quality_monitor(output_data)
