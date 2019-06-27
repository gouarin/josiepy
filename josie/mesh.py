# josiepy
# Copyright © 2019 Ruben Di Battista
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

""" This module contains the primitives related to the mesh generation """

import numpy as np


class Mesh:
    """ This class handles the mesh generation over a domain.

    Parameters:
        left: The left BoundaryCurve
        bottom: The bottom BoundaryCurve
        right: The right BoundaryCurve
        top: The right BoundaryCurve

    """

    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def generate(self, num_xi, num_eta):
        """ This methods generates the mesh within the four given
        BoundaryCurve

        Args:
            num_xi: Number of elements in xi-direction
            num_eta: Number of elements in eta-direction
        """

        xis = np.linspace(0, 1, num_xi)
        etas = np.linspace(0, 1, num_eta)

        x = np.empty((len(xis), len(etas)))
        y = np.empty((len(xis), len(etas)))

        for i, xi in enumerate(xis):
            for j, eta in enumerate(etas):
                xl, yl = self.left(eta)
                xr, yr = self.right(eta)
                xb, yb = self.bottom(xi)
                xt, yt = self.top(xi)
                xb0, yb0 = self.bottom(0)
                xb1, yb1 = self.bottom(1)
                xt0, yt0 = self.top(0)
                xt1, yt1 = self.top(1)

                x[i, j] = \
                    (1-xi)*xl + xi*xr + \
                    (1-eta)*xb + eta*xt - \
                    (1-xi)*(1-eta)*xb0 - (1-xi)*eta*xt0 - \
                    (1-eta)*xi*xb1 - xi*eta*xt1

                y[i, j] = \
                    (1-xi)*yl + xi*yr + \
                    (1-eta)*yb + eta*yt - \
                    (1-xi)*(1-eta)*yb0 - (1-xi)*eta*yt0 - \
                    (1-eta)*xi*yb1 - xi*eta*yt1

        return (x, y)
