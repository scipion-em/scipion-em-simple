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
from pyworkflow.protocol.params import IntParam, PointerParam
from pyworkflow.em.protocol import ProtClassify2D
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.em.convert import ImageHandler
from pyworkflow.protocol.constants import LEVEL_ADVANCED
from pyworkflow.em.data import SetOfParticles
import simple

class ProtCluster2D(ProtClassify2D):
    """
    Simultaneous 2D alignment and clustering
    
    To find more information about Simple.Prime2D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'cluster2D'
    
    def __init__(self,**kwargs):
        ProtClassify2D.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputParticles', PointerParam, pointerClass='SetOfParticles', allowsNull=False,
                       label='Input Particles', important=True)
        form.addParam('mask', IntParam, default=36, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('clusters', IntParam, default=5, label='Number of clusters')
        form.addParam('maxIter', IntParam, default=0, label='Iterations', help='maximum # iterations',
                      expertLevel=LEVEL_ADVANCED)
        form.addParallelSection(threads=4, mpi=0)

                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        self._insertFunctionStep('prime2DStep')
        self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        inputPart = self.inputParticles.get()
        inputPart.writeStack(self._getExtraPath("particles.mrc"))


    def prime2DStep(self):
        partFile = self._getExtraPath("particles.mrc")
        SamplingRate = self.inputParticles.get().getSamplingRate()
        kV = self.inputParticles.get().getAcquisition().getVoltage()
        partitions = 1
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        paramsOri='prg=print_project_field oritype=ptcl2D > oritab.txt'
        paramsImp = 'prg=import_particles cs=2.7 ctf=no fraca=0.1 kv=%f smpd=%f stk=%s' %(kV, SamplingRate, os.path.abspath(partFile))
        paramsC2D = 'prg=cluster2D msk=%d ncls=%d nparts=%d nthr=%d' % (self.mask.get(), self.clusters.get(),
                                                                      partitions, self.numberOfThreads.get())
        if self.maxIter.get() > 0:
            paramsC2D = paramsC2D + (' maxits=%d' % self.maxIter.get())

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsImp, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.distr_exec(), paramsC2D, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsOri, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())

        #Move output files to ExtraPath and rename them properly
        lastIter = self.getLastIteration(tmpDir)
        os.remove(os.path.abspath(self._getExtraPath("particles.mrc")))
        mvRoot1 = os.path.join(tmpDir+'/temp/2_cluster2D', "cavgs_iter%03d.mrc" %lastIter)
        mvRoot2 = os.path.join(tmpDir+'/temp',"oritab.txt")
        # moveFile(mvRoot1, self._getExtraPath(partName + "_cavgs_final.mrc"))
        ih = ImageHandler()
        ih.convert(mvRoot1, self._getExtraPath(partName + "_cavgs_final.mrcs"))
        moveFile(mvRoot2, self._getExtraPath(partName + "_oritab.txt"))
        cleanPath(tmpDir)

    def createOutputStep(self):
        fh=open(self._getExtraPath("particles_oritab.txt"))

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
        item.setAlignment2D()
        avgFile = self._getExtraPath('particles_cavgs_final.mrcs')
        rep = item.getRepresentative()
        rep.setSamplingRate(item.getSamplingRate())
        rep.setLocation(classId, avgFile)

    def getLastIteration(self,tmpDir):
        lastIter = 1
        pattern = tmpDir+'/temp/2_cluster2D/cavgs_iter%03d.mrc'
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1
        