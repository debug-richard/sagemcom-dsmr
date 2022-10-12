import json

from decode import decrypt_frame, convert_to_dict, check_and_encode_frame

data_1 = ""
data_2 = ""

GLOBAL_UNICAST_ENC_KEY = ""
GLOBAL_AUTHENTICATION_KEY = ""

if __name__ == "__main__":
    if GLOBAL_UNICAST_ENC_KEY == "":
        raise RuntimeError("Please set the GLOBAL_UNICAST_ENC_KEY")

    if GLOBAL_AUTHENTICATION_KEY == "":
        raise RuntimeError("Please set the GLOBAL_AUTHENTICATION_KEY")

    for data in (data_1, data_2):
        data = bytes.fromhex(data)
        decrypted = decrypt_frame(GLOBAL_UNICAST_ENC_KEY, GLOBAL_AUTHENTICATION_KEY, data)
        encoded_frame = check_and_encode_frame(decrypted)
        response_as_dict = convert_to_dict(encoded_frame)
        #print("Raw frame:\n" + str(data.hex()))
        #print(json.dumps(response_as_dict, indent=2))
        print("Wird aktuell geliefert: " + str(response_as_dict["1-0:1.7.0"]))
        print("Wird aktuell eingespeist: " + str(response_as_dict["1-0:2.7.0"]))
        print("Wurde geliefert (Zählerstand): " + str(response_as_dict["1-0:1.8.0"]))
        print("Wurde eingespeist (Zählerstand): " + str(response_as_dict["1-0:2.8.0"]))
        print()
