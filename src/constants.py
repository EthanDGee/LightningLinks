import os

from dotenv import load_dotenv


load_dotenv()

# File info
NOTE_EXTENSION = ".md"
EXCLUSIVE_EXTENSION = ".excalidraw.md"
ENCODING = "utf-8"

# File Pattern Indicators
LIGHTNING_LINKS_HEADER = "### Lightning Links"
LINK_START = "[["
LINK_END = "]]"
YAML_INDICATOR = "---\n"
TAG_INDICATOR = "#"

# Model and API configuration
NUM_REFERENCE_NOTES = int(os.getenv("NUM_REFERENCE_NOTES", 10))
NUM_LIGHTNING_LINKS = int(os.getenv("NUM_LIGHTNING_LINKS", 3))
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"
)

# AI Provider
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")


# OpenAI Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
