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
#import seaborn
import plotly.graph_objects as go
#seaborn.set()

from django.db import IntegrityError
#from django.conf import settings
from django.forms.models import model_to_dict
#from sqlalchemy import create_engine
from keys.models import Keys
from stats.models import Stats, KeysetFreq

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
        print("Error saving obj {}".format(e))
        return False
    return True

def save_keysetfreq(dictionary):
    obj = KeysetFreq()
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

def exists_keysetfreq(keyset_freq_dict):

    datestring = keyset_freq_dict['datestring']
    freq = keyset_freq_dict['freq']
    try:
        ksf = KeysetFreq.objects.get(datestring=datestring)
        if ksf.freq == freq:
            ret = True
    except:
        ret = False

    return ret

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

    # keyset freq by date to plotly
    x_dates = []
    y_freqs = []
    #title = 'Main Source for News'
    colors = 'rgb(67,67,67)'
    #mode_size = 10
    line_size = 3
    for k, v in seen_freq_dict.items():
        x_dates.append(k)
        y_freqs.append(v)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_dates, y=y_freqs,
                             mode='lines',
                             line=dict(color=colors, width=line_size),
                             name='Keyset Frequentie/datum'))
    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(67,67,67)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=False,
        plot_bgcolor='white'
    )
    annotations = []
    # Title
    annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                            xanchor='left', yanchor='bottom',
                            text='Aantal keysets/datum',
                            font=dict(family='Arial', size=30, color='rgb(37,37,37)'),
                            showarrow=False))
    # Source
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1,
                            xanchor='center', yanchor='top',
                            text='Bron: CoronaMelder backend API (datum hier)',
                            font=dict(family='Arial', size=12, color='rgb(150,150,150)'),
                            showarrow=False))

    fig.update_traces(mode='lines+markers')
    fig.update_layout(annotations=annotations)
    fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16))

    fig.to_image(format="svg", engine="kaleido")
    keyset_freq_date_svg_filename = "keyset_freq_date.svg"
    datastore_filename = os.path.join(datastore, keyset_freq_date_svg_filename)
    print("INFO: writing keyset frequency by date svg to datastore .. ", end='')
    fig.write_image(datastore_filename)
    print("OK")
    datastore_filename = os.path.join('stats/static', keyset_freq_date_svg_filename)
    print("INFO: writing keyset frequency by date svg to static dir .. ", end='')
    fig.write_image(datastore_filename)
    print("OK")
    #fig.show()

    # keysets
    keysets_total = len(keysets_list)

    # TRL
    trl_daily_dist = 1

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
