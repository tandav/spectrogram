import subprocess
# import cupy as cp
import numpy as np
import time
from scipy.io.wavfile import read
# from google.colab import files
import matplotlib.animation as manimation
import matplotlib.pyplot as plt
FFMpegWriter = manimation.writers['ffmpeg']

writer = FFMpegWriter(
    fps=60,
    # codec='ffv1', default codec is 'h264'
    # bitrate=
    metadata = dict(title='Radiant', artist='N. Rajam',)
)

print(manimation.writers.list()) # should contains 'ffmpeg'

INPUT_AUDIO  = '/Users/tandav/Documents/GoogleDrive/radiant.wav'
OUTPUT_VIDEO = '/Users/tandav/Desktop/radiant.mp4'
BACKEND = np


frame_width  = 1920 #* 2
frame_height = 1080 #* 2

# frame_width  = 1920//4
# frame_height = 1080//4


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


# use supersolver (lite-solver) to find nperseg and step
nperseg = frame_height * 2 + 1
step    = 715 # abap
noverlap = nperseg - step

# if 1 column per frame then number_of_columns = number_of_frames = fps * seconds
print((n - noverlap) // step, fps * seconds)



x = track
shape   = ((x.shape[0] - noverlap) // step, nperseg)
strides = (step * x.strides[-1], x.strides[-1])
audio_rolled = BACKEND.array(np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides))
win = BACKEND.hanning(audio_rolled.shape[1])
audio_rolled.shape



frame = BACKEND.zeros((frame_width, frame_height))

#TODO # t_frame = np.linspace (0 + dt * fi, seconds / frames, frame_width)
t_frame = np.linspace (0, 1, frame_width)
f_frame = np.geomspace(1, rate / 2, frame_height) # second arg: nperseg//2 (Nyquist limit)    
T_frame, F_frame = np.meshgrid(t_frame, f_frame)

fig = plt.figure(figsize=(frame_width / 100, frame_height / 100))
# fig.subplots_adjust(left=0.1, bottom=0, right=0.9, top=1, wspace=None, hspace=None)
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
ff = frame.T
if BACKEND is not np:
    ff = cp.asnumpy(ff)
im = plt.pcolormesh(T_frame, F_frame, ff, cmap='viridis', vmin=0, vmax=30) # shading='gouraud' nearest
plt.semilogy()
plt.grid(False)
plt.ylim(0, 30)


t = time.time()
last_frame = 0
# todo: configure DPI and bitrate
with writer.saving(fig, 'tmp.mp4', dpi=100):
    # for i, chunk in enumerate(audio_rolled[frame_width]):
    for i, chunk in enumerate(audio_rolled):
        if i % 10 == 0:
            fps = (i - last_frame) / (time.time() - t)
            print(f'{i + 1} / {len(audio_rolled)}, {round((i + 1)/len(audio_rolled), 3)}, FPS: {fps}')
            t = time.time()
            last_frame = i
        a = 20 * np.log10(np.abs(BACKEND.fft.rfft(chunk * win)))
        #f = np.fft.rfftfreq(n, d = 1. / rate)
        frame[i % frame_width, :] = a[:-1]
        ff = frame.T
        if BACKEND is not np:
            ff = cp.asnumpy(ff)
        im.set_array(ff[:-1,:-1].ravel())
        writer.grab_frame()



cmd = 'ffmpeg', '-y', '-i', 'tmp.mp4', '-i', INPUT_AUDIO, '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', OUTPUT_VIDEO
subprocess.check_output(cmd)
