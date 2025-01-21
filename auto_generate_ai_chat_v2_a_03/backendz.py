import os
import shutil
import json
import time
import re
import logging
import numpy as np
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from config import API_KEY, ENABLE_HISTORY, ENABLE_MEMORY, MEMORY_FILE, SYSTEM_PROMPT_FILE

logging.basicConfig(level=logging.DEBUG)

CHAT_HISTORY_FOLDER = "./Workspace/chat_history"
DATA_MEMORY_FOLDER = "./Workspace/datamemory"

class AgentGroq:
    def __init__(self):
        self.initialize_groq_chat()
        self.initialize_memory()
        self.initialize_prompt_template()

    def initialize_groq_chat(self):
        try:
            self.groq_chat = ChatGroq(api_key=API_KEY, model_name="llama3-8b-8192")
        except Exception as e:
            logging.error(f"Failed to initialize ChatGroq: {e}")
            return
        self.system_prompt = load_system_prompt()

    def initialize_memory(self):
        self.memory = None
        self.additional_memory = []
        if ENABLE_MEMORY:
            conversational_memory_length = 1
            self.memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
            self.additional_memory = load_memory()

    def initialize_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        self.conversation_chain = LLMChain(
            llm=self.groq_chat,
            prompt=self.prompt_template,
            verbose=False,
            memory=self.memory if ENABLE_MEMORY else None,
        )

    def send_message(self, user_message, system_message, prefix_texts_first, prefix_texts_last):
        try:
            save_system_prompt(system_message)
            user_message = " ".join(prefix_texts_first) + " " + user_message + " " + " ".join(prefix_texts_last)

            file_contents = self.handle_file_patterns(user_message)
            messages = self.prepare_messages(system_message, user_message)
            embeddings = self.load_embeddings(file_contents)

            if embeddings:
                logging.debug(f"Loaded embeddings: {embeddings}")

            response = self.get_response_from_groq(messages, user_message)
            self.save_chat_log(user_message, response)
            self.handle_code_block_saving(response, user_message)
            
            return response, file_contents
        except Exception as e:
            logging.error(f"Error in send_message: {e}")
            return f"An error occurred: {e}", {}

    def handle_file_patterns(self, user_message):
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

        for match in update_matches:
            file_content = read_file_from_datamemory(match)
            if file_content:
                file_contents[match] = file_content
                user_message = user_message.replace(f"@@{match}", f"```{self.get_file_language(match)}\n{file_content}\n```")
                update_code_block_in_datamemory(match, file_content)

        return file_contents

    def get_file_language(self, filename):
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

    def prepare_messages(self, system_message, user_message):
        messages = [{"role": "system", "content": system_message}]
        if ENABLE_MEMORY:
            messages += self.additional_memory
        messages.append({"role": "user", "content": user_message})
        return messages

    def load_embeddings(self, file_contents):
        embedding_files = [file for file in file_contents.keys() if file.endswith('.npy')]
        embeddings = []
        for embedding_file in embedding_files:
            embedding = load_embedding(os.path.join("Workspace/embedding/output", embedding_file))
            if embedding is not None:
                embeddings.append(embedding)
        return embeddings

    def get_response_from_groq(self, messages, user_message):
        try:
            response = self.conversation_chain.predict(human_input=user_message)
            logging.debug(f"Response from Groq: {response}")
            return response
        except Exception as e:
            logging.error(f"Error during message prediction: {e}")
            return "An error occurred while processing your request."

    def save_chat_log(self, user_message, response):
        if ENABLE_HISTORY:
            chat_content = f"You: {user_message}\nAssistant: {response}\n"
            filename = f"chat_{int(time.time())}.txt"
            filepath = os.path.join(CHAT_HISTORY_FOLDER, filename)
            try:
                with open(filepath, 'w') as file:
                    file.write(chat_content)
            except Exception as e:
                logging.error(f"Error saving chat log: {e}")

    def extract_code_blocks(self, response):
        code_blocks = []
        pattern = re.compile(r"```(?:python|markdown|json|js)?\n(.*?)```", re.DOTALL)
        matches = pattern.findall(response)
        for match in matches:
            code_blocks.append(match.strip())
        return code_blocks

    def handle_code_block_saving(self, response, user_message):
        code_blocks = self.extract_code_blocks(response)
        if code_blocks:
            for code_block in code_blocks:
                logging.debug(f"Extracted code block:\n{code_block}")

                file_name_match = re.search(r'#(\w+\.\w+)', user_message)
                if file_name_match:
                    file_name = file_name_match.group(1)
                    if '@@' in user_message:
                        update_code_block_in_datamemory(file_name, code_block)
                    else:
                        save_code_block(code_block, filename=file_name)
                else:
                    logging.warning("No file name found in user message. Skipping code block saving.")

