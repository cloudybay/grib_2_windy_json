import os
import sys
import json
import pygrib


class PrettyFloat(float):
    def __repr__(self):
        return '%.15g' % round(float(self), 2)


if __name__ == "__main__":
    # grbs = pygrib.open("gfs.t06z.pgrb2.1p00.f003")
    # grbs = pygrib.open("interim_2014-07-01to2014-07-31_00061218.grib")


    grbs = pygrib.open("gfs.t06z.pgrb2.1p00.f009")
    """
    latitudeOfFirstGridPoint=-90000000
    longitudeOfFirstGridPoint=0
    """

    outout = []
    for grb in grbs:
        for key in grb.keys():
            p = key.lower()
            if "time" in p or "date" in p:
                try:
                    print("%s=%s" %(key, grb[key]), type(grb[key]))
                except:
                    pass
        print("%s%04d" % (grb['dataDate'], grb['dataTime']))
        break

        # if grb['GRIBEditionNumber'] == 2 and grb['parameterCategory'] == 2:
        #     print(">>>>>>", grb['parameterName'])
        #     print(">>>>>>", grb['parameterNumber'])
        #     print(">>>", grb['parameterUnits'])
        #     print(">>>", grb["typeOfLevel"], grb['level'])
        #     print(">>>", grb['latitudeOfFirstGridPoint'])


        header = {}
        data = [[], []]
        if grb['GRIBEditionNumber'] == 2 and grb['parameterCategory'] == 2 and grb['level'] == 1000:
            la1, lo1, la2, lo2, dy, dx = grb['g2grid']

            header['lo1'] = lo1
            header['lo2'] = lo2

            # CWB
            header['la1'] = grb['latitudeOfFirstGridPoint']
            header['la2'] = grb['latitudeOfLastGridPoint']

            # NOAA
            header['la1'] = la1
            header['la2'] = la2

            header['dx'] = dx
            header['dy'] = dy
            header['nx'] = grb['Ni']
            header['ny'] = grb['Nj']
            header['refTime'] = grb['forecastTime']

        elif "U wind" in grb['parameterName']:
            lats, lons = grb.latlons()
            header['lo1'] = lons.min()
            header['lo2'] = lons.max()
            header['la1'] = lats.max()
            header['la2'] = lats.min()
            header['dx'] = float(lons.max() - lons.min() + 1) / grb['Ni']
            header['dy'] = float(lats.max() - lats.min() + 1) / grb['Nj']
            header['nx'] = grb['Ni']
            header['ny'] = grb['Nj']
            header['refTime'] = grb['forecastTime']
            for vs in grb.values:
                for v in vs:
                    data[0].append(PrettyFloat(v))

        elif "V wind" in grb['parameterName']:
            for vs in grb.values:
                for v in vs:
                    data[1].append(PrettyFloat(v))
        else:
            continue

        outout.append({"header":header, "data": data})

        """
        dataDate,
        dataTime,
        forecastTime,
        validityDate,
        validityTime,
        """


    with open("cwb.json", "w") as ff:
        json.dump(outout, ff, separators=(',', ':'))
