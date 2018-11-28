#!/usr/bin/env python
import zipfile
import logging
import tempfile

log = logging.getLogger(__name__)

class ACLayer(object):
	def __init__(self, zf, path):
		log.info("Loading layer %s" % (path,))

		with zf.open(path) as f:
			self.png_data = f.read()

		self.visible = True
		self.opacity = 100.

class ACFrame(object):
	def __init__(self):
		self.layers = []

	@classmethod
	def load(cls, zf, uid):
		frame = cls()

		log.info("Loading frame %s" % (uid,))

		with zf.open("%s.layers" % (uid,)) as lf:

			for n, line in enumerate(lf):
				try:
					layer = ACLayer(zf, "%s.%d" % (uid, n))
				except:
					# empty layers have an entry in
					# .layers, but no data file
					log.error("Loading of layer %d failed! (probably an empty layer)" % (n,))
					continue

				frame.layers.append(layer)

				f = line.split(',')
				try:
					layer.visible = int(f[1]) > 0
				except:
					log.error("Can't determine layer %d visibility: %s" % (n, line))

				try:
					layer.opacity = float(f[0])*100
				except:
					log.error("Can't determine layer %d opacity: %s" % (n, line))

		return frame

class ACProject(object):
	def __init__(self):
		self.frames = []
		self.background = None

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

			try:
				proj.background = ACLayer(zf, "background")
			except:
				log.error("Can't load background layer.")

		return proj

def _load_layer(img, layer):
	f = tempfile.NamedTemporaryFile(suffix=".png")
	f.write(layer.png_data)
	f.flush()

	lay = pdb.gimp_file_load_layer(img, f.name)

	f.close()

	return lay

def _add_group(img):
	grp = pdb.gimp_layer_group_new(img)

	img.active_layer = img.layers[-1]
	img.insert_layer(grp)

	return grp

def import_ac(img, layer, path):

	proj = ACProject.load(path)

	img.undo_group_start()

	#i = 0
	frame_n = len(proj.frames)
	for frame in reversed(proj.frames):

		grp = _add_group(img)
		grp.name = "frame%04d" % (frame_n,)

		layer_n = 0
		for layer in frame.layers:
			lay = _load_layer(img, layer)
			lay.name = "frame%04d_%d" % (frame_n, layer_n)
			lay.opacity = layer.opacity
			lay.visible = layer.visible

			img.insert_layer(lay, grp)
			lay.transform_rotate_simple(2, False, 0, 0)

			layer_n += 1

		frame_n -= 1
		#i += 1
		#if i > 3:
		#	break

	# Add [background] group before removing the remaining empty image
	# layer. This way it ends up at the top level, not inside the last
	# frame group.
	grp = _add_group(img)
	grp.name = "[background]"

	img.remove_layer(img.layers[-1])
	img.resize_to_layers()

	# there is a default white background that can be seen through
	# transparent areas in the actual background image.
	#
	# Note that projects that do not have a defined background image
	# seem to have a 1x1 PNG as the background.
	lay = pdb.gimp_layer_new(img, img.width, img.height, 0, "paper", 100, 0)
	img.insert_layer(lay, grp)
	pdb.gimp_edit_fill(lay, WHITE_FILL)

	if proj.background is not None:
		# Load the actual background
		lay = _load_layer(img, proj.background)
		lay.name = "background"

		img.insert_layer(lay, grp)
		lay.transform_rotate_simple(2, False, 0, 0)
		lay.transform_2d(0, 0, 1, 1, 0, 0, +lay.height, TRANSFORM_FORWARD, INTERPOLATION_NONE)

	img.undo_group_end()


def start():
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

if __name__ == "__main__":
	from gimpfu import *

	start()
