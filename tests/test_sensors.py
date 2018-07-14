'''
Created on 10 juil. 2018

@author: borettim
'''

from pytest import fixture

from areexsupport.sensors import sensors
from datetime import datetime
from pytz import timezone
import textwrap


@fixture(scope="session")
def simpleinput(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("input.txt")
    ffn = open(fn, 'w')
    try:
        ffn.write(textwrap.dedent('''
        Measurement log

        Sensors:
        
        Column    Sensor    Unit
        1    Maquette Partie Haute - V    V
        2    Maquette Partie Haute - RH    RH%
        3    Maquette Partie Haute - T    °C
        4    Extérieur    °C
        
        Start date: 14.07.2018
        End date: 14.07.2018
        
        Time    1    2    3    4
        14.07.2018 00:00:39     3.2        23.4    
        14.07.2018 00:00:40                25.2
        14.07.2018 00:01:07        48.2        
        14.07.2018 00:01:29            23.4    
        14.07.2018 00:01:31                25.2
        14.07.2018 00:01:47        48.2        
        14.07.2018 00:02:09                25.2
        14.07.2018 00:02:33            23.4    
        14.07.2018 00:03:00                25.2
        14.07.2018 00:03:04        48.2        
        14.07.2018 00:03:44            23.4    
        14.07.2018 00:03:46                25.2
        14.07.2018 00:04:40        48.2        
        14.07.2018 00:04:52                25.1
        14.07.2018 00:05:27            23.4    
        14.07.2018 00:05:58        48.2        
        14.07.2018 00:06:04                25.2
        14.07.2018 00:06:21            23.4    
        14.07.2018 00:06:40        48.2        
        14.07.2018 00:07:13                25.1
        14.07.2018 00:07:25            23.3    
        14.07.2018 00:07:55        48.2        
        14.07.2018 00:08:17            23.3    
        14.07.2018 00:08:22                25.1
        14.07.2018 00:08:35        48.2        
        14.07.2018 00:09:22            23.3    
        14.07.2018 00:09:33                25.1
        14.07.2018 00:10:15        48.2        
        14.07.2018 00:10:35                25.1
        14.07.2018 00:11:01            23.3    
        14.07.2018 00:11:12                25.1
        14.07.2018 00:11:51        48.2        
        14.07.2018 00:12:23            23.3    
        14.07.2018 00:12:27                25.1
        14.07.2018 00:12:46        48.2        
        14.07.2018 00:13:29                25.1
        14.07.2018 00:13:30            23.3    
        14.07.2018 00:13:59        48.2        
        14.07.2018 00:14:01                25.1
        14.07.2018 00:14:40            23.3    
        14.07.2018 00:15:13                25.1
        14.07.2018 00:15:36        48.2        
        14.07.2018 00:16:01                25.0
        14.07.2018 00:16:24            23.4    
        14.07.2018 00:17:03                25.0
        14.07.2018 00:17:12        48.2        
        14.07.2018 00:17:42                25.0
        14.07.2018 00:17:44            23.4    
        14.07.2018 00:18:07        48.2        
        14.07.2018 00:18:26            23.4    
        14.07.2018 00:18:33                25.0
        14.07.2018 00:18:43        48.2        
        14.07.2018 00:19:27     3.2            ''').replace('    ', '\t'))
    finally:
        ffn.close()
    return fn


def testSensorsInitOnlyMandataParameter(simpleinput):
    d = sensors(simpleinput)
    print(d)
    assert 'Extérieur' in d.keys()
    assert 'Maquette Partie Haute - RH' in d.keys()
    assert 'Maquette Partie Haute - T' in d.keys()
    assert 'Maquette Partie Haute - V' in d.keys()
    assert len(d.groups) == 1
    assert 'default' in d.groups
    assert len(d) == 18
