import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import subprocess
import multiprocessing
import random


width = 1920 // 2
height = 1080 // 2
shape = width, height

x = np.arange(width)
y = np.arange(height)
X, Y = np.meshgrid(x, y)
a = np.random.random(shape).T


fig, ax = plt.subplots(figsize=(width / 100, height / 100), frameon=False, dpi=100)
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
quad_mesh = ax.pcolormesh(X, Y, a, cmap='viridis')
ax.grid(False)
ax.axis('off')
# ax.semilogy()
rect = Rectangle((0, 0), 0, height, linewidth=0, facecolor='black', alpha=0.5)
ax.add_patch(rect)

OUTPUT_VIDEO = '/Users/tandav/Desktop/rect.mp4'

cmd = (
    'ffmpeg',
    '-loglevel', 'info',
    '-hwaccel', 'videotoolbox',
    '-threads', '16',
    '-y',
    '-r', '60',  # overwrite, 60fps
    '-s', f'{width}x{height}',  # size of image string
    '-f', 'rawvideo',
    '-pix_fmt', 'rgba',  # format
    '-i', '-',  # tell ffmpeg to expect raw video from the pipe
    '-c:v', 'hevc_videotoolbox',
    '-tag:v', 'hvc1', '-profile:v', 'main10',
    '-b:v', '16M',
    OUTPUT_VIDEO,
)

ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=10 ** 8)


for i in range(40):
    print('task.i:', i)
    rect.set_bounds((0, 0, i, height))
    fig.savefig(ffmpeg.stdin, format='rgba', dpi=100)



ffmpeg.communicate()
# out, err = ffmpeg.communicate()

subprocess.run(('open', OUTPUT_VIDEO))
