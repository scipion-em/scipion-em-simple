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

from simple.protocols import ProtSym
from pyworkflow.em.protocol import ProtImportVolumes

class TestSymBase(tests.BaseTest):
    """This class checks if the protocol to call Unblur
       works properly.
    """
    @classmethod
    def setUpClass(cls):
        tests.setupTestProject(cls)
        
class TestSym(TestSymBase):
    @classmethod    
    def setUpClass(cls):
        tests.setupTestProject(cls)
        cls.protImport = cls.runImportFromScipion()

    @classmethod
    def runImportFromScipion(cls):
        args = {'importFrom': ProtImportVolumes.IMPORT_FROM_FILES,
                'filesPath': '/media/david/linux/Documentos/CNB/TFG/simpleData/Symsrch_Data/',
                'filesPattern': '*.mrc',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 300,
                'samplingRate': 2.68
                }
        prot1 = cls.newProtocol(ProtImportVolumes,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Sym(self):
        oritab = '/media/david/linux/Documentos/CNB/TFG/simpleData/Symsrch_Data/particles_projvol_oris.txt'
        prot2 = self.newProtocol(ProtSym, orientations=oritab)
        prot2.inputVol.set(self.protImport.outputVolume)
        self.launchProtocol(prot2)
        
        
