from bada.processing import get_dsf_curve_features
from bada.visualization import create_melt_curve_plot_from_features
import streamlit as st

from session.state_manager import SessionStateManager
from session.utils import validate_page_access

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Well Analysis")

if not validate_page_access("well_analysis"):
    st.stop()


def get_well_classification(well_id):
    """Get the current classification of a well."""
    well_analysis_results = SessionStateManager.get_value("well_analysis_results")
    if well_id in well_analysis_results and well_analysis_results[well_id].get("reviewed"):
        if well_analysis_results[well_id].get("is_empty"):
            return "Atypical"
        else:
            return "Typical"
            
    filled_wells = SessionStateManager.get_value("dtw_filled_wells")
    undecided_wells = SessionStateManager.get_value("dtw_undecided_wells")
    empty_wells = SessionStateManager.get_value("dtw_empty_wells")
    
    if well_id in filled_wells:
        return "Typical"
    elif well_id in undecided_wells:
        return "Undecided"
    elif well_id in empty_wells:
        return "Atypical"
    else:
        return "Typical"  # not sure if needed, but shouldn't do any harm either


def update_well_classification():
    """Update well classification when changed by user."""
    selected_well = SessionStateManager.get_value("selected_well")
    new_classification = st.session_state.classification_widget
    
    filled_wells = SessionStateManager.get_value("dtw_filled_wells").copy()
    undecided_wells = SessionStateManager.get_value("dtw_undecided_wells").copy()
    empty_wells = SessionStateManager.get_value("dtw_empty_wells").copy()
    
    if selected_well in filled_wells:
        filled_wells.remove(selected_well)
    if selected_well in undecided_wells:
        undecided_wells.remove(selected_well)
    if selected_well in empty_wells:
        empty_wells.remove(selected_well)
    
    if new_classification == "Typical":
        filled_wells.append(selected_well)
    elif new_classification == "Undecided":
        undecided_wells.append(selected_well)
    elif new_classification == "Atypical":
        empty_wells.append(selected_well)
    
    SessionStateManager.set_value("dtw_filled_wells", filled_wells)
    SessionStateManager.set_value("dtw_undecided_wells", undecided_wells)
    SessionStateManager.set_value("dtw_empty_wells", empty_wells)

    well_analysis_results = SessionStateManager.get_value("well_analysis_results")
    well_analysis_results[selected_well]["reviewed"] = True
    SessionStateManager.set_value("well_analysis_results", well_analysis_results)
    
    SessionStateManager.set_value("classification_changed", True)


def update_smoothing():
    """Update smoothing value and trigger recalculation."""
    SessionStateManager.set_value("smoothing_features", st.session_state.smoothing_features_widget)


def update_selected_well():
    """Update selected well and reset parameters to that well's saved values."""
    selected_well = st.session_state.selected_well_widget
    SessionStateManager.set_value("selected_well", selected_well)
    
    # reset parameters to the selected well's saved values
    well_analysis_results = SessionStateManager.get_value("well_analysis_results")
    
    if selected_well in well_analysis_results:
        saved_data = well_analysis_results[selected_well]
        SessionStateManager.set_value("smoothing_features", saved_data["smoothing"])
        SessionStateManager.set_value("min_temp", saved_data["min_temp"])
        SessionStateManager.set_value("max_temp", saved_data["max_temp"])


def update_temperature():
    """Update temperature range values."""
    SessionStateManager.set_value("min_temp", st.session_state.min_temp_widget)
    SessionStateManager.set_value("max_temp", st.session_state.max_temp_widget)


