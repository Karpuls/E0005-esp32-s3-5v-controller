# crop.py in.png out.png [x0 y0 x1 y1 in board-local mm (centre 150,100)] ; A4 page plot at given dpi
import sys
from PIL import Image
im = Image.open(sys.argv[1]); W, H = im.size; s = W / 297.0
a = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else [-66, -36, 66, 36]
mirror = 'bot' in sys.argv[1]
x0, x1 = (150 + a[0], 150 + a[2]) if not mirror else (297 - 150 - a[2], 297 - 150 - a[0])
box = (int(x0 * s), int((100 + a[1]) * s), int(x1 * s), int((100 + a[3]) * s))
im.crop(box).save(sys.argv[2])
