'''
Created on 15 juil. 2018

@author: borettim
'''

import os

from areexsupport.sensors import sensors


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    bfolder = os.path.join(bsefolder, 'analyses')
    if not os.path.isdir(bfolder):
        os.mkdir(bfolder)
    ffolder = os.path.join(bfolder, 'Analyse sous-fenetre')
    if not os.path.isdir(ffolder):
        os.mkdir(ffolder)

    external = data['Extérieur'].asScatter(prune=prune)
    internalt = data['Intérieur - Sensor [°C]'].asScatterWithError(
        name='Température intérieur')
    external_b = data['Extérieur'].asScatter(
        prune=prune, baseline=True)
    internalt_b = data['Intérieur - Sensor [°C]'].asScatter(
        name='Température intérieur / Baseline', prune=prune, baseline=True)
    sousfenetre = data['Atelier Sous-fenêtre - T'].asScatter(
        prune=prune)
    sousfenetre_b = data['Atelier Sous-fenêtre - T'].asScatter(
        prune=prune, baseline=True)
    diff_s_ext_sous = data['Extérieur'] - data['Atelier Sous-fenêtre - T']
    diff_ext_sous = diff_s_ext_sous.asScatter(
        name='Différence extérieur et atelier sous-fenêtre', prune=prune)
    diff_ext_sous_b = diff_s_ext_sous.asScatter(
        name='Différence extérieur et atelier sous-fenêtre - Baseline', prune=prune, baseline=True)
    diff_s_int_sous = data['Intérieur - Sensor [°C]'] - \
        data['Atelier Sous-fenêtre - T']
    diff_int_sous = diff_s_int_sous.asScatter(
        name='Différence intérieur et atelier sous-fenêtre', prune=prune)
    diff_int_sous_b = diff_s_int_sous.asScatter(
        name='Différence intérieur et atelier sous-fenêtre - Baseline', prune=prune, baseline=True)

    plotters = []

    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Comparaison Intérieur vs Extérieur vs Atelier sous-fenêtre.html'), sensors.scattersToFigure(
        [external, internalt, sousfenetre], '°C', 'Intérieur vs Extérieur vs Atelier sous-fenêtre')))
    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Comparaison Intérieur vs Extérieur vs Atelier sous-fenêtre - baselines.html'), sensors.scattersToFigure(
        [external, internalt, sousfenetre, external_b, internalt_b, sousfenetre_b], '°C', 'Intérieur vs Extérieur vs Atelier sous-fenêtre - avec Baselines')))
    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Comparaison Intérieur vs Extérieur vs Atelier sous-fenêtre - uniquement baselines.html'), sensors.scattersToFigure(
        [external_b, internalt_b, sousfenetre_b], '°C', 'Intérieur vs Extérieur vs Atelier sous-fenêtre - uniquement Baselines')))

    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Différence Intérieur vs Atelier sous-fenêtre et Extérieur vs Atelier sous-fenêtre.html'), sensors.scattersToFigure(
        [diff_ext_sous, diff_int_sous], '°C', 'Comparaison par différence Intérieur, Extérieur, Atelier sous-fenêtre')))
    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Différence Intérieur vs Atelier sous-fenêtre et Extérieur vs Atelier sous-fenêtre - baselines.html'), sensors.scattersToFigure(
        [diff_ext_sous, diff_int_sous, diff_ext_sous_b, diff_int_sous_b], '°C', 'Comparaison par différence Intérieur, Extérieur, Atelier sous-fenêtre - avec Baselines')))
    plotters.append(lambda: functionToPlot(os.path.join(
        ffolder, 'Différence Intérieur vs Atelier sous-fenêtre et Extérieur vs Atelier sous-fenêtre - uniquement baselines.html'), sensors.scattersToFigure(
        [diff_ext_sous_b, diff_int_sous_b], '°C', 'Comparaison par différence Intérieur, Extérieur, Atelier sous-fenêtre - uniquement Baselines')))

    return plotters
