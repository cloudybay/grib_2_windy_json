import os
import sys
import json
import pygrib
import click


class PrettyFloat(float):
    def __repr__(self):
        return '%.15g' % self

def wrap_value(v):
    # return PrettyFloat(round(float(v), 2))
    return round(float(v))


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--source_file', '-s', required=True, is_flag=False, help="Source file to convert")
@click.option('--output_path', '-p', required=True, is_flag=False, help="Path to save json file")
def main(source_file, output_path):
    grbs = pygrib.open(source_file)

    header = {}
    data = [[], []]
    for grb in grbs:
        if grb['parameterCategory'] == 2 and grb['parameterNumber'] == 2 and grb['level'] == 10:
            la1, lo1, la2, lo2, dy, dx = grb['g2grid']

            header['lo1'] = lo1
            header['lo2'] = lo2

            header['la1'] = la1
            header['la2'] = la2

            header['dx'] = dx
            header['dy'] = dy
            header['nx'] = grb['Ni']
            header['ny'] = grb['Nj']
            header['refTime'] = "%s%04d" % (grb['validityDate'], grb['validityTime'])

            for vs in grb.values:
                for v in vs:
                    data[0].append(wrap_value(v))

        elif grb['parameterCategory'] == 2 and grb['parameterNumber'] == 3 and grb['level'] == 10:
            for vs in grb.values:
                for v in vs:
                    data[1].append(wrap_value(v))

    base_name = os.path.basename(source_file)
    if base_name.endswith(".grib2"):
        base_name = base_name[:-6]
    with open(os.path.join(output_path, base_name + ".json"), "w") as ff:
        json.dump({"header":header, "data": data}, ff, separators=(',', ':'))


if __name__ == "__main__":
    main()
