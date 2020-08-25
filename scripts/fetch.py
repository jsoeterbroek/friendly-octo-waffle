#!/usr/bin/env python3
# fetch_parse_keys.py

import os
import sys
import json
import re
from datetime import datetime
from zipfile import ZipFile
import requests

from django.db import IntegrityError
from eks.models import Eks

manifest_environment = 'productie'
#manifest_environment = 'test'

def write_json(path, json_data):
    with open(path, 'w') as file_out:
        json.dump(json_data, file_out)

def read_json(path):
    with open(path) as file_in:
        return json.load(file_in)

def shorten_exposurekeyset(exposurekeyset):

    _eks = exposurekeyset[0:8]
    return _eks

def anonymize_TEKs(filename):

    tek_pattern = re.compile(r"[0-9a-f]{24},")

    with open(filename, 'r') as f:
        raw_data = f.read().splitlines()
        f.close()

    with open(filename, 'w') as f:
        for line in raw_data:
            f.write(tek_pattern.sub("XXXXXXXXXXXXXXXXXXXXXXXX,", line) + "\n")
        f.close()

def process_data_from_dat(filename):

    _data_list = []
    with open(filename, 'r') as f:
        raw_data = f.read().splitlines()
        f.close()

    # patterns
    pattern_timewindow = re.compile(r"- Time window: ([0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*:[0-9]* [A-Z]*) - ([0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*:[0-9]* [A-Z]*)")
    pattern_num_keys = re.compile(r"Length: ([0-9]{1,}) keys")
    pattern_num_users = re.compile(r"([0-9]{1,}) user\(s\) found\.")
    pattern_num_subm = re.compile(r"([0-9]{1,}) user\(s\): ([0-9]{1,}) Diagnosis Key\(s\)")
    pattern_invalid_users = re.compile(r"([0-9]{1,}) user\(s\): Invalid Transmission Risk Profile")
    pattern_keys_not_parsed = re.compile(r"([0-9]{1,}) keys not parsed \(([0-9]{1,}) without padding\).")

    num_keys = 0
    num_users = 0
    num_invalid_users = 0
    num_keys_not_parsed = 0
    num_keys_not_parsed_without_padding = 0
    num_submitted_keys = 0
    start_timewindow = ''
    end_timewindow = ''

    # read contents
    with open(filename, 'r') as df:
        raw_data = df.read()

        # number of diagnosis keys
        pk = pattern_num_keys.findall(raw_data)
        if (len(pk) == 1):
            num_keys += int(pk[0])
        # number of users who submitted keys
        pu = pattern_num_users.findall(raw_data)
        if (len(pu) == 1):
            num_users += int(pu[0])
        # number of invalid users
        piu = pattern_invalid_users.findall(raw_data)
        if (len(piu) == 1):
            num_invalid_users += int(piu[0])
        # keys not parsed
        pknp = pattern_keys_not_parsed.findall(raw_data)
        if (len(pknp) > 0):
            for line in pknp:
                if (len(line) == 2):
                    num_keys_not_parsed += int(line[0])
                    num_keys_not_parsed_without_padding += int(line[1])
        # timewindow
        pt = pattern_timewindow.findall(raw_data)
        print(pt)
        if (len(pt) > 0):
            for line in pt:
                if (len(line) == 2):
                    start_timewindow = str(line[0])
                    end_timewindow = str(line[1])
        # number of submitted keys
        psk = pattern_num_subm.findall(raw_data)
        if (len(psk) > 0):
            for line in psk:
                if (len(line) == 2):
                    num_submitted_keys += int(line[0]) * int(line[1])

    #print("num keys: {}".format(num_keys))
    #print("num users: {}".format(num_users))
    #print("num invalid users: {}".format(num_invalid_users))
    #print("num keys not parsed: {} ({} without padding)".format(num_keys_not_parsed, num_keys_not_parsed_without_padding))
    #print("num submitted keys: {}".format(num_submitted_keys))
    #print("timewindow start: {}".format(start_timewindow))
    #print("timewindow end: {}".format(end_timewindow))


    _data_list.append(num_keys)
    _data_list.append(num_users)
    _data_list.append(num_invalid_users)
    _data_list.append(num_keys_not_parsed)
    _data_list.append(num_keys_not_parsed_without_padding)
    _data_list.append(num_submitted_keys)
    _data_list.append(start_timewindow)
    _data_list.append(end_timewindow)

    return _data_list

