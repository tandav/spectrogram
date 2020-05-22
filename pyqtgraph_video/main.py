from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import sys
import time
import signal
import subprocess
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph import functions as fn
import io

canvas_width, canvas_height = 1920, 1080

shape = canvas_width, canvas_height

outf = 'tmp.mp4'

cmd = ('ffmpeg',
    # '-hwaccel', 'videotoolbox', '-threads', '8',
    '-hwaccel', 'videotoolbox', '-threads', '16',
    '-y', '-r', '60', # overwrite, 60fps
    '-s', f'{canvas_width}x{canvas_height}', # size of image string
    '-pix_fmt', 'argb', # format
    # '-pix_fmt', 'yuv420p', # format
    '-f', 'rawvideo',
    '-i', '-', # tell ffmpeg to expect raw video from the pipe
    '-c:v', 'hevc_videotoolbox', '-profile:v', 'main10', '-tag:v', 'hvc1', '-b:v', '1M', '-an', '-sn', outf)

    # '-vcodec', 'h264_videotoolbox', '-profile:v', 'high', outf) # output encoding

# ffmpeg -i [input_file] -c:v hevc_videotoolbox -profile:v main10 -tag:v hvc1 -b:v 10000k -an -sn output_filename.mp4

p = subprocess.Popen(cmd, stdin=subprocess.PIPE)


# ib = io.BytesIO()

# -vcodec hevc_videotoolbox
print('f')
class Visualizer(QtGui.QWidget):
    def __init__(self):
        super().__init__()

        # pg.setConfigOption('background', 'w')
        # pg.setConfigOption('foreground', 'k')

        self.layout = QtGui.QVBoxLayout()

        # self.app = QtGui.QApplication(sys.argv)


        self.glayout = pg.GraphicsLayoutWidget()
        self.view = self.glayout.addViewBox(lockAspect=False)
        # self.view = self.glayout.addViewBox(lockAspect=True)
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], [0, 0, 255, 255], [255, 0, 0, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        # set colormap
        self.img.setLookupTable(lut)
        # self.img.setLevels([-140, -50])
        self.img.setLevels([-50, 20])
        self.layout.addWidget(self.glayout)

        self.setLayout(self.layout)
        self.setGeometry(10, 10, 500, 500)
    
        self.show() 
        self.hide()
        # self.close()


        self.update()


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()



    def update(self):
        print('lol')
        for frame in range(300):

            self.img.setImage(np.random.random((canvas_width, canvas_height)), autoLevels=True)
            exporter = pg.exporters.ImageExporter(self.view)

            exporter.params.param('width').setValue(canvas_width, blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(canvas_height, blockSignal=exporter.heightChanged)

            im = exporter.export(toBytes=True)

            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QIODevice.WriteOnly)
            # buffer.open(QtCore.QIODevice.ReadWrite)
            im.save(buffer, 'PNG')
            b = buffer.data()
            # print(b)

            # print(hasattr(z, 'data'))
            # print(z.pixelFormat().yuvLayout())
            # print(z.bits())
            # b = z.data.tobytes()
            # z.save(p.stdin, 'PNG')
            p.stdin.write(b)
            # ib.write(b)



        p.communicate()



# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = Visualizer()
    gui.show()
    app.exec()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
