# setup.py
from setuptools import setup, find_packages

setup(
   name="claude-sonnet",
   version="1.0.0",
   description="Claude 3.5 Sonnet System - Advanced Conversation Framework",
   author="Anthropic",
   author_email="support@anthropic.com",
   packages=find_packages(),
   install_requires=[
       "pyyaml>=6.0",
       "psutil>=5.9.0", 
       "typing-extensions>=4.5.0",
       "python-dateutil>=2.8.2",
       "requests>=2.28.0",
       "aiohttp>=3.8.0",
       "numpy>=1.21.0",
       "pandas>=1.3.0",
       "scikit-learn>=1.0.0"
   ],
   extras_require={
       'dev': [
           'pytest>=7.0.0',
           'pytest-cov>=4.0.0', 
           'black>=22.0.0',
           'isort>=5.10.0',
           'mypy>=1.0.0',
           'flake8>=4.0.0',
           'pre-commit>=2.20.0'
       ],
       'docs': [
           'sphinx>=4.5.0',
           'sphinx-rtd-theme>=1.0.0',
           'myst-parser>=0.18.0'
       ],
       'performance': [
           'ray>=2.0.0',
           'dask>=2023.0.0'
       ]
   },
   python_requires='>=3.8',
   classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 3.8',
       'Programming Language :: Python :: 3.9',
       'Programming Language :: Python :: 3.10',
       'Programming Language :: Python :: 3.11',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: Text Processing :: General',
       'Topic :: Scientific/Engineering :: Artificial Intelligence'
   ],
   entry_points={
       'console_scripts': [
           'claude-sonnet=claude_sonnet.cli:main',
       ],
   },
)