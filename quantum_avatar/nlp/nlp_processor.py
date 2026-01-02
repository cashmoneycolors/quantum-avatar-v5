from __future__ import annotations

try:
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None

try:
    from autocorrect import Speller  # type: ignore
except Exception:  # pragma: no cover
    Speller = None


class NLPProcessor:
    def __init__(self, language="en"):
        self.language = language

        self.nlp = None
        if spacy is not None:
            try:
                self.nlp = (
                    spacy.load(f"{language}_core_web_sm")
                    if language == "en"
                    else spacy.load("xx_ent_wiki_sm")
                )  # Multilingual model
            except Exception:
                self.nlp = spacy.blank(language if language == "en" else "xx")

        self._translator_model = "Helsinki-NLP/opus-mt-en-de"
        self.translator = None

        self.speller = None
        if Speller is not None:
            try:
                self.speller = Speller(lang=language)
            except Exception:
                self.speller = None

    def process_text(self, text):
        if text is None:
            text = ""
        if not isinstance(text, str):
            text = str(text)
        # Autocorrect
        corrected = self.speller(text) if self.speller is not None else text

        # NLP processing
        if self.nlp is None:
            return {
                "corrected_text": corrected,
                "entities": [],
                "tokens": str(corrected).split(),
            }

        doc = self.nlp(corrected)
        return {
            "corrected_text": corrected,
            "entities": [(ent.text, ent.label_) for ent in doc.ents],
            "tokens": [token.text for token in doc],
        }

    def translate(self, text, target_lang="de"):
        if self.translator is None and pipeline is not None:
            try:
                self.translator = pipeline(
                    "translation",
                    model=self._translator_model,
                )
            except Exception:
                self.translator = None

        if self.translator is None:
            return text

        result = self.translator(text, target_lang=target_lang)
        return result[0]["translation_text"]
