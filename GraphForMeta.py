'''
Created on 15 juil. 2018

@author: borettim
'''

import os


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    def plotIfExist(output, figure):
        if len(figure['data']) > 0:
            functionToPlot(output, figure)

    plotters = []

    for name, lst in filter(lambda x: ' [' not in x[0], data.metassensors):
        folder = os.path.join(bsefolder, name.translate(
            str.maketrans('/:\\', '---')))
        if not os.path.isdir(folder):
            os.mkdir(folder)

        plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures.html'), data.toFigure(
            lambda s: s.name in clst and s.clazz == 'Sensor', '°C', cname, '%RH', lambda s: 'y' if s.unit == '�C' else 'y2', prune=prune)))

        plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures et calculés.html'), data.toFigure(
            lambda s: s.name in clst and s.clazz in ('Sensor', 'COMPUTED'), '�C', cname, '%RH', lambda s: 'y' if s.unit == '�C' else 'y2', prune=prune)))

        plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures - baselines.html'), data.toFigure(
            lambda s: s.name in clst and s.clazz == 'Sensor', '°C', cname, '%RH', lambda s: 'y' if s.unit == '�C' else 'y2', prune=prune, baseline=True)))

        plotters.append(lambda cname=name, clst=lst, cfolder=folder: plotIfExist(os.path.join(cfolder, 'mesures et calculés - baselines.html'), data.toFigure(
            lambda s: s.name in clst and s.clazz in ('Sensor', 'COMPUTED'), '�C', cname, '%RH', lambda s: 'y' if s.unit == '�C' else 'y2', prune=prune, baseline=True)))

    return plotters
