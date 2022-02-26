from boto3.dynamodb.types import TypeSerializer, TypeDeserializer


def convert_to_dynamodb_format(data):
    serializer = TypeSerializer()
    return serializer.serialize(data)['M']


def convert_to_python_format(data):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in data}
