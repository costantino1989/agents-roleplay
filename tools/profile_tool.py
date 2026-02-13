import time
from utils.logger import get_logger

logger = get_logger("ProfileTool")

def save_employee_info(info: str, employee_name: str = None) -> str:
    """
    Save relevant employee information to their profile file.
    Call this whenever the employee provides a clear answer regarding:
    - digital_behavior
    - work_values
    - learning_development
    - diversity_inclusion
    - civic_engagement
    - communication_preferences
    
    Args:
        info (str): The information to save. Format it clearly (e.g., "Work Values: Prefers flexibility over high salary").
        employee_name (str, optional): The name of the employee to personalize the filename.
    """
    start_time = time.perf_counter()
    
    if employee_name:
        filename = f"{employee_name}_profile.md"
    else:
        filename = "employee_profile.md"
        
    logger.info(f"Saving info to {filename}: {info[:50]}...")
    
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"- {info}\n")
        result = "Information saved successfully."
    except Exception as e:
        logger.error(f"Error saving information: {str(e)}")
        result = f"Error saving information: {str(e)}"
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    logger.info(f"Save Profile Tool execution time: {duration:.4f}s")
    
    return result
