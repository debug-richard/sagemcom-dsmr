from binascii import unhexlify

from crccheck.crc import Crc16Arc as Crc16Cms
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def __find_key(key: str, data: list):
    found = list(filter(lambda x: key in x, data))
    if len(found) != 1:
        raise ValueError("Could not find key")
    value = str(found[0]).split("(")[1].rstrip(")")
    for unit in ("Wh", "W", "var", "varh"):
        if value.endswith(unit):
            value = int(value.rstrip("*" + unit))
            return {"value": value, "unit": unit}

    for unit in ("S",):
        if value.endswith(unit):
            value = value.rstrip(unit)
            return {
                "year": value[0:2],
                "month": value[2:4],
                "day": value[4:6],
                "hour": value[6:8],
                "minute": value[8:10],
                "second": value[10:12],
            }
    return value


decode_dict = {
    "DSMR Version": "1-3:0.2.8",
    "Zeitstempel": "0-0:1.0.0",

    "Wirkenergie Lieferung (Lieferung an Kunden) (+A)": "1-0:1.8.0",
    "Wirkenergie Lieferung (Lieferung an Kunden) (+A) Tarif 1": "1-0:1.8.1",
    "Wirkenergie Lieferung (Lieferung an Kunden) (+A) Tarif 2": "1-0:1.8.2",
    "Momentane Wirkleistung Bezug (+A)": "1-0:1.7.0",

    "Blindenergie Lieferung (+R)": "1-0:3.8.0",
    "Blindenergie Lieferung (+R) Tarif 1": "1-0:3.8.1",
    "Blindenergie Lieferung (+R) Tarif 2": "1-0:3.8.2",
    "Momentane Blindleistung Bezug (+R)": "1-0:3.7.0",

    "Wirkenergie Bezug (Lieferung an EV) (-A)": "1-0:2.8.0",
    "Wirkenergie Bezug (Lieferung an EV) (-A) Tarif 1": "1-0:2.8.1",
    "Wirkenergie Bezug (Lieferung an EV) (-A) Tarif 2": "1-0:2.8.2",
    "Momentane Wirkleistung Lieferung (-A)": "1-0:2.7.0",

    "Blindenergie Bezug (-R)": "1-0:4.8.0",
    "Blindenergie Bezug (-R) Tarif 1": "1-0:4.8.1",
    "Blindenergie Bezug (-R) Tarif 2": "1-0:4.8.2",
    "Momentane Blindleistung Lieferung (-R)": "1-0:4.7.0",
}


def convert_to_dict(data: str):
    data = data.splitlines()
    res = dict()
    for key, item in decode_dict.items():
        ss = __find_key(item, data)
        res[item] = {key: ss}
    return res


def decrypt_frame(global_unicast_enc_key: str, global_authentication_key: str, data: bytes):
    frame_len = len(data)
    if frame_len < 18:
        raise ValueError("Frame length to short")

    DLMS_TAG_GENERAL_GLOBAL_CIPHER = 0xDB
    if data[0] != DLMS_TAG_GENERAL_GLOBAL_CIPHER:
        raise ValueError("Wrong DLMS tag")

    system_titel_length = data[1]
    offset = system_titel_length + 2

    if offset < 10:
        raise ValueError("Frame length to short (offset)")

    system_titel = data[2:offset].hex()  # The next x bytes are the SYSTEM TITLE. The first 3 are the identifier and the remaining the serial number (?)

    length_of_length_bytes = data[offset] # https://github.com/pwitab/dlms-cosem/blob/739f81a58e5f07663a512d4a128851333a0ed5e6/dlms_cosem/a_xdr.py#L33
    offset += 1
    if length_of_length_bytes & 0b10000000:
        length_of_length_bytes = length_of_length_bytes & 0b01111111
        encrypted_length_inc_header = int.from_bytes(data[offset:offset + length_of_length_bytes], "big", signed=False)

        if encrypted_length_inc_header + system_titel_length + 3 + length_of_length_bytes != frame_len:  # 3 TAG + system_titel_length byte + length byte
            raise ValueError("Frame length to short (encrypted)")

        offset = offset + length_of_length_bytes

    AUTHENTICATED_AND_ENCRYPTED = 0x30  # 0x30=AUTH+ENC
    encryption_type = data[offset]
    if encryption_type != AUTHENTICATED_AND_ENCRYPTED:
        raise ValueError("Wrong encryption type")

    TAG_LENGTH = 12
    frame_counter = data[offset + 1:offset + 5].hex()  # The frame counter has 4 bytes and changes on each transaction
    frame = data[offset + 5:-TAG_LENGTH]  # Rest of the frame is encrypted
    tag = data[-TAG_LENGTH:]  # This is the auth tag
    init_vector = unhexlify(system_titel + frame_counter)

    try:
        decrypt = Cipher(
            algorithms.AES(unhexlify(global_unicast_enc_key)), modes.GCM(init_vector, tag, min_tag_length=12)
        ).decryptor()

        associated_data = AUTHENTICATED_AND_ENCRYPTED.to_bytes(1, "big", signed=False) + unhexlify(
            global_authentication_key)
        decrypt.authenticate_additional_data(associated_data)  # This is the GCM procedure for verifying the data

        return decrypt.update(frame) + decrypt.finalize()
    except InvalidTag:
        raise ValueError("Unable to decrypt ciphertext. Keys are wrong or the frame is corrupted.")


def check_and_encode_frame(data: bytes):
    if len(data) < 7:
        raise ValueError("Data length invalid")

    encoded_data = data[:-2].decode("ascii")  # Data is plain ASCII

    if not encoded_data.startswith("/"):
        raise ValueError("Start of decrypted frame invalid")

    if not encoded_data[-5] == "!":
        raise ValueError("End of decrypted frame invalid")

    crc_in_frame = encoded_data[-4:]
    crc = Crc16Cms.calchex(data[0:-6], byteorder="big")
    if str(crc).upper() != crc_in_frame.upper():
        raise ValueError("CRC invalid")

    if data[-2:] != b"\r\n":
        raise ValueError("End of frame invalid")

    return encoded_data
