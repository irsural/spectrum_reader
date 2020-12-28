import irspy.pyinstaller_build as py_build

from revisions import Revisions


if __name__ == "__main__":
    libs = [
        'C:\\Windows\\System32\\vcruntime140d.dll',
        'C:\\Windows\\System32\\ucrtbased.dll',
        'C:\\Users\\503\\Desktop\\Python projects\\SpectrumReader\\irspy\\clb\\pokrov_dll.dll',
        'C:\\Users\\503\\Desktop\\Python projects\\SpectrumReader\\irspy\\dlls\\mxsrclib_dll.dll',
    ]

    py_build.build_qt_app(a_main_filename="tekvisa_control.py",
                          a_app_name="SpectrumReader",
                          a_version=Revisions.SpectrumReader,
                          a_icon_filename="main_icon.ico",
                          a_noconsole=False,
                          a_one_file=True,
                          a_libs=libs)
