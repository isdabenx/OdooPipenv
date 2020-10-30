import sys
import os
import json


def get_file_parent_dir_path():
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    path_sep = os.path.sep
    components = current_dir_path.split(path_sep)
    return path_sep.join(components[:-1])


PARENT_DIR = get_file_parent_dir_path()
CUSTOM_ADDONS_PATH = PARENT_DIR + '/custom/addons/'
ADDONS_PATH = PARENT_DIR + '/enterprise/addons,' + \
    PARENT_DIR + '/odoo-server/addons'
SERVER_APP = PARENT_DIR + '/odoo-server/odoo-bin'
version = ''
mode = ''
update = False
shell = False
addons_list = ''
modul_name = ''
modul_dir = ''
log_level = 'info'
arguments = ['-i', '-u', '-debug', '-warn', '-error', '-critical']
error_syntax = 'Invalid Syntax: odoo_start.py [-i/-u/-uall] "modul_name"\nLog level is optional [-debug/-warn/-error/-crtical]\n'


def error(msg):
    global error_syntax
    valor = '\x1b[0;31m'
    err = '\x1b[0;33m'
    reset = '\x1b[0m'
    print(valor + error_syntax + reset + err + msg + reset)
    exit()


def pause():
    try:
        input('\nPRESS ENTER TO CONTINUE OR CONTROL+C TO ABORT')
    except KeyboardInterrupt:
        print('\nBye!')
        exit()


def start():
    getArgs()
    modul = getModul()
    global SERVER_APP
    global mode
    global log_level
    global update
    global version
    if update:
        command = f"{SERVER_APP} --addons-path {addons_list(modul)} -d {modul_dir} -u all --stop-after-init"
    elif shell:
        command = f"{SERVER_APP} shell --addons-path {addons_list(modul)} -d {modul} {checkMode()} {modul_dir} --log-level {log_level} --limit-time-real=0"
    else:
        command = f"{SERVER_APP} --addons-path {addons_list(modul)} -d {modul} {checkMode()} {modul_dir} --log-level {log_level} --limit-time-real=0"
    imprimir(SERVER_APP, log_level, modul, command)
    pause()
    change_version()
    os.system(f"pipenv run {command}")


def imprimir(server_app, log_level, modul, command):
    etiqueta = '\x1b[0;30;43m'
    valor = '\x1b[0;34m'
    valor2 = '\x1b[0;36m'
    valor3 = '\x1b[0;35m'
    reset = '\x1b[0m'
    fletxa = '\x1b[1;31m'
    global version
    print(
        f'{etiqueta}[ODOO VERSION]{reset}{fletxa} --> {reset}{valor2}{version}{reset}')
    global shell
    if shell:
        print(f'{etiqueta}[SHELL INTERACTIVE]{reset}')
    print(
        f'{etiqueta}[LOCAL COMMAND]{reset}{fletxa} --> {reset}{valor2}{command}{reset}')
    server_command = command.replace(PARENT_DIR, "/odoo")
    print(
        f'{etiqueta}[SERVER COMMAND]{reset}{fletxa} --> {reset}{valor3}{server_command}{reset}')
    global update
    if update:
        print(f'{etiqueta}[UPDATE ALL]{reset}')

    print(
        f'{etiqueta}[RUN APP]{reset}{fletxa} --> {reset}{valor}{server_app}{reset}')
    print(
        f'{etiqueta}[LOG-LEVEL]{reset}{fletxa} --> {reset}{valor}{log_level}{reset}')
    print(
        f'{etiqueta}[{"INSTALL" if mode == "-i" else "UPDATE"}]{reset}{fletxa} --> {reset}{valor}{modul}{reset}')
    print(f'{etiqueta}[MODULES LIST]{reset}{fletxa} --> {reset}', end='')
    for i in getModulList(modul):
        if i == getModulList(modul)[0]:
            print(valor + i + reset)
        else:
            print(19 * " " + valor + i + reset)


def getArgs():
    arguments = sys.argv[1::]
    if len(arguments) < 2:
        error('\nNeed "-i" or "-u" and addon name!')
    else:
        global modul_name
        for args in arguments:
            if not isArgument(args):
                if modul_name == '':
                    modul_name = args
            else:
                getArgument(args)


def getModul():
    global modul_name
    if modul_name == '':
        error('Need addon name')
    else:
        return modul_name


def getArgument(arg):
    global mode
    global log_level
    global update
    global shell
    if arg == '-i':
        mode = '-i'
    elif arg == '-u':
        mode = '-u'
    elif arg == '-debug':
        log_level = 'debug'
    elif arg == '-warn':
        log_level = 'warn'
    elif arg == '-error':
        log_level = 'error'
    elif arg == '-critical':
        log_level = 'critical'
    elif arg == '-uall':
        update = True
    elif arg == '-shell':
        shell = True
    else:
        error(f'Argument {arg} no exist!')


def checkMode():
    global mode
    if mode == '':
        error(f'Need argument "-i" or "-u"')
    else:
        return mode


def isArgument(arg):
    if arg[0] == '-':
        return True
    else:
        return False


def getModulList(addon=""):
    try:
        path = os.path.dirname(os.path.abspath(__file__)) + "/"
        file = open(path + "moduls.json", "r")
        result = file.read()
        result = json.loads(result.replace("'", '"'))
        file.close()

    except:
        print('ERROR to open file "moduls.json"')
        exit()

    if addon == "":
        return result
    else:
        global version
        global modul_dir
        modul_dir = result[addon]['directory']
        if len(str(version)) == 0:
            version = result[addon]['odoo']
        return result[addon]['moduls']


def addons_list(addon):
    addons_list = ''
    global arguments

    if addon in getModulList():
        addons_list = getAddonsFromDict(addon)
    elif addon not in arguments:
        error(
            f'Addon names isn\'t in addons list\n\nList of modules:\n{listOfDevelop()}')

    global ADDONS_PATH
    return addons_list + ADDONS_PATH


def listOfDevelop():
    res = ''
    for key, values in getModulList().items():
        res += f"--[{values['odoo']}]--> {key}\n"
    return res


def getAddonsFromDict(addon):
    addons_list = ''
    global modul_dir
    if check_path(addon + '/' + modul_dir):
        addons_list += path_resolv(addon) + ','
    else:
        error(f"ERROR: directorio del addon no encontrado: {addon}")

    for modul in getModulList(addon):
        if check_path(addon + '/' + modul):
            addons_list += path_resolv(addon + '/' + modul) + ','
        else:
            error(
                f"ERROR: Modulo {modul} en la lista de {addon} no encontrado")
    return addons_list


def check_path(path):
    path = path_resolv(path)
    return os.path.exists(path) and os.path.isdir(path)


def path_resolv(path):
    return CUSTOM_ADDONS_PATH + path


def change_version():
    global version
    os.chdir('../enterprise/addons')
    os.system(f"git checkout {version}")
    os.chdir('../../odoo-server')
    os.system(f"git checkout {version}")
    os.chdir(f"../script/pipenv/{version}")


if __name__ == '__main__':
    start()
    print('Bye!')
