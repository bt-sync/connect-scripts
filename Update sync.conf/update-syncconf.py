#!/usr/bin/env python
# -*- coding: utf-8 -*-
# title           :update-syncconf.py
# description     :This script updates sync.conf of Resilio Connect Agent
# author          :Alexey Costroma
# date            :20190129
# version         :0.1
# usage           :python update-syncconf.py
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
    conf = read_sync_conf(args.conf)

    print 'Current sync.conf is:\n{}'.format(conf) + os.linesep

    new_conf = process_tasks(conf, args)
    save_sync_conf(args.conf, new_conf)

    print Colors.green + 'New sync.conf is:\n{}'.format(conf) + Colors.end + os.linesep


def process_tasks(conf, args):
    if args.parameter is not None:
        set_parameter(args.parameter, conf, args.value)

    if args.host is not None:
        set_parameter('host', conf, args.host)

    if args.fingerprint is not None:
        set_parameter('cert_authority_fingerprint', conf, args.fingerprint)

    if args.disable_cert_check is not None:
        set_parameter('disable_cert_check', conf, args.disable_cert_check)

    if args.bootstrap_token is not None:
        set_parameter('bootstrap_token', conf, args.bootstrap_token)

    if args.tags is not None:
        set_parameter('tags', conf, args.tags)

    if args.folders_storage_path is not None:
        set_parameter('folders_storage_path', conf, args.folders_storage_path)

    if args.delete is not None:
        delete_parameter(args.delete, conf)

    return conf


def delete_parameter(name, conf):
    print "Deleting '{}'".format(name) + os.linesep

    if name in conf:
        del conf[name]
        return

    if 'management_server' in conf and name in conf['management_server']:
        del conf['management_server'][name]
        return

    print Colors.warn + 'Can\'t find {} in sync.conf. Skipping'.format(name) + Colors.end + os.linesep


def set_parameter(name, conf, value):
    print "Setting '{}' to '{}'".format(name, value) + os.linesep
    if 'management_server' not in conf:
        conf['management_server'] = {}

    if name in management_server_args:
        conf['management_server'][name] = value
        return
    else:
        conf[name] = value
        return


def read_sync_conf(conf):
    handle = open(conf, "r")
    try:
        data = json.load(handle)
    except ValueError:
        print Colors.red + 'Invalid sync.conf: {}\n{}'.format(handle, handle.read()) + Colors.end + os.linesep
        handle.close()
        exit(1)

    handle.close()

    return data


def save_sync_conf(conf, data):
    handle = open(conf, "w+")
    handle.write(json.dumps(data, indent=4))
    handle.write(os.linesep)
    handle.close()


def get_args():
    args = parse_arguments()
    verify_args(args)

    return args


def verify_args(args):
    if args.conf and not os.path.isfile(args.conf):
        print Colors.red + "sync.conf doesn't exist on the following path: {}".format(args.conf) + Colors.end + os.linesep
        exit(1)

    if (args.parameter is not None and args.value is None) or \
            (args.value is not None and args.parameter is None):
        print Colors.red + 'set --parameter and --value together' + Colors.end + os.linesep
        exit(1)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True

    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

    raise argparse.ArgumentTypeError('Boolean value expected.')


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
    parser.add_argument('--conf',
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

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
