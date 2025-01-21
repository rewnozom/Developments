import os
import sys
import venv
import platform
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.install import install

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()

class CustomInstallCommand(install):
    """Custom installation class that creates and activates a virtual environment."""
    
    def create_virtual_env(self):
        venv_dir = "env"
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment in {venv_dir}...")
            venv.create(venv_dir, with_pip=True)
            return True
        return False

    def get_venv_python(self):
        """Get the path to the virtual environment's Python executable."""
        if platform.system().lower() == "windows":
            return os.path.join("env", "Scripts", "python.exe")
        return os.path.join("env", "bin", "python")

    def get_venv_pip(self):
        """Get the path to the virtual environment's pip executable."""
        if platform.system().lower() == "windows":
            return os.path.join("env", "Scripts", "pip.exe")
        return os.path.join("env", "bin", "pip")

    def get_activation_script(self):
        """Get the appropriate activation command based on the platform."""
        system = platform.system().lower()
        venv_dir = "env"
        
        if system == "windows":
            if os.environ.get("SHELL") and "powershell" in os.environ["SHELL"].lower():
                activate_script = os.path.join(venv_dir, "Scripts", "Activate.ps1")
                return f"PowerShell -ExecutionPolicy Bypass -File {activate_script}"
            else:
                return os.path.join(venv_dir, "Scripts", "activate.bat")
        else:
            return f"source {os.path.join(venv_dir, 'bin', 'activate')}"

    def run(self):
        # Create virtual environment if it doesn't exist
        created_new = self.create_virtual_env()
        
        # Get virtual environment executables
        venv_python = self.get_venv_python()
        venv_pip = self.get_venv_pip()
        activate_cmd = self.get_activation_script()

        if not os.path.exists(venv_python):
            print("Error: Virtual environment Python not found!")
            return

        # Upgrade pip in virtual environment
        print("Upgrading pip in virtual environment...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])

        # Install the package in development mode inside the virtual environment
        print("Installing package in virtual environment...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "-e", "."])

        print("\nVirtual environment setup complete!")
        print("\nTo activate the virtual environment, run:")
        print(f"    {activate_cmd}")
        print("\nThen you can run the application with:")
        print("    auto-generate-ai-chat")

setup(
    name="auto-generate-ai-chat",
    version="2.0.3",
    author="Tobias R",
    description="A synthetic data generation tool and AI chat for creating training datasets and working on local modules",
    long_description=read_file("README.md"),
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.5",
        "langchain-anthropic>=0.1.1",
        "langchain-groq>=0.1.0",
        "langchain-google-genai>=0.0.5",
        "langchain-mistralai>=0.0.3",
        "langchain-huggingface>=0.0.6",
        "customtkinter>=5.2.1",
        "tiktoken>=0.5.2",
        "openai>=1.12.0",
        "groq>=0.4.2",
        "anthropic>=0.18.1",
        "mistralai>=0.1.3",
        "google-generativeai>=0.3.2",
        "ollama>=0.1.7",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dotenv>=1.0.0",
        "pyperclip>=1.8.2",
        "flask>=3.0.0",
        "werkzeug>=3.0.0",
        "xlsxwriter>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "auto-generate-ai-chat=auto_generate_ai_chat_v2_a_03.main_AgentGroq:main",
        ],
    },
    package_data={
        "auto_generate_ai_chat_v2_a_03": [
            "System_Prompts/*.md",
            "Workspace/prefix/*.md",
            "Workspace/chat_history/*.txt",
            "Workspace/datamemory/*.txt",
            "Workspace/savedmodules/*.txt",
            "llm_data_gen_examples/*.xlsx",
        ],
    },
    include_package_data=True,
    cmdclass={
        'install': CustomInstallCommand,
    },
)