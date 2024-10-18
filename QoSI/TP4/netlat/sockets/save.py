from sockets import Definitions, Payload
from utilities import Timestamp
from network import Ping
from scapy.all import IP
import json
import os

class Save:
    @staticmethod
    def _to_file(data):
        def validate_path(path):
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        validate_path(f'datasets/{data["from_"]}/{data["type_"]}')
        date = Timestamp.get_formatted().replace(" ",";").replace(":","h")
        date = date.split(";")[0]

        if not os.path.exists(f'datasets/{data["from_"]}/{data["type_"]}/{data["from_"]}_date_{date}.json'):
            with open(f'datasets/{data["from_"]}/{data["type_"]}/{data["from_"]}_date_{date}.json', 'w') as f:
                f.write(json.dumps([data], indent=4))
        else:
            current_data = []
            with open(f'datasets/{data["from_"]}/{data["type_"]}/{data["from_"]}_date_{date}.json', 'r') as f:
                current_data = json.load(f)
                current_data.append(data)
            with open(f'datasets/{data["from_"]}/{data["type_"]}/{data["from_"]}_date_{date}.json', 'w') as f:
                f.write(json.dumps(current_data, indent=4))


    @staticmethod
    def process_packet(data, key, timestamp, filter):
        packet_key = (key[0][0], key[0][1], key[1][0], key[1][1])
        my_payload = Payload.deserialize(data)
        if my_payload is not None:
            scapy_sniff = filter.packet_info.get(packet_key, None)
            while scapy_sniff is None:
                scapy_sniff = filter.packet_info.get(packet_key, None)
            json_object = {"from_": my_payload.from_, "sent_at":my_payload.timestamp, "recieved_at":timestamp.get_timestamp(), "type_": my_payload.type_}
            json_object["tos_changed"] = my_payload.tos != scapy_sniff[IP].tos
            json_object["recieved_tos"] = scapy_sniff[IP].tos
            json_object["send_tos"] = my_payload.tos
            json_object["time_it_took"] = timestamp.get_timestamp() - my_payload.timestamp
            Save._to_file(json_object)

    @staticmethod
    def _data(packet_data):
        try:
            my_payload = Payload.deserialize(packet_data)
        except Exception as e:
            my_payload = {"from_": "unknown", "timestamp": Timestamp.get_formatted(), "type_": "unknown", "data": {"unknown": "unknown"}}

        if my_payload.type_ == Definitions.Messages.PING_REQUEST:
            my_payload.data = Ping(my_payload.hostname).to_dict()

        json_object = {}
        has_data = False
        for attr in my_payload.__dict__.keys():
            if not attr.startswith("_"):
                json_object[attr] = getattr(my_payload, attr)
                if attr == "data":
                    if type(my_payload.data) == dict:
                        has_data = True

        json_object["from_"] = json_object.get("from_", "unknown")
        json_object["timestamp"] = json_object.get("timestamp", Timestamp.get_formatted())
        json_object["type_"] = json_object.get("type_", "unknown")

        if has_data:
            del json_object["data"]
            json_object.update(my_payload.data)

        Save._to_file(json_object)

