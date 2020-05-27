'''
todo: try save all into a buffer and pipe to ffmpeg all batch
maybe then gpu will be working


разбить по картинкам шириной frame_width
каждая картинка в отдельном треде через тредпул


todo: try переделать все-таки на concurrent.futures
'''

import matplotlib
# matplotlib.use('Qt5Agg', warn = False, force = True) # fps 4.8

import matplotlib.pyplot as plt
import subprocess
import numpy as np
import time
from scipy.io.wavfile import read
import concurrent.futures
import io
import itertools
import multiprocessing

def scale(x, newmin=0., newmax=1.):
    oldmin, oldmax = x.min(), x.max()
    return (x - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


# =================================================================================


def task(payload):
    task_id, chunks, nperseg, frame_width, frame_height, rate = payload
    b = io.BytesIO()
    frame = np.zeros((frame_width, frame_height))
    # frame = np.random.randint(7, 10, (frame_width, frame_height))

    #TODO # t_frame = np.linspace (0 + dt * fi, seconds / frames, frame_width)
    t_frame = np.linspace (0, 1, frame_width)
    # f_frame = np.geomspace(1, rate / 2, frame_height) # second arg: nperseg//2 (Nyquist limit)
    f_frame = np.fft.rfftfreq(nperseg, d = 1. / rate)[:-1][:frame_height]
    T_frame, F_frame = np.meshgrid(t_frame, f_frame)

    fig, ax = plt.subplots(figsize=(frame_width / 100, frame_height / 100), frameon=False, dpi=100)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ff = frame.T
    quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30) # shading='gouraud' nearest
    # quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='gouraud')
    # print(quad_mesh._A.shape)
    # quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='nearest')
    # ax.semilogy()
    ax.grid(False)
    ax.axis('off')

    t = time.time()
    last_frame = 0

    win = np.hanning(nperseg)

    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            fps = (i - last_frame) / (time.time() - t)
            print(f'{task_id} {i + 1} / {len(chunks)}, {round((i + 1) / len(chunk), 3)}, FPS: {fps}')
            t = time.time()
            last_frame = i
        a = 20 * np.log10(np.abs(np.fft.rfft(chunk * win)))[:-1]
        a = scale(a, newmin=0, newmax=30)
        frame[i % frame_width, :] = a[:frame_height]
        ff = frame.T
        quad_mesh.set_array(ff[:-1,:-1].ravel())
        fig.savefig(b, format='rgba', dpi=100)
#         fig.savefig(p.stdin, format='rgba', dpi=100)

    return b.getvalue()

# =================================================================================

# frame = np.zeros((frame_width, frame_height))
# # frame = np.random.randint(7, 10, (frame_width, frame_height))
#
# #TODO # t_frame = np.linspace (0 + dt * fi, seconds / frames, frame_width)
# t_frame = np.linspace (0, 1, frame_width)
# # f_frame = np.geomspace(1, rate / 2, frame_height) # second arg: nperseg//2 (Nyquist limit)
# f_frame = np.fft.rfftfreq(audio_rolled.shape[1], d = 1. / rate)[:-1][:frame_height]
# T_frame, F_frame = np.meshgrid(t_frame, f_frame)
#
#
# # fig = plt.figure(frameon=False, figsize=(4, 5), dpi=100)
#
# fig, ax = plt.subplots(figsize=(frame_width / 100, frame_height / 100), frameon=False, dpi=100)
# # fig = plt.figure() # todo: compute dpi
#
# # fig = plt.figure(figsize=(frame_width / 100, frame_height / 100), frameon=False, dpi=100) # todo: compute dpi
# # fig.subplots_adjust(left=0.1, bottom=0, right=0.9, top=1, wspace=None, hspace=None)
# fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
# ff = frame.T
#
# quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30) # shading='gouraud' nearest
# # quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='gouraud')
# print(quad_mesh._A.shape)
# # quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='nearest')
# # ax.semilogy()
# ax.grid(False)
# ax.axis('off')
#
# # ax.set_ylim(30, 2.5e3)
#
# # fig.show()
# # fig.canvas.draw()
#
#
# t = time.time()
# last_frame = 0
#
#
#

