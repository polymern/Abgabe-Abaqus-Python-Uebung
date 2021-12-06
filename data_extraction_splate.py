# data extraction
# S. Pistor, 2021-12-05
# execfile("data_extraction_splate.py")

from __future__ import division
from abaqus import *
from abaqusConstants import *
from caeModules import *
import numpy as np
from os import path,getcwd
from splate import model_name,part_name,job_name,notchtype

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
