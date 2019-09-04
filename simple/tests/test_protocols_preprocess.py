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

from simple.protocols import ProtUnblurSimple
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
        cls.dsMovies = tests.DataSet.getDataSet('riboMovies')
        args = {'importFrom': ProtImportMovies.IMPORT_FROM_FILES,
                'filesPath': cls.dsMovies.getFile(''),
                'filesPattern': '35_movie_gc_window.mrcs',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.0,
                'voltage': 300,
                'samplingRate': 2.37
                }
        prot1 = cls.newProtocol(ProtImportMovies,**args)
        prot1.setObjLabel('from files')
        cls.launchProtocol(prot1)
        return prot1
        
    def test_Unblur(self):
        prot2 = self.newProtocol(ProtUnblurSimple)
        prot2.inputMovies.set(self.protImport.outputMovies)
        self.launchProtocol(prot2)
        
        
