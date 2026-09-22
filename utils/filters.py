from typing import Tuple
import pandas as pd
import streamlit as st
from utils.data_loader import MONTH_ORDER


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders sidebar filter controls, state management buttons (Select All / Reset),
    and active filter summaries. Returns the filtered pandas DataFrame.
    """
    st.sidebar.markdown("## 🔍 Data Filters")
    st.sidebar.markdown("---")

    all_states = sorted(df["State of Residence"].unique().tolist())
    all_months = MONTH_ORDER
    all_sexes = ["All", "Female", "Male"]

    # Initialize Session State Defaults if not present
    if "selected_states" not in st.session_state:
        st.session_state["selected_states"] = all_states
    if "selected_months" not in st.session_state:
        st.session_state["selected_months"] = all_months
    if "selected_sex" not in st.session_state:
        st.session_state["selected_sex"] = "All"

    # Reset Filters Button Callback
    def reset_filters():
        st.session_state["selected_states"] = all_states
        st.session_state["selected_months"] = all_months
        st.session_state["selected_sex"] = "All"

    # Select / Clear All callbacks
    def select_all_states():
        st.session_state["selected_states"] = all_states

    def clear_all_states():
        st.session_state["selected_states"] = []

    def select_all_months():
        st.session_state["selected_months"] = all_months

    def clear_all_months():
        st.session_state["selected_months"] = []

    # Reset Button at Top of Sidebar
    st.sidebar.button("🔄 Reset All Filters", on_click=reset_filters, use_container_width=True)
    st.sidebar.markdown("---")

    # 1. Geography Multiselect
    st.sidebar.markdown("### 📍 Geographies (States & DC)")
    col_st1, col_st2 = st.sidebar.columns(2)
    col_st1.button("Select All", key="btn_sel_st", on_click=select_all_states, use_container_width=True)
    col_st2.button("Clear All", key="btn_clr_st", on_click=clear_all_states, use_container_width=True)

    selected_states = st.sidebar.multiselect(
        "Choose Geographies:",
        options=all_states,
        key="selected_states",
        help="Select one or more US states/DC to include in the analysis."
    )

    st.sidebar.markdown("---")

    # 2. Month Multiselect
    st.sidebar.markdown("### 📅 Months")
    col_m1, col_m2 = st.sidebar.columns(2)
    col_m1.button("Select All", key="btn_sel_m", on_click=select_all_months, use_container_width=True)
    col_m2.button("Clear All", key="btn_clr_m", on_click=clear_all_months, use_container_width=True)

    selected_months = st.sidebar.multiselect(
        "Choose Months:",
        options=all_months,
        key="selected_months",
        help="Select one or more months of 2025."
    )

    st.sidebar.markdown("---")

    # 3. Infant Sex Selector
    st.sidebar.markdown("### 👶 Infant Sex Category")
    selected_sex = st.sidebar.radio(
        "Filter by Sex:",
        options=all_sexes,
        key="selected_sex",
        horizontal=True,
        help="Select 'All' to aggregate both sexes, or filter specifically for Female/Male."
    )

    st.sidebar.markdown("---")

    # Active Filters Summary Box in Sidebar
    st.sidebar.markdown("### 📊 Active Filter Summary")
    num_states = len(selected_states)
    num_months = len(selected_months)
    st.sidebar.info(
        f"• **Geographies**: {num_states} of {len(all_states)}\n"
        f"• **Months**: {num_months} of {len(all_months)}\n"
        f"• **Infant Sex**: {selected_sex}"
    )

    # Filter Logic
    filtered_df = df.copy()

    if selected_states:
        filtered_df = filtered_df[filtered_df["State of Residence"].isin(selected_states)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    if selected_months:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    if selected_sex != "All":
        filtered_df = filtered_df[filtered_df["Sex of Infant"] == selected_sex]

    return filtered_df
