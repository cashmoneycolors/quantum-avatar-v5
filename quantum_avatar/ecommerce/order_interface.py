from flask import Flask, request, jsonify

app = Flask(__name__)

orders = []


@app.route("/order", methods=["POST"])
def place_order():
    data = request.json
    product = data["product"]
    pickup_time = data["pickup_time"]
    orders.append({"product": product, "pickup_time": pickup_time})
    return jsonify({"status": "Order placed"})


@app.route("/pickup_windows")
def get_pickup_windows():
    return jsonify(["10:00-11:00", "14:00-15:00", "17:00-18:00"])


if __name__ == "__main__":
    app.run(port=5001)