def check_key_exists(_key):
    if Eks.objects.filter(key=_key).exists():
        return True
    else:
        return False

def create_obj(klass, dictionary):
    obj = klass()
    # check if object exists
    _key = dictionary['key']
    if Eks.objects.filter(key=_key).exists():
        print(' key exists, skipping.. ', end="")
        return True
    else:
        # set regular fields
        for field, value in dictionary.items():
            if not isinstance(value, list):
                setattr(obj, field, value)
        try:
            obj.save()
        except IntegrityError as e:
            print("Error saving obj {}".format(e.message))
            return False
        return True

def process_trl_from_dat(_key, filename):
    """ returns: dict """

    _trl_data = {}
    _trl_data_list = [_key, process_trl_data(filename)]
    _trl_data['key'] = _trl_data_list[0]
    _trl_data['1'] = _trl_data_list[1][0]
    _trl_data['2'] = _trl_data_list[1][1]
    _trl_data['3'] = _trl_data_list[1][2]
    _trl_data['4'] = _trl_data_list[1][3]
    _trl_data['5'] = _trl_data_list[1][4]
    _trl_data['6'] = _trl_data_list[1][5]
    _trl_data['7'] = _trl_data_list[1][6]
    _trl_data['8'] = _trl_data_list[1][7]
    return _trl_data

def process_trl_data(filename):

    data = [0, 0, 0, 0, 0, 0, 0, 0]
    trl_pattern = re.compile(r"Transmission Risk Level: ([0-8])")

    with open(filename, 'r') as f:
        raw_data = f.read().splitlines()
    f.close()

    for line in raw_data:
        pt = trl_pattern.search(line)
        if pt is not None:
            data[int(pt.group(1)) - 1] += 1

    return data

