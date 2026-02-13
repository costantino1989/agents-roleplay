rag_schema = {
    "type": "function",
    "function": {
        "name": "rag",
        "description": "Search the knowledge base for behavioral insights about a specific generation and country. Use this to understand values, preferences, and behaviors to formulate better questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "generation": {
                    "type": "string",
                    "enum": ["genz", "millenials"],
                    "description": "The generation to search for: 'genz' or 'millenials'."
                },
                "country": {
                    "type": "string",
                    "description": "The country (e.g., 'Italy', 'France')."
                },
                "query": {
                    "type": "string",
                    "description": "The specific topic to search for (e.g., 'work values', 'digital habits')."
                }
            },
            "required": ["generation", "country", "query"]
        }
    }
}

save_employee_info_schema = {
    "type": "function",
    "function": {
        "name": "save_employee_info",
        "description": "Save relevant employee information to their profile file. Call this whenever the employee provides a clear answer regarding digital_behavior, work_values, learning_development, diversity_inclusion, civic_engagement, or communication_preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "info": {
                    "type": "string",
                    "description": "The information to save. Format it clearly (e.g., 'Work Values: Prefers flexibility over high salary')."
                }
            },
            "required": ["info"]
        }
    }
}
