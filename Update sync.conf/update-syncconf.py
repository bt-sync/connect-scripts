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
    print 'Reading {}'.format(args.config) + os.linesep
    config = read_sync_config(args.config)

    print 'Current sync.conf is:' + os.linesep + str(config) + os.linesep

    new_config = process_tasks(config, args)
    save_sync_config(args.config, new_config)

    print Colors.green + 'New sync.conf is:' + os.linesep + str(config) + Colors.end + os.linesep


def process_tasks(config, args):
    if args.parameter is not None:
        for parameter in args.parameter:
            try:
                name, value = parameter.split('=')
            except ValueError:
                raise argparse.ArgumentTypeError('--parameter has <name>=<value> syntax' + os.linesep +
                                                 'Multiple values can be set')
            name = verify_name(name)
            value = verify_value(value)
            set_parameter(name, config, value)

    if args.bootstrap_token is not None:
        value = verify_value(args.bootstrap_token)
        set_parameter('bootstrap_token', config, value)

    if args.disable_cert_check is not None:
        value = verify_value(args.disable_cert_check)
        set_parameter('disable_cert_check', config, value)

    if args.fingerprint is not None:
        value = verify_value(args.fingerprint)
        set_parameter('cert_authority_fingerprint', config, value)

    if args.folders_storage_path is not None:
        value = verify_value(args.folders_storage_path)
        set_parameter('folders_storage_path', config, value)

    if args.host is not None:
        value = verify_value(args.host)
        set_parameter('host', config, value)

    if args.tags is not None:
        value = verify_value(args.tags)
        set_parameter('tags', config, value)

    if args.use_gui is not None:
        value = verify_value(args.use_gui)
        set_parameter('use_gui', config, value)

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

    print Colors.warn + 'Can\'t find {} in sync.conf. Skipping'.format(name) + Colors.end + os.linesep


def set_parameter(name, config, value):
    print "Setting '{}' to '{}'".format(name, value) + os.linesep

    if name in management_server_args:
        if 'management_server' not in config:
            config['management_server'] = {}
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


def verify_name(value):
    if not value or \
       not isinstance(value, basestring):
        raise argparse.ArgumentTypeError('Parameter name can\'t be empty.')

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
        print Colors.red + "sync.conf doesn't exist on the following path: {}".format(args.config) \
              + Colors.end + os.linesep
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
    parser.add_argument('--parameter', '-p',
                        metavar='<name>=<value>',
                        help='E.g. --parameter use_gui=True. Several parameters can be set:' + os.linesep + \
                        '--parameter host=192.168.0.1 use_gui=True folders_storage_path="D:\\Downloads"',
                        nargs='+')
    parser.add_argument('--delete', '-d',
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
