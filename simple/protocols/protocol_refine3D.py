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

class ProtRef3D(em.ProtRefine3D):
    """
    Ab initio reconstruction from Class Averages
    
    To find more information about Simple.Prime3D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'refine_3Dmodel'
    
    def __init__(self,**kwargs):
        em.ProtRefine3D.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputVol', PointerParam, label="Input volume",
                      important=True, pointerClass='Volume',
                      help="Input Volume")
        form.addParam('inputParticles', PointerParam, pointerClass='SetOfParticles', allowsNull=False,
                      label='Input Particles', important=True)
        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('symmetry', StringParam, default='c5', important=True, label='Point-group symmetry',
                      help='cn or dn. For icosahedral viruses, use c5. \n If no symmetry is present, give c1.')
        form.addParam('lp', FloatParam, default=0.5, expertLevel=LEVEL_ADVANCED,
                      label='Low pass limit', help='Low pass limit in normalized frequency (<0.5)')
        form.addParam('maxIter', IntParam, default=0, label='Iterations', help='maximum # iterations',
                      expertLevel=LEVEL_ADVANCED)
        form.addParallelSection(threads=4, mpi=0)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        self._insertFunctionStep('refine3DStep')
        self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------

    def convertInput(self):
        inputPart = self.inputParticles.get()
        inputPart.writeStack(self._getTmpPath("particles.mrc"))
        img = ImageHandler()
        img.convert(self.inputVol.get(), self._getTmpPath("recvol_state_00.mrc"))

    def refine3DStep(self):
        inputVol = self.inputVol.get()
        fnVol = os.path.abspath(self._getTmpPath("recvol_state_00.mrc"))

        #For testing purposes
        copyFile(self._getTmpPath("recvol_state_00.mrc"),self._getTmpPath("recvol_state_00_even.mrc"))
        copyFile(self._getTmpPath("recvol_state_00.mrc"),self._getTmpPath("recvol_state_00_odd.mrc"))

        tmpDir = self._getTmpPath("volume")
        makePath(tmpDir)

        partFile = self._getTmpPath("particles.mrc")
        # partName = os.path.basename(partFile)
        # partName = os.path.splitext(partName)[0]
        SamplingRate = self.inputParticles.get().getSamplingRate()
        kV = self.inputParticles.get().getAcquisition().getVoltage()

        maskRadius = self.mask.get()
        if maskRadius < 0:
            Xdim = inputVol.getDim()[0]
            maskRadius = Xdim / 2 - 1
        lpCutoff = inputVol.getSamplingRate()/self.lp.get()

        partitions = 1

        paramsRef = ' prg=refine3D vol1=%s msk=%d pgrp=%s lp=%f eo=yes nparts=%d nthr=%d' \
                    % (fnVol, maskRadius, self.symmetry.get(), lpCutoff, partitions, self.numberOfThreads.get())

        paramsOri = 'prg=print_project_field oritype=ptcl3D > oritab.txt'

        if self.maxIter.get() > 0:
            paramsRef = paramsRef + (' maxits=%d' % self.maxIter.get())

        paramsImp = 'prg=import_particles cs=2.7 ctf=no fraca=0.1 kv=%f smpd=%f stk=%s' % (
        kV, SamplingRate, os.path.abspath(partFile))

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.sim_exec(), paramsImp, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.distr_exec(), paramsRef, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        self.runJob(simple.Plugin.sim_exec(), paramsOri, cwd=os.path.abspath(tmpDir) + '/temp',
                    env=simple.Plugin.getEnviron())

        # Move output files to ExtraPath and rename them properly
        lastIter = self.getLastIteration()
        mvRoot = os.path.join(tmpDir,"temp","2_refine3D")
        moveFile(os.path.join(mvRoot,"recvol_state01_iter%03d.mrc" %lastIter),self._getExtraPath("volume.mrc"))
        moveFile(os.path.join(mvRoot,"recvol_state01_iter%03d_pproc.mrc" %lastIter),self._getExtraPath("volume_pproc.mrc"))
        moveFile(os.path.join(mvRoot,"recvol_state01_iter%03d_even.mrc" %lastIter),self._getExtraPath("volume_even.mrc"))
        moveFile(os.path.join(mvRoot,"recvol_state01_iter%03d_odd.mrc" %lastIter),self._getExtraPath("volume_odd.mrc"))
        moveFile(os.path.join(tmpDir,"temp","oritab.txt"), self._getExtraPath( "oritab.txt"))
        for i in range(1,lastIter+1):
            moveFile(os.path.join(mvRoot,"RESOLUTION_STATE01_ITER%03d"%i),self._getExtraPath("fsc%03d.txt"%i))

    def createOutputStep(self):

        fnAngles = self._getExtraPath("oritab.txt")
        fh = open(fnAngles)

        count = 0

        lines = []
        
        for line in fh.readlines():
            count += 1
            ang1 = 0.0
            ang2 = 0.0
            ang3 = 0.0
            x = 0.0
            y = 0.0
            for token in line.split():
                if token.startswith("e1="):
                    ang1 = float(token[3:])
                elif token.startswith("e2="):
                    ang2 = float(token[3:])
                elif token.startswith("e3="):
                    ang3 = float(token[3:])
                elif token.startswith("x="):
                    x = float(token[2:])
                elif token.startswith("y="):
                    y = float(token[2:])
                    break

            lineItem = dict({"alpha": ang1, "beta": ang2, "gamma": ang3, "xTrans": x, "yTrans": y, "id": count})
            lines.append(lineItem)

        fh.close()

        vol = em.Volume()
        vol.setLocation(self._getExtraPath('volume.mrc'))
        vol.setSamplingRate(self.inputParticles.get().getSamplingRate())
        self._defineOutputs(outputVol=vol)
        self._defineSourceRelation(self.inputParticles, vol)
        self._defineSourceRelation(self.inputVol, vol)

        if os.path.exists(fnAngles):
            imgSet = self.inputParticles.get()
            imgSetOut = self._createSetOfParticles()
            imgSetOut.copyInfo(imgSet)
            imgSetOut.setAlignmentProj()
            self.iterLines = iter(lines)
            self.lastLine = next(self.iterLines)
            imgSetOut.copyItems(imgSet,
                                updateItemCallback=self._updateItem)
            self._defineOutputs(outputParticles=imgSetOut)
            self._defineSourceRelation(self.inputParticles, imgSetOut)


    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

    # ------------------------------- UTILS functions -------------------------------

    def getLastIteration(self):
        lastIter = 1
        # pattern = self._getTmpPath('volume/temp/2_refine3D/recvol_state01_iter%03d.mrc')
        pattern = self._getTmpPath(os.path.join("volume","temp","2_refine3D","recvol_state01_iter%03d.mrc"))
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1

    def getLastIterationExtra(self):
        lastIter = 1
        pattern = self._getExtraPath("fsc%03d.txt")
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1

    def _updateItem(self, particle, row):
        count = 0

        while self.lastLine and particle.getObjId() == self.lastLine["id"]:
            count += 1
            if count:
                self._createItemMatrix(particle, self.lastLine)
            try:
                self.lastLine = next(self.iterLines)
            except StopIteration:
                self.lastLine = None

        particle._appendItem = count > 0



    def _createItemMatrix(self, particle, row):

        # sa, ca = np.sin(row["alpha"]), np.cos(row["alpha"])
        # sb, cb = np.sin(row["beta"]), np.cos(row["beta"])
        # sg, cg = np.sin(row["gamma"]), np.cos(row["gamma"])
        #
        # cc = cb * ca
        # cs = cb * sa
        # sc = sb * ca
        # ss = sb * sa
        #
        # A = np.identity(4)
        # A[0,0] = cg * cc - sg * sa
        # A[0,1] = cg * cs + sg * ca
        # A[0,2] = -cg * sb
        # A[1,0] = -sg * cc - cg * sa
        # A[1,1] = -sg * cs + cg * ca
        # A[1,2] = sg * sb
        # A[2,0] = sc
        # A[2,1] = ss
        # A[2,2] = cb

        from pyworkflow.em.transformations import euler_matrix
        angles = [row["alpha"],row["beta"],row["gamma"]]
        radAngles = -np.deg2rad(angles)

        M = euler_matrix(radAngles[0], radAngles[1], radAngles[2], 'szyz')

        M[0,3] = -row["xTrans"]
        M[1,3] = -row["yTrans"]

        M = np.linalg.inv(M)

        alignment = Transform()
        alignment.setMatrix(M)

        particle.setTransform(alignment)
