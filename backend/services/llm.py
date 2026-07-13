"""LLM service — calls the local Ollama model to generate answers."""

import requests

from core.config import LLM_MODEL, OLLAMA_HOST


class LLMService:
    """Thin wrapper around the Ollama ``/api/generate`` endpoint."""

    def __init__(
        self,
        base_url: str = OLLAMA_HOST,
        model: str = LLM_MODEL,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate(self, prompt: str) -> str:
        """Send *prompt* to the LLM and return the generated text.

        Args:
            prompt: The complete prompt (system instructions + context +
                question) to send.

        Returns:
            The model's text response.

        Raises:
            requests.RequestException: If Ollama is unreachable.
            RuntimeError: If Ollama returns an error.
        """
        resp = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()["response"]
