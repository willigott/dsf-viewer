from typing import Dict, List

PAGE_STATE_REQUIREMENTS: Dict[str, List[str]] = {
    "upload_data": [
        "data",
        "file_format", 
        "available_wells",
        "plate_size",
        "min_temp",
        "max_temp"
    ],
    
    "control_analysis": [
        "data",
        "file_format",
        "available_wells", 
        "control_wells",
        "selected_control",
        "avg_control_tm"
    ],
    
    "detect_atypical_wells": [
        "data",
        "available_wells",
        "control_wells",
        "selected_control",
        "dtw_lower_threshold",
        "dtw_upper_threshold"
    ],
    
    "well_analysis": [
        "data",
        "available_wells",
        "control_wells", 
        "selected_control",
        "avg_control_tm",
        "dtw_filled_wells"
    ],
    
    "well_review": [
        "data",
        "available_wells",
        "avg_control_tm",
        "well_analysis_results",
        "dtw_filled_wells",
        "dtw_undecided_wells",
        "dtw_empty_wells"
    ],
    
    "summary_and_download": [
        "data",
        "available_wells",
        "control_wells",
        "avg_control_tm",
        "well_analysis_results",
        "plate_size"
    ]
}

# define page dependencies (which pages must be completed before this page)
PAGE_DEPENDENCIES: Dict[str, List[str]] = {
    "upload_data": [],
    "control_analysis": ["upload_data"],
    "detect_atypical_wells": ["upload_data", "control_analysis"], 
    "well_analysis": ["upload_data", "control_analysis", "detect_atypical_wells"],
    "well_review": ["upload_data", "control_analysis", "well_analysis"],
    "summary_and_download": ["upload_data", "control_analysis", "well_analysis"]
}


def get_page_requirements(page_name: str) -> List[str]:
    """Get the session state requirements for a specific page."""
    return PAGE_STATE_REQUIREMENTS.get(page_name, [])


def get_page_dependencies(page_name: str) -> List[str]:
    """Get the page dependencies for a specific page."""
    return PAGE_DEPENDENCIES.get(page_name, []) 