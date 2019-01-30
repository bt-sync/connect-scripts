#!/usr/bin/env python
# -*- coding: utf-8 -*-
# title           :update-syncconfig.py
# description     :This script updates sync.config of Resilio Connect Agent
# author          :Alexey Costroma
# date            :20190129
# version         :0.2
# usage           :python update-syncconfig.py
# python_version  :2.7.10
# ==============================================================================

import argparse
import json
import os

management_server_args = ['bootstrap_token',
                          'cert_authority_fingerprint',
                          'disable_cert_check',
                          'host']

def main():
    args = get_args()
    config = read_sync_config(args.config)

    print 'Current sync.config is:\n{}'.format(config) + os.linesep

    new_config = process_tasks(config, args)
    save_sync_config(args.config, new_config)

    print Colors.green + 'New sync.config is:\n{}'.format(config) + Colors.end + os.linesep


def process_tasks(config, args):
    if args.parameter is not None:
        set_parameter(args.parameter, config, args.value)

    if args.host is not None:
        set_parameter('host', config, args.host)

    if args.fingerprint is not None:
        set_parameter('cert_authority_fingerprint', config, args.fingerprint)

    if args.disable_cert_check is not None:
        set_parameter('disable_cert_check', config, args.disable_cert_check)

    if args.use_gui is not None:
        set_parameter('use_gui', config, args.use_gui)

    if args.bootstrap_token is not None:
        set_parameter('bootstrap_token', config, args.bootstrap_token)

    if args.tags is not None:
        set_parameter('tags', config, args.tags)

    if args.folders_storage_path is not None:
        set_parameter('folders_storage_path', config, args.folders_storage_path)

    if args.delete is not None:
        delete_parameter(args.delete, config)

    return config


def delete_parameter(name, config):
    print "Deleting '{}'".format(name) + os.linesep

    if name in config:
        del config[name]
        return

    if 'management_server' in config and name in config['management_server']:
        del config['management_server'][name]
        return

    print Colors.warn + 'Can\'t find {} in sync.config. Skipping'.format(name) + Colors.end + os.linesep


def set_parameter(name, config, value):
    print "Setting '{}' to '{}'".format(name, value) + os.linesep
    if 'management_server' not in config:
        config['management_server'] = {}

    value = verify_value(value)

    if name in management_server_args:
        config['management_server'][name] = value
        return
    else:
        config[name] = value
        return


def verify_value(value):
    if isinstance(value, bool):
        return value

    bool_value = str2bool(value, False)

    if bool_value is not None:
        return bool_value

    try:
        value = int(value)
    except ValueError:
        pass

    return value


def read_sync_config(config):
    handle = open(config, "r")
    try:
        data = json.load(handle)
    except ValueError:
        print Colors.red + 'Invalid sync.conf: {}\n{}'.format(handle, handle.read()) + Colors.end + os.linesep
        handle.close()
        exit(1)

    handle.close()

    return data


def save_sync_config(config, data):
    handle = open(config, "w+")
    handle.write(json.dumps(data, indent=4))
    handle.write(os.linesep)
    handle.close()


def get_args():
    args = parse_arguments()
    verify_args(args)

    return args


def verify_args(args):
    if args.config and not os.path.isfile(args.config):
        print Colors.red + "sync.config doesn't exist on the following path: {}".format(args.config) + Colors.end + os.linesep
        exit(1)

    if (args.parameter is not None and args.value is None) or \
            (args.value is not None and args.parameter is None):
        print Colors.red + 'set --parameter and --value together' + Colors.end + os.linesep
        exit(1)


def str2bool(v, raise_exception=True):
    if v.lower() in ('yes', 'true'):
        return True

    if v.lower() in ('no', 'false'):
        return False

    if raise_exception:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    else:
        return None


class Colors:
    def __init__():
        pass

    blue = '\033[94m'
    green = '\033[92m'
    warn = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


def parse_arguments():
    user_home = os.path.expanduser("~")
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        default='{}/Library/Application Support/Resilio Connect Agent/sync.conf'.format(user_home),
                        metavar='<path_to_sync.conf>',
                        help='path to sync.conf (default: %(default)s)')
    parser.add_argument('--parameter',
                        metavar='<name>',
                        help='name of parameter to manipulate')
    parser.add_argument('--value',
                        metavar='<value>',
                        help='value to set to parameter')
    parser.add_argument('--delete',
                        metavar='<parameter_name>',
                        help='delete parameter')

    parser.add_argument('--host',
                        metavar='<value>',
                        help='value to set to host')
    parser.add_argument('--fingerprint',
                        metavar='<value>',
                        help='value to set to fingerprint')
    parser.add_argument('--disable_cert_check',
                        type=str2bool,
                        metavar='<value>',
                        help='value to set to disable_cert_check')
    parser.add_argument('--bootstrap_token',
                        metavar='<value>',
                        help='value to set to bootstrap_token')
    parser.add_argument('--tags',
                        metavar='<value>',
                        help='value to set to tags')
    parser.add_argument('--folders_storage_path',
                        metavar='<value>',
                        help='value to set to folders_storage_path')
    parser.add_argument('--use_gui',
                        type=str2bool,
                        metavar='<value>',
                        help='value to set to use_gui')


    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
