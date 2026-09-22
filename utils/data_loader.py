from pathlib import Path
import pandas as pd
import streamlit as st

# Standard 2-letter postal code mapping for US States and District of Columbia
STATE_ABBR_MAP = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def validate_data(df: pd.DataFrame) -> None:
    """
    Performs data-quality assertions to ensure dataset integrity upon load.
    Raises ValueError with descriptive context if validation fails.
    """
    expected_cols = [
        "State of Residence", "Month", "Month Code",
        "Year Code", "Sex of Infant", "Births"
    ]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns in workbook: {missing_cols}")

    if len(df) != 1224:
        raise ValueError(f"Expected 1,224 rows, but loaded {len(df)} rows.")

    total_births = df["Births"].sum()
    if total_births != 3604640:
        raise ValueError(f"Expected total births to be 3,604,640, but got {total_births:,}.")

    null_count = df.isnull().sum().sum()
    if null_count > 0:
        raise ValueError(f"Found {null_count} null/missing values in dataset.")


@st.cache_data(show_spinner="Loading provisional natality dataset...")
def load_natality_data() -> pd.DataFrame:
    """
    Loads and preprocesses the provisional CDC natality dataset.
    Cached with st.cache_data for optimal performance.
    """
    # Locate dataset path portably relative to the project directory
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / "Provisional_Natality_2025_CDC.xlsx"

    if not data_path.exists():
        raise FileNotFoundError(f"Workbook not found at expected path: {data_path}")

    # Read sheet using openpyxl engine
    df = pd.read_excel(data_path, sheet_name=0)

    # Validate dataset before applying downstream transformations
    validate_data(df)

    # Assign 2-letter state postal abbreviation for Plotly US map rendering
    df["State Code"] = df["State of Residence"].map(STATE_ABBR_MAP)

    # Establish explicit categorical ordering for months (chronological Jan-Dec)
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    # Ensure numeric columns are properly typed
    df["Births"] = df["Births"].astype(int)
    df["Month Code"] = df["Month Code"].astype(int)
    df["Year Code"] = df["Year Code"].astype(int)

    return df
