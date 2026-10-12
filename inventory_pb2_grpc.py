# Generated-equivalent gRPC module for proto/inventory.proto.
# Regenerate with:
# python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/inventory.proto

import grpc

import inventory_pb2 as inventory__pb2


class InventoryServiceStub:
    def __init__(self, channel):
        self.CheckInventory = channel.unary_unary(
            "/inventory.InventoryService/CheckInventory",
            request_serializer=inventory__pb2.CheckInventoryRequest.SerializeToString,
            response_deserializer=inventory__pb2.CheckInventoryResponse.FromString,
        )


class InventoryServiceServicer:
    def CheckInventory(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_InventoryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "CheckInventory": grpc.unary_unary_rpc_method_handler(
            servicer.CheckInventory,
            request_deserializer=inventory__pb2.CheckInventoryRequest.FromString,
            response_serializer=inventory__pb2.CheckInventoryResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "inventory.InventoryService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))

