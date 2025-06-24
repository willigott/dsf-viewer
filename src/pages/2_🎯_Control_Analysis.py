from bada.processing import get_dsf_curve_features
from bada.visualization import create_melt_curve_plot_from_features
import pandas as pd
import streamlit as st

from session.state_manager import SessionStateManager
from session.utils import validate_page_access
from utils import natural_sort_wells

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

if not validate_page_access("control_analysis"):
    st.stop()

st.title("Control Analysis")

def update_control_wells():
    SessionStateManager.set_value("control_wells", st.session_state.control_wells_widget)
    SessionStateManager.set_value("control_results", None)
    SessionStateManager.set_value("avg_control_tm", None)
    SessionStateManager.set_value("plot_data", None)


def update_analysis():
    SessionStateManager.set_value("selected_control", st.session_state.selected_control_widget)
    SessionStateManager.set_value("smoothing_control", st.session_state.smoothing_control_widget)
    SessionStateManager.set_value("control_results", None)
    SessionStateManager.set_value("avg_control_tm", None)
    SessionStateManager.set_value("plot_data", None)


def update_temperature():
    """Update temperature values in session state.
    
    The selected temperature range is used across multiple pages and requires the recalculation of
    certain elements (e.g. the DTW analysis)
    """
    current_min_temp = SessionStateManager.get_value("min_temp")
    current_max_temp = SessionStateManager.get_value("max_temp")
    
    if (st.session_state.min_temp_widget != current_min_temp or 
        st.session_state.max_temp_widget != current_max_temp):
        
        # update temperature values
        SessionStateManager.set_value("min_temp", st.session_state.min_temp_widget)
        SessionStateManager.set_value("max_temp", st.session_state.max_temp_widget)
        
        # clear control analysis results since they depend on temperature range
        SessionStateManager.set_value("control_results", None)
        SessionStateManager.set_value("avg_control_tm", None)
        SessionStateManager.set_value("plot_data", None)
        
        # clear DTW-related session state variables to force recalculation
        SessionStateManager.set_value("dtw_distances", None)
        SessionStateManager.set_value("plate_data", None)
                
        # clear well classifications since they depend on DTW distances
        SessionStateManager.set_value("dtw_filled_wells", [])
        SessionStateManager.set_value("dtw_undecided_wells", [])
        SessionStateManager.set_value("dtw_empty_wells", [])
        
        # clear well analysis results since they depend on temperature range
        SessionStateManager.set_value("well_analysis_results", None)

control_col1, control_col2 = st.columns([0.7, 0.3])

with control_col1:
    st.multiselect(
        "Select control wells",
        options=natural_sort_wells(SessionStateManager.get_value("available_wells")),
        default=natural_sort_wells(SessionStateManager.get_value("control_wells")),
        key="control_wells_widget",
        on_change=update_control_wells,
        help="Select one or more wells that contain control measurements",
    )

if not SessionStateManager.get_value("control_wells"):
    st.warning(
        """Please select at least one control well. 
        Otherwise, you won't be able to calculate ΔTm values."""
    )
    st.stop()

with control_col2:
    control_wells = SessionStateManager.get_value("control_wells")
    selected_control = SessionStateManager.get_value("selected_control")
    
    if selected_control is None and control_wells:
        SessionStateManager.set_value("selected_control", control_wells[0])
        selected_control = SessionStateManager.get_value("selected_control")

    if selected_control in control_wells:
        selected_index = control_wells.index(selected_control)
    else:
        selected_index = 0

    st.selectbox(
        "Select control well",
        options=natural_sort_wells(control_wells),
        index=selected_index,
        help="Select a control well to view its analysis results",
        key="selected_control_widget",
        on_change=update_analysis,
    )

controls_col1, controls_col2, controls_col3 = st.columns(3)

with controls_col1:
    st.slider(
        "Spline smoothing factor",
        min_value=0.0,
        max_value=1.0,
        value=SessionStateManager.get_value("smoothing_control"),
        step=0.01,
        help="""Adjust the smoothing factor for the spline fit. The higher the smoothing factor,
        the smoother the signal; this can help to deal with noisy signals i.e. too many peaks.""",
        on_change=update_analysis,
        key="smoothing_control_widget",
    )

