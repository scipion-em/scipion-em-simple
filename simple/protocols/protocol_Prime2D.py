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
from pyworkflow import VERSION_1_1
from pyworkflow.protocol.params import IntParam, PointerParam, EnumParam, FileParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.em.convert import ImageHandler
from pyworkflow.protocol.constants import STEPS_PARALLEL
from pyworkflow.em.data import SetOfParticles, SetOfClasses2D

class ProtPrime2D(ProtMicrographs):
    """
    Simultaneous 2D alignment and clustering
    
    To find more information about Simple.Prime2D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'Prime2D'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL
    
    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputParticles', PointerParam, pointerClass='SetOfParticles', allowsNull=False,
                       label='Input Particles', important=True)
        form.addParam('mask', IntParam, default=36, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('clusters', IntParam, default=5, label='Number of clusters')
        form.addParallelSection(threads=4, mpi=1)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        deps = []
        particles = SetOfParticles(filename=self._getExtraPath("particles.mrc"))
        particleName = particles.getFileName()
        samplingRate = self.inputParticles.get().getSamplingRate()
        deps.append(self._insertFunctionStep('prime2DStep', particleName, samplingRate, prerequisites=[]))
        self._insertFunctionStep("createOutputStep", prerequisites=deps)
        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        inputPart = self.inputParticles.get()
        inputPart.writeStack(self._getExtraPath("particles.mrc"))


    def prime2DStep(self,partFile,SamplingRate):
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        params = self.getP2DParams(partFile, SamplingRate)

        self.runJob("simple_distr_exec", params, cwd=os.path.abspath(tmpDir))

        #Move output files to ExtraPath and rename them properly
        os.remove(os.path.abspath(self._getExtraPath("particles.mrc")))
        mvRoot1 = os.path.join(tmpDir, "cavgs_final.mrc")
        mvRoot2 = os.path.join(tmpDir,"prime2Ddoc_final.txt")
        moveFile(mvRoot1, self._getExtraPath(partName + "_cavgs_final.mrc"))
        moveFile(mvRoot2, self._getExtraPath(partName + "_prime2Ddoc_final.txt"))


    def getP2DParams(self, partF, SR):
        """Prepare the commmand line to call Prime2D program"""
        fn = os.path.abspath(partF)
        partitions = 1
        params = ' prg=prime2D stk=%s smpd=%f msk=%d ncls=%d ctf=no nparts=%d nthr=1' % (fn, SR, self.mask.get(), self.clusters.get(),
                                                                                         partitions)

        return params

    def createOutputStep(self):
        fh=open(self._getExtraPath("particles_prime2Ddoc_final.txt"))

        lines = []
        for line in fh.readlines():
            ang=0.0
            x=0.0
            y=0.0
            corr=0.0
            classId=0
            for token in line.split():
                if token.startswith("e3="):
                    ang=float(token[3:])
                elif token.startswith("x="):
                    x=float(token[2:])
                elif token.startswith("y="):
                    y=float(token[2:])
                elif token.startswith("corr="):
                    corr = float(token[5:])
                elif token.startswith("class="):
                    classId=int(float(token[6:]))
                    break

            lineItem = dict({"angle": ang, "class":classId, "xTranslation":x, "yTranslation":y, "corr":corr})
            lines.append(lineItem)
        fh.close()

        inputParticles = self.inputParticles.get()
        classes2DSet = self._createSetOfClasses2D(inputParticles)
        classes2DSet.classifyItems(updateItemCallback=self._updateParticle,
                                updateClassCallback=self._updateClass,
                                itemDataIterator=iter(lines))
        result = {'outputClasses': classes2DSet}
        self._defineOutputs(**result)
        # self._defineOutputs(outputClasses=classes2DSet)
        self._defineSourceRelation(self.inputParticles, classes2DSet)

    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

    #------------------------------- UTILS functions -------------------------------
    def _updateParticle(self, item, lineItem):

        # row = lineItem
        # item.setClassId(lineItem["class"])
        # For extra attributes
        # setattr(item ,"_simple_x", Integer(lineItem["x"])) or setattr(item ,"_simple_x", Float(lineItem["x"]))
        # or setattr(item ,"_simple_x", String(lineItem["x"]))

        classNum = lineItem["class"]
        item.setClassId(classNum)

    def _updateClass(self, item):
        classId = item.getObjId()
        avgFile = self._getExtraPath('particles_cavgs_final.mrc')
        rep = item.getRepresentative()
        rep.setSamplingRate(item.getSamplingRate())
        rep.setLocation(classId, avgFile)
        