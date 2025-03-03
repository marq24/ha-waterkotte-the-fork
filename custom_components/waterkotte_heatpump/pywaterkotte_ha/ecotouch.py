""" ecotouch main module"""
import aiohttp
import re
import logging

from enum import Enum
from datetime import datetime

from typing import (
    Any,
    Sequence,
    Tuple,
    List,
    Collection
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha import TagData, InvalidValueException
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import TRANSLATIONS

_LOGGER: logging.Logger = logging.getLogger(__package__)


class InvalidResponseException(Exception):
    """A InvalidResponseException."""

    # pass


class StatusException(Exception):
    """A Status Exception."""

    # pass


class TooManyUsersException(StatusException):
    """A TooManyUsers Exception."""
    # pass


class EcotouchTag(TagData, Enum):  # pylint: disable=function-redefined
    """EcotouchTag Class"""

    HOLIDAY_ENABLED = TagData(["D420"], writeable=True)
    HOLIDAY_START_TIME = TagData(
        ["I1254", "I1253", "I1252", "I1250", "I1251"],
        writeable=True,
        decode_function=TagData._decode_datetime,
        encode_function=TagData._encode_datetime,
    )
    HOLIDAY_END_TIME = TagData(
        ["I1259", "I1258", "I1257", "I1255", "I1256"],
        writeable=True,
        decode_function=TagData._decode_datetime,
        encode_function=TagData._encode_datetime,
    )
    TEMPERATURE_OUTSIDE = TagData(["A1"], "°C")
    TEMPERATURE_OUTSIDE_1H = TagData(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = TagData(["A3"], "°C")
    TEMPERATURE_SOURCE_ENTRY = TagData(["A4"], "°C")
    TEMPERATURE_SOURCE_EXIT = TagData(["A5"], "°C")
    TEMPERATURE_EVAPORATION = TagData(["A6"], "°C")
    TEMPERATURE_SUCTION_LINE = TagData(["A7"], "°C")
    PRESSURE_EVAPORATION = TagData(["A8"], "bar")
    TEMPERATURE_RETURN_SETPOINT = TagData(["A10"], "°C")
    TEMPERATURE_RETURN = TagData(["A11"], "°C")
    TEMPERATURE_FLOW = TagData(["A12"], "°C")
    TEMPERATURE_CONDENSATION = TagData(["A13"], "°C")
    TEMPERATURE_BUBBLEPOINT = TagData(["A14"], "°C")
    PRESSURE_CONDENSATION = TagData(["A15"], "bar")
    TEMPERATURE_BUFFERTANK = TagData(["A16"], "°C")
    TEMPERATURE_ROOM = TagData(["A17"], "°C")
    TEMPERATURE_ROOM_1H = TagData(["A18"], "°C")
    # TODO - CHECK... [currently no Sensors based on these tags]
    TEMPERATURE_ROOM_TARGET = TagData(["A100"], "°C", writeable=True)
    ROOM_INFLUENCE = TagData(["A101"], "%", writeable=True)

    TEMPERATURE_SOLAR = TagData(["A21"], "°C")
    TEMPERATURE_SOLAR_EXIT = TagData(["A22"], "°C")
    POSITION_EXPANSION_VALVE = TagData(["A23"], "")
    SUCTION_GAS_OVERHEATING = TagData(["A24"], "")

    POWER_ELECTRIC = TagData(["A25"], "kW")
    POWER_HEATING = TagData(["A26"], "kW")
    POWER_COOLING = TagData(["A27"], "kW")
    COP_HEATING = TagData(["A28"], "")
    COP_COOLING = TagData(["A29"], "")

    # ENERGY-YEAR-BALANCE
    COP_HEATPUMP_YEAR = TagData(["A460"], "")  # HEATPUMP_COP
    COP_HEATPUMP_ACTUAL_YEAR_INFO = TagData(["I1261"], decode_function=TagData._decode_year)  # HEATPUMP_COP_YEAR
    COP_TOTAL_SYSTEM_YEAR = TagData(["A461"], "")
    COP_HEATING_YEAR = TagData(["A695"])
    COP_HOT_WATER_YEAR = TagData(["A697"])

    ENERGY_CONSUMPTION_TOTAL_YEAR = TagData(["A450", "A451"], "kWh")
    COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR = TagData(["A444", "A445"], "kWh")  # ANUAL_CONSUMPTION_COMPRESSOR
    SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR = TagData(["A446", "A447"], "kWh")  # ANUAL_CONSUMPTION_SOURCEPUMP
    ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR = TagData(["A448", "A449"], "kWh")  # ANUAL_CONSUMPTION_EXTERNALHEATER
    ENERGY_PRODUCTION_TOTAL_YEAR = TagData(["A458", "A459"], "kWh")
    HEATING_ENERGY_PRODUCTION_YEAR = TagData(["A452", "A453"], "kWh")  # ANUAL_CONSUMPTION_HEATING
    HOT_WATER_ENERGY_PRODUCTION_YEAR = TagData(["A454", "A455"], "kWh")  # ANUAL_CONSUMPTION_WATER
    POOL_ENERGY_PRODUCTION_YEAR = TagData(["A456", "A457"], "kWh")  # ANUAL_CONSUMPTION_POOL
    COOLING_ENERGY_YEAR = TagData(["A462", "A463"], "kWh")

    # The LAST12M values for ENERGY_CONSUMPTION_TOTAL (also the individual values for compressor, sourcepump & e-heater
    # will be calculated based on values for each month (and will be summarized in the FE))
    # The same applies to the ENERGY_PRODUCTION_TOTAL (with the individual values for heating, hot_water & pool)
    COP_TOTAL_SYSTEM_LAST12M = TagData(["A435"])
    COOLING_ENERGY_LAST12M = TagData(["A436"], "kWh")

    ENG_CONSUMPTION_COMPRESSOR01 = TagData(["A782"])
    ENG_CONSUMPTION_COMPRESSOR02 = TagData(["A783"])
    ENG_CONSUMPTION_COMPRESSOR03 = TagData(["A784"])
    ENG_CONSUMPTION_COMPRESSOR04 = TagData(["A785"])
    ENG_CONSUMPTION_COMPRESSOR05 = TagData(["A786"])
    ENG_CONSUMPTION_COMPRESSOR06 = TagData(["A787"])
    ENG_CONSUMPTION_COMPRESSOR07 = TagData(["A788"])
    ENG_CONSUMPTION_COMPRESSOR08 = TagData(["A789"])
    ENG_CONSUMPTION_COMPRESSOR09 = TagData(["A790"])
    ENG_CONSUMPTION_COMPRESSOR10 = TagData(["A791"])
    ENG_CONSUMPTION_COMPRESSOR11 = TagData(["A792"])
    ENG_CONSUMPTION_COMPRESSOR12 = TagData(["A793"])

    ENG_CONSUMPTION_SOURCEPUMP01 = TagData(["A794"])
    ENG_CONSUMPTION_SOURCEPUMP02 = TagData(["A795"])
    ENG_CONSUMPTION_SOURCEPUMP03 = TagData(["A796"])
    ENG_CONSUMPTION_SOURCEPUMP04 = TagData(["A797"])
    ENG_CONSUMPTION_SOURCEPUMP05 = TagData(["A798"])
    ENG_CONSUMPTION_SOURCEPUMP06 = TagData(["A799"])
    ENG_CONSUMPTION_SOURCEPUMP07 = TagData(["A800"])
    ENG_CONSUMPTION_SOURCEPUMP08 = TagData(["A802"])
    ENG_CONSUMPTION_SOURCEPUMP09 = TagData(["A804"])
    ENG_CONSUMPTION_SOURCEPUMP10 = TagData(["A805"])
    ENG_CONSUMPTION_SOURCEPUMP11 = TagData(["A806"])
    ENG_CONSUMPTION_SOURCEPUMP12 = TagData(["A807"])

    # Docs say it should start at 806 for external heater but there is an overlapp to source pump
    ENG_CONSUMPTION_EXTERNALHEATER01 = TagData(["A808"])
    ENG_CONSUMPTION_EXTERNALHEATER02 = TagData(["A809"])
    ENG_CONSUMPTION_EXTERNALHEATER03 = TagData(["A810"])
    ENG_CONSUMPTION_EXTERNALHEATER04 = TagData(["A811"])
    ENG_CONSUMPTION_EXTERNALHEATER05 = TagData(["A812"])
    ENG_CONSUMPTION_EXTERNALHEATER06 = TagData(["A813"])
    ENG_CONSUMPTION_EXTERNALHEATER07 = TagData(["A814"])
    ENG_CONSUMPTION_EXTERNALHEATER08 = TagData(["A815"])
    ENG_CONSUMPTION_EXTERNALHEATER09 = TagData(["A816"])
    ENG_CONSUMPTION_EXTERNALHEATER10 = TagData(["A817"])
    ENG_CONSUMPTION_EXTERNALHEATER11 = TagData(["A818"])
    ENG_CONSUMPTION_EXTERNALHEATER12 = TagData(["A819"])

    ENG_PRODUCTION_HEATING01 = TagData(["A830"])
    ENG_PRODUCTION_HEATING02 = TagData(["A831"])
    ENG_PRODUCTION_HEATING03 = TagData(["A832"])
    ENG_PRODUCTION_HEATING04 = TagData(["A833"])
    ENG_PRODUCTION_HEATING05 = TagData(["A834"])
    ENG_PRODUCTION_HEATING06 = TagData(["A835"])
    ENG_PRODUCTION_HEATING07 = TagData(["A836"])
    ENG_PRODUCTION_HEATING08 = TagData(["A837"])
    ENG_PRODUCTION_HEATING09 = TagData(["A838"])
    ENG_PRODUCTION_HEATING10 = TagData(["A839"])
    ENG_PRODUCTION_HEATING11 = TagData(["A840"])
    ENG_PRODUCTION_HEATING12 = TagData(["A841"])

    ENG_PRODUCTION_WARMWATER01 = TagData(["A842"])
    ENG_PRODUCTION_WARMWATER02 = TagData(["A843"])
    ENG_PRODUCTION_WARMWATER03 = TagData(["A844"])
    ENG_PRODUCTION_WARMWATER04 = TagData(["A845"])
    ENG_PRODUCTION_WARMWATER05 = TagData(["A846"])
    ENG_PRODUCTION_WARMWATER06 = TagData(["A847"])
    ENG_PRODUCTION_WARMWATER07 = TagData(["A848"])
    ENG_PRODUCTION_WARMWATER08 = TagData(["A849"])
    ENG_PRODUCTION_WARMWATER09 = TagData(["A850"])
    ENG_PRODUCTION_WARMWATER10 = TagData(["A851"])
    ENG_PRODUCTION_WARMWATER11 = TagData(["A852"])
    ENG_PRODUCTION_WARMWATER12 = TagData(["A853"])

    ENG_PRODUCTION_POOL01 = TagData(["A854"])
    ENG_PRODUCTION_POOL02 = TagData(["A855"])
    ENG_PRODUCTION_POOL03 = TagData(["A856"])
    ENG_PRODUCTION_POOL04 = TagData(["A857"])
    ENG_PRODUCTION_POOL05 = TagData(["A858"])
    ENG_PRODUCTION_POOL06 = TagData(["A859"])
    ENG_PRODUCTION_POOL07 = TagData(["A860"])
    ENG_PRODUCTION_POOL08 = TagData(["A861"])
    ENG_PRODUCTION_POOL09 = TagData(["A862"])
    ENG_PRODUCTION_POOL10 = TagData(["A863"])
    ENG_PRODUCTION_POOL11 = TagData(["A864"])
    ENG_PRODUCTION_POOL12 = TagData(["A865"])

    ENG_HEATPUMP_COP_MONTH01 = TagData(["A924"])
    ENG_HEATPUMP_COP_MONTH02 = TagData(["A925"])
    ENG_HEATPUMP_COP_MONTH03 = TagData(["A926"])
    ENG_HEATPUMP_COP_MONTH04 = TagData(["A927"])
    ENG_HEATPUMP_COP_MONTH05 = TagData(["A928"])
    ENG_HEATPUMP_COP_MONTH06 = TagData(["A929"])
    ENG_HEATPUMP_COP_MONTH07 = TagData(["A930"])
    ENG_HEATPUMP_COP_MONTH08 = TagData(["A930"])
    ENG_HEATPUMP_COP_MONTH09 = TagData(["A931"])
    ENG_HEATPUMP_COP_MONTH10 = TagData(["A932"])
    ENG_HEATPUMP_COP_MONTH11 = TagData(["A933"])
    ENG_HEATPUMP_COP_MONTH12 = TagData(["A934"])

    # Temperature stuff
    TEMPERATURE_HEATING = TagData(["A30"], "°C")
    TEMPERATURE_HEATING_DEMAND = TagData(["A31"], "°C")
    TEMPERATURE_HEATING_ADJUST = TagData(["I263"], "K", writeable=True)
    TEMPERATURE_HEATING_HYSTERESIS = TagData(["A61"], "K", writeable=True)
    TEMPERATURE_HEATING_PV_CHANGE = TagData(["A682"], "K", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_1H = TagData(["A90"], "°C")
    TEMPERATURE_HEATING_HC_LIMIT = TagData(["A93"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_TARGET = TagData(["A94"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_NORM = TagData(["A91"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_NORM = TagData(["A92"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_RESULT = TagData(["A96"], "°C")
    TEMPERATURE_HEATING_ANTIFREEZE = TagData(["A1231"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MAX = TagData(["A95"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MIN = TagData(["A104"], "°C", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MAX = TagData(["A504"], "%", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MIN = TagData(["A505"], "%", writeable=True)
    TEMPERATURE_HEATING_SGREADY_STATUS4 = TagData(["A967"], "°C", writeable=True)

    # TEMPERATURE_HEATING_BUFFERTANK_ROOM_SETPOINT = TagData(["A413"], "°C", writeable=True)

    TEMPERATURE_HEATING_MODE = TagData(["I265"], writeable=True, decode_function=TagData._decode_heat_mode,
                                       encode_function=TagData._encode_heat_mode)
    # this A32 value is not visible in the GUI - and IMHO (marq24) there should
    # be no way to set the heating temperature directly - use the values of the
    # 'TEMPERATURE_HEATING_HC' instead (HC = HeatCurve)
    TEMPERATURE_HEATING_SETPOINT = TagData(["A32"], "°C", writeable=True)
    # same as A32 ?!
    TEMPERATURE_HEATING_SETPOINT_FOR_SOLAR = TagData(["A1710"], "°C", writeable=True)

    TEMPERATURE_COOLING = TagData(["A33"], "°C")
    TEMPERATURE_COOLING_DEMAND = TagData(["A34"], "°C")
    TEMPERATURE_COOLING_SETPOINT = TagData(["A109"], "°C", writeable=True)
    TEMPERATURE_COOLING_OUTDOOR_LIMIT = TagData(["A108"], "°C", writeable=True)
    TEMPERATURE_COOLING_HYSTERESIS = TagData(["A107"], "K", writeable=True)
    TEMPERATURE_COOLING_PV_CHANGE = TagData(["A683"], "K", writeable=True)

    TEMPERATURE_WATER = TagData(["A19"], "°C")
    TEMPERATURE_WATER_DEMAND = TagData(["A37"], "°C")
    TEMPERATURE_WATER_SETPOINT = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_WATER_HYSTERESIS = TagData(["A139"], "K", writeable=True)
    TEMPERATURE_WATER_PV_CHANGE = TagData(["A684"], "K", writeable=True)
    TEMPERATURE_WATER_DISINFECTION = TagData(["A168"], "°C", writeable=True)
    SCHEDULE_WATER_DISINFECTION_START_TIME = TagData(["I505", "I506"],
                                                     writeable=True,
                                                     decode_function=TagData._decode_time_hhmm,
                                                     encode_function=TagData._encode_time_hhmm,
                                                     )
    # SCHEDULE_WATER_DISINFECTION_START_HOUR = TagData(["I505"], "", writeable=True)
    # SCHEDULE_WATER_DISINFECTION_START_MINUTE = TagData(["I506"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_DURATION = TagData(["I507"], "h", writeable=True)
    SCHEDULE_WATER_DISINFECTION_1MO = TagData(["D153"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_2TU = TagData(["D154"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_3WE = TagData(["D155"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_4TH = TagData(["D156"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_5FR = TagData(["D157"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_6SA = TagData(["D158"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_7SU = TagData(["D159"], "", writeable=True)

    TEMPERATURE_WATER_SETPOINT_FOR_SOLAR = TagData(["A169"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T hot water
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Warmwasser
    TEMPERATURE_WATER_CHANGEOVER_EXT_HOTWATER = TagData(["A1019"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T flow
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Vorlauf
    TEMPERATURE_WATER_CHANGEOVER_EXT_FLOW = TagData(["A1249"], "°C", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MAX = TagData(["A171"], "%", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MIN = TagData(["A172"], "%", writeable=True)

    TEMPERATURE_POOL = TagData(["A20"], "°C")
    TEMPERATURE_POOL_DEMAND = TagData(["A40"], "°C")
    TEMPERATURE_POOL_SETPOINT = TagData(["A41"], "°C", writeable=True)
    TEMPERATURE_POOL_HYSTERESIS = TagData(["A174"], "K", writeable=True)
    TEMPERATURE_POOL_PV_CHANGE = TagData(["A685"], "K", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_1H = TagData(["A746"], "°C")
    TEMPERATURE_POOL_HC_LIMIT = TagData(["A749"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_TARGET = TagData(["A750"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_NORM = TagData(["A747"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_NORM = TagData(["A748"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_RESULT = TagData(["A752"], "°C")

    TEMPERATURE_MIX1 = TagData(["A44"], "°C")  # TEMPERATURE_MIXING1_CURRENT
    TEMPERATURE_MIX1_DEMAND = TagData(["A45"], "°C")  # TEMPERATURE_MIXING1_SET
    TEMPERATURE_MIX1_ADJUST = TagData(["I776"], "K", writeable=True)  # ADAPT_MIXING1
    TEMPERATURE_MIX1_PV_CHANGE = TagData(["A1094"], "K", writeable=True)
    TEMPERATURE_MIX1_PERCENT = TagData(["A510"], "%")
    TEMPERATURE_MIX1_HC_LIMIT = TagData(["A276"], "°C", writeable=True)  # T_HEATING_LIMIT_MIXING1
    TEMPERATURE_MIX1_HC_TARGET = TagData(["A277"], "°C", writeable=True)  # T_HEATING_LIMIT_TARGET_MIXING1
    TEMPERATURE_MIX1_HC_OUTDOOR_NORM = TagData(["A274"], "°C", writeable=True)  # T_NORM_OUTDOOR_MIXING1
    TEMPERATURE_MIX1_HC_HEATING_NORM = TagData(["A275"], "°C", writeable=True)  # T_NORM_HEATING_CICLE_MIXING1
    TEMPERATURE_MIX1_HC_MAX = TagData(["A278"], "°C", writeable=True)  # MAX_TEMP_MIXING1

    TEMPERATURE_MIX2 = TagData(["A46"], "°C")  # TEMPERATURE_MIXING2_CURRENT
    TEMPERATURE_MIX2_DEMAND = TagData(["A47"], "°C")  # TEMPERATURE_MIXING2_SET
    TEMPERATURE_MIX2_ADJUST = TagData(["I896"], "K", writeable=True)  # ADAPT_MIXING2
    TEMPERATURE_MIX2_PV_CHANGE = TagData(["A1095"], "K", writeable=True)
    TEMPERATURE_MIX2_PERCENT = TagData(["A512"], "%")
    TEMPERATURE_MIX2_HC_LIMIT = TagData(["A322"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_TARGET = TagData(["A323"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_OUTDOOR_NORM = TagData(["A320"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_HEATING_NORM = TagData(["A321"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_MAX = TagData(["A324"], "°C", writeable=True)

    TEMPERATURE_MIX3 = TagData(["A48"], "°C")  # TEMPERATURE_MIXING3_CURRENT
    TEMPERATURE_MIX3_DEMAND = TagData(["A49"], "°C")  # TEMPERATURE_MIXING3_SET
    TEMPERATURE_MIX3_ADJUST = TagData(["I1017"], "K", writeable=True)  # ADAPT_MIXING3
    TEMPERATURE_MIX3_PV_CHANGE = TagData(["A1096"], "K", writeable=True)
    TEMPERATURE_MIX3_PERCENT = TagData(["A514"], "%")
    TEMPERATURE_MIX3_HC_LIMIT = TagData(["A368"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_TARGET = TagData(["A369"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_OUTDOOR_NORM = TagData(["A366"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_HEATING_NORM = TagData(["A367"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_MAX = TagData(["A370"], "°C", writeable=True)

    # no information found in <host>/easycon/js/dictionary.js
    # COMPRESSOR_POWER = TagData(["A50"], "?°C")
    PERCENT_HEAT_CIRC_PUMP = TagData(["A51"], "%")
    PERCENT_SOURCE_PUMP = TagData(["A52"], "%")
    # A58 is listed as 'Power compressor' in <host>/easycon/js/dictionary.js
    # even if this value will not be displayed in the Waterkotte GUI - looks
    # like that this is really the same as the other two values (A51 & A52)
    # just a percentage value (from 0.0 - 100.0)
    PERCENT_COMPRESSOR = TagData(["A58"], "%")

    # just found... Druckgastemperatur
    TEMPERATURE_DISCHARGE = TagData(["A1462"], "°C")

    # implement https://github.com/marq24/ha-waterkotte/issues/3
    PRESSURE_WATER = TagData(["A1669"], "bar")

    # I1264 -> Heizstab Leistung?! -> 6000

    # keep but not found in Waterkotte GUI
    TEMPERATURE_COLLECTOR = TagData(["A42"], "°C")  # aktuelle Temperatur Kollektor
    TEMPERATURE_FLOW2 = TagData(["A43"], "°C")  # aktuelle Temperatur Vorlauf

    VERSION_CONTROLLER = TagData(["I1", "I2"], writeable=False, decode_function=TagData._decode_ro_fw)
    # VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = TagData(["I3"], writeable=False, decode_function=TagData._decode_ro_bios)
    DATE_DAY = TagData(["I5"])
    DATE_MONTH = TagData(["I6"])
    DATE_YEAR = TagData(["I7"])
    TIME_HOUR = TagData(["I8"])
    TIME_MINUTE = TagData(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = TagData(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = TagData(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = TagData(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = TagData(["I20"])
    OPERATING_HOURS_SOLAR = TagData(["I22"])
    ENABLE_HEATING = TagData(["I30"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_COOLING = TagData(["I31"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_WARMWATER = TagData(["I32"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                               writeable=True)
    ENABLE_POOL = TagData(["I33"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                          writeable=True)
    ENABLE_EXTERNAL_HEATER = TagData(["I35"], decode_function=TagData._decode_state,
                                     encode_function=TagData._encode_state, writeable=True)
    ENABLE_MIXING1 = TagData(["I37"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_MIXING2 = TagData(["I38"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_MIXING3 = TagData(["I39"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_PV = TagData(["I41"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)

    # UNKNOWN OPERATION-ENABLE Switches!
    ENABLE_X1 = TagData(["I34"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)
    ENABLE_X2 = TagData(["I36"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)
    ENABLE_X4 = TagData(["I40"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)
    ENABLE_X5 = TagData(["I42"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)

    STATE_SOURCEPUMP = TagData(["I51"], bit=0)
    STATE_HEATINGPUMP = TagData(["I51"], bit=1)
    STATE_EVD = TagData(["I51"], bit=2)
    STATE_COMPRESSOR = TagData(["I51"], bit=3)
    STATE_COMPRESSOR2 = TagData(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = TagData(["I51"], bit=5)
    STATE_ALARM = TagData(["I51"], bit=6)
    STATE_COOLING = TagData(["I51"], bit=7)
    STATE_WATER = TagData(["I51"], bit=8)
    STATE_POOL = TagData(["I51"], bit=9)
    STATE_SOLAR = TagData(["I51"], bit=10)
    STATE_COOLING4WAY = TagData(["I51"], bit=11)

    # we do not have any valid information about the meaning after the bit=8...
    # https://github.com/flautze/home_assistant_waterkotte/issues/1#issuecomment-1916288553
    #ALARM_BITS = TagData(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], translate=True)
    ALARM_BITS = TagData(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8], translate=True)
    INTERRUPTION_BITS = TagData(["I53"], bits=[0, 1, 2, 3, 4, 5, 6], translate=True)

    STATE_SERVICE = TagData(["I135"])

    STATUS_HEATING = TagData(["I137"], decode_function=TagData._decode_ro_status)
    STATUS_COOLING = TagData(["I138"], decode_function=TagData._decode_ro_status)
    STATUS_WATER = TagData(["I139"], decode_function=TagData._decode_ro_status)
    STATUS_POOL = TagData(["I140"], decode_function=TagData._decode_ro_status)
    STATUS_SOLAR = TagData(["I141"], decode_function=TagData._decode_ro_status)
    # returned 2='disabled' (even if the pump is running) - could be, that this TAG has to be set to 1='on' in order
    # to allow manual enable/disable the pump??? So it's then better to rename this then operation_mode and move it to
    # the switch section (just like the 'ENABLE_*' tags)
    STATUS_HEATING_CIRCULATION_PUMP = TagData(["I1270"], decode_function=TagData._decode_ro_status,
                                              encode_function=TagData._encode_ro_status)
    MANUAL_SOURCEPUMP = TagData(["I1281"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_SOLAR_CIRCULATION_PUMP = TagData(["I1287"], decode_function=TagData._decode_ro_status,
                                            encode_function=TagData._encode_ro_status)
    MANUAL_SOLARPUMP1 = TagData(["I1287"])
    MANUAL_SOLARPUMP2 = TagData(["I1289"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_BUFFER_TANK_CIRCULATION_PUMP = TagData(["I1291"], decode_function=TagData._decode_ro_status,
                                                  encode_function=TagData._encode_ro_status)
    MANUAL_VALVE = TagData(["I1293"])
    MANUAL_POOLVALVE = TagData(["I1295"])
    MANUAL_COOLVALVE = TagData(["I1297"])
    MANUAL_4WAYVALVE = TagData(["I1299"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_COMPRESSOR = TagData(["I1307"], decode_function=TagData._decode_ro_status)
    MANUAL_MULTIEXT = TagData(["I1319"])

    INFO_SERIES = TagData(["I105"], decode_function=TagData._decode_ro_series)
    INFO_ID = TagData(["I110"], decode_function=TagData._decode_ro_id)
    INFO_SERIAL = TagData(["I114", "I115"], writeable=False, decode_function=TagData._decode_ro_sn)
    ADAPT_HEATING = TagData(["I263"], writeable=True)

    STATE_BLOCKING_TIME = TagData(["D71"])
    STATE_TEST_RUN = TagData(["D581"])

    # SERVICE_HEATING = TagData(["D251"])
    # SERVICE_COOLING = TagData(["D252"])
    # SERVICE_WATER = TagData(["D117"])
    # SERVICE_HEATING_D23 = TagData(["D23"])
    # SERVICE_HEATING_D24 = TagData(["D24"])
    # SERVICE_WATER_D118 = TagData(["D118"])
    # SERVICE_OPMODE = TagData(["I136"])
    # RAW_D430 = TagData(["D430"])  # animation
    # RAW_D28 = TagData(["D28"])  # ?QE
    # RAW_D879 = TagData(["D879"])  # ?RMH
    # MODE_HEATING_PUMP = TagData(["A522"])
    # MODE_HEATING = TagData(["A530"])
    # MODE_HEATING_EXTERNAL = TagData(["A528"])
    # MODE_COOLING = TagData(["A532"])
    # MODE_WATER = TagData(["A534"])
    # MODE_POOL = TagData(["A536"])
    # MODE_SOLAR = TagData(["A538"])

    # found on the "extended" Tab in the Waterkotte WebGui
    # (all values can be read/write) - no clue about the unit yet
    # reading the values always returned '0' -> so I guess they have
    # no use for us?!
    # ENERGY_THERMAL_WORK_1 = TagData("I1923")
    # ENERGY_THERMAL_WORK_2 = TagData("I1924")
    # ENERGY_COOLING = TagData("I1925")
    # ENERGY_HEATING = TagData("I1926")
    # ENERGY_HOT_WATER = TagData("I1927")
    # ENERGY_POOL_HEATER = TagData("I1928")
    # ENERGY_COMPRESSOR = TagData("I1929")
    # ENERGY_HEAT_SOURCE_PUMP = TagData("I1930")
    # ENERGY_EXTERNAL_HEATER = TagData("I1931")

    # D1273 "Heizungsumwäzpumpe ET 6900 Q" does not change it's value
    # HEATING_CIRCULATION_PUMP_D1273 = TagData(["D1273"], writeable=True)
    STATE_HEATING_CIRCULATION_PUMP_D425 = TagData(["D425"])
    STATE_BUFFERTANK_CIRCULATION_PUMP_D377 = TagData(["D377"])
    STATE_POOL_CIRCULATION_PUMP_D549 = TagData(["D549"])
    STATE_MIX1_CIRCULATION_PUMP_D248 = TagData(["D248"])
    STATE_MIX2_CIRCULATION_PUMP_D291 = TagData(["D291"])
    STATE_MIX3_CIRCULATION_PUMP_D334 = TagData(["D334"])
    # alternative MIX pump tags...
    STATE_MIX1_CIRCULATION_PUMP_D563 = TagData(["D563"])
    STATE_MIX2_CIRCULATION_PUMP_D564 = TagData(["D564"])
    STATE_MIX3_CIRCULATION_PUMP_D565 = TagData(["D565"])

    PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103 = TagData(["D1103"], writeable=True)
    PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104 = TagData(["D1104"], writeable=True)

    # lngA520 = ["Vollbetriebsstunden", "Operating hours", "Heures activit\xe9"],

    # assuming that I1752 will be set to "Spreizung"=0 the A479 is a DELTA Temperature
    # lngA479 = ΔT Wärmequelle - ["T Wärmequelle", "T heat source", "T captage"],
    SOURCE_PUMP_CAPTURE_TEMPERATURE_A479 = TagData(["A479"], writeable=True)

    SGREADY_SWITCH_D795 = TagData(["D795"], writeable=True)
    # lngD796 = ["SG1: EVU-Sperre", "SG1: Extern switch off", "SG1: Coupure externe"],
    SGREADY_SG1_EXTERN_OFF_SWITCH_D796 = TagData(["D796"], writeable=False)
    # lngD797 = ["SG2: Normalbetrieb", "SG2: Normal operation", "SG2: Fonction normal"],
    SGREADY_SG2_NORMAL_D797 = TagData(["D797"], writeable=False)
    # lngD798 = ["SG3: Sollwerterh.", "SG3: Setpoint change", "SG3: Augment. consigne"],
    SGREADY_SG3_SETPOINT_CHANGE_D798 = TagData(["D798"], writeable=False)
    # lngD799 = ["SG4: Zwangslauf", "SG4: Forced run", "SG4: Marche forc\xe9e"],
    SGREADY_SG4_FORCE_RUN_D799 = TagData(["D799"], writeable=False)

    def __hash__(self) -> int:
        return hash(self.name)


#
# Class to control Waterkotte Ecotouch heatpumps.
#
class EcotouchBridge:
    """Ecotouch Class"""

    auth_cookies = None

    def __init__(self, host, tagsPerRequest: int = 10, lang: str = "en"):
        self.hostname = host
        self.username = "waterkotte"
        self.password = "waterkotte"
        self.tagsPerRequest = min(tagsPerRequest, 75)
        self.lang_map = None

        if lang in TRANSLATIONS:
           self.lang_map = TRANSLATIONS[lang]
        else:
           self.lang_map = TRANSLATIONS["en"]

    # extracts statuscode from response
    def get_status_response(self, r):  # pylint: disable=invalid-name
        """get_status_response"""
        match = re.search(r"^#([A-Z_]+)", r, re.MULTILINE)
        if match is None:
            raise InvalidResponseException("Invalid reply. Status could not be parsed")
        return match.group(1)

    # performs a login. Has to be called before any other method.
    async def login(self, username="waterkotte", password="waterkotte"):
        """Login to Heat Pump"""
        _LOGGER.info(f"login to waterkotte host {self.hostname}")
        args = {"username": username, "password": password}
        self.username = username
        self.password = password
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"http://{self.hostname}/cgi/login", params=args)
            async with response:
                assert response.status == 200
                content = await response.text()

                tc = content.replace('\n', '<nl>')
                tc = tc.replace('\r', '<cr>')
                _LOGGER.info(f"LOGIN status:{response.status} response: {tc}")

                parsed_response = self.get_status_response(content)
                if parsed_response != "S_OK":
                    if parsed_response.startswith("E_TOO_MANY_USERS"):
                        raise TooManyUsersException("TOO_MANY_USERS")
                    else:
                        raise StatusException(f"Error while LOGIN: status: {parsed_response}")
                self.auth_cookies = response.cookies

    async def logout(self):
        """Logout function"""
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"http://{self.hostname}/cgi/logout")
            async with response:
                content = await response.text()
                # tc = content.replace("\n", "<nl>").replace("\r", "<cr>")
                _LOGGER.info(f"LOGOUT status:{response.status} content: {content}")
                self.auth_cookies = None

    async def read_value(self, tag: EcotouchTag):
        """Read a value from Tag"""
        res = await self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    async def read_values(self, tags: Sequence[EcotouchTag]):
        """Async read values"""
        # create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag.tags]))
        e_values, e_status = await self._read_tags(e_tags)

        result = {}
        if e_values is not None and len(e_values) > 0:
            for a_eco_tag in tags:
                try:
                    t_values = [e_values[a_tag] for a_tag in a_eco_tag.tags]
                    t_states = [e_status[a_tag] for a_tag in a_eco_tag.tags]
                    result[a_eco_tag] = {
                        "value": a_eco_tag.decode_function(a_eco_tag, t_values),
                        "status": t_states[0]
                    }

                    if a_eco_tag.translate and a_eco_tag.tags[0] in self.lang_map:
                        value_map = self.lang_map[a_eco_tag.tags[0]]
                        final_value = ""
                        temp_values = result[a_eco_tag]["value"]
                        for idx in range(len(temp_values)):
                            if temp_values[idx]:
                                final_value = final_value + ", " + str(value_map[idx])

                        # we need to trim the firsts initial added ', '
                        if len(final_value)>0:
                            final_value = final_value[2:]

                        result[a_eco_tag]["value"] = final_value

                except KeyError:
                    _LOGGER.warning(
                        f"Key Error while read_values. EcoTag: {a_eco_tag} vals: {t_values} states: {t_states}")
                except Exception as other_exc:
                    _LOGGER.error(
                        f"Exception {other_exc} while read_values. EcoTag: {a_eco_tag} vals: {t_values} states: {t_states}",
                        other_exc
                    )

        return result

    #
    # reads a list of ecotouch tags
    #
    # self, tags: Sequence[EcotouchTag], results={}, results_status={}
    async def _read_tags(self, tags: Sequence[EcotouchTag], results=None, results_status=None):
        """async read tags"""
        # _LOGGER.warning(tags)
        if results is None:
            results = {}
        if results_status is None:
            results_status = {}

        while len(tags) > self.tagsPerRequest:
            results, results_status = await self._read_tags(tags[:self.tagsPerRequest], results, results_status)
            tags = tags[self.tagsPerRequest:]

        args = {}
        args["n"] = len(tags)
        for i in range(len(tags)):
            args[f"t{(i + 1)}"] = tags[i]

        # also the readTags have a timestamp in each request...
        args["_"] = str(int(round(datetime.now().timestamp() * 1000)))

        _LOGGER.info(f"going to request {args['n']} tags in a single call from waterkotte@{self.hostname}")
        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:
            async with session.get(f"http://{self.hostname}/cgi/readTags", params=args) as resp:
                _LOGGER.debug(f"requested: {resp.url}")
                response = await resp.text()
                if response.startswith("#E_NEED_LOGIN"):
                    try:
                        await self.login(self.username, self.password)
                        return await self._read_tags(tags=tags, results=results, results_status=results_status)
                    except StatusException as status_exec:
                        _LOGGER.warning(f"StatusException (_read_tags) while trying to login: {status_exec}")
                        return None, None

                if response.startswith("#E_TOO_MANY_USERS"):
                    return None

                for tag in tags:
                    match = re.search(
                        rf"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                        response,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            rf"#{tag}\tE_INACTIVETAG",
                            response,
                            re.MULTILINE,
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        if match is None:
                            # raise Exception(tag + " tag not found in response")
                            _LOGGER.warning("Tag: %s not found in response!", tag)
                            results_status[tag] = "E_NOTFOUND"
                        else:
                            # if val_status == "E_INACTIVE":
                            results_status[tag] = "E_INACTIVE"

                        results[tag] = None
                    else:
                        # results_status[tag] = "S_OK"
                        results_status[tag] = match.group("status")
                        results[tag] = match.group("value")

        return results, results_status

    async def write_value(self, tag, value):
        """Write a value"""
        return await self.write_values([(tag, value)])

    async def write_values(self, kv_pairs: Collection[Tuple[EcotouchTag, Any]]):
        """Write values to Tag"""
        to_write = {}
        result = {}
        # we write only one EcotouchTag at the same time (but the EcotouchTag can consist of
        # multiple internal tag fields)
        for a_eco_tag, value in kv_pairs:  # pylint: disable=invalid-name
            if not a_eco_tag.writeable:
                raise InvalidValueException("tried to write to an readonly field")

            # converting the HA values to the final int or bools that the waterkotte understand
            a_eco_tag.encode_function(a_eco_tag, value, to_write)

            e_values, e_status = await self._write_tags(to_write.keys(), to_write.values())

            if e_values is not None and len(e_values) > 0:
                _LOGGER.info(
                    f"after _encode_tags of EcotouchTag {a_eco_tag} > raw-values: {e_values} states: {e_status}")

                all_ok = True
                for a_tag in e_status:
                    if e_status[a_tag] != "S_OK":
                        all_ok = False

                if all_ok:
                    str_vals = [e_values[a_tag] for a_tag in a_eco_tag.tags]
                    val = a_eco_tag.decode_function(a_eco_tag, str_vals)
                    if str(val) != str(value):
                        _LOGGER.error(
                            f"WRITE value does not match value that was READ: '{val}' (read) != '{value}' (write)")
                    else:
                        result[a_eco_tag] = {
                            "value": val,
                            # here we also take just the first status...
                            "status": e_status[a_eco_tag.tags[0]]
                        }
        return result

    #
    # writes <value> into the tag <tag>
    #
    async def _write_tags(self, tags: List[str], value: List[Any]):
        """write tag"""
        args = {}
        args["n"] = len(tags)
        args["returnValue"] = "true"
        args["rnd"] = str(int(round(datetime.now().timestamp() * 1000)))  # str(datetime.timestamp(datetime.now()))
        # for i in range(len(tags)):
        #    args[f"t{(i + 1)}"] = tags[i]
        # for i in range(len(tag.tags)):
        #     et_values[tag.tags[i]] = vals[i]
        for i, tag in enumerate(tags):
            args[f"t{i + 1}"] = tag
            args[f"v{i + 1}"] = list(value)[i]

        # args = {
        #     "n": 1,
        #     "returnValue": "true",
        #     "t1": tag,
        #     "v1": value,
        #     'rnd': str(datetime.timestamp(datetime.now()))
        # }
        # result = {}
        results = {}
        results_status = {}
        # _LOGGER.info(f"requesting '{args}' [tags: {tags}, values: {value}]")

        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:
            async with session.get(f"http://{self.hostname}/cgi/writeTags", params=args) as resp:
                response = await resp.text()  # pylint: disable=invalid-name
                if response.startswith("#E_NEED_LOGIN"):
                    try:
                        await self.login(self.username, self.password)
                        return await self._write_tags(tags=tags, value=value)
                    except StatusException as status_exec:
                        _LOGGER.warning(f"StatusException (_write_tags) while trying to login: {status_exec}")
                        return None
                if response.startswith("#E_TOO_MANY_USERS"):
                    return None

                ###
                for tag in tags:
                    match = re.search(
                        rf"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                        response,
                        re.MULTILINE
                    )
                    if match is None:
                        match = re.search(
                            rf"#{tag}\tE_INACTIVETAG",
                            response,
                            re.MULTILINE
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        if match is None:
                            # raise Exception(tag + " tag not found in response")
                            _LOGGER.warning("Tag: %s not found in response!", tag)
                            results_status[tag] = "E_NOTFOUND"
                        else:
                            # if val_status == "E_INACTIVE":
                            results_status[tag] = "E_INACTIVE"

                        results[tag] = None
                    else:
                        # results_status[tag] = "S_OK"
                        results_status[tag] = match.group("status")
                        results[tag] = match.group("value")

            return results, results_status
