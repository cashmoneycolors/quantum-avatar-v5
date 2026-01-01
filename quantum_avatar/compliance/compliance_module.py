class ComplianceModule:
    def __init__(self):
        self.dsg_compliant = True

    def check_consent(self, user_data):
        # Check if consent is given for data processing
        if "consent" in user_data and user_data["consent"]:
            return "DSG-Check: Consent vorhanden, Datenverarbeitung erlaubt."
        return "DSG-Check: Kein Consent, Datenverarbeitung verboten."

    def anonymize_data(self, data):
        # Remove personal identifiers
        anonymized = data.copy()
        personal_fields = ["name", "email", "phone", "address"]
        for field in personal_fields:
            if field in anonymized:
                anonymized[field] = "anonymisiert"
        return anonymized

    def audit_trail(self, action):
        # Log for compliance
        print(f"DSG-Audit: {action}")
        return True

    def gdpr_equivalent_check(self, data_processing):
        # Swiss DSG is similar to GDPR
        if "purpose" in data_processing and data_processing["purpose"] in [
            "marketing",
            "service",
        ]:
            return "DSG-Äquivalent: Datenverarbeitung zulässig."
        return "DSG-Äquivalent: Zweck nicht spezifiziert."
