# processing extracted data
# S. Pistor, 2021-12-05

from __future__ import division
import numpy as np
from os import path,getcwd,chdir,mkdir
import matplotlib.pyplot as plt
import glob 


def importData(infile):
    label = path.splitext(path.basename(infile))[0]
    
    try:
        header_length = 1
        data = np.loadtxt(infile, dtype=float, skiprows=header_length)
    except ValueError as ve:
        ve = str(ve)
        row_skip = int(''.join(filter(str.isdigit, ve)))

        print('ValueError: Attempt to continue reading file at line ' + str(header_length + row_skip))
            
        data = np.loadtxt(infile, dtype=float, skiprows=header_length + row_skip)
        
        print('Attempt to continue reading file at row ' + str(header_length + row_skip) + ' successful')
    
    data = np.array(sorted(list(data), key=lambda data:data[1],reverse=False))   
    
    plt.plot(data[:,1], data[:,0], '-', label=label)


def main():
    work_directory =  getcwd()  #r'D:\Dokumente\AbaqusDirectory\Abaqus und Python\Einheit 5'
    chdir(work_directory)

    infile_list = np.array(glob.glob(path.join(work_directory,r'notchtype-*_data.dat')))
    
    folderpath_plots = path.join(work_directory,'plots')    
    if path.exists(folderpath_plots) == False:
        mkdir(folderpath_plots)
    
     # =============================================================================   
    for infile in infile_list:
        importData(infile)

        title = path.splitext(path.basename(infile))[0]
        plt.title(title)
        plt.xlabel('surface area [mm^2]')
        plt.ylabel('sum(max principal stress) [MPa]')
        plt.savefig(path.join(folderpath_plots,title+'.png'), bbox_inches='tight', dpi=900)
        plt.close()
    # =============================================================================
    
    # =============================================================================
    plt.title('Combined Results')
    plt.xlabel('surface area [mm^2]')
    plt.ylabel('sum(max principal stress) [MPa]')
    
    for infile in infile_list:
        importData(infile)
        
    plt.legend(bbox_to_anchor=(0.425, -0.23),loc='center')
    plt.savefig(path.join(folderpath_plots,'combined'+'.png'), bbox_inches='tight', dpi=900)
    plt.close()
    # =============================================================================
    
if __name__ == '__main__':
    main()