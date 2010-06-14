midget Blender to glge exporter
-------------------------------
	
	The midget GLGE Exporter can create glge scene files out of your blender scene.
	
	This exporter is running with Blender 2.4x.
	For now it's working quiet rudimentarily.
	
	Installation
	------------
		
		Copy to \blender folder\.blender\scripts
		
	Use
	------------
	
		1. save: save your blender file (otherwise recently changes will not effect your exported data)
		2. export: File -> Export -> GLGE Exporter
		
	Changelog
	-------------
		0.1c
			- You don't have to triangulate your scene anymore. This work is done by the exporter.
			- Bugfix: Now the exporter ensures, that texture ids and material ids are diffrent
			- Bugfix: Correct rotation of camera and objects.