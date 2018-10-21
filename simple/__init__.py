# **************************************************************************
# *
# * Authors:     Carlos Oscar Sorzano (coss@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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
# *  e-mail address 'coss@cnb.csic.es'
# *
# **************************************************************************

import os

import pyworkflow.em
import pyworkflow.utils as pwutils

from .constants import *


_logo = "simple_logo.png"
_references = ['Elmlund2013']


class Plugin(pyworkflow.em.Plugin):
    _homeVar = SIMPLE_HOME
    _pathVars = [SIMPLE_HOME]
    _supportedVersions = ['2.1']

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(SIMPLE_HOME, 'simple-2.1')
        cls._defineVar(SIMPLE_PRIME, 'simple_prime')

    @classmethod
    def getEnviron(cls):
        """ Return the environ settings to run Simple programs. """
        environ = pwutils.Environ(os.environ)

        SIMPLEBIN = cls.getHome('bin')
        environ.update({
            'SIMPLEBIN': SIMPLEBIN,
            'SIMPLEPATH': cls.getHome(),
            'SIMPLESYS': cls.getHome(),
            'PATH': SIMPLEBIN + os.pathsep + cls.getHome('apps')
        },
            position=pwutils.Environ.BEGIN)

        return environ

    @classmethod
    def getProgram(cls):
        """ Return the simple_prime binary that will be used. """
        return os.path.join(cls.getHome('bin'), cls.getVar(SIMPLE_PRIME))

    @classmethod
    def defineBinaries(cls, env):
        env.addPackage('simple', version='2.1',
                       tar='simple2.tgz',
                       default=True)

pyworkflow.em.Domain.registerPlugin(__name__)
