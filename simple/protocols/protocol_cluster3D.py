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

import os, glob, shutil
import pyworkflow.em as em
from pyworkflow import VERSION_1_1
from pyworkflow.protocol.params import PointerParam, IntParam, StringParam, FloatParam
# from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile, copyFile
from pyworkflow.protocol.constants import LEVEL_ADVANCED
from pyworkflow.em.convert import ImageHandler
import simple

from pyworkflow.em.data import Transform
import numpy as np

class ProtCluster3D(em.ProtClassify3D):
    """
    3D Classification
    
    To find more information about Simple.Prime3D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'cluster3D'
    
    def __init__(self,**kwargs):
        em.ProtClassify3D.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputParticles', PointerParam, pointerClass='SetOfParticles', allowsNull=False,
                      label='Input Particles', important=True)
        form.addParam('states', IntParam, default=3, label='Number of states')
        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('symmetry', StringParam, default='c5', important=True, label='Point-group symmetry',
                      help='cn or dn. For icosahedral viruses, use c5. \n If no symmetry is present, give c1.')
        form.addParam('lp', FloatParam, default=0.5, expertLevel=LEVEL_ADVANCED,
                      label='Low pass limit', help='Low pass limit in normalized frequency (<0.5)')
        form.addParam('maxIter', IntParam, default=0, label='Iterations', help='maximum # iterations',
                      expertLevel=LEVEL_ADVANCED)

        ### For testing purposes
        form.addParam('inputVol', PointerParam, label="Input volume",
                      important=True, pointerClass='Volume',
                      help="Input Volume")

        form.addParallelSection(threads=4, mpi=0)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        self._insertFunctionStep('cluster3DStep')
        self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------

    def convertInput(self):
        inputPart = self.inputParticles.get()
        inputPart.writeStack(self._getTmpPath("particles.mrc"))

        ### For testing purposes
        img = ImageHandler()
        img.convert(self.inputVol.get(), self._getTmpPath("recvol_state_00.mrc"))

    def cluster3DStep(self):
        partFile = self._getTmpPath("particles.mrc")
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        SamplingRate = self.inputParticles.get().getSamplingRate()
        kV = self.inputParticles.get().getAcquisition().getVoltage()
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        ### For testing purposes
        inputVol = self.inputVol.get()
        fnVol = os.path.abspath(self._getTmpPath("recvol_state_00.mrc"))
        copyFile(self._getTmpPath("recvol_state_00.mrc"), self._getTmpPath("recvol_state_00_even.mrc"))
        copyFile(self._getTmpPath("recvol_state_00.mrc"), self._getTmpPath("recvol_state_00_odd.mrc"))

        maskRadius = self.mask.get()
        if maskRadius < 0:
            Xdim = self.inputParticles.get().getDim()[0]
            maskRadius = Xdim / 2 - 1
        lpCutoff = SamplingRate/self.lp.get()

        partitions = 1

        paramsCl3D = ' prg=cluster3D nstates=%d msk=%d pgrp=%s lp=%f eo=yes nparts=%d nthr=%d' \
                    % (self.states.get(), maskRadius, self.symmetry.get(),
                       lpCutoff, partitions, self.numberOfThreads.get())

        ### For testing purposes
        paramsRef = ' prg=refine3D vol1=%s msk=%d pgrp=%s lp=%f eo=yes nparts=%d nthr=%d maxits=1' \
                    % (fnVol, maskRadius, self.symmetry.get(), lpCutoff, partitions, self.numberOfThreads.get())

        paramsOri = 'prg=print_project_field oritype=ptcl3D > oritab.txt'

        if self.maxIter.get() > 0:
            paramsCl3D = paramsCl3D + (' maxits=%d' % self.maxIter.get())

        paramsImp = 'prg=import_particles cs=2.7 ctf=no fraca=0.1 kv=%f smpd=%f stk=%s' % (
        kV, SamplingRate, os.path.abspath(partFile))

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.sim_exec(), paramsImp, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        ### For testing purposes
        self.runJob(simple.Plugin.distr_exec(), paramsRef, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.distr_exec(), paramsCl3D, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.sim_exec(), paramsOri, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        # Move output files to ExtraPath and rename them properly
        lastIter = self.getLastIteration()
        lastState = self.getLastState()
        mvRoot = os.path.join(tmpDir,"temp","3_cluster3D")
        for n in range(lastState):
            m = n+1
            moveFile(os.path.join(mvRoot,"recvol_state%02d_iter%03d.mrc" % (m, lastIter)),
                     self._getExtraPath("volume_state%02d.mrc" % m))
        moveFile(os.path.join(tmpDir,"temp","oritab.txt"), self._getExtraPath("oritab.txt"))

    def createOutputStep(self):

        fh = open(self._getExtraPath("oritab.txt"))

        lines = []
        for line in fh.readlines():
            ang = 0.0
            x = 0.0
            y = 0.0
            corr = 0.0
            stateId = 0
            for token in line.split():
                if token.startswith("e3="):
                    ang = float(token[3:])
                elif token.startswith("x="):
                    x = float(token[2:])
                elif token.startswith("y="):
                    y = float(token[2:])
                elif token.startswith("corr="):
                    corr = float(token[5:])
                elif token.startswith("state="):
                    stateId = int(float(token[6:]))
                    break

            lineItem = dict({"angle": ang, "state": stateId, "xTranslation": x, "yTranslation": y, "corr": corr})
            lines.append(lineItem)
        fh.close()

        inputParticles = self.inputParticles.get()
        classes3DSet = self._createSetOfClasses3D(inputParticles)
        classes3DSet.classifyItems(updateItemCallback=self._updateParticle,
                                   updateClassCallback=self._updateClass,
                                   itemDataIterator=iter(lines))
        result = {'outputClasses': classes3DSet}
        self._defineOutputs(**result)
        # self._defineOutputs(outputClasses=classes2DSet)
        self._defineSourceRelation(self.inputParticles, classes3DSet)


    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

    # ------------------------------- UTILS functions -------------------------------

    def getLastIteration(self):
        lastIter = 1
        pattern = self._getTmpPath(os.path.join("particles","temp","3_cluster3D","recvol_state01_iter%03d.mrc"))
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1

    def getLastState(self):
        lastState = 1
        pattern = self._getTmpPath(os.path.join("particles", "temp", "3_cluster3D", "recvol_state%02d_iter001.mrc"))
        while os.path.exists(pattern % lastState):
            lastState += 1
        return lastState - 1

    def _updateParticle(self, item, lineItem):

        # row = lineItem
        # item.setClassId(lineItem["class"])
        # For extra attributes
        # setattr(item ,"_simple_x", Integer(lineItem["x"])) or setattr(item ,"_simple_x", Float(lineItem["x"]))
        # or setattr(item ,"_simple_x", String(lineItem["x"]))

        stateNum = lineItem["state"]
        item.setClassId(stateNum)

    def _updateClass(self, item):
        stateId = item.getObjId()
        item.setAlignment3D()
        avgFile = self._getExtraPath('volume_state%02d.mrc' % stateId)
        rep = item.getRepresentative()
        rep.setSamplingRate(item.getSamplingRate())
        rep.setLocation(stateId, avgFile)
