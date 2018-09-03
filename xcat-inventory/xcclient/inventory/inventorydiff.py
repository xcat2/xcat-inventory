#!/usr/bin/env python

from __future__ import print_function
import utils
from exceptions import *
import deepdiff
import yaml
import json
import sys
import re

class format_diff_output(object):
    def __init__(self, format_type):
        self.format_type = format_type 
        self.flag_dict = {'-diff': '-', '+diff': '+'}

    def _get_path_as_list(self, path):
        path_list = re.findall(r'(?<=\[\').+?(?=\'\])', path)
        return path_list

    def _update_dict(self, old_dict, new_dict):

        if not old_dict and new_dict:
            old_dict = new_dict
            return old_dict

        if type(new_dict) == list:
            old_dict += new_dict
            return old_dict

        keys = new_dict.keys()
        for key in keys:
            if key in old_dict:
                self._update_dict(old_dict[key], new_dict[key])
            else:
                old_dict.update({key: new_dict[key]})
        return old_dict 

    def _format_yaml(self, yamlstr):
        yaml_list = yamlstr.split('\n')
        new_list = []

        while len(yaml_list) > 0:
            tmp_str = yaml_list.pop(0)
            diff_flag = None
            flag = None
            for key, flag in self.flag_dict.items():
                if key in tmp_str:
                    diff_flag = key
                    break

            if diff_flag:
                null_num = 0
                if diff_flag + ': ' in tmp_str:
                    tmp_str = tmp_str.replace('%s: ' % diff_flag, '') 
                    if tmp_str:
                        tmp_str = flag + tmp_str.replace('\'', '')
                        new_list.append(tmp_str)
                else:
                    null_num = tmp_str.count(' ')
                    while len(yaml_list) > 0:
                        tmp_str = yaml_list.pop(0)
                        tmp_null_num = tmp_str.count(' ')
                        if tmp_null_num > null_num:
                            tmp_str = flag + tmp_str[2:]
                            new_list.append(tmp_str)
                        else:
                            yaml_list.insert(0, tmp_str)
                            break
            else:
                new_list.append(tmp_str) 

        return ('\n'.join(new_list))

    def _format_json(self, jsonstr):
        json_list = jsonstr.split('\n')
        new_list = []

        while len(json_list) > 0:
            tmp_str = json_list.pop(0)
            diff_flag = None 
            flag = None
            for key, flag in self.flag_dict.items():
                if key in tmp_str:
                    diff_flag = key
                    break

            if diff_flag:
                bracket = 0
                if '{' in tmp_str:
                    bracket += 1
                    while (bracket > 0 and len(json_list) > 0):
                        tmp_str = json_list.pop(0)
                        if '{' in tmp_str:
                            bracket += 1
                        if '}' in tmp_str:
                            bracket -= 1
                            if not bracket:
                                break
                        tmp_str = flag + tmp_str[4:]
                        new_list.append(tmp_str)
                else:
                    tmp_str = tmp_str.replace('%s: ' % diff_flag, '')
                    tmp_str = flag + tmp_str
                    new_list.append(tmp_str)
        
            else:
                new_list.append(tmp_str)

        return ('\n'.join(new_list))

    def _deal_with_diff_dict(self, result_dict):
        diff_dict = {}
        for key, value in result_dict.items():
            for change in value:
                mychange = {}
                if 'added' in key:
                    if 'iterable' in key:
                        path = self._get_path_as_list(change.up.path())
                        extra = path.pop()
                        mychange = {extra: ['+diff: %s' % change.t2]}
                    else:
                        path= self._get_path_as_list(change.path())
                        extra = path.pop()
                        mychange = { '+diff': {extra: change.t2}}
                elif 'removed' in key: 
                    if 'iterable' in key:
                        path = self._get_path_as_list(change.up.path())
                        extra = path.pop()
                        mychange = {extra: ['-diff: %s' % change.t1]}
                    else:
                        path = self._get_path_as_list(change.path())
                        extra = path.pop()
                        mychange = {'-diff': {extra: change.t1}}
                elif 'changed' in key:
                    path = self._get_path_as_list(change.path())
                    extra = path.pop()
                    mychange = {'-diff': {extra: change.t1}, '+diff': {extra: change.t2}}

                while len(path) > 0:
                    key_str = path.pop()
                    mychange = {key_str: mychange}

                for change_key in mychange:
                    diff_dict = self._update_dict(diff_dict, {change_key: mychange[change_key]}) 
        return diff_dict

    def get_diff_string(self, diff_dict):
        final_dict = self._deal_with_diff_dict(diff_dict) 
        if self.format_type == 'json':
            diff_json = json.dumps(final_dict, indent=4, separators=(',', ': '))
            return (self._format_json(diff_json))
        else:
            diff_yaml = yaml.safe_dump(final_dict, default_flow_style=False,allow_unicode=True)
            return (self._format_yaml(diff_yaml))

