import argparse
from configparser import ConfigParser
import os
import sys
import string
import subprocess
from pathlib import Path

PATH = os.path.dirname(os.path.abspath(__file__))

TOOL_DESCRIPTION = (
"""
Starts the application with the specified arguments for debug.
"""
)

EXCLUDE_QT_FILES = """opengl32sw,qt6location,qt6webchannel,
  qt6webenginequick,qt6webenginequickdelegatesqml,qt6websockets,\\
  qt6virtualkeyboard,qt6pdfquick,qt6pdf,qt6quicktimeline,qt6datavisualizationqml,\\
  qt6datavisualization,qt6charts,\\
  qt6chartsqml,qt6webenginecore,qt6quick3d,qt6quick3dassetimport,qt6quick3d,\\
  qt6quick3dassetutils,qt6quick3deffects,\\
  qt6quick3dhelpers,qt6quick3dparticleeffects,qt6quick3dparticles,qt6quick3druntimerender,\\
  qt6quick3d,qt6quick3dutils,\\
  qt6graphs,qt6test,qt6texttospeech,'qt63danimation,qt63dcore,qt63dextras,qt63dinput,\\
  qt63dlogic,\\
  qt63dquick,qt63dquickanimation,qt63dquickextras,qt63dquickinput,qt63dquickrender,\\
  qt63dquickscene2d,qt63drender,\\
  qt63dquickrender,qt6quickcontrols2fusion,qt6quickcontrols2fusionstyleimpl,\\
  qt6quickcontrols2imagine,\\
  qt6quickcontrols2imaginestyleimpl,qt6quickcontrols2universal,\\
  qt6quickcontrols2universalstyleimpl,\\
  qt6quickcontrols2windowsstyleimpl,qt6quicktest,qt6remoteobjects,qt6remoteobjectsqml,\\
  qt6scxml,\\
  qt6scxmlqml,qt6sensors,qt6sensorsquick,qt6spatialaudio,qt6sql,\\
  qt6statemachine,qt6statemachineqml"""
  
if not os.path.exists(".env"):
    api = input("Please enter the GitHub API key " +
                "(Keep empty if you want to send requests unregistered) -> ")
    with open(".env", "w") as env_file:
        env_file.write(f"DEV_API={api}\n")

if not os.path.exists("config.properties"):
    with open("config.properties", "w") as file:
        file.write(f"""\
[application]
appId=
appName=GoodbyeDPI_UI
company=Company
copyright=Copyright (c) 2025
domain=com.example.domain.appname
version=0.0.0
[build]
projectName=GoodbyeDPI_UI
hotLoad=OFF
excludeFiles={EXCLUDE_QT_FILES}
""")
    print("Please fill in the config.properties file.")
    input("Press any key to exit ...")
    exit(1)



def read_properties(file_path):
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(file_path)
    _properties = {}
    for section in config.sections():
        for _key, _value in config.items(section):
            _properties[_key] = _value
    return _properties

properties = read_properties("config.properties")

def __path_separator():
    if sys.platform.startswith("darwin"):
        return ":"
    return ";"

def environment():
    environ = os.environ.copy()
    current = os.environ.get('PYTHONPATH', '')
    work_path = str(Path().absolute())
    if current != '':
        work_path = work_path + __path_separator() + current
    environ["PYTHONPATH"] = work_path
    return environ

def uac_check():
    print("UAC check")
    if sys.platform == 'win32':
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            exit(0)

def generate_python_file(output_file, mapping=None):
    target = dict(
        application_id=properties.get('appId', ''),
        application_name=properties.get('appName', ''),
        application_company=properties.get('company', ''),
        application_copyright=properties.get('copyright', ''),
        application_domain=properties.get('domain', ''),
        application_version=properties.get('domain', ''),
        build_name=properties.get('projectName', ''),
        build_hotreload=properties.get('hotLoad', ''),
        build_project_path=Path(PATH, "src")
    )
    if mapping is None:
        mapping = dict()
    for key, value in target.items():
        if key in mapping:
            target[key] = mapping[key]
    template = string.Template("""\
application_id = "${application_id}"
application_name = "${application_name}"
application_company = "${application_company}"
application_copyright = "${application_copyright}"
application_domain = "${application_domain}"
application_version = "${application_version}"
build_name = "${build_name}"
build_hotreload = "${build_hotreload}"
build_project_path = "${build_project_path}"
""")
    rendered_content = template.substitute(target)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(rendered_content)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=TOOL_DESCRIPTION)
    parser.add_argument("-f", "--fast", action="store_true", 
                        help="Run fast start application (disable update resources)")
    parser.add_argument("-r", "--reload", action="store_true", 
                        help="Enable hot reload for qml files")
    parser.add_argument("-q", "--enable-manual-input", action="store_true", 
                        help="Enable manual input of arguments")
    parser.add_argument("-u", "--skip-uac-check", action="store_true", 
                        help="Skip UAC check (not recomended)")
    parser.add_argument("-d", "--disable-debug", action="store_true", 
                        help="Disable debug mode for application")
    args = parser.parse_args()
    
    _args = [' ']
    
    if not args.skip_uac_check:
        uac_check()
    
    if args.enable_manual_input:
        _args = input("Put here args for check (e.g. --autorun) ->").split(' ')
        
    if not args.fast:
        subprocess.run([sys.executable, Path('update-resource.py')])
        
    if not args.disable_debug:
        _args.append('--debug')
    
    mapping = dict()
    if args.reload:
        mapping["build_hotreload"] = 'ON'
    
    generate_python_file(Path(PATH, 'src', 'GlobalConfig.py'), mapping)
    subprocess.run([sys.executable, Path(PATH, 'src', 'main.py'), *_args], env=environment(), cwd=PATH)
