'''
Created on Sep 28, 2018

@author: david
'''

import os

import pyworkflow.tests as tests

from simple.protocols import ProtPrime2D
from pyworkflow.em.data import SetOfMovies
from pyworkflow.em.protocol import ProtImportParticles
class TestPrime2DBase(tests.BaseTest):
    """This class checks if the protocol to call Prime2D
       works properly.
    """
    @classmethod
    def setUpClass(cls):
        tests.setupTestProject(cls)
        
class TestPrime2D(TestPrime2DBase):
    @classmethod    
    def setUpClass(cls):
        tests.setupTestProject(cls)
        cls.protImport = cls.runImportFromScipion()

    @classmethod
    def runImportFromScipion(cls):
        args = {'importFrom': ProtImportParticles.IMPORT_FROM_FILES,
                'filesPath': '/media/david/linux/Documentos/CNB/TFG/simpleData/simple2.5tutorials/2_PRIME2D/data/',
                'filesPattern': '*.mrc',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 300,
                'samplingRate': 2.4312
                }
        prot1 = cls.newProtocol(ProtImportParticles,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Prime2D(self):
        prot2 = self.newProtocol(ProtPrime2D, clusters=10)
        prot2.inputParticles.set(self.protImport.outputParticles)
        self.launchProtocol(prot2)
        
        
