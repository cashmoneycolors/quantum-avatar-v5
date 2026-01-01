import unittest
from quantum_avatar.nlp.nlp_processor import NLPProcessor
from quantum_avatar.vision.image_generator import ImageGenerator
from quantum_avatar.vision.art_categorizer import ArtCategorizer
from quantum_avatar.quantum.quantum_calculator import QuantumCalculator
from quantum_avatar.business.business_logic import BusinessLogic
from quantum_avatar.business.margin_optimizer import MarginOptimizer
from quantum_avatar.autonomy.autonomous_executor import AutonomousExecutor
from quantum_avatar.security.security_module import SecurityModule


class TestAllModules(unittest.TestCase):
    def test_nlp(self):
        nlp = NLPProcessor()
        result = nlp.process_text("Hallo Welt")
        self.assertIsInstance(result, dict)
        self.assertIn("corrected_text", result)
        self.assertIn("tokens", result)

    def test_vision(self):
        gen = ImageGenerator()
        image = gen.generate_image("test")
        self.assertIsNone(image)

    def test_art(self):
        art = ArtCategorizer()
        # Mock image
        result = art.categorize_art("mock")
        self.assertIsInstance(result, str)

    def test_quantum(self):
        qc = QuantumCalculator()
        products = [{"name": "Apple", "spoil_rate": 0.1, "freshness_index": 0.9}]
        result = qc.optimize_produce_display(products, 20)
        self.assertIsInstance(result, list)

    def test_business(self):
        bl = BusinessLogic()
        result = bl.earn_points("user1", 10)
        self.assertEqual(result["points"], 10)

        invalid = bl.virtual_earnings("user1", "unknown_action")
        self.assertIsInstance(invalid, dict)
        self.assertIn("error", invalid)

    def test_margin_optimizer(self):
        opt = MarginOptimizer(target_margin=0.30, vat_rate=0.026)
        price = opt.calculate_sales_price(10.0, 5.0)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 10.0)

        discounted = opt.dynamic_pricing(20.0, "18:00", expiry_time="17:00")
        self.assertEqual(discounted, 10.0)

        full = opt.dynamic_pricing(20.0, "16:59", expiry_time="17:00")
        self.assertEqual(full, 20.0)

    def test_autonomy(self):
        ae = AutonomousExecutor()
        state = {"day": "Saturday", "weather": "sunny"}
        result = ae.autonomous_decision(state)
        self.assertIsInstance(result, str)

        ae2 = AutonomousExecutor()
        ae2.add_trigger({"day": "Saturday", "weather": "sunny"}, "send_whatsapp")
        self.assertEqual(
            ae2.execute({"day": "Saturday", "weather": "sunny"}),
            "WhatsApp-Einladung gesendet",
        )

    def test_security(self):
        sm = SecurityModule()
        result = sm.check_data_privacy({"name": "John"})
        self.assertIn("Consent", result)


if __name__ == "__main__":
    unittest.main()
