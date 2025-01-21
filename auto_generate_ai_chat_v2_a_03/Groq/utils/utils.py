import os
import json
import logging
import re
import numpy as np
import pandas as pd
import zipfile
import shutil
import pyperclip
from openai import OpenAI
import customtkinter as ctk
from tkinter import Menu, Toplevel, Text, END, Entry, Label, simpledialog
from tkinter.messagebox import askyesno, showinfo
import tkinter as tk

CHAT_HISTORY_FOLDER = "./Workspace/chat_history"

# Memory management
def save_memory(memory):
    """Save memory to memory.json file."""
    try:
        with open("./Workspace/memory.json", 'w') as file:
            json.dump(memory, file)
        logging.info("Memory successfully saved.")
    except Exception as e:
        logging.error(f"Unexpected error saving memory: {e}")

def load_memory():
    """Load memory from memory.json file."""
    try:
        memory_path = "./Workspace/memory.json"
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as file:
                return json.load(file)
        logging.info("No memory file found.")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error while loading memory: {e}")
    except Exception as e:
        logging.error(f"Unexpected error loading memory: {e}")
    return []

def add_memory(memory_listbox, memory_entry_var, additional_memory):
    """Add an entry to the memory listbox and update the memory file."""
    try:
        memory_entry = memory_entry_var.get()
        if memory_entry.strip():  # Ensure the memory entry is not empty
            additional_memory.append({"role": "system", "content": memory_entry})
            memory_listbox.insert(END, memory_entry)
            memory_entry_var.set("")
            save_memory(additional_memory)
            logging.info(f"Memory entry added: {memory_entry}")
        else:
            logging.warning("Attempted to add an empty memory entry.")
    except Exception as e:
        logging.error(f"Unexpected error adding memory: {e}")

def remove_memory(memory_listbox, additional_memory):
    """Remove selected entries from the memory listbox and update the memory file."""
    try:
        selected_indices = memory_listbox.curselection()
        for index in selected_indices[::-1]:
            removed_entry = additional_memory.pop(index)
            memory_listbox.delete(index)
            logging.info(f"Memory entry removed: {removed_entry}")
        save_memory(additional_memory)
    except Exception as e:
        logging.error(f"Unexpected error removing memory: {e}")

# System prompt management
def save_system_prompt(prompt):
    """Save system prompt to system_prompt.txt file."""
    try:
        prompt_path = "./System_Prompts/Original.md"
        with open(prompt_path, 'w', encoding='utf-8') as file:
            file.write(prompt)
        logging.info("System prompt saved successfully.")
    except Exception as e:
        logging.error(f"Unexpected error saving system prompt: {e}")

def load_system_prompt():
    """Load system prompt from system_prompt.txt file or use the default from Original.md."""
    try:
        prompt_path = "./Workspace/system_prompt.txt"
        default_prompt_path = "./System_Prompts/Original.md"
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as file:
                prompt = file.read()
                logging.info("System prompt loaded successfully from system_prompt.txt.")
                return prompt
        elif os.path.exists(default_prompt_path):
            with open(default_prompt_path, 'r', encoding='utf-8') as file:
                prompt = file.read()
                logging.info("Default system prompt loaded successfully from Original.md.")
                # Save the default prompt to system_prompt.txt for future use
                save_system_prompt(prompt)
                return prompt
        else:
            logging.warning("No system prompt file found. Creating a new one with default content.")
            default_prompt = "You are a helpful, smart, kind, and efficient AI assistant."
            save_system_prompt(default_prompt)
            return default_prompt
    except Exception as e:
        logging.error(f"Unexpected error loading system prompt: {e}")
        return "You are a helpful, smart, kind, and efficient AI assistant."

# Code block management
def save_code_block(code_block, filename=None, file_type=None, version=None):
    """Save the code block to a file, ensuring no overwrite."""
    try:
        if filename:
            save_dir = "./Workspace/savedmodules"
            base_name, extension = os.path.splitext(filename)
            file_path = os.path.join(save_dir, filename)
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(save_dir, f"{base_name}({counter}){extension}")
                counter += 1
        else:
            if not file_type or not version:
                raise ValueError("file_type and version must be specified if filename is not provided.")
            directory = f"./Workspace/groq/output/{version}/"
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"code_block{file_type}")

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(code_block)
        
        logging.info(f"Code block successfully saved as {file_path}.")
        showinfo("Saved", f"Code saved to {file_path}")
    except Exception as e:
        logging.error(f"Unexpected error saving code block: {e}")
        showinfo("Error", f"Failed to save code: {e}")


