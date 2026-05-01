from openai import OpenAI


class ModelAdapter:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class OpenAIAdapter(ModelAdapter):
    def __init__(self, model_name: str = "gpt-4.1-mini", api_key: str | None = None) -> None:
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""


class ClaudeAdapter(ModelAdapter):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError("Claude integration not yet implemented")