# Developments

## Directory Structure
```
.\Developments\
├── auto_generate_ai_chat_v2_a_03/
├── Auto_job_seaker/
├── auto_requirements.txt
├── Claude-like-Architecture/
├── Dashboard/
├── Development Tools/
├── fast_whisper_v2/
├── LoRA_data_prep_text_llm/
├── Markdown_csv_extract/
├── Markdown_csv_extract_to_android/
└── tobias-raanaes_v10/
```

## Project Setup and Installation

### Python Projects Installation
Run these commands in each Python project directory:

#### auto_generate_ai_chat_v2_a_03
```bash
cd auto_generate_ai_chat_v2_a_03
python setup.py install
```

#### Auto_job_seaker
```bash
cd Auto_job_seaker
python setup.py install
```

#### Claude-like-Architecture
```bash
cd Claude-like-Architecture
# Install dependencies for all workspaces
npm install
cd claude-3.5-sonnet
# Try to install package directly, if it fails, fall back to requirements.txt
pip install . || pip install -r requirements.txt
cd ..
# Start both frontend and backend in development mode
npm run dev

# view backend health-check = http://localhost:8000/docs
# view frontend = http://localhost:3000
```

#### Dashboard
```bash
cd Dashboard
python setup.py install
```

#### Development Tools
```bash
cd "Development Tools"
python setup.py install
```

#### LoRA_data_prep_text_llm
```bash
cd LoRA_data_prep_text_llm
python setup.py install
```

#### Markdown_csv_extract
```bash
cd Markdown_csv_extract
python setup.py install
```

#### Markdown_csv_extract_to_android
```bash
cd Markdown_csv_extract_to_android
python setup.py install
```

#### fast_whisper_v2
```bash
cd fast_whisper_v2
python setup.py install
```

### Node.js Project Installation

#### tobias-raanaes_v10
```bash
cd tobias-raanaes_v10
npm install
```

## Notes
- Each project is independent with its own dependencies
- Python projects use `setup.py install` for installation
- The Node.js project (tobias-raanaes_v10) uses npm for dependency management
