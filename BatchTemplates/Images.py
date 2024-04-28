#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from ase.io import read, write
from ase.visualize import view
import os, sys


def main(filerec, index, voxl_size, axis, x_min, y_min,
         x_max, y_max, units, filename=None, _rotate=False):
    """
    Parameters:
    filerec: LabCore file record, containing 3D data in numpy array format
    index: index at which slice is made
    voxl_size: size of voxel in units
    axis: axis along which slice is made
    x_min: lower range of index in x direction
    y_min: lower range of index in y direction
    x_max: upper range of index in x direction
    y_max: upper range of index in y direction
    units: the units of voxl size
    filename: the png filename to store
    _rotate: rotate the data 180 to match exp directions
    """
    from matplotlib import pyplot as plt
    import numpy as np
    
    # data sanitisation
    index = int(index)
    voxl_size = list(map(float, voxl_size))
    if len(voxl_size) == 1:
        voxl_size *= 3
    axis = int(axis)
    x_min = int(x_min)
    y_min = int(y_min)
    
    if x_max == 'None':
        x_max = None
    elif x_max is not None:
        x_max = int(x_max)
    
    if y_max == 'None':
        y_max = None
    elif y_max is not None:
        y_max = int(y_max)
    
    # data = filerec['data']
    data = filerec
    if _rotate:
        data = np.rot90(data, 2)
    if filename is None:
        filename = '.'.join(filerec.split('.')[:-1])
    a = tuple([slice(None) if i != axis else index for i in range(3)])
    img = data[a]
    a = tuple([slice(x_min, x_max), slice(y_min, y_max)])
    img = img[a]

    plt.imshow(img.T,
           #interpolation=None,
           origin='lower',
           cmap=plt.cm.Greys_r
          )
    ind = [1, 0, 0][axis]
    x = np.arange(0, img.shape[0] * voxl_size[ind], voxl_size[ind])
    nx = x.shape[0]
    n_labels = 5
    step_x = int(nx / (n_labels - 1))
    x_positions = np.arange(0 , nx, step_x)
    x_labels = x[::step_x]
    plt.xticks(x_positions, [f"{i:.2f}" for i in x_labels])
    plt.xlabel(f"{['Y', 'X', 'X'][axis]} {units}")
    
    ind = [2, 2, 1][axis]
    x = np.arange(0, img.shape[1] * voxl_size[ind], voxl_size[ind])
    nx = x.shape[0]
    n_labels = 5
    step_x = int(nx / (n_labels - 1))
    x_positions = np.arange(0 , nx, step_x)
    x_labels = x[::step_x]
    plt.yticks(x_positions, [f"{i:.2f}" for i in x_labels])
    plt.ylabel(f"{['Z', 'Z', 'Y'][axis]} {units}")
    
    plt.title(f"{['X', 'Y', 'Z'][axis]} at {index * voxl_size[axis]:.2f}{units}")
    if filename != 'dummy.png':
        plt.savefig(filename)


system=sys.argv[1]
if not os.path.exists(system):
    os.makedirs(system)
filerec = np.load('{}.npy'.format(system))
im_num = filerec.shape[-1]
for idx in range(im_num):
    if idx % 50 == 0:
        print(idx)
    if '_s6' in system:
        main(filerec, idx, [0.1], 2, 0, 0, None, None, 'A',
                '{}/{}_xy_{:.2f}_R.png'.format(system, system[:-3], idx*0.1), _rotate=True)
    else:
        main(filerec, idx, [0.1], 2, 0, 0, None, None, 'A',
        '{}/{}_xy_{:.2f}_R.png'.format(system, system, idx*0.1), _rotate=True)

