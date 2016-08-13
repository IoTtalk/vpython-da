from __future__ import print_function

import random
import threading
import time

import dan


class DF(object):
    @property
    def name(self):
        return self.__class__.__name__

    def __init__(self):
        self.selected = False


class ODF(DF):
    def pull(self, data):
        pass


class IDF(DF):
    def push(self, *args):
        dan.push(self.name, args)


class Command(object):
    @property
    def name(self):
        return self.__class__.__name__

    def run(self, dl_cmd_params, ul_cmd_params):
        print('OAO')
        pass


class DAN2DAI(object):
    def pull(self, odf_name, data):
        if odf_name == 'Control':
            cmd = get_cmd(data[0])
            if cmd:
                cmd.run(data[1]['cmd_params'], None)
                return

            logging('Command not found: {}', data[0])

        else:
            df = get_df(odf_name)
            if df:
                df.pull(data)
                return

            logging('ODF not found: {}', odf_name)


def get_df(df_name):
    try:
        return next(df for df in df_list if df.name == df_name)
    except StopIteration:
        return None


def add_cmd(*cmds):
    for cmd in cmds:
        cmd_list.append(cmd)


def get_cmd(cmd_name):
    try:
        return next(
            cmd for cmd in cmd_list
            if cmd_name in (cmd.name, cmd.name + '_RSP')
        )
    except StopIteration:
        return None


def logging(fmt, *args, **kwargs):
    if LOGGING:
        print(fmt.format(*args, **kwargs))


class SET_DF_STATUS(Command):
    def run(self, dl_cmd_params, ul_cmd_params):
        if ul_cmd_params is None:
            flags = dl_cmd_params[0]
            for index, df in enumerate(df_list):
                df.selected = (flags[index] == '1')

            get_cmd('SET_DF_STATUS_RSP').run(None, [flags])

        elif dl_cmd_params is None:
            dan.push('Control', [
                'SET_DF_STATUS_RSP',
                {'cmd_params': ul_cmd_params}
            ])

        else:
            logging('SET_DF_STATUS: Error')


class RESUME(Command):
    def run(self, dl_cmd_params, ul_cmd_params):
        if ul_cmd_params is None:
            ida.suspended = False
            get_cmd('RESUME_RSP').run(None, ['OK'])

        elif dl_cmd_params is None:
            dan.push('Control', [
                'RESUME_RSP',
                {'cmd_params': ul_cmd_params}
            ])

        else:
            logging('SET_DF_STATUS: Error')


class SUSPEND(Command):
    def run(self, dl_cmd_params, ul_cmd_params):
        if ul_cmd_params is None:
            ida.suspended = False
            get_cmd('SUSPEND_RSP').run(None, ['OK'])

        elif dl_cmd_params is None:
            dan.push('Control', [
                'SUSPEND_RSP',
                {'cmd_params': ul_cmd_params}
            ])

        else:
            logging('SET_DF_STATUS: Error')


# dan.LOGGING = True
LOGGING = True
df_list = []
cmd_list = []
ida = None


def main(endpoint, mac_addr, profile, g):
    global df_list
    global ida

    idfs = []
    odfs = []
    cmds = []
    for i in g:
        try:
            if g[i].__class__ == type:
                if IDF in g[i].__bases__:
                    print('IDF:', i)
                    idfs.append(g[i]())
                elif ODF in g[i].__bases__:
                    print('ODF:', i)
                    odfs.append(g[i]())
                elif Command in g[i].__bases__:
                    print('CMD:', i)
                    cmds.append(g[i]())

            elif i == 'ida' and g[i].__class__.__name__ == 'IDA':
                ida = g[i]

        except AttributeError:
            pass

    if ida is None:
        print('ida object not found, did you forgot inherit the IDA from "object"?')

    df_list.extend(idfs)
    df_list.extend(odfs)

    add_cmd(
        SET_DF_STATUS(),
        RESUME(),
        SUSPEND(),
    )
    add_cmd(*cmds)

    profile['df_list'] = [df.__class__.__name__ for df in df_list]

    endpoint = dan.init(DAN2DAI(), endpoint, mac_addr, profile)

    if not endpoint:
        logging('Register Failed')
        return

    logging('Registered to {}'.format(endpoint))
    ida.iot_app()

    dan.wait_until_deregister()
    logging('main() ends')
