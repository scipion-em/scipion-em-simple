# **************************************************************************
# *
# * Authors:     Mikel Iceta (miceta@cnb.csic.es)
# *
# * Natl Center for Biotechnology CNB-CSIC
# * NY Structural Biology Center (NYSBC)
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
# * All comments concerning this program package may be sent to the
# * e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

SIMPLE_HOME = 'SIMPLE_HOME'

# Supported versions
V3_0_0 = '3.0.0'
V3_1_BETA = '3.1-beta'
V4_0_0 = '4.0.0'

VERSIONS = [V3_0_0, V3_1_BETA, V4_0_0]
SIMPLE_DEFAULT_VER_NUM = V4_0_0

# Home folder default for selected version
DEFAULT_HOME = f'SIMPLE-{SIMPLE_DEFAULT_VER_NUM}'

DEFAULT_ENV_NAME = f'simple-{SIMPLE_DEFAULT_VER_NUM}'
DEFAULT_ACTIVATION_CMD = 'conda activate ' + DEFAULT_ENV_NAME
SIMPLE_ENV_ACTIVATION = 'SIMPLE_ENV_ACTIVATION'

# Git source per supported version
SIMPLE_GIT_URL = 'https://github.com/hael/SIMPLE.git'
SIMPLE_GIT_REFS = {
	V3_0_0: 'v3.0.0',
	V3_1_BETA: 'v3.1-beta',
	V4_0_0: '3318d60',
}

# Build/runtime dependencies based on SIMPLE README and compile_conda.sh
SIMPLE_CONDA_PACKAGES = [
	'python=3.10',
	'cmake',
	'gcc=15.2.0',
	'gxx=15.2.0',
	'gfortran=15.2.0',
	'fftw',
	'libtiff',
	'jbig',
	'jpeg',
	'openblas',
	'lapack',
	'arpack',
	'libcurl',
	'pip',
]

# Python tools used by SIMPLE scripts/NICE utilities
SIMPLE_PIP_PACKAGES = [
	'numpy',
	'mrcfile',
	'matplotlib',
	'pandas',
	'pillow',
	'reportlab',
	'django==5.2.5',
	'pytailwindcss==0.2.0',
	'dirsync==2.2.6',
	'gunicorn==23.0.0',
]

SIMPLE_PIP_PACKAGES_LINUX = [
	'pysqlite3-binary==0.5.4',
]
