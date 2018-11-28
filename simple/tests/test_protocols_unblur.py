'''
Created on Sep 28, 2018

@author: david
'''

import os

import pyworkflow.tests as tests

from simple.protocols import ProtUnblur
from pyworkflow.em.data import SetOfMovies
from pyworkflow.em.protocol import ProtImportMovies

class TestUnblurBase(tests.BaseTest):
    """This class checks if the protocol to call Unblur
       works properly.
    """
    @classmethod
    def setUpClass(cls):
        tests.setupTestProject(cls)
        
class TestUnblur(TestUnblurBase):
    @classmethod    
    def setUpClass(cls):
        tests.setupTestProject(cls)
        cls.protImport = cls.runImportFromScipion()

    @classmethod
    def runImportFromScipion(cls):
        args = {'importFrom': ProtImportMovies.IMPORT_FROM_FILES,
                'filesPath': '/media/david/linux/Documentos/CNB/TFG/simpleData/relion13_tutorial/betagal/Micrographs/',
                'filesPattern': '*.mrcs',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 300,
                'samplingRate': 3.54
                }
        prot1 = cls.newProtocol(ProtImportMovies,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Unblur(self):
        prot2 = self.newProtocol(ProtUnblur)
        prot2.inputMovies.set(self.protImport.outputMovies)
        self.launchProtocol(prot2)
        
        
