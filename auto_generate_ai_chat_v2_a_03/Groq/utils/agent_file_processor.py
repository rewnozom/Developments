import os
import openpyxl
from pathlib import Path

def process_files(input_dir, output_dir, ai_agent_function, file_extensions):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    excel_data = []

    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith(tuple(file_extensions)):  # Process only specified file types
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, input_dir)
            
            # Read the entire file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get input from AI agent (one-sentence description of the code)
            ai_description = ai_agent_function(relative_path, file, content)
            
            # Prepend "Create " to the AI's description
            ai_input = f"Create {ai_description}"

            # Append data for Excel
            excel_data.append({
                "input": ai_input,
                "output": content
            })

    create_excel(excel_data, os.path.join(output_dir, "training_data.xlsx"))

def create_excel(data, output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Training Data"

    headers = ["input", "output"]
    ws.append(headers)

    for row in data:
        ws.append([row[header] for header in headers])

    wb.save(output_file)

# Example AI agent function (replace with actual implementation)
def dummy_ai_agent(file_path, file_name, content):
    # This is a placeholder. Your actual AI should generate a one-sentence description.
    return "this module that [insert concise description of main functionality]."

# Usage
input_directory = "./input_data"
output_directory = "./output"
file_extensions = ('.py', '.js', '.java', '.cpp')  # Add or remove extensions as needed
process_files(input_directory, output_directory, dummy_ai_agent, file_extensions)