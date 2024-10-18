import time

def create_pdu(tag, type, message_identifier, iids, values, errors):
    timestamp = time.strftime('%d:%m:%Y:%H:%M:%S:%f')[:-3]
    pdu = f"{tag}|{type}|{timestamp}|{message_identifier}|{iids}|{values}|{errors}\0"
    return pdu

def get_timestamp():
    return time.strftime('%d:%m:%Y:%H:%M:%S:%f')[:-3]

def parse_pdu(pdu):
    fields = pdu.strip('\0').split('|')
    return {
        "tag": fields[0],
        "type": fields[1],
        "timestamp": fields[2],
        "message_identifier": fields[3],
        "iids": fields[4] if len(fields) > 4 else "",
        "values": fields[5] if len(fields) > 5 else "",
        "errors": fields[6] if len(fields) > 6 else ""
    }
