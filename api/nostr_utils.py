from hashlib import sha256
import json
import secp256k1

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
