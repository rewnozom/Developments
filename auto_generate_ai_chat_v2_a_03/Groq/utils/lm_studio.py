from openai import OpenAI
from shared_variables import get_model_var, get_temperature_var, get_max_tokens_var, get_system_prompt_var

class LMStudio:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key=None)

    def inference(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=get_model_var().get(),
            messages=[
                {"role": "system", "content": get_system_prompt_var().get()},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=get_temperature_var().get(),
            max_tokens=get_max_tokens_var().get()
        )
        return completion.choices[0].message.content