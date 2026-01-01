import logging
import time


class MonitoringModule:
    def __init__(self):
        logging.basicConfig(
            filename="quantum_avatar.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def log_action(self, action, details=""):
        logging.info(f"Action: {action} - Details: {details}")

    def monitor_performance(self, function_name, start_time):
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Performance: {function_name} took {duration:.2f} seconds")

    def alert_on_error(self, error_message):
        logging.error(f"Error: {error_message}")
        # In real world, send alert

    def feedback_loop(self, input_data, output_data):
        # Simple feedback for learning
        if "success" in output_data:
            logging.info("Feedback: Positive outcome")
        else:
            logging.warning("Feedback: Needs improvement")
