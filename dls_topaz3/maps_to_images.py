"""Will contain all the functions necessary for creating raw image files from the maps directories for machine learning"""

import numpy as np
import matplotlib.pyplot as plt


def slice_map(volume, slices_per_axis):
    """Slice the volume into 2d panes along x, y, z axes and return as an image stack"""

    # Check volume is equal in all directions
    assert (
        volume.shape[0] == volume.shape[1] == volume.shape[2]
    ), f"Please provide a volume which has dimensions of equal length, not {volume.shape[0]}x{volume.shape[1]}x{volume.shape[2]}"

    length = volume.shape[0]

    # Array to return the images
    image_stack = np.zeros((length, length, slices_per_axis*3))
    print(image_stack.shape)

    # Get x slices and put in image_stack
    for slice in range(slices_per_axis):
        image_stack[:, :, slice] = volume[(slice+1)*int((length)/(slices_per_axis+1)), :, :]

    # Get y slices and put in image_stack
    for slice in range(slices_per_axis):
        image_stack[:, :, slice + slices_per_axis] = volume[:, (slice+1)*int((length)/(slices_per_axis+1)), :]

    # Get z slices and put in image_stack
    for slice in range(slices_per_axis):
        image_stack[:, :, slice + (slices_per_axis*2)] = volume[:, :, (slice+1)*int((length)/(slices_per_axis+1))]

    return image_stack

def sphere(shape, radius, position):
    """Test function from stack overflow to create a sphere"""
    # assume shape and position are both a 3-tuple of int or float
    # the units are pixels / voxels (px for short)
    # radius is a int or float in px
    semisizes = (radius,) * 3

    # genereate the grid for the support points
    # centered at the position indicated by position
    grid = [slice(-x0, dim - x0) for x0, dim in zip(position, shape)]
    position = np.ogrid[grid]
    # calculate the distance of all points from `position` center
    # scaled by the radius
    arr = np.zeros(shape, dtype=float)
    for x_i, semisize in zip(position, semisizes):
        arr += (np.abs(x_i / semisize) ** 2)
    # the inner part of the sphere will have distance below 1
    return arr <= 1.0

if __name__ == "__main__":

    s1 = sphere((201, 201, 201), 80, (100, 100, 100))

    stack1 = slice_map(s1, 1)
    print(stack1.shape)
    stack2 = slice_map(s1, 2)
    print(stack2.shape)
    stack3 = slice_map(s1, 3)
    print(stack3.shape)

    fig, ((ax11, ax12, ax13), (ax21, ax22, ax23), (ax31, ax32, ax33)) = plt.subplots(3, 3)

    ax11.imshow(stack1[:, :, 0])

    ax21.imshow(stack2[:, :, 0])
    ax22.imshow(stack2[:, :, 1])

    ax31.imshow(stack3[:, :, 0])
    ax32.imshow(stack3[:, :, 1])
    ax33.imshow(stack3[:, :, 2])

    plt.show()
