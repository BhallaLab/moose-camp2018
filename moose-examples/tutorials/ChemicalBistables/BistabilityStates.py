#########################################################################
## This program is part of 'MOOSE', the
## Messaging Object Oriented Simulation Environment.
##           Copyright (C) 2013 Upinder S. Bhalla. and NCBS
## It is made available under the terms of the
## GNU Lesser General Public License version 2.1
## See the file COPYING.LIB for the full notice.
#########################################################################

# This demo explores state outcomes of potentially bistable system, with
# different parameters. It specially supports buffering of reagents so
# as to build up conc-effect curves.

import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider, Button, RadioButtons
import numpy
import moose
import sys
line1 = ""
line2 = ""
line3 = ""
ax2 = ""

solver = 'gsl'

def makeModel():
                # create container for model
                model = moose.Neutral( 'model' )
                compartment = moose.CubeMesh( '/model/compartment' )
                compartment.volume = 1e-21 # m^3
                # the mesh is created automatically by the compartment
                mesh = moose.element( '/model/compartment/mesh' ) 

                # create molecules and reactions
                a = moose.Pool( '/model/compartment/a' )
                b = moose.Pool( '/model/compartment/b' )
                c = moose.Pool( '/model/compartment/c' )
                enz1 = moose.Enz( '/model/compartment/b/enz1' )
                enz2 = moose.Enz( '/model/compartment/c/enz2' )
                cplx1 = moose.Pool( '/model/compartment/b/enz1/cplx' )
                cplx2 = moose.Pool( '/model/compartment/c/enz2/cplx' )
                reac = moose.Reac( '/model/compartment/reac' )

                # connect them up for reactions
                moose.connect( enz1, 'sub', a, 'reac' )
                moose.connect( enz1, 'prd', b, 'reac' )
                moose.connect( enz1, 'enz', b, 'reac' )
                moose.connect( enz1, 'cplx', cplx1, 'reac' )

                moose.connect( enz2, 'sub', b, 'reac' )
                moose.connect( enz2, 'prd', a, 'reac' )
                moose.connect( enz2, 'enz', c, 'reac' )
                moose.connect( enz2, 'cplx', cplx2, 'reac' )

                moose.connect( reac, 'sub', a, 'reac' )
                moose.connect( reac, 'prd', b, 'reac' )

                # Assign parameters
                a.concInit = 1
                b.concInit = 0
                c.concInit = 0.01
                enz1.kcat = 0.4
                enz1.Km = 4
                enz2.kcat = 0.6
                enz2.Km = 0.01
                reac.Kf = 0.0001
                reac.Kb = 0.001

                # Create the output tables
                graphs = moose.Neutral( '/model/graphs' )
                outputA = moose.Table2( '/model/graphs/concA' )
                outputB = moose.Table2( '/model/graphs/concB' )
                outputC = moose.Table2( '/model/graphs/concC' )

                # connect up the tables
                moose.connect( outputA, 'requestOut', a, 'getConc' );
                moose.connect( outputB, 'requestOut', b, 'getConc' );
                moose.connect( outputC, 'requestOut', c, 'getConc' );

def makeSolvers():
                stoich = moose.Stoich( '/model/compartment/stoich' )
                stoich.compartment = moose.element( '/model/compartment' )
                if ( solver == 'gssa' ):
                    gsolve = moose.Gsolve( '/model/compartment/ksolve' )
                    stoich.ksolve = gsolve
                else:
                    ksolve = moose.Ksolve( '/model/compartment/ksolve' )
                    stoich.ksolve = ksolve
                stoich.path = "/model/compartment/##"
                moose.setClock( 5, 1.0 ) # clock for the solver
                moose.useClock( 5, '/model/compartment/ksolve', 'process' )

def deleteSolvers():
                if ( moose.exists( 'model/compartment/stoich' ) ):
                    moose.delete( '/model/compartment/stoich' )
                    moose.delete( '/model/compartment/ksolve' )

def main():
                global solver
                makeModel()
                if ( len ( sys.argv ) == 2 ):
                    solver = sys.argv[1]
                makeSolvers() 
                runSim()
                makeDisplay()
                quit()

def updateAinit(val):
    moose.element( '/model/compartment/a' ).concInit = val
    updateDisplay()

def updateBinit(val):
    moose.element( '/model/compartment/b' ).concInit = val
    updateDisplay()

def updateCinit(val):
    moose.element( '/model/compartment/c' ).concInit = val
    updateDisplay()

def updateKcat1(val):
    moose.element( '/model/compartment/b/enz1' ).kcat = val
    updateDisplay()

def updateKcat2(val):
    moose.element( '/model/compartment/c/enz2' ).kcat = val
    updateDisplay()