def run():
    if manifest_environment:

        # timestamps and dates
        timestamp_date = '{:%Y-%m-%d}'.format(datetime.now())

        # paths and filenames
        basedir = os.path.abspath(os.path.dirname(__file__))
        datastore = os.path.join(basedir, '..', 'datastore')
        datastore_today = os.path.join(datastore, timestamp_date)

        dks_json_file = os.path.join(datastore_today, "diagnosis_keys_statistics.json")
        trl_json_file = os.path.join(datastore_today, "transmission_risk_level_statistics.json")

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'joosts-check/2.00',
        }

        # create the corresponding directory
        if not os.path.isdir(datastore_today):
            os.makedirs(datastore_today)
            if not os.path.isdir(datastore_today):
                print("ERR: Could not create data directory '{}'!".format(datastore_today))

        url = "https://" + manifest_environment + ".coronamelder-dist.nl"
        manifesturl = '%s/v1/manifest' % (url)
        #print(datastore)
        print("INFO: retrieving manifest from '{}'.. ".format(manifesturl), end='')

        try:
            r = requests.get(manifesturl)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()

        if r.ok:
            zname = os.path.join(datastore_today, 'manifest.zip')
            zfile = open(zname, 'wb')
            zfile.write(r.content)
            print("OK")
            zfile.close()

        if zname:
            with ZipFile(zname, 'r') as zipObj:
                zipObj.extractall(datastore_today)

        json_obj_file = os.path.join(datastore_today, 'content.bin')
        with open(json_obj_file) as json_file:
            json_obj = json.load(json_file)

        exposurekeysets = json_obj['exposureKeySets']
        no_keysets = len(exposurekeysets)
        json_obj['no_keysets'] = no_keysets
        json_obj['retrievaltimestamp'] = "TODO"
        json_obj['manifest_pki_signature'] = "TODO"

        #print(json.dumps(json_obj, indent=4))

        datastore_filename = "manifest.json"
        datastore_file = os.path.join(datastore_today, datastore_filename)
        print("INFO: writing to datastore '{}'.. ".format(datastore_filename), end='')
        write_json(datastore_file, json_obj)
        print("OK")

        seen = 0
        counter = 0
        trl_sum_data = {'timestamp_date': timestamp_date, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}
        dks_sum_data = {'timestamp_date': timestamp_date, 'num_keys': 0, 'num_users': 0, 'num_invalid_users': 0, 'num_keys_not_parsed': 0, 'num_keys_not_parsed_without_padding': 0, 'num_submitted_keys': 0}
        for exposurekeyset in exposurekeysets:
            eks = shorten_exposurekeyset(exposurekeyset)

            counter += 1
            if check_key_exists(exposurekeyset):
                print("exposure keyset {} allready seen, skipping...".format(eks))
                seen += 1
                continue
            else:
                print("INFO: {}/{} retrieving exposure keyset '{}'.. ".format(counter, no_keysets, eks), end='')
                keyseturl = '%s/v1/exposurekeyset/%s' % (url, exposurekeyset)
                try:
                    r = requests.get(keyseturl, headers=headers)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(err)

                if r.ok:
                    ekszip = eks + ".zip"
                    zname = os.path.join(datastore_today, ekszip)
                    zfile = open(zname, 'wb')
                    zfile.write(r.content)
                    print("OK")
                    zfile.close()

                eksdat = eks + ".dat"
                fn_eksdat = os.path.join(datastore_today, eksdat)
                if not os.path.isfile(fn_eksdat):
                    os.system("scripts/diagnosis-keys/parse_keys.py --auto-multiplier -m 5 -n -u -l -d {} > {}".format(zname, fn_eksdat))
                anonymize_TEKs(fn_eksdat)

                dks_data_list = process_data_from_dat(fn_eksdat)
                dks_data_dict = {}
                trl_data_dict = process_trl_from_dat(exposurekeyset, fn_eksdat)

                num_keys = dks_data_list[0]
                num_users = dks_data_list[1]
                num_invalid_users = dks_data_list[2]
                num_keys_not_parsed = dks_data_list[3]
                num_keys_not_parsed_without_padding = dks_data_list[4]
                num_submitted_keys = dks_data_list[5]
                dks_data_dict['environment'] = manifest_environment

                print("INFO: writing to django ({}).. ".format(dks_data_dict['environment']), end='')
                dks_data_dict['key'] = exposurekeyset
                dks_data_dict['shortkey'] = eks
                dks_data_dict['num_teks'] = num_keys
                dks_data_dict['seen'] = timestamp_date
                dks_data_dict['start_timestamp'] = dks_data_list[6]
                dks_data_dict['end_timestamp'] = dks_data_list[7]

                print("INFO: {}/{} saving exposure keyset {} to db'.. ".format(counter, no_keysets, eks), end='')
                if create_obj(Eks, dks_data_dict):
                    print("OK")
                else:
                    print("ERR")

                dks_data_dict['num_keys'] = num_keys
                dks_data_dict['num_users'] = num_users
                dks_data_dict['num_invalid_users'] = num_invalid_users
                dks_data_dict['num_keys_not_parsed'] = num_keys_not_parsed
                dks_data_dict['num_keys_not_parsed_without_padding'] = num_keys_not_parsed_without_padding
                dks_data_dict['num_submitted_keys'] = num_submitted_keys

                # increment DKS (diagnosis_keys)
                for i, v in dks_data_dict.items():
                    _filter = ['environment', 'key', 'shortkey', 'num_teks', 'seen', 'start_timestamp', 'end_timestamp']
                    if i not in _filter:
                        dks_sum_data[i] += dks_sum_data[i] + v

                # increment TRL
                for i, v in trl_data_dict.items():
                    _filter = ['key']
                    if i not in _filter:
                        trl_sum_data[i] += trl_sum_data[i] + v

                # clean up
                ekszip = os.path.join(datastore_today, ekszip)
                if os.path.isfile(ekszip):
                    os.remove(ekszip)

        # clean up
        manifestzip = os.path.join(datastore_today, 'manifest.zip')
        if os.path.isfile(manifestzip):
            os.remove(manifestzip)
        contentbin = os.path.join(datastore_today, 'content.bin')
        if os.path.isfile(contentbin):
            os.remove(contentbin)
        contentsig = os.path.join(datastore_today, 'content.sig')
        if os.path.isfile(contentsig):
            os.remove(contentsig)

        # write to datastore
        if seen != counter:
            print("INFO: saving stats DKS to datastore'.. ", end='')
            # write json to disk
            with open(dks_json_file, 'w') as f:
                f.write(json.dumps(dks_sum_data, sort_keys=True, indent=4))
                f.close()
            print("OK")
            print("INFO: saving stats TRL to datastore'.. ", end='')
            # write json to disk
            with open(trl_json_file, 'w') as f:
                f.write(json.dumps(trl_sum_data, sort_keys=True, indent=4))
                f.close()
            print("OK")

            # stats to db
            #print("sum TRLs: {}".format(trl_sum_data))
            #print("sum SKDs: {}".format(dks_sum_data))
