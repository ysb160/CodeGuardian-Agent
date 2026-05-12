from __future__ import annotations

from openai import OpenAI

from codeguardian.config import Settings, get_settings


class LLMClient:
    """Small wrapper around the OpenAI Responses API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if not self.settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Create a local .env file from "
                ".env.example and set OPENAI_API_KEY. Never commit the .env file."
            )

        self.client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url or None,
        )
        self.model = self.settings.openai_model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.output_text
        except Exception as exc:  # noqa: BLE001 - convert SDK errors to user-facing text.
            raise RuntimeError(f"LLM request failed: {exc}") from exc
