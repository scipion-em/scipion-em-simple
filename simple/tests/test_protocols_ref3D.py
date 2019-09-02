# **************************************************************************
# *
# * Authors:     David Herreros
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os

import pyworkflow.tests as tests
import pyworkflow.utils as pwutils

from simple.protocols import ProtRef3D
from pyworkflow.em.protocol import ProtImportVolumes, ProtImportParticles
from pyworkflow.tests import *

class TestRef3DBase(tests.BaseTest):
    """This class checks if the protocol to call Unblur
       works properly.
    """
    @classmethod
    def setUpClass(cls):
        tests.setupTestProject(cls)
        
class TestRef3D(TestRef3DBase):
    @classmethod    
    def setUpClass(cls):
        tests.setupTestProject(cls)
        cls.protImportVol = cls.runImportVolFromScipion()
        cls.protImportParticles = cls.runImportParticlesFromScipion()

    @classmethod
    def runImportVolFromScipion(cls):
        cls.dsXmipp = tests.DataSet.getDataSet('nma')
        args = {'importFrom': ProtImportVolumes.IMPORT_FROM_FILES,
                'filesPath': cls.dsXmipp.getFile('volumes/'),
                'filesPattern': '*.vol',
                'setOrigCoord': False,
                'samplingRate': 1.0,
                }
        prot1 = cls.newProtocol(ProtImportVolumes,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1

    @classmethod
    def runImportParticlesFromScipion(cls):
        cls.particles = tests.DataSet.getDataSet('nma')
        args = {'importFrom': ProtImportParticles.IMPORT_FROM_FILES,
                'filesPath': cls.particles.getFile('particles/'),
                'filesPattern': '*.stk',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.0,
                'voltage': 300,
                'samplingRate': 1.0
                }
        prot1 = cls.newProtocol(ProtImportParticles, **args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Ref3D(self):
        prot2 = self.newProtocol(ProtRef3D, maxIter=3, symmetry="c1")
        prot2.inputVol.set(self.protImportVol.outputVolume)
        prot2.inputParticles.set(self.protImportParticles.outputParticles)
        self.launchProtocol(prot2)
        
        
