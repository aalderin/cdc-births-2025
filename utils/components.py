from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Custom Palette & Styling Constants
COLOR_TEAL = "#00A896"
COLOR_CORAL = "#E63946"
COLOR_INDIGO = "#4A4E69"
COLOR_AMBER = "#F4A261"
COLOR_SLATE_BG = "#0F172A"
COLOR_CARD_BG = "#1E293B"

PLOT_LAYOUT_SETTINGS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15, 23, 42, 0.4)",
    font=dict(color="#F8FAFC", family="sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
)


def render_header():
    """
    Renders the main dashboard header, title, dataset overview, CDC source attribution,
    and mandatory disclaimers (Provisional status & Counts vs. Birth Rates).
    """
    st.markdown(
        """
        <div style="background-color: #1E293B; padding: 1.5rem; border-radius: 10px; border-left: 6px solid #00A896; margin-bottom: 1.5rem;">
            <h1 style="color: #F8FAFC; margin-bottom: 0.25rem;">📊 CDC Provisional Natality Dashboard (2025)</h1>
            <p style="color: #94A3B8; font-size: 1.05rem; margin-bottom: 0.75rem;">
                Interactive Business Analytics Dashboard for Exploring Birth Counts Across US Geographies, Months, and Infant Sex Categories.
            </p>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <span style="background-color: #00A89622; color: #2DD4BF; padding: 0.3rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #00A89655;">
                    📌 Source: CDC WONDER Provisional Natality Dataset
                </span>
                <span style="background-color: #F59E0B22; color: #FBBF24; padding: 0.3rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #F59E0B55;">
                    ⚠️ Status: Provisional 2025 CDC Data
                </span>
                <span style="background-color: #EF444422; color: #FCA5A5; padding: 0.3rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #EF444455;">
                    🚨 Important: Figures are RAW BIRTH COUNTS, NOT BIRTH RATES
                </span>
            </div>
        </div>
        """,
        unsafe_allowed_html=True
    )


def render_kpi_cards(filtered_df: pd.DataFrame, total_geographies_count: int = 51):
    """
    Renders 5 KPI metric cards at the top of the dashboard summarizing current selection metrics.
    """
    if filtered_df.empty:
        st.warning("⚠️ No data available for the active filter selection. Please adjust your sidebar filters.")
        return

    total_births = filtered_df["Births"].sum()
    selected_states_count = filtered_df["State of Residence"].nunique()
    selected_months_count = filtered_df["Month"].nunique()

    # Calculate average births per selected month
    if selected_months_count > 0:
        avg_births_per_month = total_births / selected_months_count
    else:
        avg_births_per_month = 0

    # Highest volume geography in selection
    state_totals = filtered_df.groupby("State of Residence", observed=True)["Births"].sum()
    if not state_totals.empty:
        top_state = state_totals.idxmax()
        top_state_val = state_totals.max()
    else:
        top_state = "N/A"
        top_state_val = 0

    # Highest volume month in selection
    month_totals = filtered_df.groupby("Month", observed=True)["Births"].sum()
    if not month_totals.empty:
        top_month = month_totals.idxmax()
        top_month_val = month_totals.max()
    else:
        top_month = "N/A"
        top_month_val = 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Births",
            value=f"{total_births:,}",
            help="Sum of live birth counts across all selected filters."
        )

    with col2:
        st.metric(
            label="Geographies Selected",
            value=f"{selected_states_count} / {total_geographies_count}",
            help="Number of US states & DC included in current selection."
        )

    with col3:
        st.metric(
            label="Avg Births / Month",
            value=f"{int(round(avg_births_per_month)):,}",
            help="Average monthly birth volume across selected months."
        )

    with col4:
        st.metric(
            label="Top Geography",
            value=top_state,
            delta=f"{top_state_val:,} births",
            delta_color="normal",
            help="Geography with the highest cumulative birth count in selection."
        )

    with col5:
        st.metric(
            label="Top Month",
            value=str(top_month),
            delta=f"{top_month_val:,} births",
            delta_color="normal",
            help="Month with the highest cumulative birth count in selection."
        )


def create_monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a line chart displaying monthly birth trends in chronological order.
    Forces Y-axis baseline to start at zero.
    """
    monthly_df = df.groupby("Month", observed=True, as_index=False)["Births"].sum()

    fig = px.line(
        monthly_df,
        x="Month",
        y="Births",
        markers=True,
        title="<b>Monthly Birth Trend (2025)</b>",
        labels={"Births": "Total Birth Count", "Month": "Month of Birth"},
        text="Births"
    )
    fig.update_traces(
        line=dict(color=COLOR_TEAL, width=3),
        marker=dict(size=8, color="#2DD4BF", symbol="circle"),
        texttemplate="%{text:,.0f}",
        textposition="top center",
        hovertemplate="<b>%{x}</b><br>Birth Count: <b>%{y:,.0f}</b><extra></extra>"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS)
    fig.update_yaxes(rangemode="tozero", gridcolor="#334155", title="Birth Count (Absolute)")
    fig.update_xaxes(gridcolor="#334155")
    return fig


def create_sex_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a bar/donut chart comparing Female vs Male birth counts.
    """
    sex_df = df.groupby("Sex of Infant", observed=True, as_index=False)["Births"].sum()

    fig = px.bar(
        sex_df,
        x="Sex of Infant",
        y="Births",
        color="Sex of Infant",
        color_discrete_map={"Female": COLOR_CORAL, "Male": COLOR_TEAL},
        title="<b>Birth Counts by Infant Sex</b>",
        labels={"Births": "Total Births", "Sex of Infant": "Infant Sex"},
        text="Births"
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS, showlegend=False)
    fig.update_yaxes(rangemode="tozero", gridcolor="#334155")
    fig.update_xaxes(gridcolor="#334155")
    return fig