# Utility functions
def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return []

def add_memory(memory_entry, additional_memory):
    additional_memory.append({"role": "human", "content": memory_entry})
    save_memory(additional_memory)

def remove_memory(index, additional_memory):
    if 0 <= index < len(additional_memory):
        del additional_memory[index]
        save_memory(additional_memory)

def save_system_prompt(prompt):
    with open(SYSTEM_PROMPT_FILE, 'w') as f:
        f.write(prompt)

def load_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_FILE):
        with open(SYSTEM_PROMPT_FILE, 'r') as f:
            return f.read()
    return ""

def save_code_block(code_block, filename):
    filepath = os.path.join(DATA_MEMORY_FOLDER, filename)
    with open(filepath, 'w') as f:
        f.write(code_block)

def update_code_block_in_datamemory(filename, code_block):
    filepath = os.path.join(DATA_MEMORY_FOLDER, filename)
    with open(filepath, 'w') as f:
        f.write(code_block)

def read_file_from_datamemory(filename):
    filepath = os.path.join(DATA_MEMORY_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return None

def load_embedding(file_path):
    try:
        return np.load(file_path)
    except Exception as e:
        logging.error(f"Error loading embedding from {file_path}: {e}")
        return None

def load_chat_history():
    chat_logs = []
    for filename in os.listdir(CHAT_HISTORY_FOLDER):
        if filename.endswith('.txt'):
            with open(os.path.join(CHAT_HISTORY_FOLDER, filename), 'r') as f:
                chat_logs.append((filename, f.read()))
    return chat_logs

def rename_chat_log(old_name, new_name):
    old_path = os.path.join(CHAT_HISTORY_FOLDER, old_name)
    new_path = os.path.join(CHAT_HISTORY_FOLDER, new_name)
    os.rename(old_path, new_path)

def delete_chat_log(filename):
    os.remove(os.path.join(CHAT_HISTORY_FOLDER, filename))

def upload_file(file_path):
    try:
        shutil.copy(file_path, DATA_MEMORY_FOLDER)
        logging.info(f"File {os.path.basename(file_path)} uploaded to datamemory.")
        return True
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return False

def list_datamemory_files():
    return os.listdir(DATA_MEMORY_FOLDER)

def rename_datamemory_file(old_name, new_name):
    old_path = os.path.join(DATA_MEMORY_FOLDER, old_name)
    new_path = os.path.join(DATA_MEMORY_FOLDER, new_name)
    os.rename(old_path, new_path)

def delete_datamemory_file(filename):
    os.remove(os.path.join(DATA_MEMORY_FOLDER, filename))

# Initialize necessary folders
if not os.path.exists(CHAT_HISTORY_FOLDER):
    os.makedirs(CHAT_HISTORY_FOLDER)

if not os.path.exists(DATA_MEMORY_FOLDER):
    os.makedirs(DATA_MEMORY_FOLDER)


def new_chat():
    # This function doesn't need to do anything in the backend
    # It's mainly for resetting the UI, which will be handled in the frontend
    pass

def count_tokens_in_string(string, encoding_name="cl100k_base"):
    # This function was mentioned in the original code but not implemented
    # You'll need to implement or import a tokenizer to count tokens
    # For example, using the tiktoken library:
    import tiktoken
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

def count_tokens_in_messages(messages, encoding_name="cl100k_base"):
    # Similarly, implement token counting for a list of messages
    import tiktoken
    encoding = tiktoken.get_encoding(encoding_name)
    total_tokens = 0
    for message in messages:
        total_tokens += len(encoding.encode(message['content']))
    return total_tokens

def save_to_excel(data, filename):
    # This function was mentioned but not implemented
    # You'll need to implement Excel saving functionality
    # For example, using the openpyxl library:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for row in data:
        ws.append(row)
    wb.save(filename)