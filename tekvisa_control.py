from enum import IntEnum
import logging
import time

from vxi11 import vxi11


class SesrBit(IntEnum):
    PON = 0x10000000, # Power On
    CME = 0x00100000, # Command Error
    EXE = 0x00010000, # Execution Error
    DDE = 0x00001000, # Device-Specific Error
    QYE = 0x00000100, # Query Error
    OPC = 0x00000001, # Operation Complete


def send_cmd(a_instr: vxi11.Device, a_cmd: str):
    try:
        a_instr.write(a_cmd)
        res = True
    except vxi11.Vxi11Exception:
        logging.error(f"Не удалось записать команду {a_cmd}")
        res = False
    return res


def read_answer(a_instr: vxi11.Device):
    try:
        res = a_instr.read()
    except vxi11.Vxi11Exception:
        logging.error(f"Не удалось прочитать данные")
        res = ""
    return res


def is_operation_completed(a_instr):
    a_instr.write("*ESR?")
    esr = int(a_instr.read())
    return esr & SesrBit.OPC


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
