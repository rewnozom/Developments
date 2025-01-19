# Developments

### Workspace Project Management

This workspace contains multiple independent projects, each with its own virtual environment (`env/`). This setup ensures that dependencies for each project remain isolated.


## Directory Structure
```
Workspace/
│
├── fast_whisper_v2/
│   ├── env/
│   ├── main.py
│   └── requirements.txt
│
├── Markdown_csv_extract/
│   ├── env/
│   ├── parser.py
│   └── requirements.txt
│
├── dynamic_main/
│   ├── env/
│   ├── app.py
│   └── requirements.txt
│
├── Dashboard/
│   ├── env/
│   ├── server.py
│   └── requirements.txt
│
└── Auto_job_seaker/
    ├── env/
    ├── scraper.py
    └── requirements.txt
└── # More coming soon (fixing the documentation on them and will update when they're ready)
```


## Project Setup and Execution (Copy-Paste Ready)

### fast_whisper_v2
```bash
cd Workspace/fast_whisper_v2
python -m venv env
source env/bin/activate  # Linux/Unix
.\env\Scripts\Activate.ps1  # PowerShell
.\env\Scripts\activate.bat  # CMD
pip install -r requirements.txt
python main.py
```

### Markdown_csv_extract
```bash
cd Workspace/Markdown_csv_extract
python -m venv env
source env/bin/activate  # Linux/Unix
.\env\Scripts\Activate.ps1  # PowerShell
.\env\Scripts\activate.bat  # CMD
pip install -r requirements.txt
python parser.py
```

### dynamic_main
```bash
cd Workspace/dynamic_main
python -m venv env
source env/bin/activate  # Linux/Unix
.\env\Scripts\Activate.ps1  # PowerShell
.\env\Scripts\activate.bat  # CMD
pip install -r requirements.txt
python app.py
```

### Dashboard
```bash
cd Workspace/Dashboard
python -m venv env
source env/bin/activate  # Linux/Unix
.\env\Scripts\Activate.ps1  # PowerShell
.\env\Scripts\activate.bat  # CMD
pip install -r requirements.txt
python server.py
```

### Auto_job_seaker
```bash
cd Workspace/Auto_job_seaker
python -m venv env
source env/bin/activate  # Linux/Unix
.\env\Scripts\Activate.ps1  # PowerShell
.\env\Scripts\activate.bat  # CMD
pip install -r requirements.txt
python scraper.py
```

## Notes for Shell-Specific Commands

### PowerShell
- Uses `&&` for command chaining
- Execution policy might need to be set:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### CMD
- Uses `&` for command chaining
- No execution policy restrictions

### Linux/Unix
- Uses `&&` for command chaining
- Make sure scripts are executable:
  ```bash
  chmod +x env/bin/activate
  ```

