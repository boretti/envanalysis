#!/usr/bin/env python
# encoding: utf-8
'''

'''

import sys
import os

from argparse import ArgumentParser
from argparse import ArgumentTypeError
from areexsupport.Sensor import SensorClass
from areexsupport.SensorData import SensorDataClass
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
            raise ArgumentTypeError('{} is a file. This should be a folder or not exists'.format(istring))
        if os.path.islink(istring):
            raise ArgumentTypeError('{} is a link. This should be a folder or not exists'.format(istring))
        return istring
    
    def validateInput(istring):
        if not os.path.isfile(istring):
            raise ArgumentTypeError('{} is not a file'.format(istring))
        return istring
    
    parser = ArgumentParser()
    parser.add_argument(dest="input", help="path to file with data",type=validateInput)
    parser.add_argument(dest="output", help="path to the output folder",type=validateOutput)
    parser.add_argument('--5min','-5',dest="by5min", action='store_true',help="aggregate value by 5min")
    arg = parser.parse_args()
    
    if not os.path.isdir(arg.output) :
        os.mkdir(arg.output)
    else :
        shutil.rmtree(arg.output, ignore_errors=True)
        shutil.rmtree(arg.output, ignore_errors=True)
        os.mkdir(arg.output)
    
    cachename = arg.input+".cache"
    if os.path.isfile(cachename) and os.path.getmtime(cachename)>os.path.getmtime(arg.input) :
        print('Valid data cache found ; Will be used')
        of = open(cachename,"rb")
        try:
            data = pickle.load(of)
        finally :
            of.close()
        
    else :
        print('Reading from {}'.format(arg.input))
        data = SensorDataClass(arg.input,SensorClass.dateTimeTo5Minute() if arg.by5min else SensorClass.dateTimeToMinute())
        data.filterOutSensor(SensorClass.sensorIsUnit('V'))
        print('Storing to cache {}'.format(cachename))
        of = open(cachename,"wb")
        pickle.dump(data,of)
        of.close()
    
    print('Datas are :\n{}'.format(data))
    
    for n,fd in sorted(data.toMultiFigures().items()) :
        print('Writing to subfolder {}'.format(n))
        if n=='/' : n=''
        targetfolder = os.path.join(arg.output,n)
        if not os.path.exists(targetfolder): os.mkdir(targetfolder)
        for sn,d in sorted(fd.items()) :
            output = os.path.join(targetfolder,sn.translate(str.maketrans('/:\\','---'))+".html")
            print ('Writing to {}'.format(output))
            plot(d,filename=output,auto_open=False)
 


if __name__ == "__main__":
    sys.exit(main())
    