def save_well_changes():
    """Save the current analysis settings and results for the selected well."""
    selected_well = SessionStateManager.get_value("selected_well")
    well_analysis_results = SessionStateManager.get_value("well_analysis_results")
    smoothing_features = SessionStateManager.get_value("smoothing_features")
    min_temp = SessionStateManager.get_value("min_temp")
    max_temp = SessionStateManager.get_value("max_temp")
    
    data = SessionStateManager.get_value("data")
    avg_control_tm = SessionStateManager.get_value("avg_control_tm")
    
    analysis_results = get_dsf_curve_features(
        data=data[data["well_position"] == selected_well],
        min_temp=min_temp,
        max_temp=max_temp,
        smoothing=smoothing_features,
        avg_control_tm=avg_control_tm,
    )
    
    # update is_empty flag based on current classification
    empty_wells = SessionStateManager.get_value("dtw_empty_wells")
    is_empty = selected_well in empty_wells
    
    well_analysis_results[selected_well].update({
        "is_empty": is_empty,
        "tm": analysis_results["tm"],
        "delta_tm": analysis_results["delta_tm"],
        "min_fluorescence": analysis_results["min_fluorescence"],
        "max_fluorescence": analysis_results["max_fluorescence"],
        "fluorescence_range": (
            analysis_results["max_fluorescence"] - analysis_results["min_fluorescence"]
        ),
        "max_slope": analysis_results["max_derivative_value"],
        "smoothing": smoothing_features,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "full_well_data": analysis_results["full_well_data"],
        "x_spline": analysis_results["x_spline"],
        "y_spline": analysis_results["y_spline"],
        "y_spline_derivative": analysis_results["y_spline_derivative"],
        "temp_at_min": analysis_results["temp_at_min"],
        "temp_at_max": analysis_results["temp_at_max"],
        "max_derivative_value": analysis_results["max_derivative_value"],
    })
    
    SessionStateManager.set_value("well_analysis_results", well_analysis_results)
    SessionStateManager.set_value("just_saved_well", selected_well)
    SessionStateManager.set_value("classification_changed", False)


if not SessionStateManager.get_value("dtw_filled_wells"):
    st.warning("Please first detect the atypical wells.")
    st.stop()

if not SessionStateManager.get_value("well_analysis_results"):
    available_wells = SessionStateManager.get_value("available_wells")
    data = SessionStateManager.get_value("data")
    min_temp = SessionStateManager.get_value("min_temp")
    max_temp = SessionStateManager.get_value("max_temp")
    smoothing_features = SessionStateManager.get_value("smoothing_features")
    avg_control_tm = SessionStateManager.get_value("avg_control_tm")
    dtw_empty_wells = SessionStateManager.get_value("dtw_empty_wells")
    
    # initial analysis for all wells
    well_analysis_results = {}
    for well in available_wells:
        single_well_data = data[data["well_position"] == well]
        analysis_results = get_dsf_curve_features(
            data=single_well_data,
            min_temp=min_temp,
            max_temp=max_temp,
            smoothing=smoothing_features,
            avg_control_tm=avg_control_tm,
        )
        # undecided wells are for now treated as typical
        # TODO: replace is_empty with is_atypical throughout the code base
        is_empty = well in dtw_empty_wells
        well_analysis_results[well] = {
            "is_empty": is_empty,
            "reviewed": False,
            "tm": analysis_results["tm"],
            "delta_tm": analysis_results["delta_tm"],
            "min_fluorescence": analysis_results["min_fluorescence"],
            "max_fluorescence": analysis_results["max_fluorescence"],
            "fluorescence_range": analysis_results["max_fluorescence"] - analysis_results["min_fluorescence"],
            "max_slope": analysis_results["max_derivative_value"],
            "smoothing": smoothing_features,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "full_well_data": analysis_results["full_well_data"],
            "x_spline": analysis_results["x_spline"],
            "y_spline": analysis_results["y_spline"],
            "y_spline_derivative": analysis_results["y_spline_derivative"],
            "temp_at_min": analysis_results["temp_at_min"],
            "temp_at_max": analysis_results["temp_at_max"],
            "max_derivative_value": analysis_results["max_derivative_value"],
        }
    
    SessionStateManager.set_value("well_analysis_results", well_analysis_results)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    available_wells = SessionStateManager.get_value("available_wells")
    selected_well = SessionStateManager.get_value("selected_well")
    
    if selected_well is None and available_wells:
        SessionStateManager.set_value("selected_well", available_wells[0])
        selected_well = available_wells[0]

    if selected_well in available_wells:
        selected_index = available_wells.index(selected_well)
    else:
        selected_index = 0

    st.selectbox(
        "Select Well for Analysis",
        options=available_wells,
        index=selected_index,
        key="selected_well_widget",
        on_change=update_selected_well,
    )

