#!/usr/bin/env python3
# fetch_parse_keys.py

import os
import sys
import json
import re
from datetime import datetime
from zipfile import ZipFile
import requests

from eks.models import Eks, Tek

manifest_environment = 'productie'
#manifest_environment = 'test'

def write_json(path, json_data):
    with open(path, 'w') as file_out:
        json.dump(json_data, file_out)

def read_json(path):
    with open(path) as file_in:
        return json.load(file_in)

def anonymize_TEKs(filename):

    tek_pattern = re.compile(r"[0-9a-f]{24},")

    with open(filename, 'r') as f:
        raw_data = f.read().splitlines()
        f.close()

    with open(filename, 'w') as f:
        for line in raw_data:
            f.write(tek_pattern.sub("XXXXXXXXXXXXXXXXXXXXXXXX,", line) + "\n")
        f.close()

def create_eks(klass, dictionary):
    obj = klass()
    # check if object exists
    _key = dictionary['key']
    if Eks.objects.filter(key=_key).exists():
        print(' key exists.. ', end="")
        return False
    else:
        # set regular fields
        for field, value in dictionary.items():
            if not isinstance(value, list):
                setattr(obj, field, value)
        try:
            obj.save()
        except:
            return False
        return True

def create_tek(klass, dictionary, exposurekeyset):
    obj = klass()
    # check if object exists
    _key = dictionary['key']
    eks_instance = Eks.objects.filter(key=exposurekeyset).first()
    if Tek.objects.filter(key=_key).exists():
        print(' key exists.. ', end="")
        return False
    else:
        # set regular fields
        setattr(obj, 'eks', eks_instance)
        for field, value in dictionary.items():
            if not isinstance(value, list):
                setattr(obj, field, value)
        try:
            obj.save()
        except:
            return False
        return True

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
        now = datetime.now()

        timestamp = datetime.timestamp(now)
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

        DKS_CSV_FILE = os.path.join(datastore, "diagnosis_keys_statistics.csv")
        DKS_JSON_FILE = os.path.join(datastore, "diagnosis_keys_statistics.json")
        TRL_CSV_FILE = os.path.join(datastore, "transmission_risk_level_statistics.csv")
        TRL_JSON_FILE = os.path.join(datastore, "transmission_risk_level_statistics.json")

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

        counter = 0
        for exposurekeyset in exposurekeysets:

            counter += 1
            print("INFO: {}/{} retrieving exposure keyset '{}'.. ".format(counter, no_keysets, exposurekeyset), end='')
            #curl ${=CFLAGS} --output eks.zip "$URL/v1/exposurekeyset/$exposureKeySets$SIG"

            keyseturl = '%s/v1/exposurekeyset/%s' % (url, exposurekeyset)
            try:
                r = requests.get(keyseturl, headers=headers)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

            if r.ok:
                ekszip = exposurekeyset + ".zip"
                zname = os.path.join(datastore_today, ekszip)
                zfile = open(zname, 'wb')
                zfile.write(r.content)
                print("OK")
                zfile.close()

            eksdat = exposurekeyset + ".dat"
            fn_analysis = os.path.join(datastore_today, eksdat)
            if not os.path.isfile(fn_analysis):
                #os.system("scripts/diagnosis-keys/parse_keys_json.py -l -d {} > {}".format(zname, fn_analysis))
                os.system("scripts/diagnosis-keys/parse_keys.py --auto-multiplier -m 5 -n -u -l -d {} > {}".format(zname, fn_analysis))
            anonymize_TEKs(fn_analysis)

            data_list.append(eksdat)

        ###########################################################################
        # PART 2: generate statistics
        ###########################################################################

        pattern_num_keys = re.compile(r"Length: ([0-9]{1,}) keys")
        pattern_num_users = re.compile(r"([0-9]{1,}) user\(s\) found\.")
        pattern_num_subm = re.compile(r"([0-9]{1,}) user\(s\): ([0-9]{1,}) Diagnosis Key\(s\)")
        #pattern_invalid_users = re.compile(r"([0-9]{1,}) user\(s\): Invalid Transmission Risk Profile")

        # initialization
        date_list = []
        trl_data = []
        trl_sum_data = [0, 0, 0, 0, 0, 0, 0, 0]
        sum_keys = sum_users = sum_subbmited_keys = 0

        # add an empty entry as origin (2020-06-22)
        date_list.append([1592784000, 0, 0, 0, 0, 0, 0])
        trl_data.append([1592784000, [0, 0, 0, 0, 0, 0, 0, 0]])

        num_keys = num_users = num_subbmited_keys = 0
        for d in data_list:
            filename = os.path.join(datastore_today, d)
            print(filename)

            ###################################################################
            # Transmission Risk Levels (TRLs)
            ###################################################################

            # process transmission risk level data
            new_trl_data = [timestamp, process_trl_data(filename)]
            trl_data.append(new_trl_data)
            for i, val in enumerate(new_trl_data[1]):
                trl_sum_data[i] += val

            ###################################################################
            # Temporary Exposure Keys (TEKs)
            ###################################################################

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

            # subtract invalid users
            #pi = pattern_invalid_users.findall(raw_data)
            #if ( len(pi) == 1 ):
            #    num_users -= int(pi[0])

            # number of submitted keys
            ps = pattern_num_subm.findall(raw_data)
            if (len(ps) > 0):
                for line in ps:
                    if (len(line) == 2):
                        num_subbmited_keys += int(line[0]) * int(line[1])

        sum_keys += num_keys
        sum_users += num_users
        sum_subbmited_keys += num_subbmited_keys

        date_list.append([timestamp, num_keys, num_users, num_subbmited_keys, sum_keys, sum_users, sum_subbmited_keys])

    # add TRL sums
    trl_data.append([0, trl_sum_data])

    ###########################################################################
    # PART 3: generate CSV and JSON files
    ###########################################################################

    # Temporary Exposure Keys (TEKs)

    # generate csv
    str_csv = "#timestamp, num_keys, num_users_submitted_keys, num_submitted_keys, sum_keys, sum_users_submitted_keys, sum_submitted_keys\n"
    for line in date_list:
        str_csv += "{},{},{},{},{},{},{}\n".format(line[0], line[1], line[2], line[3], line[4], line[5], line[6])

    # write csv to disk
    with open(DKS_CSV_FILE, 'w') as f:
        f.write(str_csv)
        f.close()

    # write json to disk
    with open(DKS_JSON_FILE, 'w') as f:
        f.write(json.dumps(date_list, sort_keys=True))
        f.close()

    # Transmission Risk Levels (TRLs)

    # generate csv
    str_trl_csv = "#timestamp, num_TRL_1, num_TRL_2, num_TRL_3, num_TRL_4, num_TRL_5, num_TRL_6, num_TRL_7, num_TRL_8\n"
    for timestamp, data in trl_data:
        str_trl_csv += "{},{},{},{},{},{},{},{},{}\n".format(timestamp, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

    # write csv to disk
    with open(TRL_CSV_FILE, 'w') as f:
        f.write(str_trl_csv)
        f.close()

    # write json to disk
    with open(TRL_JSON_FILE, 'w') as f:
        f.write(json.dumps(trl_data, sort_keys=True))
        f.close()



        #    datastore_filename = "%s.json" % exposurekeyset
        #    datastore_file = os.path.join(datastore_today, datastore_filename)
        #    print("INFO: writing to datastore '{}'.. ".format(datastore_filename), end='')
        #    write_json(datastore_file, json_obj)
        #    print("OK")

        #    data = {}
        #    data['environment'] = manifest_environment
        #    print("INFO: writing to django ({}).. ".format(data['environment']), end='')
        #    #print(json.dumps(json_obj, indent=4))
        #    data['key'] = exposurekeyset
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
        #    data['no_teks'] = len(json_obj['diagnosisKeys'])
        #    #data['no_users'] = 1

        #    teks = json_obj['diagnosisKeys']
        #    no_teks = data['no_teks']

        #    if create_eks(Eks, data):
        #        print("OK")

        #        tekcounter = 0
        #        for tek in teks:
        #            tekcounter += 1
        #            tek_key = tek['TemporaryExposureKey']
        #            tek_transmissionrisklevel = tek['transmissionRiskLevel']
        #            tek_validity = tek['validity']
        #            print("INFO: {}/{} tek '{}'.. ".format(tekcounter, no_teks, tek_key), end='')
        #            tekdata = {}
        #            tekdata['key'] = tek_key
        #            tekdata['transmissionrisklevel'] = tek_transmissionrisklevel
        #            tekdata['rollingstartintervalnumber'] = tek_validity['rollingStartIntervalNumber']
        #            tekdata['rollingperiod'] = tek_validity['rollingPeriod']
        #            tekdata['validitystart'] = tek_validity['start']
        #            tekdata['validityend'] = tek_validity['end']
#
#                    if create_tek(Tek, tekdata, exposurekeyset):
#                        print("OK")
#                    else:
#                        print("not created")

         #   else:
         #       print("not created")

            # clean up
            #if os.path.isfile(fn_analysis):
            #    os.remove(fn_analysis)
            #manifestzip = os.path.join(datastore_today, 'manifest.zip')
            #if os.path.isfile(manifestzip):
            #    os.remove(manifestzip)
            #ekszip = os.path.join(datastore_today, 'eks.zip')
            #if os.path.isfile(ekszip):
            #    os.remove(ekszip)
            #contentbin = os.path.join(datastore_today, 'content.bin')
            #if os.path.isfile(contentbin):
            #    os.remove(contentbin)
            #contentsig = os.path.join(datastore_today, 'content.sig')
            #if os.path.isfile(contentsig):
            #    os.remove(contentsig)
