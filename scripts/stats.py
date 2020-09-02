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
#import numpy as np
#import matplotlib.pyplot as plt
import plotly.graph_objects as go
#import plotly.io as pio

from django.db import IntegrityError
#from django.conf import settings
from django.forms.models import model_to_dict
#from sqlalchemy import create_engine
from keys.models import Keys
from stats.models import Stats, KeysetFreq

def write_json(path, json_data):
    with open(path, 'w') as file_out:
        json.dump(json_data, file_out)

def read_json(path):
    with open(path) as file_in:
        return json.load(file_in)

def get_all_keysets():

    keysets = Keys.objects.all()
    return keysets

def queryset_to_list(qs, fields=None, exclude=None):
    my_array = []
    for x in qs:
        my_array.append(model_to_dict(x, fields=fields, exclude=exclude))

    return my_array

def save_stats(dictionary):
    obj = Stats()
    # set regular fields
    for field, value in dictionary.items():
        if not isinstance(value, list):
            setattr(obj, field, value)
    try:
        obj.save()
    except IntegrityError as e:
        print("Error saving obj {}".format(e))
        return False
    return True

def save_keysetfreq(dictionary):
    obj = KeysetFreq()
    # set regular fields
    datestring = dictionary['datestring']
    #freq = dictionary['freq']
    try:
        obj = KeysetFreq.objects.get(datestring=datestring)
        for field, value in dictionary.items():
            if not isinstance(value, list):
                setattr(obj, field, value)
        obj.save()
    except KeysetFreq.DoesNotExist:
        for field, value in dictionary.items():
            if not isinstance(value, list):
                setattr(obj, field, value)
        obj.save()
    except IntegrityError as e:
        print("Error saving obj {}".format(e))
        return False
    return True

def exists_keysetfreq(keyset_freq_dict):

    ret = False
    datestring = keyset_freq_dict['datestring']
    freq = keyset_freq_dict['freq']
    try:
        ksf = KeysetFreq.objects.get(datestring=datestring)
        if ksf.freq == freq:
            ret = True
    except:
        ret = False

    return ret