with col2:
    st.slider(
        "Spline smoothing factor",
        min_value=0.0,
        max_value=1.0,
        value=SessionStateManager.get_value("smoothing_features"),
        step=0.01,
        help="Adjust the smoothing factor for the spline fit",
        key="smoothing_features_widget",
        on_change=update_smoothing,
    )

with col3:
    data = SessionStateManager.get_value("data")
    st.number_input(
        "Min temperature (°C)",
        min_value=float(data["temperature"].min()),
        max_value=float(data["temperature"].max()),
        value=SessionStateManager.get_value("min_temp"),
        step=1.0,
        key="min_temp_widget",
        on_change=update_temperature,
    )

with col4:
    st.number_input(
        "Max temperature (°C)",
        min_value=float(data["temperature"].min()),
        max_value=float(data["temperature"].max()),
        value=SessionStateManager.get_value("max_temp"),
        step=1.0,
        key="max_temp_widget",
        on_change=update_temperature,
    )

with col5:
    selected_well = SessionStateManager.get_value("selected_well")
    current_classification = get_well_classification(selected_well)
    classification_options = ["Typical", "Undecided", "Atypical"]
    current_index = classification_options.index(current_classification)
    
    st.selectbox(
        "Well Classification",
        options=classification_options,
        index=current_index,
        key="classification_widget",
        on_change=update_well_classification,
        help="Change the classification of this well"
    )

save_col1, save_col2, save_col3 = st.columns(3)

with save_col2:
    # check if current settings differ from saved settings for this well
    selected_well = SessionStateManager.get_value("selected_well")
    well_analysis_results = SessionStateManager.get_value("well_analysis_results")
    smoothing_features = SessionStateManager.get_value("smoothing_features")
    min_temp = SessionStateManager.get_value("min_temp")
    max_temp = SessionStateManager.get_value("max_temp")
    classification_changed = SessionStateManager.get_value("classification_changed", False)
    
    settings_changed = (
        smoothing_features != well_analysis_results[selected_well]["smoothing"] or
        min_temp != well_analysis_results[selected_well]["min_temp"] or
        max_temp != well_analysis_results[selected_well]["max_temp"] or
        classification_changed
    )
    
    # check if we just saved this well
    just_saved_well = SessionStateManager.get_value("just_saved_well")
    if just_saved_well == selected_well and not settings_changed:
        st.success("Saved updated analysis!", icon="✅")
        # clear the flag so message doesn't persist
        SessionStateManager.set_value("just_saved_well", None)
    elif settings_changed:
        st.button(
            "💾 Save Changes",
            help="Save the updated analysis settings and results for this well",
            on_click=save_well_changes,
            type="primary",
            use_container_width=True
        )
    else:
        st.success("Saved", icon="✅")

# # show current vs saved settings comparison
# if selected_well in well_analysis_results:
#     saved_settings = well_analysis_results[selected_well]
#     current_settings_differ = (
#         smoothing_features != saved_settings["smoothing"] or
#         min_temp != saved_settings["min_temp"] or
#         max_temp != saved_settings["max_temp"]
#     )
    
#     # check if classification differs from saved classification
#     saved_is_empty = saved_settings["is_empty"]
#     current_empty_wells = SessionStateManager.get_value("dtw_empty_wells")
#     current_is_empty = selected_well in current_empty_wells
#     classification_differs = saved_is_empty != current_is_empty
    
