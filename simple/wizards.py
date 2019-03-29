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

from pyworkflow.em.constants import *
from pyworkflow.em.wizard import *
from .constants import *

from .protocols import (
    ProtInit3D, ProtCluster2D, ProtSym)


class Prime3DMaskWizard(ParticleMaskRadiusWizard):
    _targets = [(ProtInit3D, ['mask'])]

    def _getParameters(self, protocol):

        label, value = self._getInputProtocol(self._targets, protocol)

        protParams = {}
        protParams['input']= protocol.inputClasses
        protParams['label']= label
        protParams['value']= value
        return protParams

    def _getProvider(self, protocol):
        _objs = self._getParameters(protocol)['input']
        return ParticleMaskRadiusWizard._getListProvider(self, _objs)

    def show(self, form):
        params = self._getParameters(form.protocol)
        _value = params['value']
        _label = params['label']
        ParticleMaskRadiusWizard.show(self, form, _value, _label, UNIT_PIXEL)

class Cluster2DMaskWizard(ParticleMaskRadiusWizard):
    _targets = [(ProtCluster2D, ['mask'])]

    def _getParameters(self, protocol):

        label, value = self._getInputProtocol(self._targets, protocol)

        protParams = {}
        protParams['input']= protocol.inputParticles
        protParams['label']= label
        protParams['value']= value
        return protParams

    def _getProvider(self, protocol):
        _objs = self._getParameters(protocol)['input']
        return ParticleMaskRadiusWizard._getListProvider(self, _objs)

    def show(self, form):
        params = self._getParameters(form.protocol)
        _value = params['value']
        _label = params['label']
        ParticleMaskRadiusWizard.show(self, form, _value, _label, UNIT_PIXEL)

class SymmetryMaskWizard(ParticleMaskRadiusWizard):
    _targets = [(ProtSym, ['mask'])]

    def _getParameters(self, protocol):

        label, value = self._getInputProtocol(self._targets, protocol)

        protParams = {}
        protParams['input']= protocol.inputVol
        protParams['label']= label
        protParams['value']= value
        return protParams

    def _getProvider(self, protocol):
        _objs = self._getParameters(protocol)['input']
        return ParticleMaskRadiusWizard._getListProvider(self, _objs)

    def show(self, form):
        params = self._getParameters(form.protocol)
        _value = params['value']
        _label = params['label']
        ParticleMaskRadiusWizard.show(self, form, _value, _label, UNIT_PIXEL)

class SymGaussianVolumesWizard(GaussianVolumesWizard):
    _targets = [(ProtSym, ['lp'])]

    def _getParameters(self, protocol):

        label, value = self._getInputProtocol(self._targets, protocol)

        protParams = {}
        protParams['input']= protocol.inputVol
        protParams['label']= label
        protParams['value']= value
        return protParams

    def _getProvider(self, protocol):
        _objs = self._getParameters(protocol)['input']
        return GaussianVolumesWizard._getListProvider(self, _objs)

    def show(self, form):
        params = self._getParameters(form.protocol)
        _value = params['value']
        _label = params['label']
        GaussianVolumesWizard.show(self, form, _value, _label, UNIT_PIXEL_FOURIER)