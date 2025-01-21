import os
import shutil
import customtkinter as ctk
from tkinter import Listbox, Text, END, Toplevel, simpledialog, Frame, Scrollbar, VERTICAL, StringVar, IntVar, BooleanVar, DoubleVar, Tk
from tkinter.messagebox import showinfo, askyesno
from tkinter import filedialog
import pyperclip
import logging
from config import Config
from models import MODELS, API_KEYS
from Groq.utils.token_counter import count_tokens_in_string
from Groq.utils import (
    save_memory,
    load_memory,
    add_memory,
    remove_memory,
    save_system_prompt,
    load_history,
    load_selected_chat,
    rename_selected_chat,
    delete_selected_chat,
    new_chat,
    insert_file_name,
    auto_suggest_files,
    KeyBindings,
    handle_file_drop
)
from Groq.utils.code_analysis_tool import start_code_analysis

# Initialize configuration
config = Config()

# Set up logging based on configuration
logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)

CHAT_HISTORY_FOLDER = "./Workspace/chat_history"
SYSTEM_PROMPTS_FOLDER = "./System_Prompts"
ORIGINAL_SYSTEM_PROMPT = os.path.join(SYSTEM_PROMPTS_FOLDER, "Original.md")


def update_token_counter(user_message_var, token_counter_label, encoding_name="cl100k_base"):
    user_message = user_message_var.get("1.0", END).strip()
    token_count = count_tokens_in_string(user_message, encoding_name)
    token_counter_label.configure(text=f"Tokens: {token_count}")

def load_system_prompts(include_file_processor=False):
    prompts = []
    if os.path.exists(SYSTEM_PROMPTS_FOLDER):
        for file in os.listdir(SYSTEM_PROMPTS_FOLDER):
            if file.endswith('.md'):
                prompts.append(file[:-3])  # Add only .md files, remove the .md extension
    
    # Add the file processor system prompt if requested
    if include_file_processor:
        file_processor_prompt = "Code Analysis Tool"
        if "system_prompt_file_processor.md" in os.listdir(SYSTEM_PROMPTS_FOLDER):
            prompts.append(file_processor_prompt)
        else:
            logging.warning(f"{file_processor_prompt} prompt file not found in {SYSTEM_PROMPTS_FOLDER}")
    
    return prompts

def update_system_prompt(prompt_name, system_prompt_var):
    try:
        if prompt_name == "Original":
            file_path = os.path.join(SYSTEM_PROMPTS_FOLDER, "Original.md")
        else:
            file_path = os.path.join(SYSTEM_PROMPTS_FOLDER, f"{prompt_name}.md")
        
        logging.info(f"Loading system prompt from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logging.info(f"Loaded content (first 50 chars): {content[:50]}...")
            system_prompt_var.set(content)
        
        # Save the selected prompt to a file
        with open("./current_system_prompt.txt", "w", encoding='utf-8') as f:
            f.write(system_prompt_var.get())
        
        logging.info(f"Updated system prompt to: {prompt_name}")
    except Exception as e:
        logging.error(f"Error updating system prompt: {e}")


def get_system_prompt_content(prompt_name):
    if prompt_name == "Code Analysis Tool":
        file_path = os.path.join(SYSTEM_PROMPTS_FOLDER, "system_prompt_file_processor.md")
    else:
        file_path = os.path.join(SYSTEM_PROMPTS_FOLDER, f"{prompt_name}.md")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"System prompt file not found: {file_path}")
        return ""

def browse_directory(dir_var):
    directory = filedialog.askdirectory()
    if directory:
        dir_var.set(directory)

def update_system_prompt_text(prompt_name, text_widget):
    content = get_system_prompt_content(prompt_name)
    text_widget.delete("1.0", END)
    text_widget.insert("1.0", content)

