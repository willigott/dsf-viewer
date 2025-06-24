import re
from typing import List


def natural_sort_wells(well_ids: List[str]) -> List[str]:
    """
    Sort well IDs in natural order (A1, A2, A3, ..., A10, A11, ..., B1, B2, ...).
    
    Args:
        well_ids: List of well IDs to sort (e.g., ['A1', 'A10', 'A2', 'B1'])
        
    Returns:
        List of well IDs sorted in natural order
        
    Example:
        >>> natural_sort_wells(['A1', 'A10', 'A2', 'B1'])
        ['A1', 'A2', 'A10', 'B1']
    """
    def well_sort_key(well_id: str):
        """Generate a sort key that handles alphanumeric well IDs naturally."""
        # Split the well ID into letter and number parts
        match = re.match(r'([A-Z]+)(\d+)', well_id.upper())
        if match:
            letter_part, number_part = match.groups()
            return (letter_part, int(number_part))
        else:
            # Fallback for non-standard well IDs
            return (well_id.upper(), 0)
    
    return sorted(well_ids, key=well_sort_key) 