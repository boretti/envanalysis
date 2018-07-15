'''
Created on 15 juil. 2018

@author: borettim
'''

import os


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    def sensorIsUnitAndClazz(unit, clazz):
        return lambda v: v.clazz == clazz and v.unit == unit
    return [
        # All T
        lambda: functionToPlot(os.path.join(bsefolder, 'Toutes les tempéatures.html'), data.toFigure(
            sensorIsUnitAndClazz('°C', 'Sensor'), '�C', 'Toutes les températures', prune=prune)),
        # All RH
        lambda: functionToPlot(os.path.join(bsefolder, 'Toutes les humidités.html'), data.toFigure(
            sensorIsUnitAndClazz('RH%', 'Sensor'), '�C', 'Toutes les humidités', prune=prune)),
        # All T - BL
        lambda: functionToPlot(os.path.join(
            bsefolder, 'Toutes les températures - Baseline.html'), data.toFigure(
            sensorIsUnitAndClazz('°C', 'Sensor'), '�C', 'Toutes les températures - Baseline', prune=prune, baseline=True)),
        # All RH - BL
        lambda: functionToPlot(os.path.join(
            bsefolder, 'Toutes les humidités - Baselines.html'), data.toFigure(
            sensorIsUnitAndClazz('RH%', 'Sensor'), '�C', 'Toutes les humidités - Baseline', prune=prune, baseline=True))]
