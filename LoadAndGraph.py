#!/usr/bin/env python
# encoding: utf-8
'''

'''

import sys
import os

from argparse import ArgumentParser
from argparse import ArgumentTypeError
from areexsupport.sensor import sensor
from areexsupport.sensors import sensors
from plotly.offline import plot
import shutil
import logging
import pickle


def main(argv=None):
    logging.basicConfig(level=logging.INFO)

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    def validateOutput(istring):
        if os.path.isfile(istring):
            raise ArgumentTypeError(
                '{} is a file. This should be a folder or not exists'.format(istring))
        if os.path.islink(istring):
            raise ArgumentTypeError(
                '{} is a link. This should be a folder or not exists'.format(istring))
        return istring

    def validateInput(istring):
        if not os.path.isfile(istring):
            raise ArgumentTypeError('{} is not a file'.format(istring))
        return istring

    parser = ArgumentParser()
    parser.add_argument(
        dest="input", help="path to file with data", type=validateInput)
    parser.add_argument(
        dest="output", help="path to the output folder", type=validateOutput)
    parser.add_argument('--5min', '-5', dest="by5min",
                        action='store_true', help="aggregate value by 5min")
    parser.add_argument('--verbose', '-v', dest="verbose",
                        action='store_true', help="generate everything")
    parser.add_argument('--details', '-d', dest="detail",
                        action='store_true', help="generate detailled charts (-v also generate -d)")
    parser.add_argument('--meta', '-m', dest="meta",
                        action='store_true', help="generate chart by metasensor (-v also generate -m)")
    parser.add_argument('--global', '-g', dest="globalc",
                        action='store_true', help="generate global chart (-v also generate -g)")
    parser.add_argument('--ext-vs-int', dest="extvsint",
                        action='store_true', help="generate external vs internal (-v also generate -ext-vs-int)")
    arg = parser.parse_args()

    if not os.path.isdir(arg.output):
        os.mkdir(arg.output)
    else:
        shutil.rmtree(arg.output, ignore_errors=True)
        shutil.rmtree(arg.output, ignore_errors=True)
        os.mkdir(arg.output)

    cachename = arg.input + ".cache"
    if os.path.isfile(cachename) and os.path.getmtime(cachename) > os.path.getmtime(arg.input):
        print('Valid data cache found ; Will be used')
        of = open(cachename, "rb")
        try:
            data = pickle.load(of)
        finally:
            of.close()

    else:
        mergeFunction = sensor.dateTimeTo5Minute(
        ) if arg.by5min else sensor.dateTimeToMinute()

        def groupFunction(
            n): return 'Extérieur' if n == 'Extérieur' else 'Intérieur'

        def metaFunction(sensorsmap):
            meta = {}
            for n, s in sensorsmap.items():
                target = n
                if ' - T' in n:
                    target = n.replace(' - T', '')
                elif ' - V' in n:
                    target = n.replace(' - V', '')
                if ' - RH' in n:
                    target = n.replace(' - RH', '')
                if target not in meta:
                    meta[target] = {}
                meta[target][n] = s
            return meta
        print('Reading from {}'.format(arg.input))
        data = sensors(arg.input, mergeFunction, groupFunction,
                       metaFunction, sensor.sensorIsUnit('V'))
        print('Storing to cache {}'.format(cachename))
        of = open(cachename, "wb")
        pickle.dump(data, of)
        of.close()

    print('Datas are :\n{}'.format(data))

    if arg.verbose or arg.globalc:
        # All temp
        output = os.path.join(arg.output, 'Toutes les températures.html')
        print('Writing to {}'.format(output))
        plot(data.toFigure(
            sensor.sensorIsUnitAndClazz('°C', 'Sensor'), '°C', 'Toutes les températures'), filename=output, auto_open=False)
    
        # All rh
        output = os.path.join(arg.output, 'Toutes les humidités.html')
        print('Writing to {}'.format(output))
        plot(data.toFigure(
            sensor.sensorIsUnitAndClazz('RH%', 'Sensor'), '°C', 'Toutes les humidités'), filename=output, auto_open=False)
    
        # All temp
        output = os.path.join(
            arg.output, 'Toutes les températures - Baseline.html')
        print('Writing to {}'.format(output))
        plot(data.toFigure(
            sensor.sensorIsUnitAndClazz('°C', 'Sensor->Baseline'), '°C', 'Toutes les températures - Baseline'), filename=output, auto_open=False)
    
        # All rh
        output = os.path.join(arg.output, 'Toutes les humidité - Baselines.html')
        print('Writing to {}'.format(output))
        plot(data.toFigure(
            sensor.sensorIsUnitAndClazz('RH%', 'Sensor->Baseline'), '°C', 'Toutes les humidités - Baseline'), filename=output, auto_open=False)

    if arg.verbose or arg.extvsint:
        # Interieur vs exterieur
        external = data['Extérieur'].asScatter()
        internalt = data['Intérieur - Sensor [°C] / Mean'].asScatter(
            name='Température intérieur', minSensor=data['Intérieur - Sensor [°C] / Min'], maxSensor=data['Intérieur - Sensor [°C] / Max'])
        internalrh = data['Intérieur - Sensor [RH%] / Mean'].asScatter(
            name='Humidité intérieur', minSensor=data['Intérieur - Sensor [RH%] / Min'], maxSensor=data['Intérieur - Sensor [RH%] / Max'], yaxis='y2')
        output = os.path.join(
            arg.output, 'Comparaison intérieur vs extérieur.html')
        print('Writing to {}'.format(output))
        plot(sensors.scattersToFigure(
            [external, internalt, internalrh], '°C', 'Intérieur vs Extérieur', 'RH%'), filename=output, auto_open=False)

    if arg.verbose or arg.meta:
        # Generate one file per meta sensor with/without baseline
        for name, lst in data.metassensors:
            folder = os.path.join(arg.output, name.translate(
                str.maketrans('/:\\', '---')))
            if not os.path.isdir(folder):
                os.mkdir(folder)
    
            output = os.path.join(folder, 'mesures.html')
            fig = data.toFigure(
                lambda s: s.name in lst and s.clazz == 'Sensor', '°C', name, '%RH', lambda s: 'y' if s.unit == '°C' else 'y2')
            if len(fig['data']) > 0:
                print('Writing to {}'.format(output))
                plot(fig, filename=output, auto_open=False)
    
            output = os.path.join(folder, 'baselines.html')
            fig = data.toFigure(
                lambda s: s.name in lst and s.clazz == 'Sensor->Baseline', '°C', name + "- Baselines", '%RH', lambda s: 'y' if s.unit == '°C' else 'y2')
            if len(fig['data']) > 0:
                print('Writing to {}'.format(output))
                plot(fig, filename=output, auto_open=False)
    
            output = os.path.join(folder, 'mesures et baselines.html')
            fig = data.toFigure(
                lambda s: s.name in lst and s.clazz in ('Sensor', 'Sensor->Baseline'), '°C', name + "- Mesures et Baselines", '%RH', lambda s: 'y' if s.unit == '°C' else 'y2')
            if len(fig['data']) > 0:
                print('Writing to {}'.format(output))
                plot(fig, filename=output, auto_open=False)
    
            output = os.path.join(folder, 'tous.html')
            fig = data.toFigure(
                lambda s: s.name in lst, '°C', name + "- Tous", '%RH', lambda s: 'y' if s.unit == '°C' else 'y2')
            if len(fig['data']) > 0:
                print('Writing to {}'.format(output))
                plot(fig, filename=output, auto_open=False)
            
    if arg.verbose or arg.detail:
        # Generate one file per sensor
        os.mkdir(os.path.join(arg.output, 'details'))
        for name, s in data.items():
            output = os.path.join(arg.output, 'details', name.translate(
                str.maketrans('/:\\', '---')) + ".html")
            print('Writing to {}'.format(output))
            plot(sensors.sensorToFigure(s, s.name),
                 filename=output, auto_open=False)

if __name__ == "__main__":
    sys.exit(main())
