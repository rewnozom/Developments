# scripts/setup.py
from setuptools import setup, find_packages

setup(
    name="claude-sonnet",
    version="1.0.0",
    description="Claude 3.5 Sonnet System",
    author="Anthropic",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "psutil>=5.9.0",
        "typing-extensions>=4.5.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'mypy>=1.0.0',
            'flake8>=4.0.0',
        ]
    },
    python_requires='>=3.8',
)