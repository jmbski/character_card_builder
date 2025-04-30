import json
import re

import requests

from typing import Optional, Dict

import jbutils

from card_builder.common import consts
from card_builder.common import CbGlobals


def clean_ai_json_response(response_text: str) -> str:
    """Cleans common AI output artifacts from a JSON string."""
    # Remove ```json or ``` wrapping
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$", "", response_text.strip(), flags=re.MULTILINE
    )
    return cleaned.strip()


def get_blank_card() -> dict:
    data = {}
    for tab in consts.TAB_SCHEMAS:
        tab_data = {
            key: schema.get_default() for key, schema in tab.property_defs.items()
        }

        if tab.value_paths:
            for tab_path in tab.value_paths:
                jbutils.set_nested(data, tab_path, tab_data)
        else:
            for key, value in tab_data.items():
                schema = tab.property_defs.get(key)
                if not schema:
                    continue
                if schema.value_paths:
                    for p_path in schema.value_paths:
                        jbutils.set_nested(data, p_path, value)
    return data


class OobaClient:
    """Client for communicating with oobabooga's text generation API."""

    def __init__(self, api_url: str = CbGlobals.OOBA_API_URL) -> None:
        self.api_url = api_url

    def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 150
    ) -> Optional[str]:
        """Send a prompt to the API and get generated text.

        Args:
            prompt: The input text prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text, or None if failed.
        """
        payload = {
            "model": "gpt-3",  # ooba often ignores this
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": ["</s>", "###"],
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=600)

            response.raise_for_status()

            return response.json()["choices"][0]["text"]
        except (requests.RequestException, KeyError) as e:
            print(f"Error during generation: {e}")
            return None

    def parse_character_card(
        self, card_text: str, template: Optional[dict] = None
    ) -> Optional[Dict[str, str]]:
        """Attempts to parse a character card text using AI assistance.

        Args:
            card_text (str): Raw text to parse.
            known_fields (Optional[list[str]]): List of known fields to prioritize.

        Returns:
            Optional[Dict[str, str]]: Parsed character data, or None if parsing failed.
        """
        """ resp_structure = (
            json.dumps(template) if template else "the most appropriate structure"
        ) """

        structure = get_blank_card()
        desc_struct = structure.get("description", {})
        pers_struct = structure.get("personality", {})
        resp_struct = json.dumps(
            {"description": desc_struct, "personality": pers_struct}
        )
        prompt = (
            "Parse the following character card text into a JSON object. "
            f"Try to fit values into the following JSON template: \n```{resp_struct}\n```\n"
            "If values do not seem to have a good place within that template, place them in a new top-level property called 'misc'"
            "Do NOT summarize or modify any text values, only assign them to appropriate properties."
            "Output ONLY valid JSON. "
            "DO NOT include any explanations, formatting, markdown, or comments."
            "Respond ONLY with a valid JSON string."
            ""
            "Text:"
            "---"
            f"{card_text}"
            "---"
        )

        ai_response = self.generate(prompt, temperature=0.3, max_tokens=3500)

        if ai_response is None:
            return None

        ai_response = clean_ai_json_response(ai_response)
        try:
            parsed = json.loads(ai_response)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Failed to decode AI response as JSON: {e}")
            print(f"AI Response was: {ai_response}")
            return None
