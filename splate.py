# Create special plate
# S. Pistor, 2021-12-05
# execfile("splate.py")

from __future__ import division
from abaqus import *
from abaqusConstants import *
from caeModules import *
from mesh import *
import numpy as np
import os
from os import path,getcwd
# from GPUtil import getGPUs

# -------------------------------------------------
# -------------------------------------------------
# names
model_name = 'specimen_plate'
sketch_name = 'plate_sketch'
part_name = 'plate'
material_name = 'PP'
instance_name = 'instance' + part_name
step_name = 'Step-DImp-' + part_name
job_name = 'Job-DImp-' + part_name
# -------------------------------------------------
# -------------------------------------------------
# Parameter units are in t / mm / s
# -------------------------------------------------
youngs_modulus = 1325
poissons_ratio = 0.45
density = 904e-12

h = 50.
h0 = 17.
b = 50.
b0 = 15.
xa = 30.0   #ya = 0.0 
ye = 30.0   #ye = 0.0

# choose shape of the dent that should be generated
# -------------------------------------------------
use_spline = False
if use_spline == True:
    # spline poitns [point1(xa,0.0), point2(x1,y1) point3(x2,y2) point4(0.0,ye)]
    x1,y1 = 7., 5.
    x2,y2 = 5., 7.
    notchtype = 1   # 1 = spline / 2 = arc / 3 = angle
# -------------------------------------------------
use_arc_with_radius = False
if use_arc_with_radius == True:
    r = 10.
    # caution values for xa and ye will be overwritten!
    xa = r
    ye = r
    notchtype = 2   # 1 = spline / 2 = arc / 3 = angle
# -------------------------------------------------
use_arc_with_3points = False
if use_arc_with_3points == True:
    x1,y1 = 3.11, 3.11
    notchtype = 2   # 1 = spline / 2 = arc / 3 = angle
# -------------------------------------------------
use_angle = True
if use_angle == True:
    x1,y1 = 15., 15.  # 0/3.75/7.5/11.25/15
    notchtype = 3   # 1 = spline / 2 = arc / 3 = angle
# -------------------------------------------------

# loadcase parameter
# -------------------------------------------------
u2 = 2.   # u2 = y-direction

# mesh parameter
# -------------------------------------------------
minSizeFactor=0.1
deviationFactor=0.1
size=1.

# step parameter
# -------------------------------------------------
timeInterval = 0.1  # write frequency for history and dield output

# job parameter
# -------------------------------------------------
numCpus = 8
numGpus = 1
auto_start = 'y'   # 'y' or 'yes' to autostart


# -------------------------------------------------
# -------------------------------------------------
# validity check for parameters
if b==0:
    raise ValueError('enter valid values for b')
elif h==0:
    raise ValueError('enter valid values for h')
elif use_spline == True:
    if b0 >= b:
        raise ValueError('b0 is either euqal to given value b or bigger')
    elif h0 >= h:
        raise ValueError('h0 is either euqal to given value h or bigger')
    elif b-b0 < xa:
        raise ValueError('b-b0 is to short for given value xa')
    elif h-h0 < ye:
        raise ValueError('h-h0 is to short for given value ye')
elif use_arc_with_radius == True:
    if r < xa:
        raise ValueError('r is to short for given value xa or bigger')
    elif r < xa:
        raise ValueError('r is to short for given value xa or bigger')
    elif r > b-b0:
        raise ValueError('r is to long to fit inbetween given values of b-b0')
    elif r > h-h0:
        raise ValueError('r is to long to fit inbetween given values of h-h0')
elif use_arc_with_3points == True:
    if x1 >= xa:
        raise ValueError('x1 must be smaller than xa')
    elif y1 >= ye:
        raise ValueError('y1 must be smaller than ye')
elif use_angle == True:
    if x1 >= xa:
        raise ValueError('x1 must be smaller than xa')
    elif y1 >= ye:
        raise ValueError('y1 must be smaller than ye')
# -------------------------------------------------
# -------------------------------------------------


# record coordinates
# -----------------------------------------------------------------
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)


# create blank model and rename it
# -----------------------------------------------------------------
Mdb()
mdb.models.changeKey(fromName='Model-1', toName=model_name) # rename model

