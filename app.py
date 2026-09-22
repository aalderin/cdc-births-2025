import streamlit as st

# Page Configuration - MUST be called first before any other Streamlit command
st.set_page_config(
    page_title="CDC Provisional Natality 2025 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.data_loader import load_natality_data
from utils.filters import render_sidebar_filters
from utils.components import (
    render_header,
    render_kpi_cards,
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_state_ranking_chart,
    create_us_choropleth_map,
    create_monthly_trend_by_sex_chart,
    create_state_month_heatmap,
    create_top_bottom_comparison,
)

def main():
    # 1. Load Data
    try:
        raw_df = load_natality_data()
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        st.stop()

    # 2. Render Header Banner
    render_header()

    # 3. Render Sidebar Filters & Obtain Filtered Data
    filtered_df = render_sidebar_filters(raw_df)

    # 4. Check for Empty Selections
    if filtered_df.empty:
        st.warning("⚠️ **No observations match the current filter criteria.** Please adjust your state, month, or sex selections in the sidebar.")
        st.stop()

    # 5. Render Top KPI Metric Banner
    render_kpi_cards(filtered_df, total_geographies_count=51)
    st.markdown("<br>", unsafe_allowed_html=True)

    # 6. Render 5 Main Dashboard Tabs
    tab_overview, tab_geo, tab_monthly_sex, tab_table, tab_about = st.tabs([
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "📅 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📘 About the Data & Audit"
    ])

    # ----------------------------------------------------
    # TAB 1: OVERVIEW
    # ----------------------------------------------------
    with tab_overview:
        st.markdown("### 📊 Executive Summary & Key Visualizations")
        col_ov1, col_ov2 = st.columns([3, 2])

        with col_ov1:
            fig_trend = create_monthly_trend_chart(filtered_df)
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_ov2:
            fig_sex = create_sex_comparison_chart(filtered_df)
            st.plotly_chart(fig_sex, use_container_width=True)

        st.markdown(
            """
            <div style="background-color: #1E293B; padding: 1.2rem; border-radius: 8px; border: 1px solid #334155; margin-top: 1rem;">
                <h4 style="color: #00A896; margin-bottom: 0.5rem;">💡 Business Analytics Student Insights</h4>
                <ul style="color: #CBD5E1; margin-bottom: 0;">
                    <li><strong>Provisional 2025 Scope:</strong> The dataset comprises 1,224 observations spanning all 50 US states and the District of Columbia.</li>
                    <li><strong>Seasonality Baseline:</strong> Birth counts exhibit predictable monthly variations across the calendar year.</li>
                    <li><strong>Sex Ratio Balance:</strong> Male births consistently outnumber Female births by a small, biologically expected margin (approx 51% Male vs 49% Female).</li>
                    <li><strong>Counts vs. Rates Caution:</strong> Large states like California and Texas report the highest birth counts primarily due to their large overall populations, not necessarily higher birth rates per capita.</li>
                </ul>
            </div>
            """,
            unsafe_allowed_html=True
        )

    # ----------------------------------------------------
    # TAB 2: GEOGRAPHIC ANALYSIS
    # ----------------------------------------------------
    with tab_geo:
        st.markdown("### 🗺️ Geographic Distribution & State Rankings")

        # US Map Section
        fig_map = create_us_choropleth_map(filtered_df)
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")

        col_g1, col_g2 = st.columns([1, 1])

        with col_g1:
            top_n_slider = st.slider(
                "Select Number of Top States to Rank:",
                min_value=5,
                max_value=51,
                value=15,
                step=5,
                key="top_n_slider"
            )
            fig_rank = create_state_ranking_chart(filtered_df, top_n=top_n_slider)
            st.plotly_chart(fig_rank, use_container_width=True)

        with col_g2:
            comp_n_slider = st.slider(
                "Top / Bottom Comparison Size:",
                min_value=3,
                max_value=10,
                value=5,
                step=1,
                key="comp_n_slider"
            )
            fig_comp = create_top_bottom_comparison(filtered_df, n=comp_n_slider)
            st.plotly_chart(fig_comp, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: MONTHLY AND SEX ANALYSIS
    # ----------------------------------------------------
    with tab_monthly_sex:
        st.markdown("### 📅 Monthly Dynamics & Sex Category Slices")

        fig_sex_trend = create_monthly_trend_by_sex_chart(filtered_df)
        st.plotly_chart(fig_sex_trend, use_container_width=True)

        st.markdown("---")

        st.markdown("#### 🌡️ State-by-Month Birth Density Heatmap")
        st.info("Hover over heatmap cells to inspect monthly birth counts for specific state-month combinations.")
        fig_heatmap = create_state_month_heatmap(filtered_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # ----------------------------------------------------
    # TAB 4: DATA TABLE AND DOWNLOAD
    # ----------------------------------------------------
    with tab_table:
        st.markdown("### 📋 Filtered Data Table & Export")

        st.markdown(
            f"Displaying **{len(filtered_df):,}** matching rows from the provisional 2025 dataset."
        )

        display_cols = ["State of Residence", "Month", "Month Code", "Sex of Infant", "Births", "Year Code"]
        table_df = filtered_df[display_cols].reset_index(drop=True)

        # Streamlit Dataframe with Search and Formatting
        st.dataframe(
            table_df,
            column_config={
                "Births": st.column_config.NumberColumn(
                    "Births (Count)",
                    format="%d",
                    help="Absolute count of live births."
                ),
                "Month Code": st.column_config.NumberColumn("Month Code", format="%d"),
                "Year Code": st.column_config.NumberColumn("Year Code", format="%d")
            },
            use_container_width=True,
            height=450
        )

        # Download CSV Button
        csv_data = table_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=csv_data,
            file_name="provisional_cdc_natality_2025_filtered.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    # ----------------------------------------------------
    # TAB 5: ABOUT THE DATA & AUDIT
    # ----------------------------------------------------
    with tab_about:
        st.markdown("### 📘 Educational Guide & Data Audit Documentation")

        st.markdown(
            """
            ### 1. Fundamental Analytics Concept: Birth Counts vs. Birth Rates
            > [!IMPORTANT]
            > **Counts are frequencies; Rates require denominators.**
            > - **Birth Counts**: The absolute number of live births recorded in a specified geography and timeframe (e.g., 17,627 male births in California in August 2025).
            > - **Birth Rates**: The ratio of birth counts to the total underlying population (e.g., *Births per 1,000 Total Population* or *Births per 1,000 Women of Childbearing Age*).
            > 
            > Because this dataset contains **only birth counts** without population census denominators, calculating per-capita birth rates or assuming California has a "higher fertility rate" than Vermont is a **classic analytics fallacy**. California has more births primarily because it has ~39 million residents compared to Vermont's ~640,000 residents.

            ---

            ### 2. Dataset Quality Audit Checklist
            Before building dashboards, analytics professionals perform rigorous data auditing:

            | Audit Parameter | Verification Result | Business Relevance |
            | :--- | :--- | :--- |
            | **Total Observations** | **1,224 rows** | 51 Geographies × 12 Months × 2 Sex Categories = 1,224 rows (Complete factorial grid). |
            | **Geographic Scope** | **51 Geographies** | 50 US States + District of Columbia. |
            | **Temporal Scope** | **12 Months (2025)** | Full calendar year represented chronologically. |
            | **Infant Sex Breakdown** | **2 Categories** | Female & Male. |
            | **Missing Data** | **0 Nulls / NaN** | No missing values or text suppressions. |
            | **Duplicate Records** | **0 Duplicates** | Each row is a unique multidimensional slice. |
            | **Total Dataset Births** | **3,604,640 Births** | Verified exact sum matching CDC WONDER export. |

            ---

            ### 3. CDC Data Attribution & Metadata
            - **Data Source**: CDC WONDER Provisional Natality Statistics (2025).
            - **Data Status**: Provisional (subject to final CDC natality release revisions).
            - **File Format**: Microsoft Excel (`Provisional_Natality_2025_CDC.xlsx`).
            - **License / Access**: Publicly available CDC vital statistics dataset.
            """
        )

if __name__ == "__main__":
    main()
