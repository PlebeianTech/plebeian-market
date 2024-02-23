from datetime import datetime, timedelta
from enum import IntEnum
from hashlib import sha256
import json
import secp256k1

class EventKind(IntEnum):
    NIP98_AUTH = 27235

class EventValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

def validate_event(event_json):
    event_data = [0, event_json['pubkey'], event_json['created_at'], event_json['kind'], event_json['tags'], event_json['content']]
    event_data_str = json.dumps(event_data, separators=(",", ":"), ensure_ascii=False)
    serialized_event = event_data_str.encode()
    expected_event_id = sha256(serialized_event).hexdigest()

    if event_json['id'] != expected_event_id:
        raise EventValidationError("Invalid event ID!")

    try:
        pub_key = secp256k1.PublicKey(bytes.fromhex("02" + event_json['pubkey']), True) # 02 for Schnorr (BIP340)
        if not pub_key.schnorr_verify(bytes.fromhex(event_json['id']), bytes.fromhex(event_json['sig']), None, raw=True):
            raise EventValidationError("Invalid event signature!")
    except ValueError:
        raise EventValidationError("Invalid event signature!")

def get_nip98_pubkey(event_json, url, method):
    try:
        validate_event(event_json)
    except EventValidationError:
        return None

    if int(event_json['kind']) != EventKind.NIP98_AUTH or event_json['content'] != "":
        return None

    now = datetime.now()
    created_at = datetime.fromtimestamp(float(event_json['created_at']))
    if created_at < now - timedelta(minutes=1) or created_at > now + timedelta(minutes=1):
        return None

    u_tag = None
    method_tag = None
    for tag in event_json['tags']:
        match tag[0]:
            case 'u':
                u_tag = tag[1]
            case 'method':
                method_tag = tag[1]
    if u_tag != url or method_tag != method:
        return None

    return event_json['pubkey']
