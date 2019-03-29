# **************************************************************************
# *
# * Authors:     David Herreros
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
    _supportedVersions = ['3.0']

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(SIMPLE_HOME, 'SIMPLE-3.0')

    @classmethod
    def getEnviron(cls):
        """ Return the environ settings to run Simple programs. """
        environ = pwutils.Environ(os.environ)

        SIMPLEBIN = cls.getHome('build/bin')
        SIMPLEPATH = cls.getHome('build')
        PATH = '${'+SIMPLEPATH+'}/scripts:${'+SIMPLEPATH+'}/bin:${PATH}'
        environ.update({
            'SIMPLEBIN': SIMPLEBIN,
            'SIMPLEPATH': SIMPLEPATH,
            'SIMPLESYS': SIMPLEPATH,
            'PATH': PATH,
        },
            position=pwutils.Environ.BEGIN)

        return environ

    @classmethod
    def distr_exec(cls):
        """ Return the simple_prime binary that will be used. """
        return os.path.join(cls.getHome('build/bin'), 'simple_distr_exec')

    @classmethod
    def sim_exec(cls):
        """ Return the simple_prime binary that will be used. """
        return os.path.join(cls.getHome('build/bin'), 'simple_exec')

    @classmethod
    def defineBinaries(cls, env):

        simple_commands = [('mkdir build; cd build; cmake ../; make -j install', ['build/bin/gui'])]

        env.addPackage('SIMPLE', version='3.0',
                        tar='SIMPLE3.0.tgz',
                        commands=simple_commands,
                        default=True)

pyworkflow.em.Domain.registerPlugin(__name__)
