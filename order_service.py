"""Order Service that can call Inventory over REST or gRPC."""

import logging
import os

from flask import Flask, jsonify, request
import grpc
import requests

import inventory_pb2
import inventory_pb2_grpc


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ORDER_PORT = int(os.getenv("ORDER_PORT", "5003"))
INVENTORY_REST_URL = os.getenv("INVENTORY_REST_URL", "http://localhost:5001/inventory/check")
INVENTORY_GRPC_TARGET = os.getenv("INVENTORY_GRPC_TARGET", "localhost:5002")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "1"))

app = Flask(__name__)


def validate_order(payload):
    item_id = payload.get("item_id")
    quantity = payload.get("quantity")
    if not isinstance(item_id, str) or not item_id or isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return None, jsonify({"error": "item_id must be non-empty and quantity must be a positive integer"}), 400
    return {"item_id": item_id, "quantity": quantity}, None


@app.get("/health")
def health():
    return jsonify({"service": "order", "status": "running"})


@app.post("/orders/rest")
def create_order_rest():
    order, error = validate_order(request.get_json(silent=True) or {})
    if error:
        return error
    try:
        inventory_response = requests.post(INVENTORY_REST_URL, json=order, timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        logger.warning("REST inventory request exceeded %.1f-second timeout", REQUEST_TIMEOUT)
        return jsonify({"error": "inventory request timed out", "transport": "REST"}), 504
    except requests.RequestException as exc:
        logger.error("REST inventory request failed: %s", exc)
        return jsonify({"error": "inventory service unavailable", "transport": "REST"}), 502

    if inventory_response.status_code != 200:
        return jsonify({"error": "order rejected", "transport": "REST", "inventory": inventory_response.json()}), inventory_response.status_code

    return jsonify({"order_status": "accepted", "transport": "REST", "inventory": inventory_response.json()}), 200


@app.post("/orders/grpc")
def create_order_grpc():
    order, error = validate_order(request.get_json(silent=True) or {})
    if error:
        return error
    try:
        with grpc.insecure_channel(INVENTORY_GRPC_TARGET) as channel:
            stub = inventory_pb2_grpc.InventoryServiceStub(channel)
            inventory_response = stub.CheckInventory(
                inventory_pb2.CheckInventoryRequest(**order), timeout=REQUEST_TIMEOUT
            )
    except grpc.RpcError as exc:
        status = exc.code()
        logger.warning("gRPC inventory request failed with %s", status.name)
        if status == grpc.StatusCode.DEADLINE_EXCEEDED:
            return jsonify({"error": "inventory request deadline exceeded", "transport": "gRPC"}), 504
        if status == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "order rejected", "transport": "gRPC", "inventory": "item not found"}), 404
        if status == grpc.StatusCode.FAILED_PRECONDITION:
            return jsonify({"error": "order rejected", "transport": "gRPC", "inventory": "insufficient inventory"}), 409
        if status == grpc.StatusCode.INVALID_ARGUMENT:
            return jsonify({"error": exc.details(), "transport": "gRPC"}), 400
        return jsonify({"error": "inventory service unavailable", "transport": "gRPC"}), 502

    return jsonify({
        "order_status": "accepted",
        "transport": "gRPC",
        "inventory": {
            "available": inventory_response.available,
            "item_id": inventory_response.item_id,
            "requested_quantity": inventory_response.requested_quantity,
            "available_quantity": inventory_response.available_quantity,
        },
    }), 200


if __name__ == "__main__":
    logger.info("Order Service listening on port %s", ORDER_PORT)
    app.run(host="0.0.0.0", port=ORDER_PORT, threaded=True, use_reloader=False)
