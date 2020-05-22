import matplotlib
# matplotlib.use('agg', warn = False, force = True) # fps 1.7
matplotlib.use('Qt5Agg', warn = False, force = True) # fps 4.8
# matplotlib.use('TkAgg', warn = False, force = True) # fps 1.6
# matplotlib.use('macosx', warn = False, force = True) # fps CORRUPT FILE
import matplotlib.pyplot as plt
import subprocess
import numpy as np
import time
from scipy.io.wavfile import read

def scale(x, newmin=0., newmax=1.):
    oldmin, oldmax = x.min(), x.max()
    return (x - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


INPUT_AUDIO  = '/Users/tandav/Documents/GoogleDrive/radiant.wav'
OUTPUT_VIDEO = '/Users/tandav/Desktop/radiant2.mp4'

frame_width  = 1920
frame_height = 1080

# frame_width  = 1920 // 4
# frame_height = 1080 // 4


rate, track = read(INPUT_AUDIO) # now supports only mono .wav files

track = track[:int(len(track) * 1)]
print(f'rate {rate}')

wav_dtype = track.dtype

wav_max = np.iinfo(wav_dtype).max
wav_min = np.iinfo(wav_dtype).min

track = track.astype(np.float32)
track = (track - wav_min) * 2 / (wav_max - wav_min) -1 # normalise -1..1

print(track.dtype)
# track = x[:20000]
# left_channel  = x[:, 0]
# right_channel = x[:, 1]
# track = left_channel
# average left and right channels to mono signal (reaaly bad, don't do this)
# track = (left_channel + right_channel) / 2 
n = len(track)
seconds = n/rate 
print(f'{seconds} seconds')
t = np.linspace(0, seconds, n, dtype=track.dtype)
print(t.dtype)
# plt.grid()
# plt.plot(t, track, 'k-', linewidth=0.1)
# track_chunks = track_to_chunks(track)
# print(track_chunks.shape)

fps = 60
frames = fps * seconds
print(f'{frames} frames')


# # use supersolver (lite-solver) to find nperseg and step
# nperseg = frame_height * 2 + 1
# step    = 715 # abap
# noverlap = nperseg - step

# use supersolver (lite-solver) to find nperseg and step
# nperseg = frame_height * 2 + 1
nperseg = 10_000
step    = 715 # abap
noverlap = nperseg - step

# if 1 column per frame then number_of_columns = number_of_frames = fps * seconds
print((n - noverlap) // step, fps * seconds)



x = track
shape   = ((x.shape[0] - noverlap) // step, nperseg)
strides = (step * x.strides[-1], x.strides[-1])
audio_rolled = np.array(np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides))
win = np.hanning(audio_rolled.shape[1])
# audio_rolled.shape


# frame = np.zeros((frame_width, frame_height))
frame = np.random.randint(7, 10, (frame_width, frame_height))

#TODO # t_frame = np.linspace (0 + dt * fi, seconds / frames, frame_width)
t_frame = np.linspace (0, 1, frame_width)
f_frame = np.geomspace(1, rate / 2, frame_height) # second arg: nperseg//2 (Nyquist limit)    
T_frame, F_frame = np.meshgrid(t_frame, f_frame)


# fig = plt.figure(frameon=False, figsize=(4, 5), dpi=100)

fig, ax = plt.subplots(figsize=(frame_width / 100, frame_height / 100), frameon=False, dpi=100)
# fig = plt.figure() # todo: compute dpi

# fig = plt.figure(figsize=(frame_width / 100, frame_height / 100), frameon=False, dpi=100) # todo: compute dpi
# fig.subplots_adjust(left=0.1, bottom=0, right=0.9, top=1, wspace=None, hspace=None)
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
ff = frame.T

quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30) # shading='gouraud' nearest
# quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='gouraud')
print(quad_mesh._A.shape)
# quad_mesh = ax.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30, shading='nearest')
# ax.semilogy()
ax.grid(False)
ax.axis('off')

ax.set_ylim(30, 5e3)

# fig.show()
# fig.canvas.draw()


t = time.time()
last_frame = 0

# R = np.random.randint(-200, 0, size=(frame_height, frame_width))
# qq = R[:-1, :-1].ravel()
# print(qq.shape)
# input()
# quad_mesh.set_array(qq)
# plt.draw()
# fig.canvas.draw()
# fig.canvas.flush_events()
# fig.savefig('frame.png', dpi=100)
# create a figure window that is the exact size of the image
# 400x500 pixels in my case
# don't draw any axis stuff ... thanks to @Joe Kington for this trick
# https://stackoverflow.com/questions/14908576/how-to-remove-frame-from-matplotlib-pyplot-figure-vs-matplotlib-figure-frame



# Open an ffmpeg process
# cmd = ('ffmpeg',
#     '-loglevel', 'trace',
#     '-hwaccel', 'videotoolbox',
#     '-threads', '16',
#     '-y', '-r', '60', # overwrite, 60fps
#      '-s', f'{frame_width}x{frame_height}',  # size of image string
#      '-f', 'rawvideo',
#      # '-pix_fmt', 'argb', # format
#      '-pix_fmt', 'rgba', # format
#      # '-pix_fmt', 'rgb24', # format
#     # '-f', 'image2pipe',
#     # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
#     '-i', '-', # tell ffmpeg to expect raw video from the pipe
#     '-i', INPUT_AUDIO,
#     # '-c:v', 'hevc_videotoolbox',
#     '-c:v', 'libx264',
#     '-pix_fmt', 'yuv420p',
#     # '-tag:v', 'hvc1', '-profile:v', 'main10',
#     # '-b:v', '16M',
#     # '-b:v', '1M',
#     '-b:v', '100k',
#      OUTPUT_VIDEO) # output encoding
#
# p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

# for i, chunk in enumerate(audio_rolled[frame_width]):
for i, chunk in enumerate(audio_rolled):
    if i % 10 == 0:
        fps = (i - last_frame) / (time.time() - t)
        print(f'{i + 1} / {len(audio_rolled)}, {round((i + 1)/len(audio_rolled), 3)}, FPS: {fps}')
        t = time.time()
        last_frame = i
    a = 20 * np.log10(np.abs(np.fft.rfft(chunk * win)))[:-1]
    a = scale(a, newmin=0, newmax=30)
    # print(a[:-1].shape)
    # print(a.mean())
    # print(a[-1])
    # print(np.isinf(a).sum())
    #f = np.fft.rfftfreq(n, d = 1. / rate)
    # print(i)
    frame[i % frame_width, :] = a[:frame_height]
    # frame[i, 800] = 30
    ff = frame.T
    quad_mesh.set_array(ff[:-1,:-1].ravel())

    # quad_mesh.set_array(np.random.randint(-200, 0, size=(frame_height, frame_width))[:-1, :-1].ravel())
    # writer.grab_frame()

    if i == 500:
        break

    # draw the frame
    # update(frame)
    # plt.draw()
    # plt.plot(np.random.random(100))

        # fig.canvas.draw()
        # fig.canvas.draw()
        # fig.canvas.flush_events()
        # fig.savefig(p.stdin, format='rgba', dpi=100)
        # break
# plt.savefig(p.stdin, format='png')
fig.savefig('frame.png', dpi=100)

# b = fig.canvas.tostring_argb()
    # b = fig.canvas.tostring_rgb()
    # print(type(b), len(b))
    # extract the image as an ARGB string
    # and write to pipe
    # p.stdin.write(fig.canvas.tostring_argb())
    # p.stdin.write(b)
#
# out, err = p.communicate()

