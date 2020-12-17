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


def get_commands_three():
    commands = {}
    description_node_name = "desc"
    with open("upper_case_commands.txt", 'r') as file:
        for line in file:
            cmd, description = line.split(" ", 1)
            cmd: str

            cmd_words = cmd.split(":")
            if cmd_words[0] == "":
                cmd_words[0] = ":"
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


def send_cmd(a_instr: vxi11.Device, a_cmd: str) -> bool:
    try:
        a_instr.write(a_cmd)
        res = True
    except vxi11.Vxi11Exception:
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


def are_data_in_queue(a_instr):
    if send_cmd(a_instr, "*STB?"):
        try:
            sbr = int(read_answer(a_instr))
            return sbr & SBR.MAV
        except ValueError:
            return False
    else:
        return False


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
