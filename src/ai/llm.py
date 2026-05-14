from typing import Any

from openai import AsyncOpenAI

from src.storage.config import load_config


class LLMClient:
    def __init__(self):
        cfg = load_config()
        ai_cfg = cfg["ai"]
        self.provider = ai_cfg.get("provider", "deepseek")
        self.model = ai_cfg.get("model", "deepseek-chat")
        self.api_key = ai_cfg.get("api_key", "")
        self.api_base = ai_cfg.get("api_base", "")
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            if self.provider == "deepseek":
                base_url = self.api_base or "https://api.deepseek.com"
            elif self.provider == "openai":
                base_url = self.api_base or "https://api.openai.com/v1"
            else:
                base_url = self.api_base

            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=base_url,
            )
        return self._client

    def _has_valid_key(self) -> bool:
        return bool(self.api_key) or bool(self._client)

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        if not self._has_valid_key():
            return await self._mock_chat(messages)

        try:
            client = self._ensure_client()
            resp = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.8),
                max_tokens=kwargs.get("max_tokens", 1024),
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"（AI暂时无法回应: {e}）"

    async def chat_stream(self, messages: list[dict[str, str]]):
        if not self._has_valid_key():
            yield "[未配置 API Key，请在 config.yaml 中设置 ai.api_key]"
            return

        try:
            client = self._ensure_client()
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=1024,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"（AI暂时无法回应: {e}）"

    async def _mock_chat(self, messages: list[dict[str, str]]) -> str:
        last = messages[-1]["content"] if messages else ""
        return (
            f"（我需要配置 API Key 才能认真回答你。\n"
            f"请先在 config.yaml 中设置 ai.api_key，或运行：\n"
            f"ai-podcast config set ai.api_key <你的key>\n"
            f"目前支持 DeepSeek / OpenAI 等 API。）\n\n"
            f"不过你刚才说的是：「{last[:50]}」对吗？"
        )
