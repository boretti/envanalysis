'''
Created on 15 juil. 2018

@author: borettim
'''

import os

from areexsupport.sensors import sensors


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    if not os.path.isdir(os.path.join(bsefolder, 'comparaisons')):
        os.mkdir(os.path.join(bsefolder, 'comparaisons'))

    internalt = data['Intérieur [°C]'].asScatterWithError(
        name='Température intérieur')
    internalt_b = data['Intérieur [°C]'].asScatter(
        name='Température intérieur / Baseline', prune=prune, baseline=True)

    atelierl = data['Atelier [°C]'].asScatterWithError(
        name='Température atelier')
    atelierl_b = data['Atelier [°C]'].asScatter(
        name='Température atelier / Baseline', prune=prune, baseline=True)

    avant = data['Avant du garage [°C]'].asScatterWithError(
        name='Température avant du garage')
    avant_b = data['Avant du garage [°C]'].asScatter(
        name='Température avant du garage / Baseline', prune=prune, baseline=True)

    internalrh = data['Intérieur [RH%]'].asScatterWithError(
        name='Humidité intérieur', yaxis='y2')
    internalrh_b = data['Intérieur [RH%]'].asScatter(
        name='Humidité intérieur / Baseline', prune=prune, baseline=True)

    atelierrh = data['Atelier - RH'].asScatter(
        name='Humidité atelier', prune=prune, yaxis='y2')
    atelierrh_b = data['Atelier - RH'].asScatter(
        name='Humidité atelier / Baseline', prune=prune, baseline=True)

    avantrh = data['Avant du garage [RH%]'].asScatterWithError(
        name='Humidité avant du garage', yaxis='y2')
    avantrh_b = data['Avant du garage [RH%]'].asScatter(
        name='Humidité avant du garage / Baseline', prune=prune, baseline=True)

    return [
        # INT vs EXT
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieurs.html'), sensors.scattersToFigure(
            [internalt, atelierl, avant, internalrh, atelierrh, avantrh], '°C', 'Intérieur vs Avant vs Arrière', 'RH%')),
        # INT vs EXT - All
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieurs - Baselines.html'), sensors.scattersToFigure(
            [internalt, atelierl, avant, internalrh, atelierrh, avantrh, internalt_b, atelierl_b, avant_b, internalrh_b, atelierrh_b, avantrh_b], '°C', 'Intérieur vs Avant vs Arrière - avec baselines', 'RH%')),
        # INT vs EXT - BL
        lambda: functionToPlot(os.path.join(
            bsefolder, 'comparaisons', 'Comparaison intérieurs - Uniquement baselines.html'), sensors.scattersToFigure(
            [internalt_b, atelierl_b, avant_b, internalrh_b, atelierrh_b, avantrh_b], '°C', 'Intérieur vs Avant vs Arrière - uniquement baselines', 'RH%'))]
