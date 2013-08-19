#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import subprocess
import numpy as np
from PIL import Image
from itertools import product

cow_fn, bkg_fn = "cow.png", "photo.jpg"
cow = np.array(Image.open(cow_fn))
bkg = Image.open(bkg_fn)
bkg.thumbnail((600, 600))
bkg = np.array(bkg)

height, width, channels = bkg.shape
cow_height, cow_width, cow_channels = cow.shape
cow_aspect = cow_height / cow_width

widths = np.arange(0.01 * width, 0.5 * width, dtype=int)
xs = np.vstack([np.zeros_like(widths), widths]).T
ys = cow_aspect * xs
xs = (xs, width - xs)
ys = (ys, height - ys)
best = (np.inf, )

for x, y in product(xs, ys):
    for xi, yi in zip(x, y):
        ff = ""
        if xi[0] < xi[1]:
            ff += "-flop "
        if yi[0] < yi[1]:
            ff += "-flip "

        xi = np.sort(xi)
        yi = np.sort(yi)

        block = bkg[yi[0]:yi[1], xi[0]:xi[1]]
        area = (xi[1] - xi[0]) * (yi[1] - yi[0])
        v = np.sqrt(np.sum([np.var(block[:, :, j])/area for j in range(3)]))
        if v < best[0]:
            best = (v, xi, yi, ff)

v, x, y, flipflop = best
cmd = ("convert \\( {bkg_fn} -resize {width}x{height} \\) "
       "\\( {cow_fn} {flipflop} -geometry {w}x{h}+{x}+{y} \\) "
       "-composite test.png").format(width=int(width),
                                     height=int(height),
                                     bkg_fn=bkg_fn,
                                     cow_fn=cow_fn,
                                     w=int(x[1]-x[0]),
                                     x=int(x[0]),
                                     h=int(y[1]-y[0]),
                                     y=int(y[0]),
                                     flipflop=flipflop)

subprocess.check_call(cmd, shell=True)
