#!/usr/bin/env python
from gimpfu import *
import zipfile
import logging
import tempfile

log = logging.getLogger(__name__)

class ACLayer(object):
	def __init__(self, zf, path):
		log.info("Loading layer %s" % (path,))

		with zf.open(path) as f:
			self.png_data = f.read()

class ACFrame(object):
	def __init__(self):
		self.layers = []

	@classmethod
	def load(cls, zf, uid):
		frame = cls()

		log.info("Loading frame %s" % (uid,))

		try:
			layer = ACLayer(zf, "%s.0" % (uid,))
		except:
			log.error("Loading of a layer failed!")
		else:
			frame.layers.append(layer)

		return frame

class ACProject(object):
	def __init__(self):
		self.frames = []

	@classmethod
	def load(cls, path):
		proj = cls()
		proj.path = path

		log.info("Loading project %s" % (path,))

		with zipfile.ZipFile(path) as zf:
			with zf.open("frames") as ff:
				for line in ff:
					uid = line.strip()
					frame = ACFrame.load(zf, uid)
					proj.frames.append(frame)

		return proj

def import_ac(img, layer, path):

	proj = ACProject.load(path)

	img.undo_group_start()

	#i = 0
	frame_n = len(proj.frames)
	for frame in reversed(proj.frames):
		grp = pdb.gimp_layer_group_new(img)
		grp.name = "frame%04d" % (frame_n,)

		img.active_layer = img.layers[-1]
		img.insert_layer(grp)

		layer_n = 0
		for layer in frame.layers:
			f = tempfile.NamedTemporaryFile(suffix=".png")
			f.write(layer.png_data)
			f.flush()

			lay = pdb.gimp_file_load_layer(img, f.name)

			f.close()

			lay.name = "frame%04d_%d" % (frame_n, layer_n)

			img.insert_layer(lay, grp)
			lay.transform_rotate_simple(2, False, 0, 0)

			layer_n += 1

		frame_n -= 1
		#i += 1
		#if i > 3:
		#	break

	img.remove_layer(img.layers[-1])
	img.resize_to_layers()

	img.undo_group_end()


register(
	"python_fu_ca_import",
	"Import frames from Animation Creator HD app (.ac file)",
	"Import frames from Animation Creator HD app",
	"Tomaz Solc",
	"GPLv3+",
	"2017",
	"<Image>/Filters/Animation/Import from AC",
	"*",
	[
		(PF_FILE, "path", "Path to file to import", ""),
	],
	[],
	import_ac)

main()
