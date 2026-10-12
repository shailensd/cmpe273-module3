"""Direct gRPC client used to demonstrate the InventoryService contract."""

import os

import grpc

import inventory_pb2
import inventory_pb2_grpc


TARGET = os.getenv("INVENTORY_GRPC_TARGET", "localhost:5002")


def main():
    with grpc.insecure_channel(TARGET) as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        response = stub.CheckInventory(
            inventory_pb2.CheckInventoryRequest(item_id="item-1", quantity=2),
            timeout=1,
        )
        print("gRPC response:")
        print({
            "available": response.available,
            "item_id": response.item_id,
            "requested_quantity": response.requested_quantity,
            "available_quantity": response.available_quantity,
        })


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as exc:
        print(f"gRPC error: {exc.code().name}: {exc.details()}")
