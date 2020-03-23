# josiepy
# Copyright © 2020 Ruben Di Battista
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY Ruben Di Battista ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Ruben Di Battista BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation
# are those of the authors and should not be interpreted as representing
# official policies, either expressed or implied, of Ruben Di Battista.
import abc
import numpy as np

from josie.solver.state import State

from .scheme import Scheme


class NonConservativeScheme(Scheme):
    r""" A mixin that provides the scheme implementation for the non
    conservative term

    A general problem can be written in a compact way:

    .. math::

        \pdeFull

    A concrete instance of this class needs to implement the discretization
    of the numerical flux on **one** face of a cell. It needs to implement
    the term :math:`\vb{G}\qty(\pdeState) = \numNonConservative`

    .. math::

        \numNonConservativeFull


    """

    def accumulate(
        self,
        values: State,
        neigh_values: State,
        normals: np.ndarray,
        surfaces: np.ndarray,
    ) -> State:

        # Compute fluxes computed eventually by the other schemes (e.g.
        # conservative)
        fluxes = super().accumulate(values, neigh_values, normals, surfaces)

        # Add nonconservative contribution
        B = 0.5 * (self.problem.B(values) + self.problem.B(neigh_values))
        G = self.G(values, neigh_values, normals, surfaces)
        fluxes += np.einsum("...ijk,...jk->...i", B, G)

        return fluxes

    @abc.abstractmethod
    def G(
        self,
        values: State,
        neigh_values: State,
        normals: np.ndarray,
        surfaces: np.ndarray,
    ) -> np.ndarray:
        r""" This is the nonconservative flux implementation of the scheme. See
        :cite:`toro` for a great overview on numerical methods for hyperbolic
        problems.

        A general problem can be written in a compact way:

        .. math::

            \pdeFull


        A concrete instance of this class needs to implement the discretization
        of the numerical flux on **one** face of a cell. It needs to implement
        the term :math:`\numNonConservative`

        .. math::

            \numNonConservativeFull

        Parameters
        ----------
        values
            The values of the state fields in each cell

        neigh_values
            The values of the state fields in the each neighbour of a cell

        normals
            The normal unit vectors associated to the face between each cell
            and its neigbour

        surfaces
            The surface values associated at the face between each cell and its
            neighbour

        Returns
        -------
        The value of the numerical nonconservative flux multiplied by
        the surface value :math:`\numNonConservative`

        """

        pass
