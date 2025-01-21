import threading
from Groq.utils.agent_file_processor import process_files
from tkinter import messagebox

def start_code_analysis(input_dir, output_dir, extensions, system_prompt, progress_var, results_text):
    def run_analysis():
        try:
            file_extensions = [ext.strip() for ext in extensions.split(',')]
            
            def ai_agent_function(file_path, file_name, content):
                # Implement your AI agent here, using the system_prompt
                # For now, we'll use a dummy function
                return f"this module that processes {file_name}"

            process_files(input_dir, output_dir, ai_agent_function, file_extensions)
            
            results_text.insert("end", f"Processing complete. Output saved to {output_dir}/training_data.xlsx\n")
            messagebox.showinfo("Processing Complete", "Code analysis has finished successfully.")
        except Exception as e:
            results_text.insert("end", f"Error occurred: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
        finally:
            progress_var.set(0)

    # Run the analysis in a separate thread to keep the UI responsive
    threading.Thread(target=run_analysis, daemon=True).start()