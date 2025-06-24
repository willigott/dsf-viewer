from bada.processing import get_dtw_distances_from_reference
from bada.utils.reformatting import convert_distances_to_plate_format
from bada.visualization import create_heatmap_plot
import pandas as pd
import streamlit as st

from session.state_manager import SessionStateManager
from session.utils import validate_page_access
from utils import natural_sort_wells

st.set_page_config(layout="wide")

st.title("Detect Atypical Wells")

if not validate_page_access("detect_atypical_wells"):
    st.stop()

def update_thresholds():
    """Update threshold values in session state when changed."""
    SessionStateManager.set_value(
        "dtw_lower_threshold", st.session_state.dtw_lower_threshold_widget
    )
    SessionStateManager.set_value(
        "dtw_upper_threshold", st.session_state.dtw_upper_threshold_widget
    )

reference_well = SessionStateManager.get_value("selected_control")

# dtw_distances and plate_data can be reset in 2_Control_Analysis
if SessionStateManager.get_value("dtw_distances") is None:
    data = SessionStateManager.get_value("data")
    min_temp = SessionStateManager.get_value("min_temp")
    max_temp = SessionStateManager.get_value("max_temp")
    
    filtered_data = data[
        (data["temperature"] >= min_temp) & (data["temperature"] <= max_temp)
    ]

    dtw_distances = get_dtw_distances_from_reference(
        filtered_data, reference_well, normalized=True
    )
    SessionStateManager.set_value("dtw_distances", dtw_distances)

if SessionStateManager.get_value("plate_data") is None:
    dtw_distances = SessionStateManager.get_value("dtw_distances")
    plate_size = SessionStateManager.get_value("plate_size")
    
    plate_data, cols, rows = convert_distances_to_plate_format(dtw_distances, plate_size)
    SessionStateManager.set_value("plate_data", plate_data)
    SessionStateManager.set_value("plate_cols", cols)
    SessionStateManager.set_value("plate_rows", rows)

fig = create_heatmap_plot(
    SessionStateManager.get_value("plate_data"),
    SessionStateManager.get_value("plate_cols"),
    SessionStateManager.get_value("plate_rows"),
    title=f"Shape comparison with reference well {reference_well}",
    colorbar_title="DTW Distance",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Threshold selection")
st.markdown("""
    Here you can set thresholds that are used to determine whether a signal is considered typical
    or atypical; for all signals where an automated classification can't be accomplished, the signal
    will be considered undecided and the associated wells can be manually reviewed in the "Well
    Review" page. For wells with atypical signals, no features (e.g. *Tm*) will be reported.
    The values are based on a distance measure from the reference well which is set in
    the "Control Analysis" page. This distance measure allows to compare the shape of signals with
    each other:
    - if the distance is small, the shape of the curves are similar (blue wells)
    - if the distance is large, the shape of the curves are different (red wells)
""")
col1, col2 = st.columns(2)

with col1:
    st.number_input(
        "Lower threshold (typical/undecided)",
        min_value=0.0,
        max_value=10.0,
        value=SessionStateManager.get_value("dtw_lower_threshold"),
        step=0.1,
        help="Wells below this threshold will be considered typical",
        key="dtw_lower_threshold_widget",
        on_change=update_thresholds,
    )

with col2:
    st.number_input(
        "Upper threshold (undecided/atypical)",
        min_value=0.0,
        max_value=10.0,
        value=SessionStateManager.get_value("dtw_upper_threshold"),
        step=0.1,
        help="Wells above this threshold will be considered atypical",
        key="dtw_upper_threshold_widget",
        on_change=update_thresholds,
    )

typical_wells = []
undecided_wells = []
atypical_wells = []

dtw_distances = SessionStateManager.get_value("dtw_distances")
lower_threshold = SessionStateManager.get_value("dtw_lower_threshold")
upper_threshold = SessionStateManager.get_value("dtw_upper_threshold")

for well, (distance, _) in dtw_distances.items():
    if distance <= lower_threshold:
        typical_wells.append(well)
    elif distance >= upper_threshold:
        atypical_wells.append(well)
    else:
        undecided_wells.append(well)

typical_wells = natural_sort_wells(typical_wells)
undecided_wells = natural_sort_wells(undecided_wells)
atypical_wells = natural_sort_wells(atypical_wells)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Typical Wells")
    st.write(f"Number of typical wells: {len(typical_wells)}")
    st.dataframe(pd.DataFrame({"Well": typical_wells}), use_container_width=True)

with col2:
    st.subheader("Undecided Wells")
    st.write(f"Number of undecided wells: {len(undecided_wells)}")
    st.dataframe(pd.DataFrame({"Well": undecided_wells}), use_container_width=True)

with col3:
    st.subheader("Atypical Wells")
    st.write(f"Number of atypical wells: {len(atypical_wells)}")
    st.dataframe(pd.DataFrame({"Well": atypical_wells}), use_container_width=True)

# store well classifications for use in sample analysis
SessionStateManager.set_value("dtw_filled_wells", typical_wells)
SessionStateManager.set_value("dtw_undecided_wells", undecided_wells)
SessionStateManager.set_value("dtw_empty_wells", atypical_wells)