#     if current_settings_differ or classification_differs:
#         warning_text = "**Viewing temporary analysis** - Current settings differ from saved:\n"
#         if current_settings_differ:
#             warning_text += f"- **Saved smoothing**: {saved_settings['smoothing']:.3f} → **Current**: {smoothing_features:.3f}\n"
#             warning_text += f"- **Saved temp range**: {saved_settings['min_temp']:.1f}°C - {saved_settings['max_temp']:.1f}°C → **Current**: {min_temp:.1f}°C - {max_temp:.1f}°C\n"
#         if classification_differs:
#             saved_classification = "Atypical" if saved_is_empty else "Typical/Undecided"
#             current_classification = get_well_classification(selected_well)
#             warning_text += f"- **Saved classification**: {saved_classification} → **Current**: {current_classification}\n"
#         warning_text += "\nUse \"Save Changes\" to permanently update this well's analysis."
        
#         st.warning(warning_text)

# get the current analysis data to display (either saved or temporary with current settings)
selected_well = SessionStateManager.get_value("selected_well")
well_analysis_results = SessionStateManager.get_value("well_analysis_results")
current_settings_differ = (
    smoothing_features != well_analysis_results[selected_well]["smoothing"] or
    min_temp != well_analysis_results[selected_well]["min_temp"] or
    max_temp != well_analysis_results[selected_well]["max_temp"]
)

# check if saved data has valid plotting data (not None values from atypical wells)
saved_data = well_analysis_results[selected_well]
saved_data_has_plot_data = (
    saved_data.get("full_well_data") is not None and
    saved_data.get("x_spline") is not None and
    saved_data.get("y_spline") is not None
)

if current_settings_differ or not saved_data_has_plot_data:
    # Calculate fresh analysis data when settings changed or saved data lacks plotting data
    data = SessionStateManager.get_value("data")
    avg_control_tm = SessionStateManager.get_value("avg_control_tm")
    
    analysis_results = get_dsf_curve_features(
        data=data[data["well_position"] == selected_well],
        min_temp=min_temp,
        max_temp=max_temp,
        smoothing=smoothing_features,
        avg_control_tm=avg_control_tm,
    )
    
    current_well_data = {
        "tm": analysis_results["tm"],
        "delta_tm": analysis_results["delta_tm"],
        "min_fluorescence": analysis_results["min_fluorescence"],
        "max_fluorescence": analysis_results["max_fluorescence"],
        "fluorescence_range": analysis_results["max_fluorescence"] - analysis_results["min_fluorescence"],
        "max_slope": analysis_results["max_derivative_value"],
        "smoothing": smoothing_features,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "full_well_data": analysis_results["full_well_data"],
        "x_spline": analysis_results["x_spline"],
        "y_spline": analysis_results["y_spline"],
        "y_spline_derivative": analysis_results["y_spline_derivative"],
        "temp_at_min": analysis_results["temp_at_min"],
        "temp_at_max": analysis_results["temp_at_max"],
        "max_derivative_value": analysis_results["max_derivative_value"],
    }
else:
    # use saved analysis data when settings haven't changed and data is valid
    current_well_data = well_analysis_results[selected_well]

fig = create_melt_curve_plot_from_features(current_well_data)

plot_col, metrics_col = st.columns([0.85, 0.15])

with plot_col:
    st.plotly_chart(fig, use_container_width=True)

with metrics_col:
    st.subheader("Analysis Results")
    st.metric(
        "Tm (°C)",
        f"{current_well_data['tm']:.2f}",
    )
    st.metric(
        "ΔTm (K)",
        f"{current_well_data['delta_tm']:.2f}",
    )
    st.metric(
        "Min Fluorescence",
        f"{current_well_data['min_fluorescence']:.2f}",
    )
    st.metric(
        "Max Fluorescence",
        f"{current_well_data['max_fluorescence']:.2f}",
    )
    st.metric(
        "Fluorescence Range",
        f"{current_well_data['fluorescence_range']:.2f}",
    )
    st.metric(
        "Max Slope",
        f"{current_well_data['max_slope']:.3f}",
    )
