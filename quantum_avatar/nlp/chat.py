# -*- coding: utf-8 -*-


class ChatBot:
    def __init__(self, nlp_processor=None):
        if nlp_processor is None:
            from .nlp_processor import NLPProcessor

            nlp_processor = NLPProcessor()

        self.nlp = nlp_processor
        self.conversation_history: list[tuple[str, str]] = []
        self.max_history = 500

    @staticmethod
    def _norm(value) -> str:
        return str(value).strip() if value is not None else ""

    def respond(self, user_input):
        text = self._norm(user_input)
        if not text:
            response = "Bitte gib eine Nachricht ein."
            self.conversation_history.append((text, response))
            self.conversation_history = self.conversation_history[-self.max_history :]
            return response

        processed = self.nlp.process_text(text)
        corrected = str(processed.get("corrected_text", text))
        if "hallo" in corrected.lower():
            response = "Hallo! Wie kann ich helfen?"
        else:
            response = "Ich verstehe. Erzähl mehr."

        self.conversation_history.append((text, response))
        self.conversation_history = self.conversation_history[-self.max_history :]
        return response
