from binascii import unhexlify

from Crypto.Cipher import AES
from crccheck.crc import Crc16Arc as Crc16Cms


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
                "hour": value[4:6],
                "minute": value[6:8],
                "second": value[8:10],
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


def decrypt_frame(global_unicast_enc_key: str, data: bytes):
    frame_len = len(data)
    if frame_len < 500:
        raise ValueError("Frame length to short")

    # First two bytes are a static header (?)
    system_titel = data[2:10].hex()  # The next 8 bytes are the SYSTEM TITLE. The first 3 are the identifier and the remaining the serial number (?)
    # There are four unknown bytes between the title and frame counter
    frame_counter = data[14:18].hex()  # The frame counter has 4 bytes and changes on each transaction
    frame = data[18:]  # Rest of the frame is encrypted
    init_vector = unhexlify(system_titel + frame_counter)
    try:
        cipher = AES.new(unhexlify(global_unicast_enc_key), AES.MODE_GCM, nonce=init_vector)
    except Exception as ex:
        raise RuntimeError("Decryption failed. Key invalid? " + str(ex))
    decrypted_data = cipher.decrypt(frame)
    return decrypted_data


def check_and_encode_frame(data: bytes):
    if len(data) < 481:
        raise ValueError("Data length invalid")

    encoded_data = data[:479].decode("ascii")  # Data is plain ASCII

    if not encoded_data.startswith("/"):
        raise ValueError("Start of decrypted frame invalid")

    if not encoded_data[-5] == "!":
        raise ValueError("End of decrypted frame invalid")

    crc_in_frame = encoded_data[-4:]
    crc = Crc16Cms.calchex(data[0:475], byteorder="big")
    if str(crc).upper() != crc_in_frame.upper():
        raise ValueError("CRC invalid")

    if data[479:481] != b"\r\n":
        raise ValueError("End of frame invalid")

    # print("Test " + str(len(data[481:]))) # Note: There are typically 12 unknown bytes attached at the end

    return encoded_data
