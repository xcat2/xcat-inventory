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

    def __init__(self, obj1, obj2, srctype='other', objtype='f'):
        self.obj1 = obj1
        self.obj2 = obj2
        self.srctype = srctype
        self.objtype = objtype
        self.fmt = 'json'

    def _get_data(self):
        try:
            d1, self.fmt = utils.loadfile(filename=self.obj1)
            d2, self.fmt = utils.loadfile(filename=self.obj2)
        except Exception,e:
            (retcode,out,err)=utils.runCommand("diff -u %s %s"%(self.obj1,self.obj2))
            if out:
                out=re.sub(r"%s.*"%(self.obj1),self.obj2,out)
                out=re.sub(r"%s.*"%(self.obj2),self.obj2,out)
            if err:
                err=re.sub(r"%s.*"%(self.obj1),self.obj2,err)
                err=re.sub(r"%s.*"%(self.obj2),self.obj2,err)
            return 1, out, err
        return 0, d1, d2

    def ShowDiff(self):
        print("\n====================BEGIN=====================\n")
        if self.objtype == 'f':
            rc, d1, d2 = self._get_data()
        else:
            rc = 0
            d1 = self.obj1
            d2 = self.obj2

        if rc:
                print(d1)
                print(d2)
        else:
            dt = deepdiff.DeepDiff(d1,d2,ignore_order=True,report_repetition=False,exclude_paths='',significant_digits=None,view='tree',verbose_level=1)
            diff_out = format_diff_output(self.fmt).get_diff_string(dt)

            if self.srctype == 'git':
                print("\n--- %s\n+++ %s"%(self.obj2, self.obj2))
            else:
                print("\n--- %s\n+++ %s"%(self.obj1,self.obj2))
            print (diff_out)
        print("\n====================END=====================\n")