def create_fig_keyset_freq_date(_seen_freq_dict, _datastore):
    _timestamp_date = '{:%d-%m-%Y %H:%M}'.format(datetime.now())
    #png_renderer = pio.renderers["png"]
    width = 450
    height = 250

    #pio.renderers.default = "png"

    # keyset freq by date to plotly
    x_dates = []
    y_freqs = []
    for k, v in _seen_freq_dict.items():
        x_dates.append(k)
        y_freqs.append(v)

    fig = go.Figure([go.Bar(x=x_dates, y=y_freqs)])
    #fig = go.Figure([go.Bar(x=x_dates, y=y_freqs, text='y_freqs')])
    #fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    annotations = []
    # Title
    datumtext = "Bron: CoronaMelder backend API ({})".format(_timestamp_date)
    annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                            xanchor='left', yanchor='bottom',
                            text='Aantal keysets/datum',
                            font=dict(family='Arial', size=24, color='rgb(37,37,37)'),
                            showarrow=False))
    # Source
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.3,
                            xanchor='center', yanchor='top',
                            text=datumtext,
                            font=dict(family='Arial', size=10, color='rgb(150,150,150)'),
                            showarrow=False))

    # margins
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=22),
    )
    fig.update_layout(annotations=annotations)

    fig.to_image(format="png", engine="kaleido")
    keyset_freq_date_fig_filename = "keyset_freq_date.png"
    datastore_filename = os.path.join(_datastore, keyset_freq_date_fig_filename)
    print("INFO: writing keyset frequency by date fig to datastore .. ", end='')
    fig.write_image(datastore_filename, width=width, height=height)
    print("OK")
    datastore_filename = os.path.join('stats/static', keyset_freq_date_fig_filename)
    print("INFO: writing keyset frequency by date fig to static dir .. ", end='')
    fig.write_image(datastore_filename, width=width, height=height)
    print("OK")

    #fig.show()

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
    ksdf = pd.DataFrame(keysets_list, columns=['key', 'shortkey', 'environment', 'seen', 'start_timestamp', 'end_timestamp', 'num_teks'])
    #df['seen'] = pd.to_datetime(df['seen'], format='%Y-%m-%d')
    ksdf['start_timestamp'] = pd.to_datetime(ksdf['start_timestamp'], format='%Y-%m-%d %H:%M:%S')
    ksdf['end_timestamp'] = pd.to_datetime(ksdf['end_timestamp'], format='%Y-%m-%d %H:%M:%S')
    #df = df.set_index('key')
    ksdf = ksdf.set_index('seen')
    seen = ksdf['shortkey']
    #seen.index = pd.to_datetime(seen.index)
    seen.index = pd.to_datetime(seen.index, format='%Y-%m-%d')
    seen_freq = seen.resample('D').count()
    seen_freq_pdict = seen_freq.to_dict()

    seen_freq_dict = {}
    for k, v in seen_freq_pdict.items():
        datestring = k.strftime('%Y-%m-%d')
        seen_freq_dict[datestring] = v

    #print(seen_freq_dict)

    # keyset freq by date to datastore jsonfile
    keyset_freq_date_json = json.dumps(seen_freq_dict)
    keyset_freq_date_filename = "keyset_freq_date.json"
    datastore_filename = os.path.join(datastore, keyset_freq_date_filename)
    print("INFO: writing keyset frequency by date to datastore .. ", end='')
    write_json(datastore_filename, keyset_freq_date_json)
    print("OK")

    # keyset freq by date to database
    print("INFO: writing keyset frequency by date to database .. ", end='')
    for k, v in seen_freq_pdict.items():
        keyset_freq_dict = {}
        keyset_freq_dict['datestring'] = k
        keyset_freq_dict['freq'] = v

        if exists_keysetfreq(keyset_freq_dict):
            RES = "SKIP"
        else:
            if save_keysetfreq(keyset_freq_dict):
                print(".", end='')
                RES = "OK"
            else:
                print("ERR")
    print(RES)

    create_fig_keyset_freq_date(seen_freq_dict, datastore)


    # keysets
    keysets_total = len(keysets_list)

    # TRL
    trl_daily_dist = 150

    #trl_sum_data = {'timestamp_date': timestamp_date, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}
    # write to datastore
    #print("INFO: saving stats sum TRL for keyset {} to datastore'.. ".format(eks), end='')
    #with open(sum_trl_json_file, 'w') as f:
    #    f.write(json.dumps(trl_sum_data, sort_keys=True, indent=4))
    #    f.close()
    #print("OK")


    # teks

    # start_timestamp
    start_timestamp_value_counts_series = ksdf.start_timestamp.dt.date.value_counts()
    start_timestamp_value_counts_series.sort_index(inplace=True)
    start_timestamp_value_counts_json = start_timestamp_value_counts_series.to_json(orient="table")

    start_timestamp_value_counts_filename = "start_timestamp_value_counts.json"
    datastore_filename = os.path.join(datastore_today, start_timestamp_value_counts_filename)
    if not os.path.isfile(datastore_filename):
        print("INFO: writing timestamp value counts to datastore '{}'.. ".format(datastore_filename), end='')
        write_json(datastore_filename, start_timestamp_value_counts_json)
        print("OK")

    print("INFO: writing stats to database .. ", end='')
    stats_data = {}
    stats_data['name'] = 'stats'
    stats_data['keysets_total'] = keysets_total
    stats_data['teks_keyset_mean'] = 150
    stats_data['trl_daily_dist'] = trl_daily_dist
    if save_stats(stats_data):
        print("OK")
    else:
        print("ERR")

    print("total_keysets: {}".format(keysets_total))
    #print("mean teks per keyset: {}".format(teks_keyset_mean))
    #for i in keysets_list:
    #    print(i)