def create_ui(parent, send_message_callback, auto_suggest_files, model_var, temperature_var, max_tokens_var, system_prompt_var, memory_entry_var, temperature_entry_var, max_tokens_entry_var):
    if not os.path.exists(CHAT_HISTORY_FOLDER):
        os.makedirs(CHAT_HISTORY_FOLDER)

    main_frame = Frame(parent, bg='#2e2e2e')
    main_frame.pack(expand=1, fill="both")

    sidebar = Frame(main_frame, width=200, bg='#2e2e2e')
    sidebar.pack(expand=False, fill="y", side="left", anchor="nw")

    # Center frame for existing chat and settings
    center_frame = Frame(main_frame, bg='#2e2e2e')
    center_frame.pack(expand=True, fill="both", side="left")

    # New right frame for the code analysis tool
    right_frame = Frame(main_frame, width=300, bg='#2e2e2e')
    right_frame.pack(expand=False, fill="y", side="right", anchor="ne")

    # Sidebar scroll and history listbox
    sidebar_scroll = Scrollbar(sidebar, orient=VERTICAL)
    sidebar_scroll.pack(side="right", fill="y")
    
    history_listbox = Listbox(sidebar, bg='#333333', fg='white', selectbackground='#555555', selectforeground='white', yscrollcommand=sidebar_scroll.set)
    history_listbox.pack(expand=1, fill="both")
    sidebar_scroll.config(command=history_listbox.yview)
    load_history(history_listbox)

    load_history_button = ctk.CTkButton(sidebar, text="Load Selected Chat", command=lambda: load_selected_chat(chat_display, user_message_var, history_listbox))
    load_history_button.pack(pady=5)
    
    new_chat_button = ctk.CTkButton(sidebar, text="New Chat", command=lambda: new_chat(chat_display, user_message_var))
    new_chat_button.pack(pady=5)

    rename_history_button = ctk.CTkButton(sidebar, text="Rename Selected Chat", command=lambda: rename_selected_chat(history_listbox))
    rename_history_button.pack(pady=5)

    delete_history_button = ctk.CTkButton(sidebar, text="Delete Selected Chat", command=lambda: delete_selected_chat(history_listbox))
    delete_history_button.pack(pady=5)

    file_management_label = ctk.CTkLabel(sidebar, text="File Management:")
    file_management_label.pack(pady=5)
    
    upload_file_button = ctk.CTkButton(sidebar, text="Upload File", command=upload_file)
    upload_file_button.pack(pady=5)

    view_files_button = ctk.CTkButton(sidebar, text="View Files", command=view_files)
    view_files_button.pack(pady=5)
    
    tab_control = ctk.CTkTabview(center_frame)
    tab_control.pack(expand=1, fill="both")

    chat_tab = tab_control.add("Chat")
    if config.ENABLE_MEMORY:
        memory_tab = tab_control.add("Memory")
    if config.ENABLE_HISTORY:
        history_tab = tab_control.add("History")
    settings_tab = tab_control.add("Settings")

    # Model and System Prompt in horizontal layout
    top_frame = Frame(chat_tab, bg='#2e2e2e')
    top_frame.pack(fill="x", pady=5)

    model_label = ctk.CTkLabel(top_frame, text="Select Model:")
    model_label.pack(side="left", padx=5)

    # Dynamically populate model selection dropdown using MODELS from models.py
    available_models = [model_name for company_models in MODELS.values() for model_name in company_models.keys()]
    model_dropdown = ctk.CTkOptionMenu(
        top_frame, 
        variable=model_var, 
        values=available_models
    )
    model_dropdown.pack(side="left", padx=5)
    
    # Add System Prompt dropdown
    system_prompt_label = ctk.CTkLabel(top_frame, text="System Prompt:")
    system_prompt_label.pack(side="left", padx=5)

    system_prompt_options = load_system_prompts()
    system_prompt_dropdown = ctk.CTkOptionMenu(
        top_frame,
        variable=system_prompt_var,
        values=system_prompt_options,
        command=lambda x: update_system_prompt(x, system_prompt_var)
    )
    system_prompt_dropdown.pack(side="left", padx=5)

    # Set the initial value to "Original" and update the system_prompt_var
    system_prompt_dropdown.set("Original")
    update_system_prompt("Original", system_prompt_var)

    system_prompt_entry = ctk.CTkEntry(top_frame, textvariable=system_prompt_var, width=300)
    system_prompt_entry.pack(side="left", padx=5, fill="x", expand=True)
    system_prompt_entry.bind("<FocusOut>", lambda event: save_system_prompt(system_prompt_var.get()))

    # Add a button to print the current system prompt (for debugging)
    debug_button = ctk.CTkButton(top_frame, text="Print System Prompt", command=lambda: print(system_prompt_var.get()))
    debug_button.pack(side="left", padx=5)

    # Temperature and Max Tokens in horizontal layout
    mid_frame = Frame(chat_tab, bg='#2e2e2e')
    mid_frame.pack(fill="x", pady=5)

    temperature_label = ctk.CTkLabel(mid_frame, text="Temperature:")
    temperature_label.pack(side="left", padx=5)

    temperature_slider = ctk.CTkSlider(mid_frame, from_=0.0, to=2.0, variable=temperature_var, command=lambda value: temperature_entry_var.set(f"{float(value):.2f}"))
    temperature_slider.pack(side="left", padx=5)

    temperature_entry = ctk.CTkEntry(mid_frame, textvariable=temperature_entry_var)
    temperature_entry.pack(side="left", padx=5)
    temperature_entry_var.trace_add("write", lambda *args: temperature_slider.set(float(temperature_entry_var.get())))

    max_tokens_label = ctk.CTkLabel(mid_frame, text="Max Tokens:")
    max_tokens_label.pack(side="left", padx=5)

    max_tokens_slider = ctk.CTkSlider(mid_frame, from_=0, to=16384, variable=max_tokens_var, command=lambda value: max_tokens_entry_var.set(int(value)))
    max_tokens_slider.pack(side="left", padx=5)

    max_tokens_entry = ctk.CTkEntry(mid_frame, textvariable=max_tokens_entry_var)
    max_tokens_entry.pack(side="left", padx=5)
    max_tokens_entry_var.trace_add("write", lambda *args: max_tokens_slider.set(int(max_tokens_entry_var.get())))

    # Add checkboxes for prefixes and their position
    prefix_frame = Frame(chat_tab, bg='#2e2e2e')
    prefix_frame.pack(pady=5, fill="x")
    
    use_prefix_vars = [BooleanVar(value=False) for _ in range(6)]
    prefix_position_vars = [BooleanVar(value=True) for _ in range(6)]
    use_prefix_checkboxes = []
    prefix_position_checkboxes = []

    for i in range(6):
        prefix_checkbox = ctk.CTkCheckBox(prefix_frame, text=f"Pre {i+1}", variable=use_prefix_vars[i])
        prefix_checkbox.grid(row=0, column=i, padx=5)
        use_prefix_checkboxes.append(prefix_checkbox)

        position_checkbox = ctk.CTkCheckBox(prefix_frame, text="First", variable=prefix_position_vars[i])
        position_checkbox.grid(row=1, column=i, padx=5)
        prefix_position_checkboxes.append(position_checkbox)

    # Add autoG checkbox
    autog_var = BooleanVar(value=False)
    autog_checkbox = ctk.CTkCheckBox(prefix_frame, text="autoG", variable=autog_var)
    autog_checkbox.grid(row=0, column=6, padx=5)

    send_button = ctk.CTkButton(chat_tab, text="Send", command=send_message_callback)
    send_button.pack(pady=5)

    chat_display = Text(chat_tab, wrap='word', bg='#333333', fg='white', insertbackground='white')
    chat_display.pack(pady=5, fill="both", expand=True)
    chat_display.config(font=("TkDefaultFont", 10))

    user_message_label = ctk.CTkLabel(chat_tab, text="Your Message:")
    user_message_label.pack(pady=5)

    user_message_var = Text(chat_tab, wrap='word', height=10, bg='#333333', fg='white', insertbackground='white')
    user_message_var.pack(pady=5, fill="x")
    user_message_var.config(font=("TkDefaultFont", 10))
    user_message_var.bind("<Shift-Return>", lambda event: user_message_var.insert("insert", "\n"))
    user_message_var.bind("<Return>", send_message_callback)
    user_message_var.bind("<KeyRelease-@>", lambda event: auto_suggest_files(event, user_message_var))
    
    # Token counter label
    token_counter_label = ctk.CTkLabel(chat_tab, text="Tokens: 0")
    token_counter_label.pack(pady=5, anchor='se')

    # Add on_modified function to update token counter
    def on_modified(event, text_widget, counter_label):
        content = text_widget.get("1.0", "end-1c")
        token_count = len(content.split())
        counter_label.configure(text=f"Tokens: {token_count}")

    user_message_var.bind("<<Modified>>", lambda event: on_modified(event, user_message_var, token_counter_label))

    if config.ENABLE_MEMORY:
        memory_label = ctk.CTkLabel(memory_tab, text="Memory Entries:")
        memory_label.pack(pady=5)

        memory_listbox = Listbox(memory_tab, bg='#333333', fg='white', selectbackground='#555555', selectforeground='white')
        memory_listbox.pack(pady=5, fill="both", expand=True)

        memory_entry_label = ctk.CTkLabel(memory_tab, text="New Memory Entry:")
        memory_entry_label.pack(pady=5)

        memory_entry_entry = ctk.CTkEntry(memory_tab, textvariable=memory_entry_var)
        memory_entry_entry.pack(pady=5)

        additional_memory = load_memory()

        add_memory_button = ctk.CTkButton(memory_tab, text="Add Memory", command=lambda: add_memory(memory_listbox, memory_entry_var, additional_memory))
        add_memory_button.pack(pady=5)

        remove_memory_button = ctk.CTkButton(memory_tab, text="Remove Selected Memory", command=lambda: remove_memory(memory_listbox, additional_memory))
        remove_memory_button.pack(pady=5)

        for memory_entry in additional_memory:
            memory_listbox.insert(END, memory_entry['content'])

    if config.ENABLE_HISTORY:
        history_label = ctk.CTkLabel(history_tab, text="Chat History:")
        history_label.pack(pady=5)

        history_listbox = Listbox(history_tab, bg='#333333', fg='white', selectbackground='#555555', selectforeground='white')
        history_listbox.pack(pady=5, fill="both", expand=True)

        load_history(history_listbox)

        load_history_button = ctk.CTkButton(history_tab, text="Load Selected Chat", command=lambda: load_selected_chat(chat_display, user_message_var, history_listbox))
        load_history_button.pack(pady=5)

        rename_history_button = ctk.CTkButton(history_tab, text="Rename Selected Chat", command=lambda: rename_selected_chat(history_listbox))
        rename_history_button.pack(pady=5)

        delete_history_button = ctk.CTkButton(history_tab, text="Delete Selected Chat", command=lambda: delete_selected_chat(history_listbox))
        delete_history_button.pack(pady=5)

    # API Key section that dynamically updates based on the selected model
    api_key_label = ctk.CTkLabel(settings_tab, text="API Key:")
    api_key_label.pack(pady=5)

    api_key_var = StringVar(value=API_KEYS.get(model_var.get(), ""))

    api_key_entry = ctk.CTkEntry(settings_tab, textvariable=api_key_var)
    api_key_entry.pack(pady=5)

    def update_api_key_var(*args):
        api_key_var.set(API_KEYS.get(model_var.get(), ""))

    model_var.trace_add("write", update_api_key_var)

    enable_memory_var = IntVar(value=config.ENABLE_MEMORY)
    enable_memory_check = ctk.CTkCheckBox(settings_tab, text="Enable Memory", variable=enable_memory_var)
    enable_memory_check.pack(pady=5)

    enable_history_var = IntVar(value=config.ENABLE_HISTORY)
    enable_history_check = ctk.CTkCheckBox(settings_tab, text="Enable History", variable=enable_history_var)
    enable_history_check.pack(pady=5)
    
    # Create the code analysis tool UI
    create_code_analysis_ui(right_frame)

    return chat_display, user_message_var, token_counter_label, use_prefix_vars, prefix_position_vars, autog_var

