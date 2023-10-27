import serial, time, math
import pandas as pd

COM_PORTWEIN = "COM7"
BAUDRATE = 9600 # Estimated
NOMINAL_POWER = 7000
FACTOR = 0.1 # Oli said divide the Power(W) by 10 :|
COLUMN_NAME = "power(W)"
ROUND_UP = False
ENDIAN = "big"

ich_bekomme_gerätenennleistung = bytearray([0x54, 0x01, 0x04, 0x00, 0x59]) # To get the nominal power

# Maybe try 0 for node
sollwert_für_P = bytearray([0xD2, 0x01, 0x34]) # To send power request

def get_dataset(file_location: str) -> pd.DataFrame:
    dataset = pd.read_csv(file_location, skiprows=[0])
    dataset[COLUMN_NAME] = dataset[COLUMN_NAME]*FACTOR
    return dataset

def calc_byte_power_percent(req_power: int) -> bytearray:
    val = (25600 * req_power) / NOMINAL_POWER
    if ROUND_UP:
        val = math.ceil(val)
    else:
        val = math.floor(val)
    byte_val = int.to_bytes(val, 2, ENDIAN)
    return bytearray(byte_val)

def calc_bytes_checksum(byte_arr: bytearray) -> bytearray:
    total_dec_val = 0
    for byte in byte_arr:
        # byte_val = int(byte, 8)
        total_dec_val+=byte
    return bytearray(int.to_bytes(total_dec_val, 2, byteorder=ENDIAN))

def generate_power_req_msg(power: float) -> bytearray:
    msg = sollwert_für_P.copy()
    msg += calc_byte_power_percent(power)
    msg += calc_bytes_checksum(msg)
    return msg


def start_endurance():
    ser = serial.Serial(COM_PORTWEIN, BAUDRATE)

    twenty_kw = get_dataset("testdata/20kW_endurance.csv")

    for power_val in twenty_kw[COLUMN_NAME]:
        msg = generate_power_req_msg(power_val)
        print(f"Sending power : {power_val} as {msg}")
        ser.write(msg)
        time.sleep(0.1)

def test_comms():
    # ser = serial.Serial(COM_PORTWEIN, BAUDRATE)
    power = 70 # (W)
    msg = generate_power_req_msg(power)
    print(f"Sending power : {power} as {msg}")


## Start from me

test_comms()

# start_endurance()


## TESTING
def test_calc_bytes_checksum():
    test_msg = bytearray([0x55, 0x01, 0x47])
    checksum = calc_bytes_checksum(test_msg)
    return (bytearray([0x00, 0x9D]) == checksum)

def test_calc_byte_power_percent():
    # NOMINAL_POWER = 640
    value = calc_byte_power_percent(500)
    return (20000 == int.from_bytes(value, "big"))

def test_generate_power_req_mesg():
    # NOMINAL_POWER = 7000
    return bytearray([0xD2, 0x01, 0x34, 0x4E, 0x20, 0x01, 0x75]) == generate_power_req_msg(5469)

print(test_calc_bytes_checksum() and test_generate_power_req_mesg())