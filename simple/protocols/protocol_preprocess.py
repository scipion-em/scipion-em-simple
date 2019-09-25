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
#import pyworkflow.em as em
from pyworkflow import VERSION_1_1
import pyworkflow.protocol.params as param
from pyworkflow.protocol.params import PointerParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.protocol.constants import STEPS_PARALLEL
import simple

class ProtUnblurSimple(ProtMicrographs):
    """
    Maximising the SNR of the integrated movie
    
    To find more information about Simple.Unblur go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'preprocess'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL

    #--------------------------- DEFINE param functions -------------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputMovies', PointerParam, pointerClass='SetOfMovies', allowsNull=False,
                       label='Input Movies', important=True)
        form.addParallelSection(threads=4, mpi=1)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self.inputMV = self.inputMovies.get()
        self.partitions=1
        self.kV = self.inputMV.getAcquisition().getVoltage()
        self.dose = self.inputMV.getAcquisition().getDosePerFrame()
        self.fraca = self.inputMV.getAcquisition().getAmplitudeContrast()
        self.cs = self.inputMV.getAcquisition().getSphericalAberration()

        deps = []
        for movie in self.inputMV:
            movieName = movie.getFileName()
            samplingRate = movie.getSamplingRate()
            deps.append(self._insertFunctionStep('unblurStep', movieName, samplingRate, prerequisites=[]))
        self._insertFunctionStep("createOutputStep",prerequisites=deps)
        
    #--------------------------- STEPS functions -------------------------------
    def unblurStep(self,mvF,samplingRate):
        mvName = os.path.basename(mvF)
        mvName = os.path.splitext(mvName)[0]
        tmpDir = self._getTmpPath(mvName)
        makePath(tmpDir)
        mvRoot = os.path.join(tmpDir,mvName)

        fnInput = os.path.abspath(mvRoot+'.txt')
        fhInput = open(fnInput,'w')
        fhInput.write(os.path.abspath(mvF))
        fhInput.close()

        paramsUnblur = ' prg=preprocess nparts=%d nthr=%d' %(self.partitions,self.numberOfThreads.get())
        paramsMovies = ' prg=import_movies filetab=%s cs=%f ctf=no fraca=%f kv=%d smpd=%f' %(fnInput,self.cs, self.fraca,
                                                                                             self.kV, samplingRate)

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsMovies, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.distr_exec(), paramsUnblur, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())

        #Move output files to ExtraPath and rename them properly
        mvRoot = os.path.join(tmpDir+'/temp/2_preprocess', mvName)
        moveFile(mvRoot+"_intg.mrc",self._getExtraPath(mvName+".mrc"))
        moveFile(os.path.join(tmpDir+"/temp/2_preprocess","pspec.mrc"),self._getExtraPath(mvName+"_psd.mrc"))
        cleanPath(tmpDir)

    def createOutputStep(self):
        outputMics= self._createSetOfMicrographs()
        outputMics.copyInfo(self.inputMV)

        for movie in self.inputMV:
            mic = outputMics.ITEM_TYPE()
            mic.copyObjId(movie)
            mvName = movie.getFileName()
            mic.setMicName(mvName)            # Update movie name and append to the new Set
            mvName = os.path.basename(mvName)
            mvName = os.path.splitext(mvName)[0]
            mic.setFileName(self._getExtraPath(mvName+".mrc"))
            outputMics.append(mic)

        self._defineOutputs(outputMovies=outputMics)
        self._defineTransformRelation(self.inputMV, outputMics)
        
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

        
        
