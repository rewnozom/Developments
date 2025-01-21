# Auto-Generate AI Chat v2

A specialized tool for generating synthetic training data through AI-powered chat interactions. The application features continuous data generation and chat functions for creating realistic training datasets for AI agents.

## Primary Features

### 🤖 Synthetic Data Generation
- Continuous Generation Mode with Start/Stop controls
- Automated generation of diverse training scenarios
- Structured data output in Excel format
- Customizable data generation templates
- Support for various data formats and patterns
- Quality control and validation features

### 📊 Data Output Formats
- Excel file generation with structured columns
- Customizable data schemas
- Support for multiple tables per file
- Automated file versioning
- Example dataset templates

### 💬 AI Chat Capabilities
- Multiple LLM Backend Support:
  - Groq (llama, mixtral)
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude models)
  - Mistral AI
  - Google Generative AI
  - Local models via Ollama and LM Studio

### 🔧 File Management Features
- Direct code manipulation through chat:
  - Use `#filename.ext` to save generated code
  - Use `@filename.ext` to reference existing files
  - Use `@@filename.ext` to update existing files
- Version control for generated files
- Auto-completion for file references
- Syntax highlighting

## Installation

1. Install the package:
```bash
python setup.py install
```

The installation process will automatically:
- Create a virtual environment named 'env'
- Install all required dependencies
- Provide activation commands for your specific platform

2. Activate the virtual environment:

For Linux/Unix:
```bash
source env/bin/activate
```

For Windows PowerShell:
```powershell
.\env\Scripts\Activate.ps1
```

For Windows CMD:
```cmd
.\env\Scripts\activate.bat
```

For development installation:
```bash
python setup.py develop
```

## Configuration

1. Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_key
API_KEY_ANTHROPIC=your_anthropic_key
API_KEY_GROQ=your_groq_key
MISTRAL_API_KEY=your_mistral_key
GOOGLE_API_KEY=your_google_key
```

2. Optional: Configure LM Studio or Ollama for local model support

## Usage

1. Start the application:
```bash
python main_AgentGroq.py
```

### Synthetic Data Generation

1. Configure generation settings:
   - Select appropriate system prompt
   - Set temperature and token limits
   - Choose output format template

2. Use Continuous Generation:
   - Click "Start Continuous Generation" to begin automatic data generation
   - Monitor progress in real-time
   - Click "Stop Continuous Generation" to halt the process
   - Generated files are saved automatically with timestamps

3. Manual Generation:
   - Enter specific prompts for custom data generation
   - Use templates and examples from the system
   - Review and modify generated data before saving

### File Management in Chat

The application supports direct file manipulation through chat commands:

```
# File Operation Commands
@filename.ext     # Reference and display file content
@@filename.ext    # Update existing file with new content
#filename.ext     # Save new generated content to file
```

## Project Structure

```
auto_generate_ai_chat_v2/
├── auto_generate_ai_chat_v2_a_03/
│   ├── Groq/
│   │   ├── ui/
│   │   └── utils/
│   ├── System_Prompts/
│   ├── Workspace/
│   ├── custom_logging/
│   ├── memory/
│   └── tabs/
├── setup.py
└── README.md
```

## Sample Data Generation

The tool generates data following structured formats like:

```
| prompt | agent_response | system_output | metadata |
|--------|----------------|----------------|----------|
| User query or task | JSON response | Tool output | Description/tags |
```

