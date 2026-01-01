class DeliveryRouting:
    def __init__(self):
        self.routes = {
            "amriswil": ["customer1", "customer2"],
            "romanshorn": ["customer3"],
            "arbon": ["customer4"],
        }

    def optimize_route(self, start="amriswil"):
        # Simple route optimization
        route = self.routes.get(start, [])
        return f"Route: {start} -> {' -> '.join(route)}"

    def calculate_cost(self, distance_km):
        fuel_cost_per_km = 0.50  # CHF
        return distance_km * fuel_cost_per_km
