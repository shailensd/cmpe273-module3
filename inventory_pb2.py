# Generated-equivalent protobuf module for proto/inventory.proto.
# Regenerate with:
# python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/inventory.proto

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder


_file = _descriptor_pb2.FileDescriptorProto(
    name="inventory.proto", package="inventory", syntax="proto3"
)


def _add_message(name, fields):
    message = _file.message_type.add(name=name)
    for field_name, number, field_type in fields:
        message.field.add(
            name=field_name,
            number=number,
            label=_descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL,
            type=field_type,
        )


_add_message(
    "CheckInventoryRequest",
    [
        ("item_id", 1, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("quantity", 2, _descriptor_pb2.FieldDescriptorProto.TYPE_INT32),
    ],
)
_add_message(
    "CheckInventoryResponse",
    [
        ("available", 1, _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL),
        ("item_id", 2, _descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("requested_quantity", 3, _descriptor_pb2.FieldDescriptorProto.TYPE_INT32),
        ("available_quantity", 4, _descriptor_pb2.FieldDescriptorProto.TYPE_INT32),
    ],
)
service = _file.service.add(name="InventoryService")
method = service.method.add(name="CheckInventory")
method.input_type = ".inventory.CheckInventoryRequest"
method.output_type = ".inventory.CheckInventoryResponse"

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(_file.SerializeToString())

_sym_db = _symbol_database.Default()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "inventory_pb2", globals())

