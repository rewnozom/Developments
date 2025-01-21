from groq import Groq as _Groq
from config import GROQ_API_KEY
from shared_variables import get_model_var, get_temperature_var, get_max_tokens_var, get_system_prompt_var

class Groq:
    def __init__(self):
        self.client = _Groq(api_key=GROQ_API_KEY)

    def inference(self, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": get_system_prompt_var().get()},
                {"role": "user", "content": prompt.strip()}
            ],
            model=get_model_var().get(),
            temperature=get_temperature_var().get(),
            max_tokens=get_max_tokens_var().get()
        )
        return chat_completion.choices[0].message.content