from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from ...config import Config
from shared_variables import model_var, temperature_var, max_tokens_var, system_prompt_var

class MistralAi:
    def __init__(self):
        config = Config()
        api_key = config.get_mistral_api_key()
        self.client = MistralClient(api_key=api_key)

    def inference(self, model_id: str, prompt: str) -> str:
        chat_completion = self.client.chat(
            model=model_id,
            messages=[
                ChatMessage(role="user", content=prompt.strip())
            ],
            temperature=0
        )
        return chat_completion.choices[0].message.content