class InventoryDiff(object):

    def __init__(self, objs, objtype, isgit=False):
        self.objtype = objtype
        if objtype == 'f':
            self.obj1 = objs.pop(0)
        else:
            self.obj1 = 'xCAT_DB'
        self.obj2 = objs.pop(0)
        self.isgit = isgit
        self.fmt = 'json'

    def _get_file_data(self, data_file):
        data, self.fmt = utils.loadfile(filename=data_file)
        return data

    def _diff_with_cmd(self):
        (retcode,out,err)=utils.runCommand("diff -u %s %s"%(self.obj1,self.obj2))
        if out:
            out=re.sub(r"%s.*"%(self.obj1),self.obj2,out)
            out=re.sub(r"%s.*"%(self.obj2),self.obj2,out)
        if err:
            err=re.sub(r"%s.*"%(self.obj1),self.obj2,err)
            err=re.sub(r"%s.*"%(self.obj2),self.obj2,err)
        return out, err

    def _filter_DB_keys(self, d1, d2):
        for key in d1.keys():
            if key not in d2:
                del d1[key]
                continue
            if type(d1[key]) != dict:
                continue
            for subkey in d1[key].keys():
                if subkey not in d2[key]:
                    del d1[key][subkey]

    def ShowDiff(self):
        rc = None
        out = None
        if self.objtype == 'f':
            try:
                d1 = self._get_file_data(self.obj1)
                d2 = self._get_file_data(self.obj2)
            except FileNotExistException as e:
                err = e.message
                rc = 1
            except InvalidFileException as e:
                out, err = self._diff_with_cmd()
                rc = 1
        elif self.objtype == 'fvso':
            try:
                d2 = self._get_file_data(self.obj2) 
                if type(d2) != dict:
                    err = 'Error: Format of data from file \'%s\' is not correct, please check...' % self.obj2
                    rc = 1
            except FileNotExistException as e:
                err = e.message
                rc = 1
            except InvalidFileException as e:
                err = 'Error: Could not get json or yaml data from file \'%s\', please check or export object to diff files' % self.obj2
                rc = 1 

            if not rc:
                import xcclient.inventory.manager as mgr
                d1 = mgr.export_by_type(None, None, fmt='dict')
                self._filter_DB_keys(d1, d2)
        else:
            d1 = self.obj1
            d2 = self.obj2

        if rc and err:
            return print(err)

        print("\n====================BEGIN=====================\n")
        if not rc:
            dt = deepdiff.DeepDiff(d1,d2,ignore_order=True,report_repetition=False,exclude_paths='',significant_digits=None,view='tree',verbose_level=1)
            diff_out = format_diff_output(self.fmt).get_diff_string(dt)

            if self.isgit:
                print("\n--- %s\n+++ %s"%(self.obj2, self.obj2))
            else:
                print("\n--- %s\n+++ %s"%(self.obj1, self.obj2))

            if diff_out and diff_out != '{}':
                print(diff_out)
            else:
                print('No difference')
        else:
            if out:
                print(out) 
        print("\n====================END=====================\n")

def validate_args(args):
    if args.files and args.source:
        raise CommandException("Error: --files and --source cannot be used together!")
    if not args.files and not args.source:
        raise CommandException("Error: No valid source type!")

    if args.files:
        objs = args.files
        objtype = 'f'
    elif args.source:
        objs = args.source
        objtype = 'fvso'
    return (objs, objtype)