data = SessionStateManager.get_value("data")
with controls_col2:
    st.number_input(
        "Minimum temperature (°C)",
        min_value=float(data["temperature"].min()),
        max_value=float(data["temperature"].max()),
        value=SessionStateManager.get_value("min_temp"),
        step=1.0,
        key="min_temp_widget",
        on_change=update_temperature,
        help="""Set the minimum temperature for the analysis. Only the selected temperature range
        will be used for the calculation of Tm and also for the detection of atypical wells (next
        page). If the range is too wide, there is a risk to pick up peaks based on noise, if the
        range is too narrow, one might miss the important range for certain wells.""",
    )

with controls_col3:
    st.number_input(
        "Maximum temperature (°C)",
        min_value=float(data["temperature"].min()),
        max_value=float(data["temperature"].max()),
        value=SessionStateManager.get_value("max_temp"),
        step=1.0,
        key="max_temp_widget",
        on_change=update_temperature,
        help="""Set the maximum temperature for the analysis. Only the selected temperature range
        will be used for the calculation of Tm and also for the detection of atypical wells (next
        page). If the range is too wide, there is a risk to pick up peaks based on noise, if the
        range is too narrow, one might miss the important range for certain wells.""",
    )

selected_control = SessionStateManager.get_value("selected_control")
well_data = data[data["well_position"] == selected_control]
plot_data = get_dsf_curve_features(
    data=well_data,
    min_temp=SessionStateManager.get_value("min_temp"),
    max_temp=SessionStateManager.get_value("max_temp"),
    smoothing=SessionStateManager.get_value("smoothing_control"),
    avg_control_tm=SessionStateManager.get_value("avg_control_tm"),
)

fig = create_melt_curve_plot_from_features(plot_data)

plot_col, metrics_col = st.columns([0.85, 0.15])

with plot_col:
    st.plotly_chart(fig, use_container_width=True)

with metrics_col:
    st.subheader("Analysis results")
    st.metric("Tm (°C)", f"{plot_data['tm']:.2f}")
    st.metric("Min fluorescence", f"{plot_data['min_fluorescence']:.2f}")
    st.metric("Max fluorescence", f"{plot_data['max_fluorescence']:.2f}")
    st.metric(
        "Fluorescence range", f"{plot_data['max_fluorescence'] - plot_data['min_fluorescence']:.2f}"
    )
    st.metric("Max slope", f"{plot_data['max_derivative_value']:.3f}")

if SessionStateManager.get_value("control_results") is None:
    control_results = []
    total_tm = 0
    control_wells = SessionStateManager.get_value("control_wells")

    for well in control_wells:
        single_well_data = data[data["well_position"] == well]
        well_data = get_dsf_curve_features(
            data=single_well_data,
            min_temp=SessionStateManager.get_value("min_temp"),
            max_temp=SessionStateManager.get_value("max_temp"),
            smoothing=SessionStateManager.get_value("smoothing_control"),
        )

        control_results.append(
            {
                "Well": well,
                "Tm (°C)": f"{well_data['tm']:.2f}",
                "Min fluorescence": f"{well_data['min_fluorescence']:.2f}",
                "Max fluorescence": f"{well_data['max_fluorescence']:.2f}",
                "Fluorescence range": (
                    f"{well_data['max_fluorescence'] - well_data['min_fluorescence']:.2f}"
                ),
                "Max slope": f"{well_data['max_derivative_value']:.3f}",
            }
        )

        total_tm += well_data["tm"]

    avg_control_tm = total_tm / len(control_wells)
    SessionStateManager.set_value("control_results", control_results)
    SessionStateManager.set_value("avg_control_tm", avg_control_tm)

st.subheader("Summary of control wells")
st.dataframe(pd.DataFrame(SessionStateManager.get_value("control_results")))

st.info(f"Average Tm of control wells: {SessionStateManager.get_value('avg_control_tm'):.2f}°C")