def create_code_analysis_ui(parent):
    # Code Analysis Tool UI components
    tool_label = ctk.CTkLabel(parent, text="Code Analysis Tool", font=("TkDefaultFont", 16, "bold"))
    tool_label.pack(pady=10)

    # Input Directory Selection
    input_dir_var = StringVar()
    input_dir_label = ctk.CTkLabel(parent, text="Input Directory:")
    input_dir_label.pack(pady=5)
    input_dir_entry = ctk.CTkEntry(parent, textvariable=input_dir_var)
    input_dir_entry.pack(pady=5)
    input_dir_button = ctk.CTkButton(parent, text="Browse", command=lambda: browse_directory(input_dir_var))
    input_dir_button.pack(pady=5)

    # Output Directory Selection
    output_dir_var = StringVar()
    output_dir_label = ctk.CTkLabel(parent, text="Output Directory:")
    output_dir_label.pack(pady=5)
    output_dir_entry = ctk.CTkEntry(parent, textvariable=output_dir_var)
    output_dir_entry.pack(pady=5)
    output_dir_button = ctk.CTkButton(parent, text="Browse", command=lambda: browse_directory(output_dir_var))
    output_dir_button.pack(pady=5)

    # File Extensions
    extensions_var = StringVar(value=".py,.js,.java,.cpp")
    extensions_label = ctk.CTkLabel(parent, text="File Extensions (comma-separated):")
    extensions_label.pack(pady=5)
    extensions_entry = ctk.CTkEntry(parent, textvariable=extensions_var)
    extensions_entry.pack(pady=5)

    # System Prompt
    system_prompt_label = ctk.CTkLabel(parent, text="System Prompt:")
    system_prompt_label.pack(pady=5)
    
    system_prompt_var = StringVar()
    system_prompts = load_system_prompts(include_file_processor=True)
    system_prompt_dropdown = ctk.CTkOptionMenu(
        parent,
        variable=system_prompt_var,
        values=system_prompts,
        command=lambda x: update_system_prompt_text(x, system_prompt_text)
    )
    system_prompt_dropdown.pack(pady=5)
    
    system_prompt_text = ctk.CTkTextbox(parent, height=100)
    system_prompt_text.pack(pady=5)
    
    # Set default to Code Analysis Tool prompt
    system_prompt_var.set("Code Analysis Tool")
    update_system_prompt_text("Code Analysis Tool", system_prompt_text)

    # Start Processing Button
    start_button = ctk.CTkButton(parent, text="Start Processing", command=lambda: start_code_analysis(input_dir_var.get(), output_dir_var.get(), extensions_var.get(), system_prompt_text.get("1.0", "end-1c")))
    start_button.pack(pady=10)

    # Progress Bar
    progress_var = DoubleVar()
    progress_bar = ctk.CTkProgressBar(parent, variable=progress_var)
    progress_bar.pack(pady=10)

    # Results Display
    results_text = ctk.CTkTextbox(parent, height=100)
    results_text.pack(pady=10)