m = mdb.models[model_name]


# create sketch
# -----------------------------------------------------------------
if h > b:
    m.ConstrainedSketch(name=sketch_name, sheetSize=h*3)
else:
    m.ConstrainedSketch(name=sketch_name, sheetSize=b*3)

s = mdb.models[model_name].sketches[sketch_name]

s.sketchOptions.setValues(gridOrigin=(0., 0.))

s.Line(point1=(xa, 0.), point2=(b-b0, 0.))
s.Line(point1=(b-b0, 0.), point2=(b-b0, -h0))
s.Line(point1=(b-b0, -h0), point2=(-b0, -h0))
s.Line(point1=(-b0, -h0), point2=(-b0, h-h0))
s.Line(point1=(-b0, h-h0), point2=(0., h-h0))
s.Line(point1=(0., h-h0), point2=(0., ye))

if use_angle == True:
    s.Line(point1=(xa, 0.), point2=(x1, y1))
    s.Line(point1=(x1, y1), point2=(0., ye))
    
if use_arc_with_3points == True:
    s.Arc3Points(point1=(xa, 0.), point2=(0., ye), point3=(3.11, 3.11))

if use_arc_with_radius == True:
    s.ArcByCenterEnds(center=(xa, ye), direction=CLOCKWISE, point1=(xa, 0.0), point2=(0.0, ye))
    
if use_spline == True:
    spline_points = [[xa,0.], [x1,y1], [x2,y2], [0.,ye]]
    s.Spline(points=spline_points)    


# create part
# -----------------------------------------------------------------
m.Part(dimensionality=TWO_D_PLANAR, name=part_name, type=DEFORMABLE_BODY)
p = mdb.models[model_name].parts[part_name]
p.BaseShell(sketch=s)

mat = mdb.models[model_name].Material(name=material_name)
mat.Elastic(table=((youngs_modulus, poissons_ratio), ))
# plastic_data = np.loadtxt(datapath)
# mat.Plastic(table= plastic_data)
mat.Density(table=((density, ), ))

p.DatumPlaneByPrincipalPlane(offset=0.0, principalPlane=XZPLANE)
p.DatumPlaneByPrincipalPlane(offset=0.0, principalPlane=YZPLANE)
p.PartitionFaceByDatumPlane(datumPlane=p.datums[p.datums.keys()[0]], faces=p.faces)
p.PartitionFaceByDatumPlane(datumPlane=p.datums[p.datums.keys()[1]], faces=p.faces)

m.HomogeneousSolidSection(material=material_name, name='Section-' + part_name, thickness=None)
p.Set(faces=p.faces, name='Set-' + part_name)
p.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=p.sets['Set-' + part_name], 
                    sectionName='Section-' + part_name, thicknessAssignment=FROM_SECTION)


# create step
# -----------------------------------------------------------------
m.ImplicitDynamicsStep(alpha=DEFAULT, amplitude=RAMP, 
    application=MODERATE_DISSIPATION, initialConditions=ON, initialInc=1e-06, 
    maxNumInc=100000, minInc=1e-12, name=step_name, nlgeom=ON, nohaf=OFF, 
    previous='Initial')

m.fieldOutputRequests['F-Output-1'].setValues(timeInterval=timeInterval)
m.historyOutputRequests['H-Output-1'].setValues(timeInterval=timeInterval)
m.fieldOutputRequests['F-Output-1'].setValues(variables=('S', ))


# partitioning part
# -----------------------------------------------------------------
root = m.rootAssembly

root.DatumCsysByDefault(CARTESIAN)
root.Instance(dependent=ON, name=instance_name, part=p)
inst = mdb.models[model_name].rootAssembly.instances[instance_name]

root.Set(edges= inst.edges.findAt(((-b0/2., h-h0, 0.), )), name='Set-Disp-' + part_name)
m.DisplacementBC(amplitude=UNSET, createStepName=step_name, distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None,
                name='BC-Disp-U2-' + part_name, region= m.rootAssembly.sets['Set-Disp-' + part_name], u1=UNSET, u2=u2 , ur3=UNSET)

