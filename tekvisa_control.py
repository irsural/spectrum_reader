from enum import IntEnum
import logging
import time

from vxi11 import vxi11


# The Standard Event Status Register
class SESR(IntEnum):
    PON = 0x10000000, # Power On
    CME = 0x00100000, # Command Error
    EXE = 0x00010000, # Execution Error
    DDE = 0x00001000, # Device-Specific Error
    QYE = 0x00000100, # Query Error
    OPC = 0x00000001, # Operation Complete


# The Status Byte Register
class SBR(IntEnum):
    OSS = 0x10000000, # Operation Summary Status
    MSS = 0x01000000, # Master Status Summary
    ESB = 0x00100000, # Event Status Bit
    MAV = 0x00010000, # Message Available Bit
    QSS = 0x00001000, # Questionable Summary Status
    EAV = 0x00000100, # Event Quantity Available


class CmdCase(IntEnum):
    UPPER = 0,
    LOWER = 1


def get_commands_three(a_cmd_case: CmdCase):
    commands = {}
    description_node_name = "desc"
    cmd_file = "upper_case_commands.txt" if a_cmd_case == CmdCase.UPPER else "lower_case_commands.txt"
    with open(cmd_file, 'r') as file:
        for line in file:
            cmd, description = line.split(" ", 1)

            cmd_words = cmd.split(":")
            if cmd_words[0] == "":
                del cmd_words[0]
                cmd_words[0] = f":{cmd_words[0]}"
            cmd_words.append(description_node_name)

            current_node = commands
            for word in cmd_words:
                if word not in current_node:
                    if word != description_node_name:
                        current_node[word] = {}
                    else:
                        current_node[word] = description
                current_node = current_node[word]
    return commands


def get_cmd_description(a_cmd: str, a_cmd_tree: dict) -> str:
    description = ""
    if a_cmd:
        cmd_path = a_cmd.split(":")
        if cmd_path[0] == "":
            # Происходит, когда a_cmd начинается с ':'
            del cmd_path[0]

        if not cmd_path[0].startswith("*"):
            cmd_path[0] = f":{cmd_path[0]}"

        current_node = a_cmd_tree
        try:
            for cmd in cmd_path:
                current_node = current_node[cmd]
            description = current_node["desc"]
        except KeyError:
            description = ""

    return description


def send_cmd(a_instr: vxi11.Device, a_cmd: str) -> bool:
    try:
        a_instr.write(a_cmd)
        res = True
    except (vxi11.Vxi11Exception, TimeoutError):
        logging.error(f"Не удалось записать команду {a_cmd}")
        res = False
    return res


def read_answer(a_instr: vxi11.Device, a_encoding='utf-8') -> str:
    try:
        res = a_instr.read(encoding=a_encoding)
    except vxi11.Vxi11Exception:
        logging.error(f"Не удалось прочитать данные")
        res = ""
    return res


def read_raw_answer(a_instr: vxi11.Device) -> bytes:
    try:
        res = a_instr.read_raw()
    except vxi11.Vxi11Exception:
        logging.error(f"Не удалось прочитать данные")
        res = bytes()
    return res


def is_operation_completed(a_instr):
    a_instr.write("*ESR?")
    esr = int(a_instr.read())
    return esr & SESR.OPC


def opc_sync(a_instr):
    a_instr.write("*OPC")

    while not is_operation_completed(a_instr):
        time.sleep(1)


def some_test(a_instr):
    a_instr.write("*CLS")
    a_instr.write("*ESE 1")
    a_instr.write("*SRE 32")
    opc_sync(a_instr)
    a_instr.write("INSTrument 'SANORMAL'")
    a_instr.write("*RST")
    opc_sync(a_instr)
    a_instr.write("CONFigure:SPECtrum:CHPower")
    a_instr.write("FREQuency:CENTer 1GHz")
    a_instr.write("FREQuency:SPAN 1MHz")
    opc_sync(a_instr)
    a_instr.write("*CAL?")
    res = a_instr.read()
    print(f"*CAL? result = {res}")
    opc_sync(a_instr)
    a_instr.write("CHPower:BANDwidth:INTegration 300kHz")
    a_instr.write("SPECtrum:AVERage ON")
    a_instr.write("SPECtrum:AVERage:COUNt 10")
    opc_sync(a_instr)
    a_instr.write("INITiate:CONTinuous OFF;*OPC")
    opc_sync(a_instr)
    time.sleep(10)
    a_instr.write("INITiate;*OPC")
    opc_sync(a_instr)
    time.sleep(10)
    a_instr.write("FETCh:SPECtrum:CHPower?")
    print("res", a_instr.read())


if __name__ == "__main__":
    instr = vxi11.Instrument("192.168.0.91")
    instr.timeout = 3
    instr.write("abort")
    print(instr.ask("*idn?"))
    # try:
    #     some_test(instr)
    # except vxi11.vxi11.Vxi11Exception:
    #     instr.write("SYST:ERR:ALL?")
    #     errors = instr.read()
    #     print(errors)
