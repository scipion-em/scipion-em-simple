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

import pwem
import pyworkflow.utils as pwutils
from pyworkflow import Config, SPA

from constants import *

_logo = "simple_logo.png"
_references = ['Elmlund2013']

class Plugin(pwem.Plugin):
    _homeVar = SIMPLE_HOME
    _pathVars = [SIMPLE_HOME]
    _supportedVersions = VERSIONS
    _url = "https://github.com/scipion-em/scipion-em-simple"
    _processingField = [SPA]

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(SIMPLE_HOME, DEFAULT_HOME)
        cls._defineVar(SIMPLE_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)

    @classmethod
    def getDependencies(cls):
        """Return required programs for SIMPLE installation."""
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = ['git']
        if not condaActivationCmd:
            neededProgs.append('conda')
        return neededProgs

    @classmethod
    def getSimpleEnvActivation(cls):
        """Remove scipion home and activate the conda environment."""
        activation = cls.getVar(SIMPLE_ENV_ACTIVATION)
        scipionHome = Config.SCIPION_HOME + os.path.sep
        return activation.replace(scipionHome, "", 1)

    @classmethod
    def getActivationCmd(cls):
        """Return the activation command."""
        return '%s %s' % (cls.getCondaActivationCmd(),
                          cls.getSimpleEnvActivation())

    @classmethod
    def getEnviron(cls):
        """ Return the environ settings to run Simple programs. """
        environ = pwutils.Environ(os.environ)

        SIMPLEBIN = cls.getHome('build/bin')
        SIMPLEPATH = cls.getHome('build')
        PATH = '${'+SIMPLEPATH+'}/scripts:${'+SIMPLEPATH+'}/bin:${PATH}'
        environ.update({
            'SIMPLEBIN': SIMPLEBIN,
            'SIMPLE_PATH': SIMPLEPATH,
            'SIMPLE_QSYS': "local",
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
        condaPackages = ' '.join(SIMPLE_CONDA_PACKAGES)
        pipPackages = ' '.join(SIMPLE_PIP_PACKAGES)
        pipPackagesLinux = ' '.join(SIMPLE_PIP_PACKAGES_LINUX)

        for ver in cls._supportedVersions:
            gitRef = SIMPLE_GIT_REFS[ver]
            envName = f'simple-{ver}'
            simple_commands = [(
                ' '.join([
                    cls.getCondaActivationCmd(),
                    f'(conda run -n {envName} python -V >/dev/null 2>&1 || conda create -y -n {envName} -c conda-forge {condaPackages}) &&',
                    f'conda run -n {envName} python -m pip install --no-input --no-cache-dir {pipPackages} &&',
                    f'conda run -n {envName} bash -lc "if [ \"$(uname)\" = \"Linux\" ]; then python -m pip install --no-input --no-cache-dir {pipPackagesLinux}; fi" &&',
                    f'cd .. && (test -d SIMPLE-{ver} || git clone {SIMPLE_GIT_URL} SIMPLE-{ver}) &&',
                    f'git -C SIMPLE-{ver} fetch --all --tags && git -C SIMPLE-{ver} checkout {gitRef} &&',
                    f'conda run -n {envName} bash -lc "cd SIMPLE-{ver} && mkdir -p build && cd build && cmake ../ && make -j install"',
                ]),
                ['build/bin/gui']
            )]

            env.addPackage('SIMPLE', version=ver,
                           tar='void.tgz',
                           commands=simple_commands,
                           neededProgs=cls.getDependencies(),
                           default=ver == SIMPLE_DEFAULT_VER_NUM)
