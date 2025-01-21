import ollama
from custom_logging.logger import Logger
from config import OLLAMA_API_ENDPOINT
from shared_variables import get_model_var, get_temperature_var, get_max_tokens_var, get_system_prompt_var

log = Logger()

class Ollama:
    def __init__(self):
        try:
            self.client = ollama.Client(base_url=OLLAMA_API_ENDPOINT)
            self.models = self.client.list()["models"]
            get_model_var().set(self.models[0])  # Default to the first model
            log.info("Ollama available")
        except Exception as e:
            self.client = None
            log.warning(f"Ollama not available: {e}")

    def inference(self, prompt: str) -> str:
        response = self.client.generate(
            model=get_model_var().get(),
            prompt=prompt.strip(),
            system_prompt=get_system_prompt_var().get(),
            options={"temperature": get_temperature_var().get()}
        )
        return response['response']