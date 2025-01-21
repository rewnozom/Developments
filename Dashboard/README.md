# Search Dashboard

A desktop application for managing search fields and AI prompts with dark-themed interface.

## Features

- Search field management with customizable parameters
- AI prompt vault for organizing and categorizing prompts
- Dark mode interface
- Tag-based filtering
- Multi-page support
- Undo/redo functionality

## Installation

### Requirements
- Python 3.10 or newer (recommended)
- Git (for cloning the repository)

### Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/search-dashboard
cd search-dashboard
```

2. Install the package:
```bash
python setup.py install
```

The installation will automatically create a virtual environment named 'env' in your project directory.

3. Activate the virtual environment:

- **Windows Command Prompt**:
```cmd
.\env\Scripts\activate.bat
```

- **Windows PowerShell**:
```powershell
.\env\Scripts\Activate.ps1
```

- **Linux/Mac**:
```bash
source env/bin/activate
```

## Usage

1. Start the dashboard:
```bash
python main_dashboard.py
```

2. Create search fields:
   - Click "Add New Search Field"
   - Enter words or URLs
   - Use swap options for custom formatting

3. Use the AI Prompt Vault:
   - Create categories
   - Add and organize prompts
   - Filter by tags

## Project Structure

```
search-dashboard/
├── Dashboard/
│   ├── ai_vault_tab.py
│   ├── main_dashboard.py
│   ├── search_tab.py
│   └── utils/
│       ├── card_utils.py
│       └── theme_utils.py
├── setup.py
└── README.md
```
