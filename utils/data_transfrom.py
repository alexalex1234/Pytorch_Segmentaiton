import numpy as np
import os
from PIL import Image
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

import collections
import torch
import torchvision
from scipy import linalg
import scipy.ndimage as ndi
from six.moves import range


def img_to_array(img):

    img = np.array(img).astype(float)
    if len(img.shape) == 3:
        img = img.transpose(2,0,1)
    elif len(img.shape) == 2:
        img = np.expand_dims(img,axis=0)

    return img

def transform_matrix_offset_center(matrix, x, y):
    o_x = float(x) / 2 + 0.5
    o_y = float(y) / 2 + 0.5
    offset_matrix = np.array([[1, 0, o_x], [0, 1, o_y], [0, 0, 1]])
    reset_matrix = np.array([[1, 0, -o_x], [0, 1, -o_y], [0, 0, 1]])
    transform_matrix = np.dot(np.dot(offset_matrix, matrix), reset_matrix)
    return transform_matrix


def apply_transform(x, transform_matrix, channel_axis=0, fill_mode='nearest', cval=0.):
    x = np.rollaxis(x, channel_axis, 0)
    final_affine_matrix = transform_matrix[:2, :2]
    final_offset = transform_matrix[:2, 2]
    channel_images = [ndi.interpolation.affine_transform(x_channel, final_affine_matrix,
                                                         final_offset, order=0, mode=fill_mode, cval=cval) for x_channel in x]
    x = np.stack(channel_images, axis=0)
    x = np.rollaxis(x, 0, channel_axis + 1)
    return x
def flip_axis(x, axis):
    x = np.asarray(x).swapaxes(axis, 0)
    x = x[::-1, ...]
    x = x.swapaxes(0, axis)
    return x

def pair_random_crop(img,label,crop_size):
    w = img.shape[2]
    h =img.shape[1]
    np.random.seed(None)
    rangew = (w - crop_size)//2
    rangeh = (h - crop_size)//2
    offsetw = 0 if rangew == 0 else np.random.randint(rangew)
    offseth = 0 if rangeh == 0 else np.random.randint(rangeh)
    img = img[:,offseth:offseth+crop_size,offsetw:offsetw+crop_size]
    label = label[:,offseth:offseth+crop_size,offsetw:offsetw+crop_size]
    return img ,label

def standardlize(img):

    img[2,:,:] -= 104.008
    img[1,:,:] -= 116.669
    img[0,:,:] -= 122.675

    return img
def random_channel_shift(x, intensity, channel_axis=0):
    x = np.rollaxis(x, channel_axis, 0)
    min_x, max_x = np.min(x), np.max(x)
    channel_images = [np.clip(x_channel + np.random.uniform(-intensity, intensity), min_x, max_x)
                      for x_channel in x]
    x = np.stack(channel_images, axis=0)
    x = np.rollaxis(x, 0, channel_axis + 1)
    return x
