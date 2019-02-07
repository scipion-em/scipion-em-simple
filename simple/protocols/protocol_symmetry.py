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
from pyworkflow.protocol.params import PointerParam, IntParam, StringParam, FileParam, FloatParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.protocol.constants import LEVEL_ADVANCED

import simple

class ProtSym(ProtMicrographs):
    """
    Maximising the SNR of the integrated movie
    
    To find more information about Simple.Unblur go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'symmetry_test'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -------------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputVol', PointerParam, pointerClass='Volume', allowsNull=False,
                       label='Input Volume')
        form.addParam('mask', IntParam, default=-1, label='Mask radius', help='Mask radius (in voxels).')
        form.addParam('lp', FloatParam, default=0.5, expertLevel=LEVEL_ADVANCED,
                      label='Low pass limit', help='Low pass limit in normalized frequency (<0.5)')
        form.addParallelSection(threads=4, mpi=0)
                
    #--------------------------- INSERT steps functions -------------------------------
    def _insertAllSteps(self):
        self._insertFunctionStep('symStep')
        
    #--------------------------- STEPS functions -------------------------------
    def symStep(self):
        inputVol = self.inputVol.get()
        fnVol = inputVol.getFileName()
        samplingRate = inputVol.getSamplingRate()
        volName = os.path.basename(fnVol)
        volName = os.path.splitext(volName)[0]
        tmpDir = self._getTmpPath(volName)
        fnVol = os.path.abspath(fnVol)
        makePath(tmpDir)

        maskRadius = self.mask.get()
        if maskRadius<0:
            Xdim = inputVol.getDim()[0]
            maskRadius=Xdim/2-1
        lpCutoff = inputVol.getSamplingRate()/self.lp.get()

        paramsSym = ' prg=symmetry_test vol1=%s smpd=%f msk=%d lp=%f nthr=%d' \
                 %(fnVol, samplingRate, maskRadius, lpCutoff, self.numberOfThreads.get())

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsSym, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())


        #Move output files to ExtraPath and rename them properly
        mvRoot1 = os.path.join(tmpDir+'/temp/1_symmetry_test', "symmetry_test_output.txt")
        moveFile(mvRoot1, self._getExtraPath('point_group_symmetry_.txt'))
        cleanPath(tmpDir)

    # def createOutputStep(self):
        
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites
        
        