# chunks = audio_rolled[:500]
# for i, chunk in enumerate(chunks):
#     if i % 10 == 0:
#         fps = (i - last_frame) / (time.time() - t)
#         print(f'{i + 1} / {len(chunks)}, {round((i + 1)/len(chunk), 3)}, FPS: {fps}')
#         t = time.time()
#         last_frame = i
#     a = 20 * np.log10(np.abs(np.fft.rfft(chunk * win)))[:-1]
#     a = scale(a, newmin=0, newmax=30)
#     frame[i % frame_width, :] = a[:frame_height]
#     ff = frame.T
#     quad_mesh.set_array(ff[:-1,:-1].ravel())
#
#     # fig.savefig(i, format='rgba', dpi=100)
#     # break
#     fig.savefig(p.stdin, format='rgba', dpi=100)


def f(x):
    return x*x


def screens_chunks(audio_rolled, frame_width):
    start, stop = 0, frame_width

    while True:
        if stop >= len(audio_rolled):
            break

        chunks = audio_rolled[start:stop]
        start += frame_width
        stop += frame_width

        yield chunks


if __name__ == '__main__':

    INPUT_AUDIO = '/Users/tandav/Documents/GoogleDrive/radiant.wav'
    OUTPUT_VIDEO = '/Users/tandav/Desktop/radiant2.mp4'

    frame_width = 1920 // 2
    frame_height = 1080 // 2
    # frame_width = 3840
    # frame_height = 2160

    fps = 60

    rate, track = read(INPUT_AUDIO)  # now supports only mono .wav files

    print(len(track))
    # track = track[:int(len(track) * 1)]
    print(f'rate {rate}')

    wav_dtype = track.dtype

    wav_max = np.iinfo(wav_dtype).max
    wav_min = np.iinfo(wav_dtype).min

    track = track.astype(np.float32)
    track = (track - wav_min) * 2 / (wav_max - wav_min) - 1  # normalise -1..1

    seconds = len(track) / rate
    n_frames = int(seconds * fps)

    print(len(track), n_frames)
    print('^' * 80)

    nperseg = 13804
    step = 734

    noverlap = nperseg - step

    div, mod = divmod(len(track) - noverlap, step)

    print(track.dtype)
    if mod:
        track = np.pad(track, (0, step - mod))

    div, mod = divmod(len(track) - noverlap, step)
    assert not mod
    print(div)

    # print(track.dtype)
    # track = x[:20000]
    # left_channel  = x[:, 0]
    # right_channel = x[:, 1]
    # track = left_channel
    # average left and right channels to mono signal (reaaly bad, don't do this)
    # track = (left_channel + right_channel) / 2

    seconds = len(track) / rate
    print(f'{seconds} seconds')
    # t = np.linspace(0, seconds, n, dtype=track.dtype)
    # print(t.dtype)

    # plt.grid()
    # plt.plot(t, track, 'k-', linewidth=0.1)
    # track_chunks = track_to_chunks(track)
    # print(track_chunks.shape)

    n_steps = div
    print(n_steps, n_frames)

    assert n_steps == n_frames, (n_steps, n_frames)
    # assert n_steps <= n_frames, f'{(n_steps, n_frames)}, decrease nperseg'

    # if 1 column per frame then number_of_columns = number_of_frames = fps * seconds
    print(n_steps, fps * seconds)

    shape = n_steps, nperseg
    strides = step * track.strides[-1], track.strides[-1]
    audio_rolled = np.array(np.lib.stride_tricks.as_strided(track, shape=shape, strides=strides))


    n_processes = 16

    # Open an ffmpeg process
    cmd = (
        'ffmpeg',
        '-loglevel', 'info',
        '-hwaccel', 'videotoolbox',
        '-threads', '16',
        '-y', '-r', '60',  # overwrite, 60fps
        '-s', f'{frame_width}x{frame_height}',  # size of image string
        '-f', 'rawvideo',
        # '-pix_fmt', 'argb', # format
        '-pix_fmt', 'rgba',  # format
        # '-pix_fmt', 'rgb24', # format
        # '-f', 'image2pipe',
        # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
        '-i', '-',  # tell ffmpeg to expect raw video from the pipe
        '-i', INPUT_AUDIO,
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

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)


    with multiprocessing.Pool(processes=n_processes) as pool:
        blocks = screens_chunks(audio_rolled, frame_width)
        args = [(f'TASK_{i}', chunks, nperseg, frame_width, frame_height, rate) for i, chunks in enumerate(blocks)]
        for b in pool.imap(task, args):
            print(type(b), len(b))
            p.stdin.write(b)
    p.communicate()
    # out, err =

    subprocess.run(('open', OUTPUT_VIDEO))
