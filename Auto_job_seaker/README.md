# Auto Job Seeker

A tool that helps you find job listings that match your skills and interests. It collects job posts, ranks them based on how well they match your preferences, and saves them in easy-to-read formats.

## What it does

- Finds job posts automatically
- Scores jobs based on how well they match your keywords
- Removes duplicate job posts
- Filters jobs by date posted
- Creates reports in different formats (CSV, JSON, and Markdown)
- Lets you customize your search terms

## Installation

### What you need before starting
- Python 3.10 # recomended


### How to install


1. Install:
```bash
python setup.py install
```

2. Start the virtual environment:

If you're using Windows, open PowerShell and run:
```powershell
.\env\Scripts\Activate.ps1
```

Or if you're using Windows CMD:
```cmd
.\env\Scripts\activate.bat
```

If you're using Linux or Mac:
```bash
source env/bin/activate
```

## How to use

1. Set up your preferences in `job/Utils/config_manager.py`:
   - Add job titles you're interested in
   - Add keywords that matter to you
   - Choose how recent you want the job posts to be

2. Start the search:
```bash
python main.py
```

3. Find your results in the `output` folder:
   - `jobs_TIMESTAMP.csv`: For opening in Excel
   - `jobs_TIMESTAMP.json`: For using with other programs
   - `jobs_TIMESTAMP.md`: For reading directly

## Files and folders

```
Auto_job_seaker/
├── del1_Live/
│   ├── job/
│   │   ├── DataProcessing/      # Handles job filtering and scoring
│   │   ├── DataSources/         # Gets job listings
│   │   ├── Storage/             # Saves results
│   │   ├── Utils/               # Helper functions
│   │   └── Visualization/       # Shows results
│   ├── main.py                  # Main program
│   └── omvandla.py             # Data conversion
├── setup.py
└── README.md
```

## Settings

### Job Titles to Search For
In `config_manager.py`, you can edit `SEARCH_TERMS`:

```python
SEARCH_TERMS = [
    "python developer",
    "full stack developer",
    "ai developer"
]
```

### Keywords
You can set which keywords are important to you:
- Add keywords that make a job more interesting to you
- Add keywords that make a job less interesting to you

### Search Settings
You can change how the tool searches:
- How long to wait between searches
- How many jobs to look for at once
- How new the job posts should be