def on_modified(event, user_message_var, token_counter_label):
    if user_message_var.edit_modified():
        update_token_counter(user_message_var, token_counter_label)
        user_message_var.edit_modified(False)

def upload_file():
    """Upload a file to the datamemory folder."""
    from tkinter import filedialog
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            shutil.copy(file_path, "./Workspace/datamemory")
            logging.info(f"File {os.path.basename(file_path)} uploaded to datamemory.")
            showinfo("Upload Successful", f"File {os.path.basename(file_path)} uploaded successfully.")
        except Exception as e:
            logging.error(f"Error uploading file: {e}")
            showinfo("Upload Error", f"An error occurred while uploading the file: {e}")

def view_files():
    """View files in the datamemory folder."""
    files = os.listdir("./Workspace/datamemory")
    file_window = Toplevel()
    file_window.title("Files in Datamemory")
    file_window.geometry("300x300")
    file_listbox = Listbox(file_window, bg='#333333', fg='white', selectbackground='#555555', selectforeground='white')
    file_listbox.pack(expand=1, fill="both")

    for file in files:
        file_listbox.insert(END, file)
    
    rename_button = ctk.CTkButton(file_window, text="Rename File", command=lambda: rename_file(file_listbox))
    rename_button.pack(pady=5)

    delete_button = ctk.CTkButton(file_window, text="Delete File", command=lambda: delete_file(file_listbox))
    delete_button.pack(pady=5)

def rename_file(file_listbox):
    """Rename a selected file in the datamemory folder."""
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=selected_file)
        if new_name and new_name != selected_file:
            try:
                os.rename(os.path.join("./Workspace/datamemory", selected_file), os.path.join("./Workspace/datamemory", new_name))
                logging.info(f"Renamed file {selected_file} to {new_name}.")
                showinfo("Rename Successful", f"File renamed to {new_name}.")
                file_listbox.delete(selected_index)
                file_listbox.insert(selected_index, new_name)
            except Exception as e:
                logging.error(f"Error renaming file: {e}")
                showinfo("Rename Error", f"An error occurred while renaming the file: {e}")

def delete_file(file_listbox):
    """Delete a selected file in the datamemory folder."""
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        if askyesno("Delete File", f"Are you sure you want to delete {selected_file}?"):
            try:
                os.remove(os.path.join("./Workspace/datamemory", selected_file))
                logging.info(f"Deleted file {selected_file}.")
                showinfo("Delete Successful", f"File {selected_file} deleted successfully.")
                file_listbox.delete(selected_index)
            except Exception as e:
                logging.error(f"Error deleting file: {e}")
                showinfo("Delete Error", f"An error occurred while deleting the file: {e}")
