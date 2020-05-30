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

# x = np.arange(width)
# y = np.arange(height)
# X, Y = np.meshgrid(x, y)

def scale(x, newmin=0., newmax=1.):
    oldmin, oldmax = x.min(), x.max()
    return (x - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


x = np.linspace(0, width, width)
y = np.linspace(0, height, height)
X, Y = np.meshgrid(x, y)
a = scale(np.sin(X * Y))
# a = np.random.random(shape).T

print(a.shape)


fig, ax = plt.subplots(figsize=(width / 100, height / 100), frameon=False, dpi=100)
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
# quad_mesh = ax.pcolormesh(X, Y, a.T, cmap='viridis')
quad_mesh = ax.pcolormesh(X, Y, a, cmap='viridis')
# rect = Rectangle((0, 0), 50, 50, linewidth=0, facecolor='black', alpha=0.3)
# rect = Rectangle((0, 0), width // 3, height, linewidth=0, facecolor='black', alpha=0.3)
# ax.add_patch(rect)
# ax.grid(False)
# ax.axis('off')
# ax.semilogy()

# plt.show()
# fig.savefig('/Users/tandav/Desktop/img/1.png', format='rgb', dpi=100)
# fig.savefig('/Users/tandav/Desktop/img/1.png', format='rgba', dpi=100)
# subprocess.run(('open', '/Users/tandav/Desktop/img/1.png'))


OUTPUT_VIDEO = '/Users/tandav/Desktop/rect.mp4'

cmd = (
    'ffmpeg',
    '-loglevel', 'info',
    '-hwaccel', 'videotoolbox',
    '-threads', '16',
    '-y', '-r', '30',  # overwrite, 60fps
    '-s', f'{width}x{height}',  # size of image string
    '-f', 'rawvideo',
    # '-pix_fmt', 'argb', # format
    '-pix_fmt', 'rgba',  # format
    # '-pix_fmt', 'rgb24', # format
    # '-f', 'image2pipe',
    # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
    '-i', '-',  # tell ffmpeg to expect raw video from the pipe
    # '-i', INPUT_AUDIO,
    '-c:v', 'hevc_videotoolbox',
    # '-c:v', 'libx264',
    # '-pix_fmt', 'yuv420p',
    '-tag:v', 'hvc1', '-profile:v', 'main10',
    '-b:v', '16M',
    # '-b:v', '1M',
    # '-b:v', '100k',
    '-shortest',
    OUTPUT_VIDEO,
)

ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=10 ** 8)


for i in range(20):
    rect = Rectangle((i, i * 20), 50, 50, linewidth=0, facecolor='black', alpha=0.5)
    ax.add_patch(rect)

    # rect.set_bounds((0, 0, i*20, height))
    # rect.set_bounds(random.choice(100, 200), random.randint(0, 200), 50, 50) # left, bottom, width, height
    # rect.set_bounds(i, random.randint(0, 200), 50, 50) # left, bottom, width, height
    # rect.set_xy((0, random.randint(0, 200)))


    # rect.set_width(i * 20)

    fig.savefig(ffmpeg.stdin, format='rgba', dpi=100)
    # fig.savefig(ffmpeg.stdin, dpi=100)
    print('task.i:', i)
    # fig.savefig('/Users/tandav/Desktop/img/0.png', format='rgba', dpi=100)
    # fig.savefig('/Users/tandav/Desktop/img/0.png', dpi=100)
    # fig.savefig('/Users/tandav/Desktop/img/1.png', format='rgba', dpi=100)
    # fig.savefig('/Users/tandav/Desktop/img/1.png', dpi=100)
    rect.remove()



ffmpeg.communicate()
# out, err = ffmpeg.communicate()

subprocess.run(('open', OUTPUT_VIDEO))