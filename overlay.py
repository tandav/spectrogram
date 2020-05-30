import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import subprocess
import multiprocessing


class color:
    RED   = lambda s: '\033[31m' + str(s) + '\033[0m'
    GREEN = lambda s: '\033[32m' + str(s) + '\033[0m'


def task(args):
    task_id, a, slice_ = args
    width, height = a.shape
    b = io.BytesIO()

    x = np.arange(width)
    y = np.arange(height)
    X, Y = np.meshgrid(x, y)


    fig, ax = plt.subplots(figsize=(width / 100, height / 100), frameon=False, dpi=100)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    quad_mesh = ax.pcolormesh(X, Y, a.T, cmap='viridis')
    ax.grid(False)
    ax.axis('off')
    # ax.semilogy()

    rect = Rectangle((0, 0), 0, height, linewidth=0, facecolor='black', alpha=0.5)
    ax.add_patch(rect)

    for i in range(slice_.start, slice_.stop):
        rect.set_bounds((0, 0, i, height))
        fig.savefig(b, format='rgba', dpi=100)
        print('task_id:', task_id, 'i', i)

    return task_id, b.getvalue()


# for i, chunk in enumerate(chunks):
#     if i % 10 == 0:
#         fps = (i - last_frame) / (time.time() - t)
#         print(f'{task_id} {i + 1} / {len(chunks)}, {round((i + 1) / len(chunk), 3)}, FPS: {fps}')
#         t = time.time()
#         last_frame = i
#     a = 20 * np.log10(np.abs(np.fft.rfft(chunk * win)))[:-1]
#     a = scale(a, newmin=0, newmax=30)
#     frame[i % frame_width, :] = a[:frame_height]
#     ff = frame.T
#     quad_mesh.set_array(ff[:-1, :-1].ravel())
#     fig.savefig(b, format='rgba', dpi=100)
#
# return task_id, b.getvalue()


def yield_block_slices(n, block_size=10):
    start = 0
    stop  = block_size

    while stop < n:
        yield slice(start, stop)
        start += block_size
        stop  += block_size


if __name__ == '__main__':

    width       = 1920
    height      = 1080
    shape       = width, height
    fpp         = 10  # frames per process
    n_processes = 16

    a = np.random.random(shape)

    # print(X.shape)
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
        # '-i', INPUT_AUDIO,
        '-c:v', 'hevc_videotoolbox',
        # '-c:v', 'libx264',
        # '-pix_fmt', 'yuv420p',
        '-tag:v', 'hvc1', '-profile:v', 'main10',
        '-b:v', '16M',
        # '-b:v', '1M',
        '-shortest',
        OUTPUT_VIDEO,
    )

    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=10 ** 8)

    with multiprocessing.Pool(processes=n_processes) as pool:
        _ = yield_block_slices(width, block_size=fpp)
        _ = enumerate(_)
        args = [(i, a, slice_) for i, slice_ in _]

        args = args[:20] # debug

        for task_id, b in pool.imap(task, args):
            print(color.RED('START task'), task_id)
            ffmpeg.stdin.write(b)
            print(color.GREEN('END task'), task_id)


    ffmpeg.communicate()
    # out, err = ffmpeg.communicate()

    subprocess.run(('open', OUTPUT_VIDEO))
