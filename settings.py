from irspy.qt.qt_settings_ini_parser import QtSettings


def get_ini_settings():
    return QtSettings("./settings.ini", [
        QtSettings.VariableInfo(a_name="tip_full_cmd", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT),
        QtSettings.VariableInfo(a_name="save_folder_path", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING),
        QtSettings.VariableInfo(a_name="device_ip", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING),
        QtSettings.VariableInfo(a_name="default_start_config_enabled", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT),
        QtSettings.VariableInfo(a_name="log_scale_enabled", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT),
        # QtSettings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_FLOAT,
        #                         a_default=[0.0001, 0.01, 0.1, 1, 10, 20, 100]),
        # QtSettings.VariableInfo(a_name="checkbox_states", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_INT),
        # QtSettings.VariableInfo(a_name="rough_step", a_section="PARAMETERS", a_type=QtSettings.ValueType.FLOAT, a_default=0.5),
        # QtSettings.VariableInfo(a_name="last_configuration_path", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING),
    ])
