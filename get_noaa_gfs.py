# -*- coding:utf-8 -*-

import os, sys
import requests
from datetime import datetime, timedelta
import click


from subprocess import call
import subprocess


NOAA_URL = 'http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl'
DAY_LIMIT = 10
TAU_RES = 3
TAU_MAX = 336 # 14 days
FCST_FEG = 6


def pick_fcst_time(init_time):
    wind_time = init_time - timedelta(hours=(init_time.hour%6))
    return wind_time


def _get_noaa_raw_data(query_wind_time, output_path, tau=0):
    query_wind_time_str = query_wind_time.strftime('%Y%m%d%H')
    query_wind_time_hour_str = query_wind_time.strftime('%H')

    file_name = 'gfs.t'+ query_wind_time_hour_str +'z.pgrb2.1p00.f' + str(tau).zfill(3)

    options = {
        'file': file_name,
        'lev_10_m_above_ground': 'on',
        'lev_surface': 'on',
        'var_TMP': 'off',
        'var_UGRD': 'on',
        'var_VGRD': 'on',
        'leftlon': 0,
        'rightlon': 360,
        'toplat': -90,
        'bottomlat': 90,
        'dir': '/gfs.'+ query_wind_time_str
    }

    download_content = requests.get(NOAA_URL, params=options)

    if download_content.ok:
        with open(os.path.join(output_path, "noaa_%s_%03d.grib2"%(query_wind_time_str, tau)), 'wb') as fd:
            fd.write(download_content.content)
        return True
    else:
        pass
    return False


def get_noaa_raw_data(query_init_time, output_path, init_time_offset=0):

    _query_init_time = query_init_time - timedelta(hours=init_time_offset)

    if abs((query_init_time - datetime.utcnow()).days > DAY_LIMIT):
        return

    if _get_noaa_raw_data(query_init_time, output_path):
        taus = range(TAU_RES, (TAU_MAX+1), TAU_RES)
        for tau in taus:
            _get_noaa_raw_data(query_init_time, output_path, tau)
    else:
        get_noaa_raw_data(_query_init_time, output_path, FCST_FEG)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--init_time', '-d', is_flag=False, help="Init time to download (%Y%m%d%H%M)")
@click.option('--output_path', '-p', required=True, is_flag=False, help="Path to save download file")
def main(init_time, output_path):
    if init_time:
        init_time = datetime.strptime(init_time, "%Y%m%d%H%M")
    else:
        init_time = datetime.utcnow()

    get_noaa_raw_data(pick_fcst_time(init_time), output_path)


if __name__ == "__main__":
    main()
