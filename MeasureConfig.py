from typing import Dict, List, Optional

from irspy.metrology import Pchip


class MeasureConfig:
    def __init__(self, a_cmd_list=None, a_device_responses=None, a_normalizing_coef=0.,
                 a_apply_on_limit=False, a_limit=0, a_enable=False):
        self._cmd_list = [] if a_cmd_list is None else a_cmd_list
        self._device_responses: Dict[str, List[List[float]]] = {} if a_device_responses is None else a_device_responses
        self._normalizing_coef = a_normalizing_coef
        self._apply_on_limit = a_apply_on_limit
        self._limit = a_limit
        self._enable = a_enable

        self.__pchip_splines: List[Optional[None, Pchip]] = []
        self.__calculate_splines()

    def cmd_list(self):
        return self._cmd_list

    def set_cmd_list(self, a_cmd_list: list):
        self._cmd_list = a_cmd_list

    def get_device_responses(self):
        return self._device_responses

    def set_device_responses(self, a_device_responses):
        self._device_responses = a_device_responses
        self.__calculate_splines()

    def __calculate_splines(self):
        self.__pchip_splines = []
        for dr_name, dr_table in self._device_responses.items():
            spline = Pchip()
            spline.set_points([p[0] for p in dr_table], [p[1] for p in dr_table])
            self.__pchip_splines.append(spline)

    def total_device_response(self, a_frequency_mhz: float):
        """
        Возвращает суммарный отклик всех устройств на частоте a_frequency
        :param a_frequency_mhz: Частота, в МГц !!
        """
        total_response = 0.
        for spline in self.__pchip_splines:
            total_response += spline.interpolate(a_frequency_mhz)
        return total_response

    def set_normalize_coef(self, a_value):
        self._normalizing_coef = a_value

    def normalize_coef(self):
        return self._normalizing_coef

    def set_apply_on_limit(self, a_enable):
        self._apply_on_limit = a_enable

    def apply_on_limit(self):
        return self._apply_on_limit

    def set_limit(self, a_value):
        self._limit = a_value

    def limit(self):
        return self._limit

    def is_enabled(self):
        return self._enable

    def enable(self, a_enable: bool):
        self._enable = a_enable

    def to_dict(self):
        return {
            "cmd_list": self._cmd_list,
            "device_responses": self._device_responses,
            "normalizing_coef": self._normalizing_coef,
            "apply_on_limit": self._apply_on_limit,
            "limit": self._limit,
            "enable": self._enable,
        }

    @classmethod
    def from_dict(cls, a_dict: dict):
        cmd_list = a_dict["cmd_list"]
        device_responses = a_dict["device_responses"]
        normalizing_coef = a_dict["normalizing_coef"]
        try:
            apply_on_limit = a_dict["apply_on_limit"]
            limit = a_dict["limit"]
        except KeyError:
            apply_on_limit = False
            limit = 0

        enable = a_dict["enable"]
        return cls(cmd_list, device_responses, normalizing_coef, apply_on_limit, limit, enable)
