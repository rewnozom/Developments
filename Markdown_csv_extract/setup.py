import os
import sys
import venv
import platform
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

# Read README.md for the long description
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A tool for summarizing and extracting information"

class CustomInstallCommand(install):
    def run(self):
        # Create virtual environment if it doesn't exist
        venv_dir = "env"
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment in {venv_dir}...")
            venv.create(venv_dir, with_pip=True)
            
            # Get the path to the Python executable in the virtual environment
            if platform.system() == "Windows":
                python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
                pip_executable = os.path.join(venv_dir, "Scripts", "pip.exe")
                activate_cmd = f".\\{venv_dir}\\Scripts\\activate"
                ps_cmd = f".\\{venv_dir}\\Scripts\\Activate.ps1"
            else:
                python_executable = os.path.join(venv_dir, "bin", "python")
                pip_executable = os.path.join(venv_dir, "bin", "pip")
                activate_cmd = f"source {venv_dir}/bin/activate"

            # Install dependencies in the virtual environment
            print("Installing dependencies in virtual environment...")
            requirements = [
                "PySide6==6.4.2",
                "pandas==1.3.5",
                "toml==0.10.2",
                "pathlib==1.0.0"
            ]
            
            for req in requirements:
                print(f"Installing {req}...")
                try:
                    subprocess.check_call([pip_executable, "install", req])
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Failed to install {req}. Error: {e}")
                    continue
            
            # Print activation instructions
            if platform.system() == "Windows":
                print("\nVirtual environment created! To activate it:")
                print(f"- Command Prompt: {activate_cmd}")
                print(f"- PowerShell: {ps_cmd}")
            else:
                print("\nVirtual environment created! To activate it:")
                print(f"Run: {activate_cmd}")

        # Run the standard install
        install.run(self)

setup(
    name="summarize_extract",
    version="0.1.0",
    author="Tobias R",
    description="A tool for summarizing and extracting frameworks to work with llm on your framework easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9, <3.12",
    install_requires=[
        "PySide6==6.4.2",
        "pandas==1.3.5",
        "toml==0.10.2",
        "pathlib==1.0.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'summarize-extract=summarize_extract.main:main',
        ],
    }
)