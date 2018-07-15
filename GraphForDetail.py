'''
Created on 15 juil. 2018

@author: borettim
'''

import os

from areexsupport.sensors import sensors


def generateFunctionToPlot(bsefolder, data, functionToPlot, prune):
    os.mkdir(os.path.join(bsefolder, 'details'))

    return [lambda cname=name, cs=s: functionToPlot(os.path.join(bsefolder, 'details', cname.translate(
        str.maketrans('/:\\', '---')) + ".html"), sensors.sensorToFigure(cs, cs.name, prune=prune, withBaseline=True)) for name, s in data.items()]
