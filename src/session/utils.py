import streamlit as st

from .page_states import get_page_dependencies
from .state_manager import SessionStateManager


def init_page(page_name: str) -> None:
    """
    Initialize all session state variables.
    Note: We now initialize all keys regardless of page for simplicity.
    """
    SessionStateManager.initialize_all()


def check_prerequisites(page_name: str) -> bool:
    """
    Check if all prerequisites for a page are met.
    Returns True if the page can be accessed, False otherwise.
    """
    dependencies = get_page_dependencies(page_name)
    
    # Check each dependency
    for dep in dependencies:
        if dep == "upload_data" and not SessionStateManager.has_data():
            return False
        elif dep == "control_analysis" and not SessionStateManager.has_control_analysis():
            return False
        elif dep == "well_analysis" and not SessionStateManager.has_well_analysis():
            return False
    
    return True


def show_prerequisite_warning(page_name: str) -> None:
    """
    Show a warning message if prerequisites are not met.
    """
    dependencies = get_page_dependencies(page_name)
    missing_deps = []
    
    for dep in dependencies:
        if dep == "upload_data" and not SessionStateManager.has_data():
            missing_deps.append("📊 Upload Data")
        elif dep == "control_analysis" and not SessionStateManager.has_control_analysis():
            missing_deps.append("🎯 Control Analysis")
        elif dep == "well_analysis" and not SessionStateManager.has_well_analysis():
            missing_deps.append("🔍 Well Analysis")
    
    if missing_deps:
        st.warning(
            f"⚠️ Please complete the following steps first: {', '.join(missing_deps)}"
        )


def validate_page_access(page_name: str) -> bool:
    """
    Validate that a page can be accessed and show warnings if not.
    Returns True if the page can be accessed, False otherwise.
    """
    # Initialize the page state
    init_page(page_name)
    
    # Check prerequisites
    if not check_prerequisites(page_name):
        show_prerequisite_warning(page_name)
        return False
    
    return True


def get_session_summary() -> dict:
    """
    Get a summary of the current session state for debugging.
    """
    return {
        "has_data": SessionStateManager.has_data(),
        "has_control_analysis": SessionStateManager.has_control_analysis(), 
        "has_results": SessionStateManager.has_results(),
        "has_well_analysis": SessionStateManager.has_well_analysis(),
        "data_shape": getattr(st.session_state.get("data"), "shape", None),
        "num_available_wells": len(st.session_state.get("available_wells", [])),
        "num_control_wells": len(st.session_state.get("control_wells", [])),
        "selected_control": st.session_state.get("selected_control"),
        "plate_size": st.session_state.get("plate_size"),
        "num_well_analysis_results": len(st.session_state.get("well_analysis_results", {})),
    } 