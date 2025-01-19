from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fast_whisper_v2",  # Replace with your desired package name
    version="0.1.0",  # Follow semantic versioning
    author="Tobias R",
    description="Fast Whisper-v2 is a simple and user-friendly application that uses Faster Whisper for fast and accurate transcription. It provides an easy way to handle audio transcription tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyaudio",
        "PySide6",
        "keyboard",
        "faster-whisper",
        "ctranslate2",
    ],
    entry_points={
        "console_scripts": [
            "fast-whisper=main:main",  # Entry point for CLI
        ]
    },
    extras_require={
        "dev": [
            "pytest",
            "flake8",
        ]
    },
    package_data={
        "": ["*.json", "*.md", "*.css"],  # Include additional files
    },
    data_files=[
        ("config", ["config.json"]),  # Example of adding config files
    ],
    zip_safe=False,  # For easier debugging with source code
)
