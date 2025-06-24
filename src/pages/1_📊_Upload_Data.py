from pathlib import Path

from bada.parsers import LightCycler480Parser, QuantStudio7Parser
import streamlit as st

from session.state_manager import SessionStateManager
from session.utils import validate_page_access
from utils import natural_sort_wells

st.set_page_config(layout="wide")

if not validate_page_access("upload_data"):
    st.stop()

st.title("Upload Data")

SUPPORTED_FORMATS = ["QuantStudio 7", "LightCycler 480"]

current_format = SessionStateManager.get_value("file_format")
file_format = st.radio(
    "Select file format",
    SUPPORTED_FORMATS,
    index=SUPPORTED_FORMATS.index(current_format) if current_format in SUPPORTED_FORMATS else 0,
    help="Choose the format of your DSF data file",
)

uploaded_file = st.file_uploader(
    "Upload DSF data file",
    type=["csv", "txt"],
    help="Upload your DSF data file in CSV or txt format",
)

if SessionStateManager.has_data():
    st.success(f"""
        Current data loaded:
        - Format: {SessionStateManager.get_value("file_format")}
        - Plate size: {SessionStateManager.get_value("plate_size")}-well
    """)

    st.subheader("Data preview")
    st.dataframe(SessionStateManager.get_value("data").head())

if uploaded_file is not None:
    try:
        temp_path = Path("temp_dsf_file.csv")
        temp_path.write_bytes(uploaded_file.getvalue())

        if file_format == "QuantStudio 7":
            validated_data = QuantStudio7Parser(temp_path).parse()
            plate_size = 384  # QuantStudio 7 uses only(?) 384-well plates

        else:
            validated_data = LightCycler480Parser(temp_path).parse()
            num_wells = validated_data["well_position"].nunique()
            plate_size = 384 if num_wells > 96 else 96

        temp_path.unlink()

        # reset all state since we have new data, then set the new values
        SessionStateManager.reset_all()

        SessionStateManager.set_value("data", validated_data)
        SessionStateManager.set_value("file_format", file_format)
        SessionStateManager.set_value(
            "available_wells",
            natural_sort_wells(list(validated_data["well_position"].unique()))
        )
        SessionStateManager.set_value("plate_size", plate_size)
        SessionStateManager.set_value("min_temp", float(validated_data["temperature"].min()))
        SessionStateManager.set_value("max_temp", float(validated_data["temperature"].max()))

        st.success(f"""
            File uploaded and validated successfully!
            - Format: {file_format}
            - Plate size: {plate_size}-well
        """)

        st.subheader("Data preview (already reformatted)")
        st.dataframe(validated_data.head())

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        SessionStateManager.reset_all()