def update_code_block_in_datamemory(filename, code_block):
    """Update a code block in the datamemory folder."""
    file_path = os.path.join("./Workspace/datamemory", filename)
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(code_block)
        logging.info(f"Code block successfully updated in {file_path}.")
    except Exception as e:
        logging.error(f"Unexpected error updating code block in datamemory: {e}")


def read_file_from_datamemory(filename):
    """Read content from a file in the datamemory folder."""
    filepath = os.path.join("./Workspace/datamemory", filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                logging.info(f"File {filename} successfully read from datamemory.")
                return content
    except Exception as e:
        logging.error(f"Unexpected error reading file from datamemory: {e}")
    return None

# Excel management
def save_to_excel(data, file_path):
    """Save data to an Excel file."""
    try:
        df = pd.DataFrame(data, columns=["Path", "Metrics", "Code"])
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Adjust column width
            worksheet = writer.sheets['Sheet1']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(idx, idx, max_length)
        logging.info(f"Data successfully saved to Excel file {file_path}.")
    except Exception as e:
        logging.error(f"Unexpected error saving to Excel: {e}")

# Chat history management
def load_history(history_listbox):
    """Load chat history files into the listbox."""
    history_listbox.delete(0, END)
    try:
        for file in os.listdir(CHAT_HISTORY_FOLDER):
            if file.endswith(".txt"):
                history_listbox.insert(END, file)
        logging.info("Chat history successfully loaded.")
    except Exception as e:
        logging.error(f"Unexpected error loading chat history: {e}")

def load_selected_chat(chat_display, user_message_var, history_listbox):
    """Load the selected chat log into the chat display."""
    selected_index = history_listbox.curselection()
    if selected_index:
        selected_file = history_listbox.get(selected_index)
        try:
            with open(os.path.join(CHAT_HISTORY_FOLDER, selected_file), 'r') as file:
                chat_log = file.read()
            chat_display.delete("1.0", END)
            chat_display.insert(END, chat_log)
            user_message_var.delete("1.0", END)
            logging.info(f"Selected chat {selected_file} successfully loaded.")
        except Exception as e:
            logging.error(f"Unexpected error loading selected chat: {e}")

def rename_selected_chat(history_listbox):
    """Rename the selected chat log file."""
    try:
        selected_index = history_listbox.curselection()
        if selected_index:
            selected_file = history_listbox.get(selected_index)
            new_name = simpledialog.askstring("Rename Chat", "Enter new name:", initialvalue=selected_file)
            if new_name and new_name != selected_file:
                os.rename(os.path.join(CHAT_HISTORY_FOLDER, selected_file), os.path.join(CHAT_HISTORY_FOLDER, new_name))
                load_history(history_listbox)
                logging.info(f"Renamed {selected_file} to {new_name}.")
    except Exception as e:
        logging.error(f"Unexpected error renaming chat: {e}")

def delete_selected_chat(history_listbox):
    """Delete the selected chat log file."""
    selected_index = history_listbox.curselection()
    if selected_index:
        selected_file = history_listbox.get(selected_index)
        if askyesno("Delete Chat", f"Are you sure you want to delete {selected_file}?"):
            try:
                os.remove(os.path.join(CHAT_HISTORY_FOLDER, selected_file))
                load_history(history_listbox)
            except Exception as e:
                logging.error(f"Unexpected error deleting chat: {e}")

def new_chat(chat_display, user_message_var):
    """Start a new chat session."""
    try:
        chat_display.delete("1.0", END)
        user_message_var.delete("1.0", END)
    except Exception as e:
        logging.error(f"Unexpected error starting new chat: {e}")

# Embedding management
def load_embedding(file_path):
    """Load embedding from a numpy file."""
    try:
        with open(file_path, 'rb') as f:
            embedding = np.load(f)
            logging.info(f"Embedding successfully loaded from {file_path}.")
            return embedding
    except Exception as e:
        logging.error(f"Unexpected error loading embedding from {file_path}: {e}")
        return None

# File name insertion
def insert_file_name(file_name, user_message_var):
    """Insert the file name into the user message variable."""
    try:
        user_message = user_message_var.get("1.0", "end-1c").strip()
        user_message_var.delete("1.0", "end")
        user_message_var.insert("end", f"{user_message}{file_name}")
        logging.info(f"File name {file_name} inserted into the user message.")
    except Exception as e:
        logging.error(f"Unexpected error inserting file name: {e}")

def auto_suggest_files(event, user_message_var):
    """Auto-suggest files in the datamemory folder based on user input."""
    try:
        user_message = user_message_var.get("1.0", "end-1c").strip()
        if user_message.endswith("@"):
            files = os.listdir("./Workspace/datamemory")
            logging.debug(f"Files in datamemory: {files}")
            suggestion_menu = Menu(event.widget, tearoff=0)
            for file in files:
                suggestion_menu.add_command(label=file, command=lambda f=file: insert_file_name(f, user_message_var))
            try:
                x = event.widget.winfo_rootx()
                y = event.widget.winfo_rooty() + event.widget.winfo_height()
                logging.debug(f"Popup coordinates: x={x}, y={y}")
                suggestion_menu.tk_popup(x, y, 0)
            finally:
                suggestion_menu.grab_release()
    except Exception as e:
        logging.error(f"Unexpected error in auto_suggest_files: {e}")

# Key bindings management
class KeyBindings:
    def __init__(self, app):
        self.app = app
        self._setup_key_bindings()

    def _setup_key_bindings(self):
        """Setup key bindings for copy, paste, and undo."""
        self.app.terminal.bind("<Control-c>", self.copy, add="+")
        self.app.terminal.bind("<Control-v>", self.paste, add="+")
        self.app.terminal.bind("<Control-z>", self.undo, add="+")

    def copy(self, event=None):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.app.terminal.get_selection()
            self.app.clipboard_clear()
            self.app.clipboard_append(selected_text)
            print("Copied to clipboard:", selected_text)  # Debug output
        except Exception as e:
            logging.error(f"Copy operation failed: {e}")
        return "break"

    def paste(self, event=None):
        """Paste text from clipboard."""
        try:
            clipboard_text = self.app.clipboard_get()
            print("Attempting to paste:", clipboard_text)  # Debug output
            self.app.terminal.insert_text_at_cursor(clipboard_text)
        except tk.TclError as e:
            logging.error(f"Paste operation failed: Clipboard is empty or contains non-text data. {e}")
        except Exception as e:
            logging.error(f"Paste operation failed: {e}")
        return "break"

    def undo(self, event=None):
        """Undo the last action."""
        try:
            self.app.terminal.undo()
            print("Undo operation successful")  # Debug output
        except Exception as e:
            logging.error(f"Undo operation failed: {e}")
        return "break"

# UI management
def show_code_window(code_block):
    """Show a new window displaying the code block."""
    logging.debug(f"Showing code window with code block:\n{code_block}")
    code_window = Toplevel()
    code_window.title("Code Block")
    code_window.geometry("400x400")
    code_window.configure(bg='#2e2e2e')

    copy_button = ctk.CTkButton(code_window, text="Copy Code", command=lambda: copy_to_clipboard(code_block))
    copy_button.pack(side='top', pady=5, padx=5)

    file_type_label = Label(code_window, text="File Type:", bg='#2e2e2e', fg='#ffffff')
    file_type_label.pack(side='top', pady=5)
    file_type_entry = Entry(code_window, width=10)
    file_type_entry.insert(0, ".py")
    file_type_entry.pack(side='top', pady=5)

    version_label = Label(code_window, text="Version:", bg='#2e2e2e', fg='#ffffff')
    version_label.pack(side='top', pady=5)
    version_entry = Entry(code_window, width=10)
    version_entry.insert(0, "v1")
    version_entry.pack(side='top', pady=5)

    save_button = ctk.CTkButton(code_window, text="Save Code", command=lambda: save_code_block(code_block, file_type=file_type_entry.get(), version=version_entry.get()))
    save_button.pack(side='top', pady=5, padx=5)

    code_text = Text(code_window, wrap='none', bg='#2e2e2e', fg='#ffffff', insertbackground='white')
    code_text.insert(END, code_block)
    code_text.pack(expand=1, fill='both')


def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        pyperclip.copy(text)
        showinfo("Copied", "Code copied to clipboard!")
    except Exception as e:
        logging.error(f"Unexpected error copying to clipboard: {e}")

def handle_file_drop(event, user_message_var):
    """Handle file drop event."""
    try:
        file_path = event.data
        with open(file_path, 'r') as file:
            file_content = file.read()
        user_message_var.insert(END, f"\n\nDropped file content:\n{file_content}")
    except Exception as e:
        logging.error(f"Unexpected error handling file drop: {e}")
