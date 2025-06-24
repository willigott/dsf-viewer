from bada.utils.reformatting import convert_features_to_plate_format
from bada.visualization import create_heatmap_plot

import numpy as np
import pandas as pd
import streamlit as st

from session.state_manager import SessionStateManager
from session.utils import validate_page_access

st.set_page_config(layout="wide")

st.title("Plate Heatmap View")

if not validate_page_access("summary_and_download"):
    st.stop()

st.info("""
📊 **Review your results**: This heatmap shows the final ΔTm values for all wells. 
If you notice any unexpected patterns or values, you can return to the **Well Analysis** page to
select specific wells, adjust their smoothing parameters and save the updated analysis.
""")

well_analysis_results = SessionStateManager.get_value("well_analysis_results")

plate_size = SessionStateManager.get_value("plate_size")

# create a copy of well_analysis_results and set delta_tm to NaN for empty wells
well_analysis_for_heatmap = {}
for well, data in well_analysis_results.items():
    well_data = data.copy()
    # if well is marked as empty/atypical, set delta_tm to NaN so it appears white in heatmap
    if data.get("is_empty", False):
        well_data["delta_tm"] = np.nan
    well_analysis_for_heatmap[well] = well_data

plate_data, cols, rows = convert_features_to_plate_format(
    well_analysis_for_heatmap,
    plate_size,
    "delta_tm"
)

fig = create_heatmap_plot(
    plate_data,
    cols,
    rows,
    title="ΔTm Values",
    colorbar_title="ΔTm (K)"
)

st.plotly_chart(fig, use_container_width=True)

results_data = []
available_wells = SessionStateManager.get_value("available_wells")
reviewed_wells = SessionStateManager.get_value("reviewed_wells")

for well in available_wells:
    result = {
        "well": well,
        "reviewed": well in reviewed_wells,
        "is_empty": False,
        "tm": None,
        "delta_tm": None,
        "min_fluorescence": None,
        "max_fluorescence": None,
        "fluorescence_range": None,
        "max_slope": None,
        "smoothing": None,
        "min_temp": None,
        "max_temp": None,
    }

    if well in well_analysis_results:
        well_data = well_analysis_results[well]
        result.update(well_data)

    results_data.append(result)

results_df = pd.DataFrame(results_data)
results_df = results_df.drop(
    columns=[
        "x_spline",
        "y_spline",
        "full_well_data",
        "y_spline_derivative",
        # "temp_at_min",
        # "temp_at_max",
        # "max_derivative_value",
    ]
)

# temp solution until it's updated everywhere in the code
results_df = results_df.rename(
    columns={
        "is_empty": "atypical",
    }
)

csv = results_df.to_csv(index=False)

col1, col2, col3 = st.columns(3)
with col2:
    st.download_button(
        label="📥 Download Analysis Results (CSV)", 
        data=csv, 
        file_name="dsf_analysis_results.csv", 
        mime="text/csv",
        type="secondary",
        use_container_width=True
    )
