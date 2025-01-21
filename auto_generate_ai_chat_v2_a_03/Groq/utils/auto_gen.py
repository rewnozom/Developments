import os
import re
import logging
from openpyxl import Workbook
from openai import OpenAI

def read_system_prompt(filename='system_prompt.md'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: {filename} not found in {script_dir}. Using default system message.")
        return "You are a helpful assistant that provides information in table format."

def parse_tables(text):
    # Ensure text is UTF-8 encoded
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    elif not isinstance(text, str):
        text = str(text)
    
    tables = []
    current_table = []
    for line in text.split('\n'):
        if line.strip() == '---':
            if current_table:
                tables.append(current_table)
                current_table = []
        elif line.strip().startswith('|'):
            current_table.append([cell.strip() for cell in line.split('|')[1:-1]])
    if current_table:
        tables.append(current_table)
    return tables

def save_to_excel(tables, base_filename='auto_llm_data_'):
    base_path = f'./llm_data_gen/{base_filename}'
    os.makedirs('./llm_data_gen', exist_ok=True)
    index = 1
    while os.path.exists(f'{base_path}{index:03d}.xlsx'):
        index += 1
    filename = f'{base_path}{index:03d}.xlsx'

    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    for i, table in enumerate(tables):
        ws = wb.create_sheet(title=f'Table {i+1}')
        for row in table:
            # Ensure each cell is properly encoded as UTF-8
            encoded_row = [cell.encode('utf-8').decode('utf-8') if isinstance(cell, str) else cell for cell in row]
            ws.append(encoded_row)

    wb.save(filename)
    return filename

def process_llm_output(output, base_filename='auto_llm_data_'):
    # Ensure output is UTF-8 encoded
    if isinstance(output, bytes):
        output = output.decode('utf-8')
    elif not isinstance(output, str):
        output = str(output)
    
    output = re.sub(r'```python\n|```', '', output)
    tables = parse_tables(output)
    saved_file = save_to_excel(tables, base_filename)
    return saved_file

def generate_data(api_key, system_prompt, user_prompt, model, temperature, max_tokens):
    client = OpenAI(api_key=api_key)

    try:
        # Ensure prompts are UTF-8 encoded
        system_prompt = system_prompt.encode('utf-8').decode('utf-8')
        user_prompt = user_prompt.encode('utf-8').decode('utf-8')
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response_content = completion.choices[0].message.content
        # Ensure response is UTF-8 encoded
        return response_content.encode('utf-8').decode('utf-8')
    except Exception as e:
        logging.error(f"Error in generate_data: {str(e)}")
        return None

def generate_data_and_save_excel(response, base_filename='auto_llm_data_'):
    """
    Generate structured data from the response and save it as an Excel file.
    
    :param response: The response from the AI model (assumed to be UTF-8 encoded)
    :param base_filename: Base filename for the Excel file
    :return: Path to the saved Excel file or None if no data was generated
    """
    try:
        # Ensure response is UTF-8 encoded
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        elif not isinstance(response, str):
            response = str(response)
        
        tables = parse_tables(response)
        if tables:
            saved_file = save_to_excel(tables, base_filename)
            logging.info(f"Data saved to {saved_file}")
            return saved_file
        else:
            logging.warning("No structured data found in the response.")
            return None
    except Exception as e:
        logging.error(f"Error in generate_data_and_save_excel: {str(e)}")
        return None

# Add a function to log errors with UTF-8 encoding
def log_error(message):
    log_file = 'error_log.txt'
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")