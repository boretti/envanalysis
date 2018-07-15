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
from concurrent.futures.thread import ThreadPoolExecutor

logger = logging.getLogger(__name__)


def main(argv=None):
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - [%(threadName)s] [%(module)s] [%(filename)s]>[%(funcName)s]@%(lineno)d - %(message)s', level=logging.INFO)

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
    parser.add_argument('--remove-cache', '-rc', dest="removecache",
                        action='store_true', help="Force remove cache before run")
    parser.add_argument('--5min', '-5', dest="by5min",
                        action='store_true', help="aggregate value by 5min")
    parser.add_argument('--verbose', '-v', dest="verbose",
                        action='store_true', help="generate everything")
    parser.add_argument('--prune', '-p', dest="prune",
                        action='store_true', help="prune chart")
    parser.add_argument('--details', '-d', dest="detail",
                        action='store_true', help="generate detailled charts (-v also generate -d)")
    parser.add_argument('--meta', '-m', dest="meta",
                        action='store_true', help="generate chart by metasensor (-v also generate -m)")
    parser.add_argument('--global', '-g', dest="globalc",
                        action='store_true', help="generate global chart (-v also generate -g)")
    parser.add_argument('--ext-vs-int', dest="extvsint",
                        action='store_true', help="generate external vs internal (-v also generate -ext-vs-int)")
    parser.add_argument("--threadcount", "-tc", dest="tc", type=int, default=4,
                        help="specify thread number")
    arg = parser.parse_args()

    if not os.path.isdir(arg.output):
        os.mkdir(arg.output)
    else:
        shutil.rmtree(arg.output, ignore_errors=True)
        shutil.rmtree(arg.output, ignore_errors=True)
        os.mkdir(arg.output)

    cachename = arg.input + ".cache"
    if arg.removecache and os.path.isfile(cachename):
        logger.info('Forced remove of the cache')
        os.remove(cachename)
    if os.path.isfile(cachename) and os.path.getmtime(cachename) > os.path.getmtime(arg.input):
        logger.info('Valid data cache found ; Will be used')
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

        def filteroutFunction(n): return n.unit == 'V'

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
        logger.info('Reading from {}'.format(arg.input))
        data = sensors(arg.input, mergeFunction, groupFunction,
                       metaFunction, filteroutFunction)
        logger.info('Storing to cache {}'.format(cachename))
        of = open(cachename, "wb")
        pickle.dump(data, of)
        of.close()

    logger.info('Datas are :\n{}'.format(data))

    def logAndPlot(output, figure):
        logger.info('Writing to {}'.format(output))
        plot(figure, filename=output, auto_open=False)

    plotters = []

    if arg.verbose or arg.globalc:
        def sensorIsUnitAndClazz(unit, clazz):
            return lambda v: v.clazz == clazz and v.unit == unit

        plotters.append(lambda: logAndPlot(os.path.join(arg.output, 'Toutes les températures.html'), data.toFigure(
            sensorIsUnitAndClazz('°C', 'Sensor'), '°C', 'Toutes les températures'), prune=arg.prune))

        plotters.append(lambda: logAndPlot(os.path.join(arg.output, 'Toutes les humidités.html'), data.toFigure(
            sensorIsUnitAndClazz('RH%', 'Sensor'), '°C', 'Toutes les humidités'), prune=arg.prune))

        plotters.append(lambda: logAndPlot(os.path.join(
            arg.output, 'Toutes les températures - Baseline.html'), data.toFigure(
            sensorIsUnitAndClazz('°C', 'Sensor'), '°C', 'Toutes les températures - Baseline'), prune=arg.prune, baseline=True))

        plotters.append(lambda: logAndPlot(os.path.join(
            arg.output, 'Toutes les humidité - Baselines.html'), data.toFigure(
            sensorIsUnitAndClazz('RH%', 'Sensor'), '°C', 'Toutes les humidités - Baseline'), prune=arg.prune, baseline=True))

    if arg.verbose or arg.extvsint:
        # Interieur vs exterieur
        external = data['Extérieur'].asScatter()
        internalt = data['Intérieur - Sensor [°C]'].asScatter(
            name='Température intérieur', withError=True)
        internalrh = data['Intérieur - Sensor [RH%]'].asScatter(
            name='Humidité intérieur', withError=True, yaxis='y2')
        external_b = data['Extérieur'].asScatter(
            prune=arg.prune, baseline=True)
        internalt_b = data['Intérieur - Sensor [°C]'].asScatter(
            name='Température intérieur / Baseline', prune=arg.prune, baseline=True)
        internalrh_b = data['Intérieur - Sensor [RH%]'].asScatter(
            name='Humidité intérieur / Baseline', prune=arg.prune, baseline=True)

        def extvsint():
            logAndPlot(os.path.join(
                arg.output, 'Comparaison intérieur vs extérieur.html'), sensors.scattersToFigure(
                [external, internalt, internalrh], '°C', 'Intérieur vs Extérieur', 'RH%'))
            logAndPlot(os.path.join(
                arg.output, 'Comparaison intérieur vs extérieur - Baselines.html'), sensors.scattersToFigure(
                [external, internalt, internalrh, external_b, internalt_b, internalrh_b], '°C', 'Intérieur vs Extérieur - avec baselines', 'RH%'))
            logAndPlot(os.path.join(
                arg.output, 'Comparaison intérieur vs extérieur - Uniquement baselines.html'), sensors.scattersToFigure(
                [external_b, internalt_b, internalrh_b], '°C', 'Intérieur vs Extérieur - uniquement baselines', 'RH%'))
        plotters.append(extvsint)

    if arg.verbose or arg.meta:
        # Generate one file per meta sensor with/without baseline - working meta

        def plotIfExist(output, figure):
            if len(figure['data']) > 0:
                logAndPlot(output, figure)

        for name, lst in filter(lambda x:' [' not in x[0],data.metassensors):
            folder = os.path.join(arg.output, name.translate(
                str.maketrans('/:\\', '---')))
            if not os.path.isdir(folder):
                os.mkdir(folder)

            plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures.html'), data.toFigure(
                lambda s: s.name in clst and s.clazz == 'Sensor', '°C', cname, '%RH', lambda s: 'y' if s.unit == '°C' else 'y2', prune=arg.prune)))

            plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures et calculés.html'), data.toFigure(
                lambda s: s.name in clst and s.clazz in ('Sensor', 'COMPUTED'), '°C', cname, '%RH', lambda s: 'y' if s.unit == '°C' else 'y2', prune=arg.prune)))
            
            plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures - baselines.html'), data.toFigure(
                lambda s: s.name in clst and s.clazz == 'Sensor', '°C', cname, '%RH', lambda s: 'y' if s.unit == '°C' else 'y2', prune=arg.prune, baseline=True)))

            plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures et calculés - baselines.html'), data.toFigure(
                lambda s: s.name in clst and s.clazz in ('Sensor', 'COMPUTED'), '°C', cname, '%RH', lambda s: 'y' if s.unit == '°C' else 'y2', prune=arg.prune, baseline=True)))

    if arg.verbose or arg.detail:
        # Generate one file per sensor
        os.mkdir(os.path.join(arg.output, 'details'))

        for name, s in data.items():

            plotters.append(lambda cname=name, cs=s: logAndPlot(os.path.join(arg.output, 'details', cname.translate(
                str.maketrans('/:\\', '---')) + ".html"), sensors.sensorToFigure(cs, cs.name, prune=arg.prune, withBaseline=True)))

    with ThreadPoolExecutor(max_workers=arg.tc, thread_name_prefix='plotter') as e:
        [e.submit(p) for p in plotters]

    logger.info('Processing ended')


if __name__ == "__main__":
    sys.exit(main())
