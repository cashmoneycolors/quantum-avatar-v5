# -*- coding: utf-8 -*-


class ChatBot:
    def __init__(self, nlp_processor=None):
        if nlp_processor is None:
            from .nlp_processor import NLPProcessor

            nlp_processor = NLPProcessor()

        self.nlp = nlp_processor
        self.conversation_history = []

    def respond(self, user_input):
        processed = self.nlp.process_text(user_input)
        if "hallo" in processed["corrected_text"].lower():
            response = "Hallo! Wie kann ich helfen?"
        else:
            response = "Ich verstehe. Erzähl mehr."

        self.conversation_history.append((user_input, response))
        return response
