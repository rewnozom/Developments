import tkinter as tk
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tabs.agentgroq import AgentGroq
from custom_logging.logger import Logger, logger
from shared_variables import get_model_var, get_temperature_var, get_max_tokens_var, get_system_prompt_var

def main():
    # Initialize the logger
    app_logger = Logger()
    logger.info("Initializing Agent Groq application")

    root = tk.Tk()
    root.title("Agent Groq")
    
    # Initialize shared variables
    get_model_var().set("gemma-7b-it")  # Set a default value
    get_temperature_var().set(1.0)  # Set a default value
    get_max_tokens_var().set(12988)  # Set a default value
    get_system_prompt_var().set("")  # Set a default value
    
    try:
        app = AgentGroq(parent=root)
        app.pack(expand=True, fill='both')
        logger.info("Agent Groq UI initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Agent Groq UI: {e}")
        raise

    logger.info("Starting main event loop")
    root.mainloop()
    logger.info("Application closed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unhandled exception in main: {e}")