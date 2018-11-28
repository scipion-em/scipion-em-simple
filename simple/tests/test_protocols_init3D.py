'''
Created on Sep 28, 2018

@author: david
'''

import os

import pyworkflow.tests as tests

from simple.protocols import ProtInit3D
from pyworkflow.em.data import SetOfMovies
from pyworkflow.em.protocol import ProtImportParticles

class TestInit3DBase(tests.BaseTest):
    """This class checks if the protocol to call Unblur
       works properly.
    """
    @classmethod
    def setUpClass(cls):
        tests.setupTestProject(cls)
        
class TestInit3D(TestInit3DBase):
    @classmethod    
    def setUpClass(cls):
        tests.setupTestProject(cls)
        cls.protImport = cls.runImportFromScipion()

    @classmethod
    def runImportFromScipion(cls):
        args = {'importFrom': ProtImportParticles.IMPORT_FROM_FILES,
                'filesPath': '/media/david/linux/Documentos/CNB/TFG/simpleData/simple2.5tutorials/3_PRIME3D/data/',
                'filesPattern': '*.mrc',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 300,
                'samplingRate': 2.68
                }
        prot1 = cls.newProtocol(ProtImportParticles,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Init3D(self):
        prot2 = self.newProtocol(ProtInit3D, symmetry='c1')
        prot2.inputClasses.set(self.protImport.outputParticles)
        self.launchProtocol(prot2)
        
        
