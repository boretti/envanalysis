#!/usr/bin/env python
# encoding: utf-8
'''

'''

import sys
import os

from argparse import ArgumentParser
from areexsupport.Sensor import SensorClass
from areexsupport.SensorData import SensorDataClass
from plotly.offline import plot


def main(argv=None):
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    program_name = os.path.basename(sys.argv[0])
        
    try:
        parser = ArgumentParser()
        parser.add_argument(dest="input", help="paths to file with data")
        parser.add_argument('--5min','-5',dest="by5min", action='store_true',help="aggregate value by 5min")
        parser.add_argument('--unit','-u',dest="unit",action='store',default="°C",choices=["°C","RH%","ALL"],help="choose the unit to be used, default is °C")
        parser.add_argument('--rosee','-r',dest="pointrosee", action='store_true',help="compute point de rosee")
        arg = parser.parse_args()
        
        print('Reading from {}'.format(arg.input))
        
        data = SensorDataClass(arg.input)
        
        print('Readed : {}'.format(data))
        
        data.filterOutSensor(SensorClass.sensorIsUnit('V'))
        
        print('Removed V : {}'.format(data))
        
        data.mergeValueBy(SensorClass.dateTimeToMinute())
        
        print('Merged by 1min : {}'.format(data))
        
        if arg.by5min:
            data.mergeValueBy(SensorClass.dateTimeTo5Minute())
        
            print('Merged by 5min : {}'.format(data))
        
        if arg.pointrosee or arg.unit=='ALL':
            data.computePointRosee()
        
            print('Point de rosee : {}'.format(data))
        
        if arg.unit!='ALL':
            fig = dict(
                data=data.toScatters(arg.unit),
                layout=dict(
                    xaxis=dict(
                        title='Date'),
                    yaxis=dict(
                        title=arg.unit)
                    )
                )
            
            output = os.path.join(os.path.dirname(arg.input),os.path.basename(arg.input)+".html")
            print ('Writing to {}'.format(output))
            
            plot(fig,filename=output)
        else :
            for n,d in data.toMultiScatters().items() :
                fig = dict(
                    data=d,
                    layout=dict(
                        xaxis=dict(
                            title='Date'),
                        yaxis=dict(
                            title='°C' if 'temp' in n else 'RH%')
                        )
                    )
                
                output = os.path.join(os.path.dirname(arg.input),os.path.basename(arg.input)+n+".html")
                print ('Writing to {}'.format(output))
                plot(fig,filename=output)
            

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    sys.exit(main())
    