def bufferFunc(val):
    deleteSolvers()
    if val == 'Buffering: None':
        moose.element( '/model/compartment/b' ).isBuffered = 0
        moose.element( '/model/compartment/c' ).isBuffered = 0
    elif val == 'B':
        moose.element( '/model/compartment/b' ).isBuffered = 1
        moose.element( '/model/compartment/c' ).isBuffered = 0
    elif val == 'C':
        moose.element( '/model/compartment/b' ).isBuffered = 0
        moose.element( '/model/compartment/c' ).isBuffered = 1
    makeSolvers()
    updateDisplay()

def updateDisplay():
    runSim()
    a = moose.element( '/model/graphs/concA' )
    b = moose.element( '/model/graphs/concB' )
    c = moose.element( '/model/graphs/concC' )
    line1.set_ydata( a.vector )
    line2.set_ydata( b.vector )
    line3.set_ydata( c.vector )
    ax2.relim()
    ax2.autoscale_view( True, True, True )

def doQuit( event ):
    quit()

def makeDisplay():
    global line1
    global line2
    global line3
    global ax2
    a = moose.element( '/model/graphs/concA' )
    b = moose.element( '/model/graphs/concB' )
    c = moose.element( '/model/graphs/concC' )
    img = mpimg.imread( 'simple_bistab.png' )
    #plt.ion()
    fig = plt.figure( figsize=(8,10) )
    png = fig.add_subplot(411)
    imgplot = plt.imshow( img )
    plt.axis('off')
    ax2 = fig.add_subplot(412)
    #ax.set_ylim( 0, 0.1 )
    plt.ylabel( 'Conc (mM)' )
    plt.xlabel( 'Time (s)' )
    ax2.autoscale( enable = True, axis = 'y' )
    plt.title( "States of system." )
    t = numpy.arange( 0, a.vector.size, 1 ) #sec
    line1, = ax2.plot( t, a.vector, 'r-', label = 'a' )
    line2, = ax2.plot( t, b.vector, 'b-', label = 'b' )
    line3, = ax2.plot( t, c.vector, 'g-', label = 'c' )
    plt.legend()
    ax = fig.add_subplot(414)
    plt.axis('off')
    axcolor = 'palegreen'
    axReset = plt.axes( [0.25,0.05, 0.30,0.03], facecolor='blue' )
    axQuit = plt.axes( [0.25,0.10, 0.30,0.03], facecolor='blue' )
    axBuffer = plt.axes( [0.60,0.05, 0.30,0.08], facecolor='yellow' )
    axAinit = plt.axes( [0.25,0.15, 0.65,0.03], facecolor=axcolor )
    axBinit = plt.axes( [0.25,0.20, 0.65,0.03], facecolor=axcolor )
    axCinit = plt.axes( [0.25,0.25, 0.65,0.03], facecolor=axcolor )
    axKcat2 = plt.axes( [0.25,0.30, 0.65,0.03], facecolor=axcolor )
    axKcat1 = plt.axes( [0.25,0.35, 0.65,0.03], facecolor=axcolor )
    #aInit = Slider( axAinit, 'A init conc', 0, 10, valinit=1.0, valstep=0.2)
    reset = Button( axReset, 'Reset', color = 'cyan' )
    q = Button( axQuit, 'Quit', color = 'pink' )
    aInit = Slider( axAinit, 'A init conc', 0, 10, valinit=1.0 )
    bInit = Slider( axBinit, 'B init conc', 0, 10, valinit=0.0 )
    cInit = Slider( axCinit, 'C init conc', 0, 0.1, valinit=0.01 )
    kcat2 = Slider( axKcat2, 'Kcat for enz2', 0, 2, valinit=0.6 )
    kcat1 = Slider( axKcat1, 'Kcat for enz1', 0, 2, valinit=0.4 )
    setBuffer = RadioButtons(axBuffer, ('Buffering: None', 'B', 'C'))
    def resetParms( event ):
        deleteSolvers()
        aInit.reset()
        bInit.reset()
        cInit.reset()
        kcat2.reset()
        kcat1.reset()
        makeSolvers()
        updateDisplay()
        


    reset.on_clicked( resetParms )
    q.on_clicked( doQuit )
    aInit.on_changed( updateAinit )
    bInit.on_changed( updateBinit )
    cInit.on_changed( updateCinit )
    kcat1.on_changed( updateKcat1 )
    kcat2.on_changed( updateKcat2 )
    setBuffer.on_clicked(bufferFunc)

    plt.show()

def runSim():
    moose.reinit()
    moose.start( 500.0 ) # Run the model for 500 seconds.


# Run the 'main' if this script is executed standalone.
if __name__ == '__main__':
        main()
