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
        self.assertEqual(s.clazz, 'Sensor', 'Validate clazz is OK')
        self.assertEqual(s.parent, [], 'Validate parent is OK')
        self.assertEqual(s.children, [], 'Validate children is OK')
        self.assertEqual(s.groupe, None, 'Validate group is OK')
          
    def testSensorInitExplicit(self):
        s1 = SensorClass('name1')
        s = SensorClass('name','RH%',2,{'x':'y'},'y','c',[s1],'g')
        self.assertEqual(s.name, 'name', 'Validate name is OK')
        self.assertEqual(s.unit, 'RH%', 'Validate unit is OK')
        self.assertEqual(s.pos, 2, 'Validate pos is OK')
        self.assertEqual(s.values, {'x':'y'}, 'Validate value is OK')
        self.assertEqual(s.mode, 'y', 'Validate mode is OK')
        self.assertEqual(s.clazz, 'c', 'Validate clazz is OK')
        self.assertEqual(len(s.parent), 1, 'Validate parent is OK')
        self.assertEqual(s.parent[0].name, 'name1', 'Validate parent is OK')
        self.assertEqual(s.children, [], 'Validate children is OK')
        self.assertEqual(s.groupe, 'g', 'Validate group is OK')
        
    def testSensorIsGroup(self):
        s1 = SensorClass('name','RH%',2)
        s2 = SensorClass('name','V',2,groupe='g')
        self.assertFalse(SensorClass.sensorIsGroup('g')(s1), "Validate that s1 is not g")
        self.assertTrue(SensorClass.sensorIsGroup('g')(s2), "Validate that s2 is not g")

    def testSensorSensorIsUnit(self):
        s1 = SensorClass('name','RH%',2)
        s2 = SensorClass('name','V',2)
        self.assertFalse(SensorClass.sensorIsUnit('V')(s1), "Validate that s1 is not V")
        self.assertTrue(SensorClass.sensorIsUnit('V')(s2), "Validate that s2 is not V")
        
    def testSensorSensorIsClazz(self):
        s1 = SensorClass('name','RH%',2,clazz='s')
        s2 = SensorClass('name','V',2,clazz='t')
        self.assertFalse(SensorClass.sensorIsClazz('t')(s1), "Validate that s1 is not V")
        self.assertTrue(SensorClass.sensorIsClazz('t')(s2), "Validate that s2 is not V")
        
    def testSensorIsUnitAndClazz(self):
        s1 = SensorClass('name','RH%',2)
        s2 = SensorClass('name','V',2)
        self.assertFalse(SensorClass.sensorIsUnitAndClazz('V','Sensor')(s1), "Validate that s1 is not V")
        self.assertTrue(SensorClass.sensorIsUnitAndClazz('V','Sensor')(s2), "Validate that s2 is not V")
        
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
        
    def testToBaseLine(self):
        d1 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        d2 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01','%d.%m.%Y %H:%M:%S'))
        d3 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02','%d.%m.%Y %H:%M:%S'))
        d4 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01','%d.%m.%Y %H:%M:%S'))
        s = SensorClass('name')
        s.add(1.0, d1)
        s.add(2.1, d2)
        s.add(3.1, d3)
        s.add(4.1, d4)
        s2 = s.toBaseLine()
        self.assertAlmostEqual(s2.values[d1], 1, msg="First value should be around 1")
        self.assertAlmostEqual(s2.values[d2], 2.1, msg="Second value should be around 2.1")
        self.assertAlmostEqual(s2.values[d3], 3.1, msg="Third value should be around 3.1")
        self.assertAlmostEqual(s2.values[d4], 4.1, msg="Fourth value should be around 4.1")
        self.assertEqual(len(s.children),1,'Validate parent as one child')
        self.assertEqual(s.children[0].name,'name - baseline','Validate parent have correct children')
        self.assertEqual(len(s2.parent),1,'Validate child as one parent')
        self.assertEqual(s2.parent[0].name,'name','Validate children have correct parent')
        
    def testSub(self):
        d1 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        d2 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01','%d.%m.%Y %H:%M:%S'))
        d3 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02','%d.%m.%Y %H:%M:%S'))
        d4 = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01','%d.%m.%Y %H:%M:%S'))
        s1 = SensorClass('name')
        s1.add(1.0, d1)
        s1.add(2.1, d2)
        s1.add(3.1, d3)
        s1.add(4.1, d4)
        s2 = SensorClass('name')
        s2.add(0.5, d1)
        s2.add(1, d2)
        s2.add(5, d3)
        s3 = s1-s2
        self.assertAlmostEqual(s3.values[d1], 0.5, msg="First value should be around 1")
        self.assertAlmostEqual(s3.values[d2], 1.1, msg="Second value should be around 2.1")
        self.assertAlmostEqual(s3.values[d3], -1.9, msg="Third value should be around 3.1")
        

if __name__ == "__main__":
    unittest.main()