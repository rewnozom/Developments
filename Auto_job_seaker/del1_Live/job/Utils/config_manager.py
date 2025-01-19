# ..\..\job\Utils\config_manager.py
# config_manager.py
from typing import List, Dict

CONFIG = {
    "browser_visible": True,
    "output_dir": "output",
    "start_page": 18,
    "max_jobs_per_url_search": 295,
    "base_url": "https://se.jooble.org/SearchResult?p={}&rgns=Stockholm&ukw={}",

    # Performance settings
    "performance": {
        "min_delay": 0.3,  # Increased from 0.3
        "max_delay": 3,  # Increased from 0.7
        "page_load_wait": 17,  # Increased from 1.5
        "concurrent_parsing": True,
        "batch_size": 33
    },

    # Scoring system
    "give_points_keywords": {
        "include": [
            # Enstaka ord (teknologier)
            "python",
            "react",
            "flask",
            "fastapi",
            "django",
            "json",
            "electron",
            "tailwind",
            "typescript",
            "javascript",
            "nodejs",
            "html",
            "prisma",
            "mongodb",
            "mysql",
            "git",
            "docker",
            "opencv",
            "selenium",
            "pandas",
            "numpy",
            "pytorch",
            "tensorflow",
            "matplotlib",
            "pillow",
            "ffmpeg",
            "backend",
            "backend developer",
            "backend utvecklare",
            "ai agent",
            "agent",
            "multi agent",
            "ai agents",
            "agenter",
            "llm",
            "fullstack",
            "utvecklare",
            "developer",
            "automation",
            "api",
            "fastapi",
            "problemlösning",
            "automatisering",
            "datastruktur",
            "integration",
            "opencv",
            "whisper",
            "langchain",
            "beautifulsoup",
            "ai",
            "ml",
            "computer vision",
            "machine learning",
            "deep learning",
            "data science",
            "api integration",
            "system development",
            "full stack",
            "text to speech",
            "speech to text",
            "prompt engineering",
            "data analysis",
            "software development",
            "stable diffusion",
            "ai development",
            "data processing",
            "data engineering",
            "system automation",
            "image processing",
            "project development",
            "team lead",
            "project manager",
        ],
        "deduct_points_keywords": [
            # Roller som inte matchar
            "lead",
            "chef",
            "konsultchef",
            "enterprise",
            "director",
            "vp",
            "vice president",

            # Teknologier
            "scala",
            "cobol",
            "ruby",
            "golang",
            "pearl",
            "fortran",
            "wordpress",
            "drupal",
            "sharepoint",
            "C++",
            "C#",

            # Brancher utanför fokus
            "cisco",
            "nätverk",
            "nätverkstekniker",
            "cloud architect",

            # Certifieringar
            "cisco certified",
            "aws certified",
            "azure certified",
            "mcse",
            "ccna",
            "pmp"
        ]
    },

    # Random delays for anti-detection
    "random_delays": {
        "min": 1,
        "max": 3
    },

    # Date Filtering Settings
    "date_filter": {
        "enabled": True,  # Toggle för att aktivera/inaktivera datumfiltrering
        "max_days": 30    # Maximalt antal dagar sedan annonsen lades ut
    }
}

SEARCH_TERMS: List[str] = [
    "python utvecklare",
    "python developer",
    "python programmering",
    "python programming",
    "python backend",
    "python backend developer",
    "python backend utvecklare",
    "full stack",
    "full stack developer",
    "full stack utvecklare",
    "fullstack developer",
    "fullstack utvecklare",
    "fullstack engineer",
    "ai python",
    "ai developer",
    "ai utvecklare",
    "python ai",
    "python automation",
    "automation developer",
    "automation utvecklare",
    "automationsutvecklare",
    "developer",
    "utvecklare",
    "systemutvecklare",
    "system developer",
    "application developer",
    "applikationsutvecklare",
    "mjukvaruutvecklare",
    "software developer",
    "data engineer",
    "data utvecklare",
    "backend developer",
    "backend utvecklare",
    "python engineer",
    "python fullstack",
    "python system developer",
    "python application developer",
    "python data engineer",
    "python software developer"
]
