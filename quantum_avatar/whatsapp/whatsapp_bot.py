class WhatsAppBot:
    def __init__(self):
        self.responses = {
            "preis sucuk": "Sucuk kostet CHF 5.99 pro 100g.",
            "öffnungszeiten": "Wir sind täglich von 8:00 bis 19:00 geöffnet.",
            "vorbestellung fleisch": "Bitte geben Sie Menge und Art an.",
        }

    def respond(self, message):
        for key, response in self.responses.items():
            if key in message.lower():
                return response
        return "Wie können wir Ihnen helfen?"
