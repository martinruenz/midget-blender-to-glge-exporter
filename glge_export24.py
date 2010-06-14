#!BPY
# coding: utf-8
# Todos: complete scene, complete materials, lights, (replace copy image)
# Date: 14.06.2010
"""
Name: 'GLGE Exporter (.xml)'
Blender: 244
Group: 'Export'
Tooltip: 'Export to GLGE's scene format'
"""
__author__ = "Martin Rünz seamonkey@uni-koblenz.de (idea: objectexport.py)"
__url__ = ["University of Koblenz, http://www.uni-koblenz.de/", "GLGE, http://www.glge.org"]
__version__ = "0.1c"
__bpydoc__ = """\
Description:
This script exports all meshes into the glge scene format.
"""
import Blender, os, copy
from Blender import sys

# configuration (todo), now: rotate_coordinates = False
#rotate_coordinates = False # if True: the xz-plane will be the bottom, if False: xy-plane will be the bottom 
	
# this function copies a file on your filesystem
def copy_file(source, dest):
	file = open(source, 'rb')
	data = file.read()
	file.close()
	
	file = open(dest, 'wb')
	file.write(data)
	file.close()
	
# scene class
# 	this class represents an glge scene. 
class Scene:
	# scene object constructor
	def __init__(self, id="Scene", camera="Camera", ambient_color="#666", fog_type="FOG_NONE"):
		self.blender_scene = Blender.Scene.GetCurrent()
		self.id = id
		self.camera = camera
		self.ambient_color = ambient_color
		self.fog_type = fog_type
		self.scene_objects = []
		self.scene_lights = []
	
	# add object to scene
	def add_object(self, object):
		self.scene_objects.append(object)
	
	# write scene open tag (xml output)
	def get_opentag(self):
		return "<scene id=\"" + self.id + "\" camera=\"#"+self.camera+"\" ambient_color=\""+self.ambient_color+"\" fog_type=\""+self.fog_type+"\">"
	
	# write scene close text (xml output)
	def get_closetag(self):
		return "</scene>"
	
		self.out.write("\t<scene id=\"" + scene.name + "\" camera=\"#"+self.camera.name+"\" ambient_color=\"#666\" fog_type=\"FOG_NONE\">\n")
		self.out.write("\t</scene>")
	
	# iterate over scene object
	def next(self):
		if len(self.scene_objects) > 0:
			return self.scene_objects.pop()
		elif len(self.scene_lights) > 0:
			return self.scene_lights.pop()
		return None
	
	# has next? (while iterating)
	def has_next(self):
		if (len(self.scene_objects) > 0) or (len(self.scene_lights) > 0):
			return True
		return False		

# scene-object class
# 	objects of this class are member of a scene (always meshes)
class Scene_Object:
	def __init__(self, id, mesh, locx="0", locy="0", locz="0", rotx="0", roty="0", rotz="0", scalex="1", scaley="1", scalez="1", material=None):
		self.id = id
		self.mesh = mesh
		self.scalex = scalex
		self.scaley = scaley
		self.scalez = scalez
		self.rotx = rotx
		self.roty = roty
		self.rotz = rotz
		self.locx = locx
		self.locy = locy
		self.locz = locz
		self.material = material
	
	# get xml output
	def to_xml(self):
		output = "<object id=\"%s\" mesh=\"#%s\" loc_x=\"%f\" loc_y=\"%f\" loc_z=\"%f\" rot_order=\"ROT_XZY\" rot_x=\"%f\" rot_y=\"%f\" rot_z=\"%f\" scale_x=\"%f\" scale_y=\"%f\" scale_z=\"%f\"" % (self.id, self.mesh, self.locx, self.locy, self.locz, self.rotx, self.roty, self.rotz, self.scalex, self.scaley, self.scalez)
		if self.material != None:
			output += " material=\"#"+self.material+"\""
		output += " />"
		return output

