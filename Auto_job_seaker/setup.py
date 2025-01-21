import os
import sys
import venv
import platform
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

def read_readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

class CustomInstallCommand(install):
    def run(self):
        # Create virtual environment if it doesn't exist
        venv_dir = os.path.join(os.getcwd(), 'env')
        if not os.path.exists(venv_dir):
            print("Creating virtual environment...")
            venv.create(venv_dir, with_pip=True)
            
            # Determine platform-specific activation command and pip path
            system_platform = platform.system().lower()
            if system_platform == "windows":
                pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
                print("\nTo activate the virtual environment, run:")
                print("PowerShell: .\\env\\Scripts\\Activate.ps1")
                print("CMD: .\\env\\Scripts\\activate.bat")
            else:  # Linux/Unix
                pip_path = os.path.join(venv_dir, "bin", "pip")
                print("\nTo activate the virtual environment, run:")
                print("source env/bin/activate")

            # Install dependencies in the virtual environment
            print("\nInstalling dependencies in virtual environment...")
            try:
                subprocess.check_call([pip_path, "install", "-e", "."])
                print("Dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error installing dependencies: {e}")
                raise

        # Run the standard installation
        install.run(self)

setup(
    name="auto_job_seeker",
    version="1.0.3",
    author="Tobias R",
    description="An automated job finder searching and filtering tool",
    long_description=read_readme(),
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "playwright>=1.30.0",
        "beautifulsoup4>=4.9.3",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
        "markdown>=3.3.4",
        "pytest>=6.2.5",
        "pytest-asyncio>=0.18.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "jobseeker=Auto_job_seaker.del1_Live.main:main",
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
)