def create_state_ranking_chart(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """
    Creates a horizontal bar chart ranking states by cumulative birth counts.
    """
    state_df = (
        df.groupby("State of Residence", observed=True, as_index=False)["Births"]
        .sum()
        .sort_values(by="Births", ascending=True)
    )

    if len(state_df) > top_n:
        state_df = state_df.tail(top_n)

    fig = px.bar(
        state_df,
        x="Births",
        y="State of Residence",
        orientation="h",
        title=f"<b>State Ranking by Birth Count (Top {min(top_n, len(state_df))})</b>",
        labels={"Births": "Total Births", "State of Residence": "Geography"},
        text="Births",
        color="Births",
        color_continuous_scale=["#1E293B", COLOR_TEAL]
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Births: <b>%{x:,.0f}</b><extra></extra>"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS, coloraxis_showscale=False)
    fig.update_xaxes(rangemode="tozero", gridcolor="#334155")
    fig.update_yaxes(gridcolor="#334155")
    return fig


def create_us_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive Plotly US state choropleth map color-coded by birth count.
    """
    state_map_df = df.groupby(["State of Residence", "State Code"], observed=True, as_index=False)["Births"].sum()

    fig = px.choropleth(
        state_map_df,
        locations="State Code",
        locationmode="USA-states",
        color="Births",
        scope="usa",
        hover_name="State of Residence",
        hover_data={"State Code": False, "Births": ":,.0f"},
        color_continuous_scale="Viridis",
        title="<b>Geographic Distribution of Live Birth Counts (US Map)</b>"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#0F172A",
            landcolor="#1E293B",
            showlakes=True,
            subregioncolor="#334155"
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig


def create_monthly_trend_by_sex_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a multi-line/grouped bar chart comparing Male vs Female birth trends month-by-month.
    """
    trend_df = df.groupby(["Month", "Sex of Infant"], observed=True, as_index=False)["Births"].sum()

    fig = px.bar(
        trend_df,
        x="Month",
        y="Births",
        color="Sex of Infant",
        barmode="group",
        color_discrete_map={"Female": COLOR_CORAL, "Male": COLOR_TEAL},
        title="<b>Monthly Birth Trend Breakdown by Infant Sex</b>",
        labels={"Births": "Birth Count", "Month": "Month of Birth"},
        text="Births"
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x} (%{fullData.name})</b><br>Births: <b>%{y:,.0f}</b><extra></extra>"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS, legend_title_text="Infant Sex")
    fig.update_yaxes(rangemode="tozero", gridcolor="#334155")
    fig.update_xaxes(gridcolor="#334155")
    return fig


def create_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Creates a heatmap of State vs Month birth count intensity.
    """
    pivot_df = df.pivot_table(
        index="State of Residence",
        columns="Month",
        values="Births",
        aggfunc="sum",
        fill_value=0,
        observed=True
    )

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="Geography", color="Birth Count"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Plasma",
        title="<b>Geography vs. Month Birth Count Intensity Heatmap</b>",
        aspect="auto"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS)
    return fig


def create_top_bottom_comparison(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Creates a comparative horizontal bar chart of the Top N vs Bottom N states.
    """
    totals = df.groupby("State of Residence", observed=True)["Births"].sum().sort_values(ascending=False)
    if len(totals) == 0:
        return go.Figure()

    top_n = totals.head(n).reset_index()
    top_n["Group"] = f"Top {n}"

    bottom_n = totals.tail(n).reset_index()
    bottom_n["Group"] = f"Bottom {n}"

    combined = pd.concat([top_n, bottom_n]).sort_values(by="Births", ascending=True)

    fig = px.bar(
        combined,
        x="Births",
        y="State of Residence",
        color="Group",
        orientation="h",
        color_discrete_map={f"Top {n}": COLOR_TEAL, f"Bottom {n}": COLOR_CORAL},
        title=f"<b>Volume Contrast: Top {n} vs. Bottom {n} Geographies</b>",
        labels={"Births": "Total Births", "State of Residence": "Geography"},
        text="Births"
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y} (%{fullData.name})</b><br>Births: <b>%{x:,.0f}</b><extra></extra>"
    )
    fig.update_layout(**PLOT_LAYOUT_SETTINGS, legend_title_text="Group")
    fig.update_xaxes(rangemode="tozero", gridcolor="#334155")
    return fig
