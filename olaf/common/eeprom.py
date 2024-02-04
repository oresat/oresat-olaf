"""Quick class to access hardware metadata on the am335x's EEPROM."""

import os


class Eeprom:
    """Get all the hardware metadata from EEPROM."""

    BOARD_NAMES = {
        "A335PBGL": "pocketbeagle",
        "A335BNLT": "boneblack",
        "A335OSC3": "c3",
        "A335OSST": "star-tracker",
        "A335OGPS": "gps",
        "A335ODWF": "dxwifi",
        "A335OCFC": "cfc",
    }

    def __init__(self):
        """
        Raises
        ------
        FileNotFound:
            EEPROM file was not found.
        PermissionError:
            Must be ran as root.
        """

        i2c_path = "/sys/bus/i2c/devices/"
        for file in os.listdir(i2c_path):
            eeprom_path = f"/sys/bus/i2c/devices/{file}/eeprom"
            if not os.path.exists(eeprom_path):
                eeprom_path = ""
            else:
                break  # found
        if eeprom_path == "":
            raise FileNotFoundError("eeprom file not found")

        with open(eeprom_path, "rb") as f:
            self.raw = f.read(28)

        self.header = self.raw[0:4]

        raw = bytes([0] * 4) + self.raw[4:]
        data = raw.decode()
        self.board_name = data[4:12]
        self.nice_name = self.BOARD_NAMES.get(self.board_name, "unknown")

        self.version = data[12:16]

        self.serial_number = data[16:28]
        self.week = data[16:18]
        self.year = data[18:20]
        self.serial_id = data[20:24]
        self.id = data[24:28]

        # non oresat card defaults
        self.is_oresat_card = False
        self.major = 0
        self.minor = 0

        if self.nice_name == "pocketbeagle":
            self.device_tree = "am335x-pocketbeagle.dtb"
        elif self.nice_name == "boneblack":
            self.device_tree = "am335x-boneblack.dtb"
        elif self.nice_name != "unknown":  # aka an oresat card
            self.is_oresat_card = True
            self.device_tree = f"{self.nice_name}-{self.version}.dtb"
            self.major = int(data[12:14])
            self.minor = int(data[14:16])
        else:
            self.device_tree = "unknown"
