import os
import customtkinter as ctk
from tkinter import StringVar, DoubleVar, IntVar, END
from tkinter.messagebox import showinfo
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from config import Config
from models import get_model
import threading
from openpyxl import Workbook
from memory.history import ShortTermHistory
from custom_logging.logger import logger
from Groq.ui.create_ui import create_ui, update_token_counter
from Groq.utils.auto_gen import generate_data_and_save_excel
from Groq.utils.code_analysis_tool import start_code_analysis  # Import the new tool

import re
import json
import time

from Groq.utils import (
    save_memory,
    load_memory,
    add_memory,
    remove_memory,
    save_system_prompt,
    load_system_prompt,
    save_code_block,
    update_code_block_in_datamemory,
    read_file_from_datamemory,
    save_to_excel,
    load_history,
    load_selected_chat,
    rename_selected_chat,
    delete_selected_chat,
    new_chat,
    load_embedding,
    insert_file_name,
    auto_suggest_files,
    KeyBindings,
    show_code_window,
    copy_to_clipboard,
    handle_file_drop
)
from shared_variables import get_model_var, get_temperature_var, get_max_tokens_var, get_system_prompt_var

# Initialize the configuration
config = Config()

class AgentGroq(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.short_term_history = ShortTermHistory()
        self.initialize_clients()
        self.initialize_memory()
        self.initialize_ui_components()
        self.initialize_code_analysis_tool()  # Initialize the code analysis tool
        
        # Initialize variables using config values
        get_model_var().set(config.CHAT_MODEL)
        get_temperature_var().set(config.CHAT_TEMPERATURE)
        get_max_tokens_var().set(8192)  # Adjust if necessary
        self.system_prompt = get_system_prompt_var().get()  # Use selected system prompt
        
        self.auto_system_prompt = self.load_auto_system_prompt()
        

    def load_auto_system_prompt(self):
        """Load the auto system prompt from file."""
        try:
            with open("./auto_system_prompt.md", "r") as file:
                return file.read()
        except FileNotFoundError:
            logger.error("auto_system_prompt.md not found")
            return "You are a helpful assistant."

    def initialize_memory(self):
        """Initialize the memory components if enabled."""
        self.memory = None
        self.additional_memory = []
        if config.ENABLE_MEMORY:
            conversational_memory_length = 1
            self.memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
            self.additional_memory = load_memory()
            logger.info("Memory initialized")

    def initialize_prompt_template(self):
        """Initialize the prompt template for conversation."""
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{human_input}")
            ]
        )

        self.conversation_chain = LLMChain(
            llm=self.current_client,
            prompt=self.prompt_template,
            verbose=False,
            memory=self.memory if config.ENABLE_MEMORY else None,
        )
        logger.info("Prompt template and conversation chain initialized")

    def initialize_clients(self):
        """Initialize the AI model clients based on the selected model."""
        self.current_client = get_model(config.CHAT_MODEL, temperature=config.CHAT_TEMPERATURE)
        logger.info(f"Initialized client for model: {config.CHAT_MODEL}")

    def initialize_ui_components(self):
        """Initialize the UI components."""
        self.memory_entry_var = StringVar(value="")
        self.temperature_entry_var = StringVar(value=f"{config.CHAT_TEMPERATURE:.2f}")
        self.max_tokens_entry_var = StringVar(value="8192")  # Adjust if necessary
        
        self.start_continuous_button = ctk.CTkButton(self, text="Start Continuous Generation", command=self.start_continuous_generation)
        self.start_continuous_button.pack(pady=5)

        self.stop_continuous_button = ctk.CTkButton(self, text="Stop Continuous Generation", command=self.stop_continuous_generation)
        self.stop_continuous_button.pack(pady=5)
        self.stop_continuous_button.configure(state="disabled")

        self.chat_display, self.user_message_var, self.token_counter_label, self.use_prefix_vars, self.prefix_position_vars, self.autog_var = create_ui(
            self, 
            self.send_message, 
            auto_suggest_files, 
            get_model_var(), 
            get_temperature_var(), 
            get_max_tokens_var(), 
            get_system_prompt_var(), 
            self.memory_entry_var, 
            self.temperature_entry_var, 
            self.max_tokens_entry_var
        )
        logger.info("UI components initialized")

    def initialize_code_analysis_tool(self):
        """Initialize the code analysis tool."""
        # Example: Set up a button to start the code analysis process
        self.start_code_analysis_button = ctk.CTkButton(
            self, 
            text="Start Code Analysis", 
            command=lambda: start_code_analysis(
                input_dir=self.input_dir_var.get(), 
                output_dir=self.output_dir_var.get(), 
                extensions=self.extensions_var.get(), 
                system_prompt=self.system_prompt_var.get(), 
                progress_var=self.progress_var, 
                results_text=self.results_text
            )
        )
        self.start_code_analysis_button.pack(pady=10)
        logger.info("Code analysis tool initialized")

    def save_chat_log(self):
        """Save the chat log if history is enabled."""
        if config.ENABLE_HISTORY:
            chat_content = self.chat_display.get("1.0", END).strip()
            if chat_content:
                filename = f"chat_{int(time.time())}.txt"
                filepath = os.path.join("Workspace/chat_history", filename)
                try:
                    with open(filepath, 'w') as file:
                        file.write(chat_content)
                    logger.info(f"Chat log saved to {filepath}")
                except Exception as e:
                    logger.error(f"Error saving chat log: {e}")

    def send_message(self, event=None):
        try:
            save_system_prompt(get_system_prompt_var().get())
            system_message = self.auto_system_prompt if self.autog_var.get() else get_system_prompt_var().get()
            user_message = self.user_message_var.get("1.0", END).strip()

            # Add event to short-term history
            self.short_term_history.add_event({"type": "user_message", "content": user_message})
            logger.info(f"User message: {user_message}")

            # Load the prefix text from files if the checkboxes are checked
            prefix_texts_first = []
            prefix_texts_last = []
            for i, use_prefix_var in enumerate(self.use_prefix_vars):
                if use_prefix_var.get():
                    prefix_file = os.path.join("Workspace", "prefix", f"check{i+1}.md")
                    if os.path.exists(prefix_file):
                        with open(prefix_file, "r", encoding='utf-8') as f:
                            prefix_text = f.read().strip()
                            if self.prefix_position_vars[i].get():
                                prefix_texts_first.append(prefix_text)
                            else:
                                prefix_texts_last.append(prefix_text)

            # Combine the prefixes and user message
            user_message = " ".join(prefix_texts_first) + " " + user_message + " " + " ".join(prefix_texts_last)

            # Handle file patterns and update the user message with file contents
            file_contents = self.handle_file_patterns(user_message)
            user_message = self.user_message_var.get("1.0", END).strip()  # Get the updated user message

            messages = self.prepare_messages(system_message, user_message)
            embeddings = self.load_embeddings(file_contents)

            if embeddings:
                logger.debug(f"Loaded embeddings: {embeddings}")

            # Use the current client (AI model) to get the response
            response = self.current_client(messages)
            if isinstance(response, str):
                response_content = response
            elif isinstance(response, dict) and 'content' in response:
                response_content = response['content']
            elif hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)

            self.display_response(response_content, file_contents)
            self.save_chat_log()

            # Update token counter
            update_token_counter(self.user_message_var, self.token_counter_label)
            
            # Handle saving the code block
            self.handle_code_block_saving(response_content, user_message)

            # Handle saving data lists
            self.handle_data_list_saving(response_content)

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            showinfo("Error", f"An error occurred: {e}")
            self.display_response("I apologize, but an error occurred while processing your request. Please try again or check the application logs for more information.", {})

        finally:
            # Clear the user message input area
            self.user_message_var.delete("1.0", END)

    def handle_data_list_saving(self, response):
        """Handle saving of data lists in the response."""
        try:
            saved_file = generate_data_and_save_excel(response)
            if saved_file:
                logger.info(f"Data list saved to {saved_file}")
                showinfo("Data Saved", f"Data list saved to {saved_file}")
            else:
                logger.warning("No structured data found in the response.")
        except Exception as e:
            logger.error(f"Error in handling data list saving: {e}")
            showinfo("Error", f"An error occurred while saving data: {e}")

    def parse_tables(self, text):
        """Parse tables from the text."""
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

    def save_to_excel(self, tables, base_filename='auto_llm_data_'):
        """Save tables to an Excel file in the ./llm_data_gen directory."""
        os.makedirs("./llm_data_gen", exist_ok=True)
        base_path = f'./llm_data_gen/{base_filename}'
        index = 1
        while os.path.exists(f'{base_path}{index:03d}.xlsx'):
            index += 1
        filename = f'{base_path}{index:03d}.xlsx'

        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet

        for i, table in enumerate(tables):
            ws = wb.create_sheet(title=f'Table {i+1}')
            for row in table:
                ws.append(row)

        wb.save(filename)
        return filename

    def start_continuous_generation(self):
        """Start continuous data generation."""
        self.continuous_generation = True
        self.start_continuous_button.configure(state="disabled")
        self.stop_continuous_button.configure(state="normal")
        threading.Thread(target=self.continuous_generation_loop, daemon=True).start()

    def stop_continuous_generation(self):
        """Stop continuous data generation."""
        self.continuous_generation = False
        self.start_continuous_button.configure(state="normal")
        self.stop_continuous_button.configure(state="disabled")

    def continuous_generation_loop(self):
        """Continuous data generation loop."""
        while self.continuous_generation:
            try:
                response = self.generate_data()
                self.handle_data_list_saving(response)
                time.sleep(1)  # Add a small delay to prevent overwhelming the system
            except Exception as e:
                logger.error(f"Error in continuous generation: {e}")
                self.stop_continuous_generation()
                showinfo("Error", f"Continuous generation stopped due to an error: {e}")
                break

    def generate_data(self):
        """Generate new high-quality training dataset following the system prompt."""
        system_message = self.auto_system_prompt if self.autog_var.get() else get_system_prompt_var().get()
        messages = self.prepare_messages(system_message, "Generate new high-quality training dataset following the system prompt.")
        response = self.current_client(messages)
        
        return generate_data_and_save_excel(response)

    def extract_data_lists(self, text):
        """Extract data lists from the text."""
        pattern = r'#\s*(\d+)\s*kolumner\s*\n\n\|(.*?)\|\n\|[-\s|]+\n((?:\|.*?\|\n)+)'
        matches = re.findall(pattern, text, re.DOTALL)
        data_lists = []
        for match in matches:
            columns = [col.strip() for col in match[1].split('|') if col.strip()]
            rows = [
                [cell.strip() for cell in row.split('|')[1:-1]]
                for row in match[2].strip().split('\n')
            ]
            data_lists.append({'columns': columns, 'rows': rows})
        return data_lists

    def save_data_list_to_excel(self, data_list, index):
        """Save a data list to an Excel file."""
        base_filename = f'auto_llm_data_{int(time.time())}_{index+1}'
        filename = f'{base_filename}.xlsx'
        i = 1
        while os.path.exists(filename):
            filename = f'{base_filename}_{i}.xlsx'
            i += 1

        return save_to_excel([data_list['columns']] + data_list['rows'], filename)

    def handle_file_patterns(self, user_message):
        """Handle @filename and @@filename patterns in the user message."""
        file_pattern = r'@(\w+\.\w+)'
        update_file_pattern = r'@@(\w+\.\w+)'
        matches = re.findall(file_pattern, user_message)
        update_matches = re.findall(update_file_pattern, user_message)
        file_contents = {}

        for match in matches:
            if match not in file_contents:
                file_content = read_file_from_datamemory(match)
                if file_content:
                    file_contents[match] = file_content
                    user_message = user_message.replace(f"@{match}", f"```{self.get_file_language(match)}\n{file_content}\n```")
                    logger.info(f"File content added for {match}")

        for match in update_matches:
            file_content = read_file_from_datamemory(match)
            if file_content:
                file_contents[match] = file_content
                user_message = user_message.replace(f"@@{match}", f"```{self.get_file_language(match)}\n{file_content}\n```")
                update_code_block_in_datamemory(match, file_content)
                logger.info(f"File content updated for {match}")

        # Update the text box with the modified user message
        self.user_message_var.delete("1.0", END)
        self.user_message_var.insert("1.0", user_message)

        # Update token counter
        update_token_counter(self.user_message_var, self.token_counter_label)

        return file_contents

    def get_file_language(self, filename):
        """Determine the language of the file for code block formatting."""
        if filename.endswith('.py'):
            return 'python'
        elif filename.endswith('.md'):
            return 'markdown'
        elif filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.js'):
            return 'js'
        elif filename.endswith('.ts'):
            return 'ts'
        else:
            return ''

    def append_file_contents(self, user_message):
        """Append file contents to the user message if referenced."""
        file_pattern = r'@(\w+\.\w+)'
        matches = re.findall(file_pattern, user_message)
        file_contents = {}
        for match in matches:
            file_content = read_file_from_datamemory(match)
            if file_content:
                file_contents[match] = file_content
                user_message += f"\n\nContent of {match}:\n```{self.get_file_language(match)}\n{file_content}\n```"
                logger.info(f"File content appended for {match}")
        return file_contents

    def prepare_messages(self, system_message, user_message):
        messages = [{"role": "system", "content": system_message}]
        if config.ENABLE_MEMORY:
            messages += [{"role": m["role"], "content": m["content"]} for m in self.additional_memory if m["content"]]
        messages.append({"role": "user", "content": user_message})
        return [m for m in messages if m["content"]]  # Filter out any empty messages

    def load_embeddings(self, file_contents):
        """Load embeddings if referenced in the user message."""
        embedding_files = [file for file in file_contents.keys() if file.endswith('.npy')]
        embeddings = []
        for embedding_file in embedding_files:
            embedding = load_embedding(os.path.join("Workspace/embedding/output", embedding_file))
            if embedding is not None:
                embeddings.append(embedding)
                logger.info(f"Embedding loaded for {embedding_file}")
        return embeddings

    def get_response_from_groq(self, messages, user_message):
        """Get the response from the Groq chat client."""
        try:
            response = self.current_client(messages)
            logger.debug(f"Response from Groq: {response}")
            return response
        except Exception as e:
            logger.error(f"Error during message prediction: {e}")
            return "An error occurred while processing your request."

    def extract_code_blocks(self, response):
        """Extract code blocks from the response."""
        code_blocks = []
        pattern = re.compile(r"```(?:python|markdown|json|js)?\n(.*?)```", re.DOTALL)
        matches = pattern.findall(response)
        for match in matches:
            code_blocks.append(match.strip())
        return code_blocks

    def display_response(self, response, file_contents):
        try:
            self.chat_display.insert(ctk.END, f"You: {self.user_message_var.get('1.0', END).strip()}\n")
            response_content = response.encode('utf-8').decode('utf-8') if isinstance(response, str) else str(response)
            self.chat_display.insert(ctk.END, f"Assistant: {response_content}\n")

            code_blocks = self.extract_code_blocks(response_content)
            if code_blocks:
                for code_block in code_blocks:
                    logger.debug(f"Extracted code block:\n{code_block}")
                    show_code_window(code_block)
                    response_content = response_content.replace(code_block, f"\n[Code block shown separately]\n")

            for match in file_contents.keys():
                if match in response_content:
                    code_block = next((block for block in code_blocks if match in block), None)
                    if code_block:
                        logger.debug(f"Extracted update code block for {match}:\n{code_block}")
                        update_code_block_in_datamemory(match, code_block)
                        save_code_block(code_block, filename=match)

            self.user_message_var.delete("1.0", END)
            logger.info("Response displayed and code blocks handled")
        except Exception as e:
            logger.error(f"Error in display_response: {e}")

    def handle_code_block_saving(self, response, user_message):
        """Save the code block if Groq provides an updated module."""
        code_blocks = self.extract_code_blocks(response)
        if code_blocks:
            for code_block in code_blocks:
                logger.debug(f"Extracted code block:\n{code_block}")

                # Determine the file name based on user message with `#`
                file_name_match = re.search(r'#(\w+\.\w+)', user_message)
                if file_name_match:
                    file_name = file_name_match.group(1)
                    if '@@' in user_message:
                        update_code_block_in_datamemory(file_name, code_block)
                        logger.info(f"Code block updated in datamemory: {file_name}")
                    else:
                        save_code_block(code_block, filename=file_name)
                        logger.info(f"Code block saved: {file_name}")
                else:
                    logger.warning("No file name found in user message. Skipping code block saving.")

