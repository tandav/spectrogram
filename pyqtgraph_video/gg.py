import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
import time
import signal
import subprocess
import pyqtgraph as pg
import pyqtgraph.exporters
import io

canvas_width, canvas_height = 1920, 1080




# img = pg.ImageItem(border='w')

# # w = pg.plot()
# img.win.hide()

# # x = np.arange(0, 256)
# # y = np.arange(0, 256)
# # # w.plot(x, y)
# # exporter = pg.exporters.ImageExporter(self.w.plotItem)
# # exporter.params.param('width').setValue(256, blockSignal=exporter.widthChanged)
# # exporter.params.param('height').setValue(256, blockSignal=exporter.heightChanged)
# # for i in np.arange(0, 100):
# #     print(i)
# #     self.img.setImage(np.random.random((1920, 1080)), autoLevels=True)
# #     exporter = pg.exporters.ImageExporter(self.img)


# #     # x = np.arange(0, 256)
# #     # y = np.arange(0, 256)
# #     # w.plot(x, y)
# #     b = exporter.export(toBytes=True).data.tobytes()
# #     p.stdin.write(b)


# # p.communicate()

import pyqtgraph as pg
import pyqtgraph.exporters


fd = io.BytesIO()

n = 10

app = QtGui.QApplication(sys.argv)


# plt = pg.plot(np.arange(n), np.random.random(n))
glayout = pg.GraphicsLayoutWidget()
view = glayout.addViewBox(lockAspect=False)
img = pg.ImageItem(border='w')
view.addItem(img)



for frame in range(100):
    print(frame)
    # plt.setData(np.arange(n), np.random.random(n))
    img.setImage(np.random.random((1920, 1080)), autoLevels=True)
    
    exporter = pg.exporters.ImageExporter(view)
    exporter.params.param('width').setValue(1920, blockSignal=exporter.widthChanged)
    exporter.params.param('height').setValue(1080, blockSignal=exporter.heightChanged)
    # exporter.parameters()['width'] = 640
    # exporter.export('fileName.png')


    b = exporter.export(toBytes=True).data.tobytes()
    fd.write(b)
#     p.stdin.write(b)
# plt.win.close()


outf = 'tmp.mp4'

cmd = ('ffmpeg',
    # '-hwaccel', 'videotoolbox', '-threads', '8',
    # '-hwaccel', 'videotoolbox', '-threads', '16',
    '-y', '-r', '60', # overwrite, 60fps
    '-s', '%dx%d' % (canvas_width, canvas_height), # size of image string
    '-pix_fmt', 'argb', # format
    '-f', 'rawvideo',  '-i', '-', # tell ffmpeg to expect raw video from the pipe
    '-vcodec', 'h264_videotoolbox', '-profile:v', 'high', outf) # output encoding
    # '-vcodec', 'mpeg4',  outf) # output encoding
# p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

p = subprocess.run(cmd, stdin=fd)


# p.communicate()
