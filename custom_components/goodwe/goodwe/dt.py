from typing import Tuple

from .inverter import Inverter
from .inverter import SensorKind as Kind
from .protocol import ProtocolCommand, ModbusReadCommand, ModbusWriteCommand
from .sensor import *


class DT(Inverter):
    """Class representing inverter of DT, D-NS and XS families"""

    _READ_DEVICE_VERSION_INFO: ProtocolCommand = ModbusReadCommand(0x7531, 0x0028)
    _READ_DEVICE_RUNNING_DATA: ProtocolCommand = ModbusReadCommand(0x7594, 0x0049)

    __sensors: Tuple[Sensor, ...] = (
        Timestamp("timestamp", 0, "Timestamp"),
        Voltage("vpv1", 6, "PV1 Voltage", Kind.PV),
        Current("ipv1", 8, "PV1 Current", Kind.PV),
        Calculated("ppv1", 0,
                   lambda data, _: round(read_voltage(data, 6) * read_current(data, 8)),
                   "PV1 Power", "W", Kind.PV),
        Voltage("vpv2", 10, "PV2 Voltage", Kind.PV),
        Current("ipv2", 12, "PV2 Current", Kind.PV),
        Calculated("ppv2", 0,
                   lambda data, _: round(read_voltage(data, 10) * read_current(data, 12)),
                   "PV2 Power", "W", Kind.PV),
        Integer("xx14", 14, "Unknown sensor@14"),
        Integer("xx16", 16, "Unknown sensor@16"),
        Integer("xx18", 18, "Unknown sensor@18"),
        Integer("xx20", 20, "Unknown sensor@20"),
        Integer("xx22", 22, "Unknown sensor@22"),
        Integer("xx24", 24, "Unknown sensor@24"),
        Integer("xx26", 26, "Unknown sensor@26"),
        Integer("xx28", 28, "Unknown sensor@28"),
        Voltage("vline1", 30, "On-grid L1-L2 Voltage", Kind.AC),
        Voltage("vline2", 32, "On-grid L2-L3 Voltage", Kind.AC),
        Voltage("vline3", 34, "On-grid L3-L1 Voltage", Kind.AC),
        Voltage("vgrid1", 36, "On-grid L1 Voltage", Kind.AC),
        Voltage("vgrid2", 38, "On-grid L2 Voltage", Kind.AC),
        Voltage("vgrid3", 40, "On-grid L3 Voltage", Kind.AC),
        Current("igrid1", 42, "On-grid L1 Current", Kind.AC),
        Current("igrid2", 44, "On-grid L2 Current", Kind.AC),
        Current("igrid3", 46, "On-grid L3 Current", Kind.AC),
        Frequency("fgrid1", 48, "On-grid L1 Frequency", Kind.AC),
        Frequency("fgrid2", 50, "On-grid L2 Frequency", Kind.AC),
        Frequency("fgrid3", 52, "On-grid L3 Frequency", Kind.AC),
        Calculated("pgrid1", 0,
                   lambda data, _: round(read_voltage(data, 36) * read_current(data, 42)),
                   "On-grid L1 Power", "W", Kind.AC),
        Calculated("pgrid2", 0,
                   lambda data, _: round(read_voltage(data, 38) * read_current(data, 44)),
                   "On-grid L2 Power", "W", Kind.AC),
        Calculated("pgrid3", 0,
                   lambda data, _: round(read_voltage(data, 40) * read_current(data, 46)),
                   "On-grid L3 Power", "W", Kind.AC),
        Integer("xx54", 54, "Unknown sensor@54"),
        Power("ppv", 56, "PV Power", Kind.PV),
        Integer("work_mode", 58, "Work Mode code"),
        Enum2("work_mode_label", 58, WORK_MODES, "Work Mode"),
        Integer("xx60", 60, "Unknown sensor@60"),
        Integer("xx62", 62, "Unknown sensor@62"),
        Integer("xx64", 64, "Unknown sensor@64"),
        Integer("xx66", 66, "Unknown sensor@66"),
        Integer("xx68", 68, "Unknown sensor@68"),
        Integer("xx70", 70, "Unknown sensor@70"),
        Integer("xx72", 72, "Unknown sensor@72"),
        Integer("xx74", 74, "Unknown sensor@74"),
        Integer("xx76", 76, "Unknown sensor@76"),
        Integer("xx78", 78, "Unknown sensor@78"),
        Integer("xx80", 80, "Unknown sensor@80"),
        Temp("temperature", 82, "Inverter Temperature", Kind.AC),
        Integer("xx84", 84, "Unknown sensor@84"),
        Integer("xx86", 86, "Unknown sensor@86"),
        Energy("e_day", 88, "Today's PV Generation", Kind.PV),
        Integer("xx90", 90, "Unknown sensor@90"),
        Energy("e_total", 92, "Total PV Generation", Kind.PV),
        Integer("xx94", 94, "Unknown sensor@94"),
        Integer("h_total", 96, "Hours Total", "h", Kind.PV),
        Integer("safety_country", 98, "Safety Country code", "", Kind.AC),
        Enum2("safety_country_label", 98, SAFETY_COUNTRIES_ET, "Safety Country", "", Kind.AC),
        Integer("xx100", 100, "Unknown sensor@100"),
        Integer("xx102", 102, "Unknown sensor@102"),
        Integer("xx104", 104, "Unknown sensor@104"),
        Integer("xx106", 106, "Unknown sensor@106"),
        Integer("xx108", 108, "Unknown sensor@108"),
        Integer("xx110", 110, "Unknown sensor@110"),
        Integer("xx112", 112, "Unknown sensor@112"),
        Integer("xx114", 114, "Unknown sensor@114"),
        Integer("xx116", 116, "Unknown sensor@116"),
        Integer("xx118", 118, "Unknown sensor@118"),
        Integer("xx120", 120, "Unknown sensor@120"),
        Integer("xx122", 122, "Unknown sensor@122"),
        Integer("funbit", 124, "FunBit", "", Kind.PV),
        Voltage("vbus", 126, "Bus Voltage", Kind.PV),
        Voltage("vnbus", 128, "NBus Voltage", Kind.PV),
        Integer("xx130", 130, "Unknown sensor@130"),
        Integer("xx132", 132, "Unknown sensor@132"),
        Integer("xx134", 134, "Unknown sensor@134"),
        Integer("xx136", 136, "Unknown sensor@136"),
        Integer("xx138", 138, "Unknown sensor@138"),
        Integer("xx140", 140, "Unknown sensor@140"),
        Integer("xx142", 142, "Unknown sensor@142"),
        Integer("xx144", 144, "Unknown sensor@144"),
    )

    async def read_device_info(self):
        response = await self._read_from_socket(self._READ_DEVICE_VERSION_INFO)
        response = response[5:-2]
        self.model_name = response[22:32].decode("ascii").rstrip()
        self.serial_number = response[6:22].decode("ascii")
        self.software_version = "{}.{}.{:02x}".format(
            int.from_bytes(response[66:68], byteorder='big'),
            int.from_bytes(response[68:70], byteorder='big'),
            int.from_bytes(response[70:72], byteorder='big'),
        )

    async def read_runtime_data(self, include_unknown_sensors: bool = False) -> Dict[str, Any]:
        raw_data = await self._read_from_socket(self._READ_DEVICE_RUNNING_DATA)
        data = self._map_response(raw_data[5:-2], self.__sensors, include_unknown_sensors)
        return data

    async def set_ongrid_battery_dod(self, dod: int):
        pass

    async def set_work_mode(self, work_mode: int):
        if work_mode == 0:
            await self._read_from_socket(ModbusWriteCommand(0x9d8b, 0))
        elif work_mode == 3:
            await self._read_from_socket(ModbusWriteCommand(0x9d8a, 0))

    @classmethod
    def sensors(cls) -> Tuple[Sensor, ...]:
        return cls.__sensors