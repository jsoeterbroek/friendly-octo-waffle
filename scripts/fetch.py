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

    _data_list.append(num_keys)
    _data_list.append(num_users)
    _data_list.append(num_invalid_users)
    _data_list.append(num_keys_not_parsed)
    _data_list.append(num_keys_not_parsed_without_padding)
    _data_list.append(num_submitted_keys)
    return _data_list

def check_key_exists(_key):
    # check if object exists
    if Eks.objects.filter(key=_key).exists():
        #print('INFO: key exists..')
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

        # date pattern
        #pattern_date = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")

        # timestamps and dates
        _now = datetime.now()
        now = _now.replace(microsecond=0)
        _timestamp = datetime.timestamp(now)
        timestamp = int(_timestamp)
        #pd = pattern_date.findall(date_str)
        #timestamp = int(datetime(year=int(pd[0][0]), month=int(pd[0][1]), day=int(pd[0][2]), hour=2).strftime("%s"))

        #dt_object = datetime.fromtimestamp(timestamp)
        #today = datetime.date.today()
        timestamp_date = '{:%Y-%m-%d}'.format(datetime.now())
        timestamp_hour = '{:%H}'.format(datetime.now())
        timestamp_full = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())

        print("timestamp: {}".format(timestamp))
        print("timestamp_date: {}".format(timestamp_date))
        print("timestamp_hour: {}".format(timestamp_hour))
        print("timestamp_full: {}".format(timestamp_full))

        # paths and filenames
        basedir = os.path.abspath(os.path.dirname(__file__))
        datastore = os.path.join(basedir, 'datastore')
        datastore_today = os.path.join(datastore, timestamp_date)

        #DKS_CSV_FILE = os.path.join(datastore, "diagnosis_keys_statistics.csv")
        #DKS_JSON_FILE = os.path.join(datastore, "diagnosis_keys_statistics.json")
        #TRL_CSV_FILE = os.path.join(datastore, "transmission_risk_level_statistics.csv")
        #TRL_JSON_FILE = os.path.join(datastore, "transmission_risk_level_statistics.json")

        data_list = []

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
        #retrieval_timestamp = get_local_timestamp()
        json_obj['retrievaltimestamp'] = "TODO"
        json_obj['manifest_pki_signature'] = "TODO"

        #environment_json = json_obj
        #print(json.dumps(environment_json, indent=2))

        datastore_filename = "manifest.json"
        datastore_file = os.path.join(datastore_today, datastore_filename)
        print("INFO: writing to datastore '{}'.. ".format(datastore_filename), end='')
        write_json(datastore_file, json_obj)
        print("OK")

        seen = 0
        counter = 0
        sum_keys = 0
        sum_users = sum_submitted_keys = 0
        sum_invalid_users = 0
        sum_keys_not_parsed = 0
        sum_keys_not_parsed_without_padding = 0
        sum_submitted_keys = 0
        trl_sum_data = {}
        for exposurekeyset in exposurekeysets:
            eks = shorten_exposurekeyset(exposurekeyset)

            counter += 1
            if check_key_exists(eks):
                print("exposure keyset {} allready seen...".format(eks))
                seen += 1
                continue
            else:
                print("INFO: {}/{} retrieving exposure keyset '{}'.. ".format(counter, no_keysets, eks), end='')
                #curl ${=CFLAGS} --output eks.zip "$URL/v1/exposurekeyset/$exposureKeySets$SIG"

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
                    #os.system("scripts/diagnosis-keys/parse_keys_json.py -l -d {} > {}".format(zname, fn_analysis))
                    os.system("scripts/diagnosis-keys/parse_keys.py --auto-multiplier -m 5 -n -u -l -d {} > {}".format(zname, fn_eksdat))
                anonymize_TEKs(fn_eksdat)

                data_list = process_data_from_dat(fn_eksdat)

                num_keys = data_list[0]
                num_users = data_list[1]
                num_invalid_users = data_list[2]
                num_keys_not_parsed = data_list[3]
                num_keys_not_parsed_without_padding = data_list[4]
                num_submitted_keys = data_list[5]
                data = {}
                data['environment'] = manifest_environment
                print("INFO: writing to django ({}).. ".format(data['environment']), end='')
                #    #print(json.dumps(json_obj, indent=4))
                data['key'] = exposurekeyset
                data['shortkey'] = eks
                #    data['timewindow_start_timestamp'] = json_obj['timeWindowStart']
                #    data['timewindow_end_timestamp'] = json_obj['timeWindowEnd']
                #    data['region'] = json_obj['region']
                #    data['batch_num'] = json_obj['batchNum']
                #    data['batch_size'] = json_obj['batchCount']
                #    #data['app_bundle_id'] =
                #    data['verification_key_version'] = json_obj['signatureInfos']['verification_key_version']
                #    data['verification_key_id'] = json_obj['signatureInfos']['verification_key_id']
                #    data['signature_algorithm'] = json_obj['signatureInfos']['signature_algorithm']
                #    #data['padding_multiplier'] = 5
                data['num_teks'] = num_keys
                print("INFO: {}/{} saving exposure keyset {} to db'.. ".format(counter, no_keysets, eks), end='')
                if create_obj(Eks, data):
                    print("OK")
                else:
                    print("ERR")

                # increment
                sum_keys += num_keys
                sum_users += num_users
                sum_invalid_users += num_invalid_users
                sum_keys_not_parsed += num_keys_not_parsed
                sum_keys_not_parsed_without_padding += num_keys_not_parsed_without_padding
                sum_submitted_keys += num_submitted_keys

                # tabubulate TRL's
                trl_sum_data = {'key': exposurekeyset, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}
                trl_data = process_trl_from_dat(exposurekeyset, fn_eksdat)
                for i, v in trl_data.items():
                    if i != 'key':
                        trl_sum_data[i] = trl_sum_data[i] + v

                # clean up
                manifestzip = os.path.join(datastore_today, 'manifest.zip')
                if os.path.isfile(manifestzip):
                    os.remove(manifestzip)
                ekszip = os.path.join(datastore_today, ekszip)
                if os.path.isfile(ekszip):
                    os.remove(ekszip)
                contentbin = os.path.join(datastore_today, 'content.bin')
                if os.path.isfile(contentbin):
                    os.remove(contentbin)
                contentsig = os.path.join(datastore_today, 'content.sig')
                if os.path.isfile(contentsig):
                    os.remove(contentsig)

        if seen == counter:
            # stats to db
            print("INFO: stats to db'.. ")
            print("date: {}".format(timestamp_date))
            print("sum keys: {}".format(sum_keys))
            print("users: {}".format(sum_users))
            print("invalid users: {}".format(sum_invalid_users))
            print("keys not parsed: {}".format(sum_keys_not_parsed))
            print("keys not parsed without padding: {}".format(sum_keys_not_parsed_without_padding))
            print("submitted keys: {}".format(sum_submitted_keys))
            print("sum TRLs: {}".format(trl_sum_data))

