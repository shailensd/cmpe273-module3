"""Inventory Service with equivalent REST and gRPC interfaces."""

import logging
import os
import time
from concurrent import futures

from flask import Flask, jsonify, request
import grpc

import inventory_pb2
import inventory_pb2_grpc


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REST_PORT = int(os.getenv("INVENTORY_REST_PORT", "5001"))
GRPC_PORT = int(os.getenv("INVENTORY_GRPC_PORT", "5002"))
INVENTORY_DELAY = float(os.getenv("INVENTORY_DELAY", "0"))
STOCK = {"item-1": 10, "item-2": 0}

app = Flask(__name__)


def check_inventory(item_id: str, quantity: int) -> tuple[bool, str | None, int]:
    """Return availability, an error category, and current stock."""
    if item_id not in STOCK:
        return False, "not_found", 0
    available_quantity = STOCK[item_id]
    if available_quantity < quantity:
        return False, "insufficient", available_quantity
    return True, None, available_quantity


def apply_delay() -> None:
    if INVENTORY_DELAY > 0:
        logger.info("Delaying inventory response for %.1f seconds", INVENTORY_DELAY)
        time.sleep(INVENTORY_DELAY)


@app.get("/health")
def health():
    return jsonify({"service": "inventory", "status": "running"})


@app.post("/inventory/check")
def rest_check_inventory():
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("item_id")
    quantity = payload.get("quantity")

    if not isinstance(item_id, str) or not item_id or isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "item_id must be non-empty and quantity must be a positive integer"}), 400

    apply_delay()
    available, error, available_quantity = check_inventory(item_id, quantity)
    response = {
        "available": available,
        "item_id": item_id,
        "requested_quantity": quantity,
        "available_quantity": available_quantity,
    }
    if error == "not_found":
        return jsonify({"error": "item not found", **response}), 404
    if error == "insufficient":
        return jsonify({"error": "insufficient inventory", **response}), 409
    return jsonify(response), 200


class InventoryServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckInventory(self, request_message, context):
        if not request_message.item_id or request_message.quantity <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "item_id and positive quantity are required")

        apply_delay()
        available, error, available_quantity = check_inventory(
            request_message.item_id, request_message.quantity
        )
        if error == "not_found":
            context.abort(grpc.StatusCode.NOT_FOUND, "item not found")
        if error == "insufficient":
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "insufficient inventory")

        return inventory_pb2.CheckInventoryResponse(
            available=available,
            item_id=request_message.item_id,
            requested_quantity=request_message.quantity,
            available_quantity=available_quantity,
        )


def serve_grpc() -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServicer(), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    logger.info("gRPC Inventory Service listening on port %s", GRPC_PORT)
    return server


if __name__ == "__main__":
    grpc_server = serve_grpc()
    try:
        logger.info("REST Inventory Service listening on port %s", REST_PORT)
        app.run(host="0.0.0.0", port=REST_PORT, threaded=True, use_reloader=False)
    finally:
        grpc_server.stop(0)
