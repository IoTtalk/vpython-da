from __future__ import print_function

import json
import time
import socket
import sys
import os

from threading import Thread, Lock

import csmapi


IOTTALK_BROADCAST_PORT = 17000
RETRY_COUNT = 3
RETRY_INTERVAL = 2
LOGGING = False

_dan2dai = None
_mac_addr = None
_profile = None
_registered = False
_df_list = None
_df_selected = None
_df_is_odf = None
_df_timestamp = None
_ctl_timestamp = None
_suspended = False

_deregister_lock = Lock()


def logging(fmt, *args, **kwargs):
    if LOGGING:
        print(fmt.format(*args, **kwargs))


def init(dan2dai, endpoint, mac_addr, profile):
    global _dan2dai
    global _mac_addr

    logging('init()')
    _dan2dai = dan2dai
    _mac_addr = mac_addr.replace(':', '')

    if endpoint == None:
        logging('init(): Scanning IoTtalk server...')
        endpoint = _search()
        logging('init(): Found: {}', csmapi.ENDPOINT)

    if register(endpoint, profile):
        return csmapi.ENDPOINT

    return ''


def register(endpoint, profile):
    global _profile
    global _registered
    global _df_list
    global _df_selected
    global _df_is_odf
    global _df_timestamp

    if endpoint is not None:
        csmapi.ENDPOINT = endpoint

    if csmapi.ENDPOINT is None:
        return False

    _profile = profile
    _profile['d_name'] = profile['dm_name'] + _mac_addr[-4:]

    for i in range(RETRY_COUNT):
        try:
            if csmapi.register(_mac_addr, profile):
                logging('init(): Register succeed: {}', csmapi.ENDPOINT)
                _df_list = [df_name for df_name in profile['df_list']]
                _df_selected = {odf_name: False for odf_name in _df_list}
                _df_is_odf = {odf_name: True for odf_name in _df_list}
                _df_timestamp = {odf_name: '' for odf_name in _df_list}
                _ctl_timestamp = ''
                _suspended = True

                if not _registered:
                    _registered = True
                    t = Thread(target=main_loop)
                    t.daemon = True
                    t.start()
                    _deregister_lock.acquire()

                return True

        except csmapi.CSMError as e:
            logging('init(): Register: CSMError({})', e)

        logging('init(): Register failed, wait {} seconds before retry', RETRY_INTERVAL)
        time.sleep(RETRY_INTERVAL)

    return False


def push(idf_name, data):
    logging('push({})', idf_name)
    try:
        if idf_name == 'Control':
            idf_name = '__Ctl_I__'

        else:
            _df_is_odf[idf_name] = False
            if not _df_selected[idf_name]:
                return False

            if _suspended:
                return False

        return csmapi.push(_mac_addr, idf_name, data)
    except csmapi.CSMError as e:
        logging('push({}): CSMError({})', idf_name, e)

    return False


def deregister():
    logging('deregister()')
    _registered = False
    for i in range(RETRY_COUNT):
        try:
            if csmapi.deregister(_mac_addr):
                logging('deregister(): Deregister succeed: {}', csmapi.ENDPOINT)
                _deregister_lock.release()
                return True

        except csmapi.CSMError as e:
            logging('init(): Deregister: CSMError({})', e)

        logging('init(): Deregister failed, wait {} seconds before retry', RETRY_INTERVAL)
        time.sleep(RETRY_INTERVAL)

    return False


def wait_until_deregister():
    _deregister_lock.acquire()


def main_loop():
    logging('main_loop(): Main loop starts')
    while _registered:
        try:
            pull_ctl()

            for df_name in _df_list:
                if not _registered or _suspended:
                    break

                pull_odf(df_name)

        except csmapi.CSMError as e:
            logging('main_loop(): CSMError({})', e)

        time.sleep(0.05)

    logging('main_loop(): Main loop stops')


def pull_ctl():
    global _ctl_timestamp

    dataset = csmapi.pull(_mac_addr, '__Ctl_O__')
    if has_new_data(dataset, _ctl_timestamp):
        _ctl_timestamp = dataset[0][0]
        if _handle_control_message(dataset[0][1]):
            _dan2dai.pull('Control', dataset[0][1])

        else:
            logging('Problematic command message: {}', dataset[0][1])


def pull_odf(df_name):
    if not _df_is_odf[df_name] or not _df_selected[df_name]:
        return

    dataset = csmapi.pull(_mac_addr, df_name)
    if has_new_data(dataset, _df_timestamp[df_name]):
        _df_timestamp[df_name] = dataset[0][0]
        _dan2dai.pull(df_name, dataset[0][1])


def has_new_data(dataset, timestamp):
    if len(dataset) == 0 or timestamp == dataset[0][0]:
        return False

    return True


def _handle_control_message(data):
    global _suspended
    global _df_selected

    if data[0] == 'RESUME':
        _suspended = False

    elif data[0] == 'SUSPEND':
        _suspended = True

    elif 'SET_DF_STATUS':
        flags = data[1]['cmd_params'][0]
        if len(flags) != len(_df_list):
            return False

        for idx, df_name in enumerate(_df_list):
            _df_selected[df_name] = (flags[idx] == '1')

    else:
        logging('Unknown Command: {}', data)
        return False

    return True


def _search():
    UDP_IP = ''
    UDP_PORT = int(IOTTALK_BROADCAST_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((UDP_IP, UDP_PORT))
    while True:
        message, addr = s.recvfrom(1024)
        if message == b'easyconnect':
            return 'http://{}:9999'.format(addr[0])
