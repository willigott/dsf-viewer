from typing import Any, List

import streamlit as st


class SessionStateManager:
    """Manages session state initialization and utilities."""
    
    # default values for all session state variables
    DEFAULT_VALUES = {
        # data-related state
        "data": None,
        "file_format": None,
        "available_wells": [],
        "plate_size": None,
        "min_temp": None,
        "max_temp": None,
        
        # control analysis state
        "control_wells": [],
        "selected_control": None,
        "avg_control_tm": None,
        "control_results": None,
        "smoothing_control": 0.01,
        "plot_data": None,
        
        # detection thresholds
        "dtw_lower_threshold": 0.5,
        "dtw_upper_threshold": 1.5,
        
        # results state
        "results": None,
        
        # dtw-related state (for atypical well detection)
        "dtw_distances": None,
        "plate_data": None,
        "plate_cols": None,
        "plate_rows": None,
        "dtw_filled_wells": [],
        "dtw_undecided_wells": [],
        "dtw_empty_wells": [],
        "well_analysis_results": {},
        
        # well analysis state
        "smoothing_features": 0.01,
        "selected_well": None,
        
        # well review state
        "smoothing_review": 0.01,
        "current_well_index": 0,
        "reviewed_wells": set(),
        "reviewed_as_empty": set(),
        "reviewed_as_filled": set(),
        "initial_wells_to_review": [],
        "current_review_filters": None,
    }
    
    @classmethod
    def initialize_all(cls) -> None:
        """Initialize all session state variables with their default values."""
        for key, default_value in cls.DEFAULT_VALUES.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @classmethod
    def initialize_keys(cls, keys: List[str]) -> None:
        """Initialize only specific session state keys."""
        for key in keys:
            if key in cls.DEFAULT_VALUES and key not in st.session_state:
                st.session_state[key] = cls.DEFAULT_VALUES[key]
    
    @classmethod
    def reset_key(cls, key: str) -> None:
        """Reset a specific session state key to its default value."""
        if key in cls.DEFAULT_VALUES:
            st.session_state[key] = cls.DEFAULT_VALUES[key]
    
    @classmethod
    def reset_all(cls) -> None:
        """Reset all session state variables to their default values."""
        for key, default_value in cls.DEFAULT_VALUES.items():
            st.session_state[key] = default_value    

    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """Get a session state value with optional fallback default."""
        return st.session_state.get(key, default or cls.DEFAULT_VALUES.get(key))
    
    @classmethod
    def set_value(cls, key: str, value: Any) -> None:
        """Set a session state value."""
        st.session_state[key] = value
    
    @classmethod
    def has_data(cls) -> bool:
        """Check if data has been uploaded."""
        return st.session_state.get("data") is not None
    
    @classmethod
    def has_control_analysis(cls) -> bool:
        """Check if control analysis has been completed."""
        return (st.session_state.get("selected_control") is not None and 
                st.session_state.get("avg_control_tm") is not None)
    
    @classmethod
    def has_results(cls) -> bool:
        """Check if analysis results are available."""
        return st.session_state.get("results") is not None
    
    @classmethod
    def has_well_analysis(cls) -> bool:
        """Check if well analysis has been completed."""
        well_analysis_results = st.session_state.get("well_analysis_results", {})
        return len(well_analysis_results) > 0


# convenience functions for common operations
def init_session_state() -> None:
    """Initialize all session state variables."""
    SessionStateManager.initialize_all()


 