root.Set(edges=inst.edges.findAt(((-b0, -h0/2., 0.), ), ((-b0, (h-h0)/2., 0.), ), ), name='Set-Disp-U1LCK-' + part_name)
m.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, 
                name='BC-Disp-U1LCK-' + part_name, region=m.rootAssembly.sets['Set-Disp-U1LCK-' + part_name], u1=SET, u2=UNSET, ur3=UNSET)

root.Set(edges= inst.edges.findAt(((-b0/2., -h0, 0.), ), (((b-b0)/2., -h0, 0.), ), ), name='Set-Disp-U2LCK-' + part_name)
m.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, 
                name='BC-Disp-U2LCK-' + part_name, region=m.rootAssembly.sets['Set-Disp-U2LCK-' + part_name], u1=UNSET, u2=SET, ur3=UNSET)


# generate mesh
# -----------------------------------------------------------------
p.seedPart(deviationFactor=deviationFactor, minSizeFactor=minSizeFactor, size=size)
p.setMeshControls(algorithm=ADVANCING_FRONT, elemShape=QUAD_DOMINATED, regions=p.faces)
p.generateMesh()
# use CPS6M for e.g. viscoelastic formulations!!!!
p.setElementType(regions=(p.faces, ), elemTypes=(ElemType(
    elemCode=CPS8, elemLibrary=STANDARD), ElemType(elemCode=CPS6, elemLibrary=STANDARD, secondOrderAccuracy=OFF, distortionControl=DEFAULT)))


# create job
# -----------------------------------------------------------------
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
    multiprocessingMode=DEFAULT, name=job_name, nodalOutputPrecision=SINGLE, 
    numCpus=numCpus, numDomains=numCpus, numGPUs=numGpus, queue=None, resultsFormat=ODB, scratch=
    '', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)


# automatically starts the job in Abaqus CAE and processes the data afterwards
# -----------------------------------------------------------------
if auto_start == 'yes' or auto_start == 'y':
    for job_tmp in mdb.jobs.keys():
        mdb.jobs[job_tmp].writeInput()

    for job_tmp in mdb.jobs.keys():
        mdb.jobs[job_tmp].submit(consistencyChecking=ON)
        mdb.jobs[job_tmp].waitForCompletion()
                
        
    # open the odb with the odb_name
    # -----------------------------------------------------------------
    odb_name = job_name
    odb = session.openOdb(name=odb_name+'.odb')
    vp = session.viewports['Viewport: 1']


    # extract max_principal_stress data and surface_area value
    # -----------------------------------------------------------------
    vp.odbDisplay.setPrimaryVariable(variableLabel='S', outputPosition=INTEGRATION_POINT,
                                    refinement=(INVARIANT, 'Max. Principal'),)

    max_principal_stress = np.array([i.maxPrincipal for i in odb.steps['Step-DImp-plate'].frames[-1].fieldOutputs['S'].values])

    sum_max_principal_stress = np.sum(max_principal_stress)

    p = mdb.models[model_name].parts[part_name]
    surface_area = p.getArea(p.faces)


    # writing data to file
    # -----------------------------------------------------------------
    if notchtype == 1:
        outfile_name = 'notchtype-spline_data.dat'
    elif notchtype == 2:
        outfile_name = 'notchtype-arc_data.dat'
    elif notchtype == 3:
        outfile_name = 'notchtype-angle_data.dat'
        
    outfile_path = path.join(getcwd(), outfile_name)

    output = np.array([[sum_max_principal_stress, surface_area]])
    output_string = '%1.6f %1.6f\n' % (output[0][0],output[0][1])    # \n' is important when compared with the whole list. otherwise %1.6f ' with blank space will suffice
    fmt = '%1.6f', '%1.6f'    # number format in saved in file

    if path.isfile(outfile_path) == False:
        
        np.savetxt(outfile_name, output, fmt=fmt, header='sum of max. princ. s. 75avg (MPa) / surface Area (mm^2)')

    elif path.isfile(outfile_path) == True:
        
        with open(outfile_path, 'r') as comparisson_file:
            if output_string not in comparisson_file.readlines():
                comparisson_file.close()    # close comparrison_file so that it can't possible interfere when opening outfile
                
                with open(outfile_path, 'a') as outfile:
                    np.savetxt(outfile, output, fmt=fmt)
                outfile.close()
                
            else:
                comparisson_file.close()
