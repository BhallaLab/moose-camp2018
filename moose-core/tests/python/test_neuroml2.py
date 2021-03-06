# -*- coding: utf-8 -*-
# test_neurom2.py, modified from run_cell.py
# Description:
# Author:
# Maintainer: P Gleeson, Dilawar Singh
# Version:
# URL:
# Keywords:
# Compatibility:
#
#

# Commentary:
#
#
#
#

# Change log:
#
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA.
#
#

# Code:

from __future__ import absolute_import, print_function, division

import moose
import moose.utils as mu
import sys
import os
import numpy as np

SCRIPT_DIR = os.path.dirname( os.path.realpath( __file__ ) )
    
def run( nogui = True ):
    global SCRIPT_DIR
    filename = os.path.join(SCRIPT_DIR, 'test_files/passiveCell.nml' )
    mu.info('Loading: %s' % filename )
    nml = moose.mooseReadNML2( filename )
    if not nml:
        mu.warn( "Failed to parse NML2 file" )
        return 

    assert nml, "Expecting NML2 object"
    msoma = nml.getComp(nml.doc.networks[0].populations[0].id,0,0)
    data = moose.Neutral('/data')
    pg = nml.getInput('pulseGen1')
    
    inj = moose.Table('%s/pulse' % (data.path))
    moose.connect(inj, 'requestOut', pg, 'getOutputValue')
    
    
    vm = moose.Table('%s/Vm' % (data.path))
    moose.connect(vm, 'requestOut', msoma, 'getVm')
    
    simtime = 150e-3
    moose.reinit()
    moose.start(simtime)
    print("Finished simulation!")
    t = np.linspace(0, simtime, len(vm.vector))
    yvec = vm.vector 
    injvec = inj.vector * 1e12
    m1, u1 = np.mean( yvec ), np.std( yvec )
    m2, u2 = np.mean( injvec ), np.std( injvec )
    assert np.isclose( m1, -0.0456943 ), m1
    assert np.isclose( u1, 0.0121968 ), u1
    assert np.isclose( m2, 26.64890 ), m2
    assert np.isclose( u2, 37.70607574 ), u2
    quit( 0 )

if __name__ == '__main__':
    run( )
