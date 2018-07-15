'''
Created on 15 juil. 2018

@author: borettim
'''

import os

from areexsupport.sensors import sensors


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    os.mkdir(os.path.join(bsefolder, 'comparaisons'))
    external = data['Extérieur'].asScatter()
    internalt = data['Intérieur - Sensor [°C]'].asScatter(
        name='Température intérieur', withError=True)
    internalrh = data['Intérieur - Sensor [RH%]'].asScatter(
        name='Humidité intérieur', withError=True, yaxis='y2')
    external_b = data['Extérieur'].asScatter(
        prune=prune, baseline=True)
    internalt_b = data['Intérieur - Sensor [°C]'].asScatter(
        name='Température intérieur / Baseline', prune=prune, baseline=True)
    internalrh_b = data['Intérieur - Sensor [RH%]'].asScatter(
        name='Humidité intérieur / Baseline', prune=prune, baseline=True)

    return [
        # INT vs EXT
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieur vs extérieur.html'), sensors.scattersToFigure(
            [external, internalt, internalrh], '°C', 'Intérieur vs Extérieur', 'RH%')),
        # INT vs EXT - All
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieur vs extérieur - Baselines.html'), sensors.scattersToFigure(
            [external, internalt, internalrh, external_b, internalt_b, internalrh_b], '°C', 'Intérieur vs Extérieur - avec baselines', 'RH%')),
        # INT vs EXT - BL
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieur vs extérieur - Uniquement baselines.html'), sensors.scattersToFigure(
            [external_b, internalt_b, internalrh_b], '°C', 'Intérieur vs Extérieur - uniquement baselines', 'RH%'))]
