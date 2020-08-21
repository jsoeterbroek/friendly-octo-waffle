#!/usr/bin/env python3
# fetch_parse_keys.py

import os
import sys
import json
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

def run():
    if manifest_environment:
        basedir = os.path.abspath(os.path.dirname(__file__))
        datastore = os.path.join(basedir, 'datastore')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'joosts-check/2.00',
        }

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
            zname = os.path.join(datastore, 'manifest.zip')
            zfile = open(zname, 'wb')
            zfile.write(r.content)
            print("OK")
            zfile.close()

        if zname:
            with ZipFile(zname, 'r') as zipObj:
                zipObj.extractall(datastore)

        json_obj_file = os.path.join(datastore, 'content.bin')
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
        datastore_file = os.path.join(datastore, datastore_filename)
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
                zname = os.path.join(datastore, 'eks.zip')
                zfile = open(zname, 'wb')
                zfile.write(r.content)
                print("OK")
                zfile.close()

            fn_analysis = os.path.join(datastore, 'eks.json')
            if not os.path.isfile(fn_analysis):
                os.system("scripts/diagnosis-keys/parse_keys_json.py -l -d {} > {}".format(zname, fn_analysis))
            #anonymize_TEKs(fn_analysis)
            with open(fn_analysis) as json_file:
                json_obj = json.load(json_file)

            datastore_filename = "%s.json" % exposurekeyset
            datastore_file = os.path.join(datastore, datastore_filename)
            print("INFO: writing to datastore '{}'.. ".format(datastore_filename), end='')
            write_json(datastore_file, json_obj)
            print("OK")

            data = {}
            data['environment'] = manifest_environment
            print("INFO: writing to django ({}).. ".format(data['environment']), end='')
            #print(json.dumps(json_obj, indent=4))
            data['key'] = exposurekeyset
            data['timewindow_start_timestamp'] = json_obj['timeWindowStart']
            data['timewindow_end_timestamp'] = json_obj['timeWindowEnd']
            data['region'] = json_obj['region']
            data['batch_num'] = json_obj['batchNum']
            data['batch_size'] = json_obj['batchCount']
            #data['app_bundle_id'] =
            data['verification_key_version'] = json_obj['signatureInfos']['verification_key_version']
            data['verification_key_id'] = json_obj['signatureInfos']['verification_key_id']
            data['signature_algorithm'] = json_obj['signatureInfos']['signature_algorithm']
            #data['padding_multiplier'] = 5
            data['no_teks'] = len(json_obj['diagnosisKeys'])
            #data['no_users'] = 1

            teks = json_obj['diagnosisKeys']
            no_teks = data['no_teks']

            if create_eks(Eks, data):
                print("OK")

                tekcounter = 0
                for tek in teks:
                    tekcounter += 1
                    tek_key = tek['TemporaryExposureKey']
                    tek_transmissionrisklevel = tek['transmissionRiskLevel']
                    tek_validity = tek['validity']
                    print("INFO: {}/{} tek '{}'.. ".format(tekcounter, no_teks, tek_key), end='')
                    tekdata = {}
                    tekdata['key'] = tek_key
                    tekdata['transmissionrisklevel'] = tek_transmissionrisklevel
                    tekdata['rollingstartintervalnumber'] = tek_validity['rollingStartIntervalNumber']
                    tekdata['rollingperiod'] = tek_validity['rollingPeriod']
                    tekdata['validitystart'] = tek_validity['start']
                    tekdata['validityend'] = tek_validity['end']

                    if create_tek(Tek, tekdata, exposurekeyset):
                        print("OK")
                    else:
                        print("not created")

            else:
                print("not created")

            # clean up
            if os.path.isfile(fn_analysis):
                os.remove(fn_analysis)
            manifestzip = os.path.join(datastore, 'manifest.zip')
            if os.path.isfile(manifestzip):
                os.remove(manifestzip)
            ekszip = os.path.join(datastore, 'eks.zip')
            if os.path.isfile(ekszip):
                os.remove(ekszip)
            contentbin = os.path.join(datastore, 'content.bin')
            if os.path.isfile(contentbin):
                os.remove(contentbin)
            contentsig = os.path.join(datastore, 'content.sig')
            if os.path.isfile(contentsig):
                os.remove(contentsig)
    else:
        print("ERR: please provide environment")
