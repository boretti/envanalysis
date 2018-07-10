'''
Created on 10 juil. 2018

@author: borettim
'''
import unittest

from areexsupport.Sensor import SensorClass
from datetime import datetime
from pytz import timezone

class SensorTest(unittest.TestCase):

    def testSensorInitOnlyMandataParameter(self):
        s = SensorClass('name')
        self.assertEqual(s.name, 'name', 'Validate name is OK')
        self.assertEqual(s.unit, 'V', 'Validate unit is OK')
        self.assertEqual(s.pos, 1, 'Validate pos is OK')
        self.assertEqual(len(s.values), 0, 'Validate value is OK')
        self.assertEqual(s.mode, 'lines', 'Validate mode is OK')
        
    def testSensorInitExplicit(self):
        s = SensorClass('name','RH%',2,{'x':'y'},'y')
        self.assertEqual(s.name, 'name', 'Validate name is OK')
        self.assertEqual(s.unit, 'RH%', 'Validate unit is OK')
        self.assertEqual(s.pos, 2, 'Validate pos is OK')
        self.assertEqual(s.values, {'x':'y'}, 'Validate value is OK')
        self.assertEqual(s.mode, 'y', 'Validate mode is OK')

    def testSensorSensorIsUnit(self):
        s1 = SensorClass('name','RH%',2)
        s2 = SensorClass('name','V',2)
        self.assertFalse(SensorClass.sensorIsUnit('V')(s1), "Validate that s1 is not V")
        self.assertTrue(SensorClass.sensorIsUnit('V')(s2), "Validate that s2 is not V")
        
    def testSensorDateTimeToMinute(self):
        m = SensorClass.dateTimeToMinute();
        d1 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        d2 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01','%d.%m.%Y %H:%M:%S'))
        self.assertEqual(m(d1), d1, "Validate that value with s second stay equals")
        self.assertEqual(m(d2), d1, "Validate that value with 1s second stay equals")
        
    def testSensorDateTimeTo5Minute(self):
        m = SensorClass.dateTimeTo5Minute();
        d1 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        d2 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01','%d.%m.%Y %H:%M:%S'))
        d3 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01','%d.%m.%Y %H:%M:%S'))
        d4 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:05:00','%d.%m.%Y %H:%M:%S'))
        d5 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:05:01','%d.%m.%Y %H:%M:%S'))
        d6 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:06:01','%d.%m.%Y %H:%M:%S'))
        self.assertEqual(m(d1), d1, "Validate that value with s second stay equals")
        self.assertEqual(m(d2), d1, "Validate that value with 1s second stay equals")
        self.assertEqual(m(d3), d1, "Validate that value with 1m1s second stay equals")
        self.assertEqual(m(d4), d4, "Validate that value with s second stay equals")
        self.assertEqual(m(d5), d4, "Validate that value with 1s second stay equals")
        self.assertEqual(m(d6), d4, "Validate that value with 1m1s second stay equals")
        
    def testMergeValueBy(self):
        m = SensorClass.dateTimeToMinute();
        d1 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        d2 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01','%d.%m.%Y %H:%M:%S'))
        d3 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02','%d.%m.%Y %H:%M:%S'))
        d4 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01','%d.%m.%Y %H:%M:%S'))
        d5 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:00','%d.%m.%Y %H:%M:%S'))
        s = SensorClass('name')
        s.add(1.2, d1)
        s.add(1.8, d2)
        s.add(2.4, d3)
        s.add(2.5, d4)
        s.mergeValueBy(m)
        self.assertDictEqual(s.values, {d1:1.8,d5:2.5}, "Validate the merge result")

if __name__ == "__main__":
    unittest.main()