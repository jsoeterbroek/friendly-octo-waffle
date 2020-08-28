#!/usr/bin/env python3
# fetch_parse_keys.py

import os
#import sys
import json
#from django.core.serializers.json import DjangoJSONEncoder
import re
from datetime import datetime
#from zipfile import ZipFile
#import requests
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn

#seaborn.set()

from django.db import IntegrityError
#from django.conf import settings
from django.forms.models import model_to_dict
#from sqlalchemy import create_engine
from keys.models import Keys, Trl
from stats.models import Stats

#manifest_environment = 'productie'
#manifest_environment = 'test'

#user = settings.DATABASES['default']['USER']
#password = settings.DATABASES['default']['PASSWORD']
#database_name = settings.DATABASES['default']['NAME']
#database_url = "sqlite:///%s" % (database_name)

def write_json(path, json_data):
    with open(path, 'w') as file_out:
        json.dump(json_data, file_out)

def read_json(path):
    with open(path) as file_in:
        return json.load(file_in)

#def shorten_exposurekeyset(exposurekeyset):
#
#    _eks = exposurekeyset[0:8]
#    return _eks

def get_all_keysets():

    keysets = Keys.objects.all()
    return keysets

def queryset_to_list(qs, fields=None, exclude=None):
    my_array = []
    for x in qs:
        my_array.append(model_to_dict(x, fields=fields, exclude=exclude))

    return my_array

#class MyEncoder(json.JSONEncoder):
#    def default(self, obj):  # pylint: disable=arguments-differ, method-hidden
#        if isinstance(obj, ndarray):
#            return obj.tolist()
#        return json.JSONEncoder.default(self, obj)

def save_stats(dictionary):
    obj = Stats()
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


def run():

    # timestamps and dates
    timestamp_date = '{:%Y-%m-%d}'.format(datetime.now())

    basedir = os.path.abspath(os.path.dirname(__file__))
    datastore = os.path.join(basedir, '..', 'datastore')
    datastore_today = os.path.join(datastore, timestamp_date)

    if not os.path.exists(datastore_today):
        print("INFO: creating dir {}'.. ".format(datastore_today))
        os.makedirs(datastore_today)

    print("INFO: running stats on {}'.. ".format(timestamp_date))

    keysets_queryset = get_all_keysets()
    keysets_list = queryset_to_list(keysets_queryset)


    # remove timezone from timestamps
    for key in keysets_list:
        if 'CEST' in key['start_timestamp']:
            key['start_timestamp'] = re.sub(' CEST$', '', key['start_timestamp'])
        if 'CEST' in key['end_timestamp']:
            key['end_timestamp'] = re.sub(' CEST$', '', key['end_timestamp'])

    #print(keysets_list)
    df = pd.DataFrame(keysets_list, columns=['key', 'shortkey', 'environment', 'seen', 'start_timestamp', 'end_timestamp', 'num_teks'])
    df['seen'] = pd.to_datetime(df['seen'], format='%Y-%m-%d')
    df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='%Y-%m-%d %H:%M:%S')
    df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='%Y-%m-%d %H:%M:%S')
    df = df.set_index('key')
    del df['environment']

    # keysets
    keysets_total = len(keysets_list)

    # TRL
    trl_daily_dist = 1

    # teks
    teks_keyset_total = df['num_teks']
    teks_keyset_mean = int(teks_keyset_total.mean())

    # start_timestamp
    start_timestamp_value_counts_series = df.start_timestamp.dt.date.value_counts()
    start_timestamp_value_counts_series.sort_index(inplace=True)
    start_timestamp_value_counts_json = start_timestamp_value_counts_series.to_json(orient="table")

    start_timestamp_value_counts_filename = "start_timestamp_value_counts.json"
    datastore_filename = os.path.join(datastore_today, start_timestamp_value_counts_filename)

    print("INFO: writing to datastore '{}'.. ".format(datastore_filename), end='')
    write_json(datastore_filename, start_timestamp_value_counts_json)
    print("OK")

    print("INFO: writing stats to database .. ", end='')
    #sql_engine = create_engine(database_url, echo=False)
    #conn = sql_engine.raw_connection()
    #df.to_sql(PandasKeys, conn, if_exists='append')

    stats_data = {}
    stats_data['name'] = 'stats'
    stats_data['keysets_total'] = keysets_total
    stats_data['teks_keyset_mean'] = teks_keyset_mean
    stats_data['trl_daily_dist'] = trl_daily_dist
    if save_stats(stats_data):
        print("OK")
    else:
        print("ERR")

    print("total_keysets: {}".format(keysets_total))
    print("mean teks per keyset: {}".format(teks_keyset_mean))
    #for i in keysets_list:
    #    print(i)
