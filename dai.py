import random
import threading
import time

import dan


class DF(object):
    def __init__(self, name):
        self.name = name
        self.selected = False


class ODF(DF):
    def __init__(self, name):
        super(ODF, self).__init__(name)

    def pull(self, data):
        pass


class IDF(DF):
    def __init__(self, name):
        super(IDF, self).__init__(name)

    def push(self, *args):
        dan.push(self.name, args)


class Command(object):
    def __init__(self, name):
        self.name = name

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


def add_df(*dfs):
    global df_list
    for df in dfs:
        df_list.append(df)


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
            if cmd.name == cmd_name or cmd.name + '_RSP' == cmd_name
        )
    except StopIteration:
        return None


def logging(fmt, *args, **kwargs):
    if LOGGING:
        print(fmt.format(*args, **kwargs))


class SET_DF_STATUS(Command):
    def __init__(self):
        super(SET_DF_STATUS, self).__init__('SET_DF_STATUS')

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
    def __init__(self):
        super(RESUME, self).__init__('RESUME')

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
    def __init__(self):
        super(SUSPEND, self).__init__('SUSPEND')

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


def main(endpoint, mac_addr, profile, ida, dfs, cmds):
    
    add_df(*dfs)
    add_cmd(
        SET_DF_STATUS(),
        RESUME(),
        SUSPEND(),
    )
    add_cmd(*cmds)

    profile['df_list'] = [df.name for df in df_list]

    endpoint = dan.init(DAN2DAI(), endpoint, mac_addr, profile)

    if not endpoint:
        logging('Register Failed')
        return

    logging('Registered to {}'.format(endpoint))
    ida.iot_app()

    dan.wait_until_deregister()
    logging('main() ends')