class Scene_Camera:
	def __init__(self, id, locx="0", locy="0", locz="0", rotx="0", roty="0", rotz="0", rotorder="ROT_XZY"):
		self.rotx = rotx
		self.roty = rotz
		self.rotz = -roty
		self.locx = locx
		self.locy = locy
		self.locz = locz
		self.id = id
		self.rotorder = rotorder

	def to_xml(self):
		output = "<camera id=\"%s\" loc_x=\"%f\" loc_y=\"%f\" loc_z=\"%f\" rot_order=\"%s\" rot_x=\"%f\" rot_y=\"%f\" rot_z=\"%f\" />\n" % (self.id, self.locx, self.locy, self.locz, self.rotorder, self.rotx, self.roty, self.rotz)
		return output
		
# exporter application class
class GLGE_Exporter:
	# constructor
	def __init__(self, path):
		self.filepath = path
		self.dir = os.path.dirname(path)+os.sep
		
		# create texture dir
		self.texture_dir = self.dir+"images"+os.sep
		if not os.path.exists(self.texture_dir): 
			os.makedirs(self.texture_dir) 
			
		# actual output file
		self.out = file(self.filepath, 'w')
		
		# list of found meshes and materials (avoid doublicates)
		self.meshes = []
		self.materials = []

	# export a mesh object
	def export_mesh(self, mesh):
		# Variables 
		coordinates=""
		normals=""
		faces=""
		face_counter=0
		uv=""
		uv_enabled = True
		
		# first: export materials (if not yet done)
		if len(mesh.materials) > 0:
			if not(mesh.materials[0].getName() in self.materials):
				self.materials.append(mesh.materials[0].getName())
				self.export_material(mesh.materials[0])
		
		# start writing
		self.out.write("\t<mesh id=\""+mesh.name+"\">\n")
		
		# collect output (go through all the faces)
		mesh_faces = mesh.faces
		uv_enabled = False
		for face in mesh_faces:
			for i in range(len(face.v)):
				coordinates += "%f,%f,%f," % (face.v[i].co[0],face.v[i].co[1],face.v[i].co[2])
				normals += "%f,%f,%f," % (face.v[i].no[0],face.v[i].no[1],face.v[i].no[2])
				try:
					if len(face.uv)>0:
						uv += "%f,%f," % (face.uv[i][0],face.uv[i][1])
						uv_enabled=True
				except ValueError:
					uv_enabled = False
			if len(face.v) < 4:
				faces += "%i,%i,%i," % (face_counter,face_counter+1,face_counter+2)
			else:
				for j in range(len(face.v)-2):
					faces += "%i,%i,%i," % (face_counter,face_counter+1+j,face_counter+2+j)
			face_counter=face_counter+len(face.v)
		
		self.out.write("\t\t<positions>"+coordinates[:-1]+"</positions>\n")
		self.out.write("\t\t<normals>"+normals[:-1]+"</normals>\n")
		if uv_enabled:
			self.out.write("\t\t<uv1>"+uv[:-1]+"</uv1>\n")
		self.out.write("\t\t<faces>"+faces[:-1]+"</faces>\n")

		# end writing
		self.out.write("\t</mesh>\n")

	# export some material
	def export_material(self, material):
		# XML-EXAMPLE:
		# <material id="treematerial" specular="0" reflect="0">
			# <texture id="treetexture" src="images/tree2.png" />
			# <texture id="treenorm" src="images/treenorm.jpg" />
			# <material_layer texture="#treetexture" mapinput="UV1" mapto="M_ALPHA" />
			# <material_layer texture="#treetexture" mapinput="UV1" mapto="M_COLOR" />
			# <material_layer texture="#treenorm" mapinput="UV1" mapto="M_NOR" />
		# </material>
		self.out.write("\t<material id=\""+ material.getName() +"\" specular=\"0\" reflect=\"0\">\n")
		for texture in material.getTextures():
			if texture == None:
				break
			self.export_texture(texture.tex, material)
		self.out.write("\t</material>\n")
	
	# export some texture (todo)
	def export_texture(self, texture, material):
		image = texture.getImage()
			
		image_path = sys.expandpath(image.filename)
		dest_path = self.texture_dir + image_path.split('\\')[-1].split('/')[-1]
		
		texture_id = texture.getName()
		if material.getName() == texture_id:
			texture_id += "Texture"
		
		self.out.write("\t\t<texture id=\""+ texture_id +"\" src=\"images"+os.sep+os.path.basename(image.getFilename())+"\" />\n")
		self.out.write("\t\t<material_layer texture=\"#"+ texture_id +"\" mapinput=\"UV1\" mapto=\"M_COLOR\" />\n")
		
		if sys.exists(image_path) and not sys.exists(dest_path):
			copy_file(image_path, dest_path)
	
	# export scene
	def export_scene(self, scene):
		# XML-EXAMPLE:
		# <scene id="mainscene" camera="#maincamera" ambient_color="#666" fog_type="FOG_NONE">
			# <object id="wallobject" mesh="#cube" scale_x="10" scale_y="10" scale_z="10" material="#wallmaterial" />
			# <collada document="duck.dae" animation="#spin" rot_x="1.57" loc_y="-15" scale="0.05" />
			# <collada document="seymourplane_triangulate.dae" rot_x="1.57" rot_y="1.57" loc_y="5" loc_z="3" scale="1" />
			
			# <light id="mainlight" loc_x="0" loc_y="15" loc_z="10" rot_x="-1.3"  attenuation_constant="0.5" type="L_POINT" />
			# <light id="mainlight" loc_x="20" loc_y="-15" loc_z="5" rot_x="1.3"  attenuation_constant="0.5" type="L_POINT" />
		# </scene>
		self.out.write("\t"+scene.get_opentag()+"\n")
		while (scene.has_next()):
			self.out.write("\t\t"+scene.next().to_xml()+"\n")
		self.out.write("\t"+scene.get_closetag()+"\n")
		
	
	# start exporter
	def export(self):
		print("GLGE Exporter started\nPath: "+self.filepath+"\n")

		# xml header		
		self.out.write("<?xml version=\"1.0\"?>\n<glge>\n")
		
		camera_name = ""
		if Blender.Scene.getCurrent().getCurrentCamera() != None:
			camera_name = Blender.Scene.getCurrent().getCurrentCamera().getName()
			
		scene = Scene(Blender.Scene.getCurrent().getName(), camera_name)
		
		# get all objects
		objects = Blender.Object.Get()

		# run through all of them
		for obj in objects:			
			entity = obj.getData(mesh=1)
			class_name = entity.__class__.__name__
			# export mesh
			if class_name == 'Blender Mesh':
				if not(entity.name in self.meshes):
					print("export mesh: " + entity.name)
					self.meshes.append(entity.name)
					self.export_mesh(entity)
				if len(entity.materials) > 0:
					# add mesh with material to scene
					scene.add_object(Scene_Object(obj.name, entity.name, obj.LocX, obj.LocY, obj.LocZ, obj.RotX, obj.RotY, obj.RotZ, obj.SizeX, obj.SizeY, obj.SizeZ, entity.materials[0].getName()))
				else:
					# add mesh without material to scene
					scene.add_object(Scene_Object(obj.name, entity.name, obj.LocX, obj.LocY, obj.LocZ, obj.RotX, obj.RotY, obj.RotZ, obj.SizeX, obj.SizeY, obj.SizeZ))
			# export camera
			elif class_name == 'Blender Camera':
				print("export camera: " + entity.name)
				scene.add_object(Scene_Camera(obj.name, obj.LocX, obj.LocY, obj.LocZ, obj.RotX, obj.RotY, obj.RotZ))	
		
		# export scene (allready filled)
		self.export_scene(scene)
			
		self.out.write("</glge>")
		print("export finished!")

# button action
def export(filepath):
	Exporter = GLGE_Exporter(filepath)
	Exporter.export()
	
# export-button
Blender.Window.FileSelector(export, "Export")