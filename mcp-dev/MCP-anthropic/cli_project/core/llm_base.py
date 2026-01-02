class LLMServiceBase:
    """
    Universal base class for all LLM providers.
    Handles:
    - extract_text()
    - add_assistant_message()
    - add_user_message()
    - text_from_message()
    """

    @staticmethod
    def extract_text(response):
        """Extract text from OpenAI, Gemini, Anthropic, or unknown formats."""

        # Gemini (google-genai)
        if hasattr(response, "content") and hasattr(response.content, "parts"):
            return "".join(
                (p.text or "")
                for p in response.content.parts
                if hasattr(p, "text")
            )

        # OpenAI
        if hasattr(response, "content") and isinstance(response.content, str):
            return response.content

        # Anthropic
        if hasattr(response, "content") and isinstance(response.content, list):
            return "".join(
                block.text for block in response.content
                if getattr(block, "type", "") == "text"
            )

        return str(response)

    @staticmethod
    def add_assistant_message(messages, response):
        text = LLMServiceBase.extract_text(response)
        messages.append({"role": "assistant", "content": text})

    @staticmethod
    def add_user_message(messages, text):
        messages.append({"role": "user", "content": str(text)})

    @staticmethod
    def text_from_message(response):
        return LLMServiceBase.extract_text(response)
