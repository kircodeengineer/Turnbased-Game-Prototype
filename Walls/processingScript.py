import bpy
import bmesh
import re
import random
from math import sqrt

def currentLayer():
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = 0
    for layer in scene.layers:
        if layer:
            break
        else:
            layerNum += 1
    return layerNum
    #current number of group

#1. RENAME BRICKS 
def rename():
    #current layer number
    layerNum = currentLayer()
    #remove selection from all objects on scene
    bpy.ops.object.select_all(action='DESELECT')
    #digging scene
    context = bpy.context
    scene = context.scene
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                object.name = 'Brick.000'

#2. REMOVING DOUBLES
def removeDoubles():
	bpy.ops.object.select_all(action='SELECT')

	context = bpy.context

	distance = 0.0001

	if True:
		meshes = [obj.data for obj in context.selected_objects if obj.type == 'MESH']
		
		bm = bmesh.new()
		
		for mesh in meshes:
			bm.from_mesh(mesh)
			bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = distance)
			#соединение рядом стоящих точек
			#bmesh.ops.automerge(bm, verts = bm.verts, dist = distance)
			#print(mesh.name)
			bm.to_mesh(mesh)
			mesh.update()
			bm.clear()
		bm.free()

	bpy.ops.object.select_all(action='DESELECT')

#3. CORRECTING TEXTURES
def textureCorrection():
    #deselecting objects on scene    
    bpy.ops.object.select_all(action='DESELECT')
    #knocking to necessery scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #list of faces in object
    face_list = []     
    for object in scene.objects:
        #Be sure to specify the desired layer
        if object.layers[layerNum] and object.type == 'MESH':
            #set active object for editing
            scene.objects.active = object
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
            #deselecting all faces
            for face in object.data.polygons:
                face.select  = False
            #selecting daces only with material = 1
            for face in object.data.polygons:
                if face.material_index == 1:
                    face.select  = True
            bpy.ops.object.editmode_toggle()    
            bpy.ops.uv.smart_project()
            bpy.ops.object.editmode_toggle()
            
#4. CREATING GROUPS OF VERTICES
def groupsCreation(objLocGroup):
    #remove selection from all objects on scene
    bpy.ops.object.select_all(action='DESELECT')
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #list of verticies
    vertexList = []
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                #activating object to start editing it
                scene.objects.active = object
                #clear list of vertex groups in object if it  somehow been there
                object.vertex_groups.clear()
                #create vertexGroup
                vertexGroup = object.vertex_groups.new(name = object.name)
                #create list of vertices in  object
                for vertex in object.data.vertices:
                    vertexList.append(vertex.index)
                #assign vertices in list to created group
                vertexGroup.add(vertexList, 1.0, 'ADD')
                #clear list of vertices for new group
                vertexList.clear()
                objLocGroup.append([object.location, vertexGroup.name])

#5. JOINING PIECES IN ONE MESH        
def joinPieces():
    bpy.ops.object.select_all(action='SELECT')
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            bpy.context.scene.objects.active = bpy.data.objects[object.name]
    bpy.ops.object.join()        
                                               
#6. MAKE PAIR OF VERTEX AND GROUP FOR COLORIZE
def makePairVertexGroup(groupsAndVerticies, objLocGroup, vertexDistObjCoColorList):
    #remove selection from all objects on scene
    bpy.ops.object.select_all(action='DESELECT')
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum] and object.type == 'MESH':
            #looking for group
            for vGroup in object.vertex_groups:
                if 'Brick' in vGroup.name:
                    #group color
                    color = (random.random(), random.random(), random.random())
                    #list of verticies
                    vertexList = []
                    for vertex in object.data.vertices:
                        for g in vertex.groups:
                            if g.group == vGroup.index:
                                for elem in objLocGroup:
                                    if vGroup.name == elem[1]:
                                        objLoc = elem[0]
                                groupsAndVerticies.append([vertex.index, vGroup.index, color])
                                #collecting distance of vertex to object centr
                                vertexWorldCo = object.matrix_world * vertex.co
                                deltaX = objLoc[0] - vertexWorldCo.x
                                deltaY = objLoc[1] - vertexWorldCo.y
                                deltaZ = objLoc[2] - vertexWorldCo.z
                                distance = sqrt(deltaX*deltaX + deltaY*deltaY + deltaZ*deltaZ)
                                vertexDistObjCoColorList.append([distance, objLoc, color])

#7. VERTEX COLORIZE
def colorizeVerticies(groupsAndVerticies):
    bpy.ops.object.select_all(action='DESELECT')
    layerNum = currentLayer()
    #knocking to necessery scene
    context = bpy.context
    scene = context.scene
    #vertex color
    newColor = (0.0, 0.0, 0.0)
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                #mesh from object
                mesh = bpy.context.object.data
                if mesh.vertex_colors.active is None:
                    mesh.vertex_colors.new()
                for poly in mesh.polygons:
                    #here we need to pair vertex with group
                    for vertex in poly.vertices:
                        for pair in groupsAndVerticies:
                            if vertex == pair[0]:
                                newColor = pair[2]
                                groupsAndVerticies.remove(pair)
                                break
                    for loop in poly.loop_indices:
                        mesh.vertex_colors.active.data[loop].color = newColor
                        #print(mesh.vertex_colors.active.data[loop].color)
                        mesh.update()
                                                
    
#8. NORMALS CORRECTION
def normalsCorrection():
    bpy.ops.object.select_all(action='DESELECT')
    layerNum = currentLayer()
    #knocking to necessery scene
    context = bpy.context
    scene = context.scene
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                object.select = True
                bpy.context.scene.objects.active = object
                # go edit mode
                bpy.ops.object.mode_set(mode='EDIT')
                # select al faces
                bpy.ops.mesh.select_all(action='SELECT')
                # recalculate outside normals 
                bpy.ops.mesh.normals_make_consistent(inside=False)
                # go object mode again
                bpy.ops.object.editmode_toggle()    

#9. CLEAR GROUPS                                
def clearVertexGroups():
    #remove selection from all objects on scene
    bpy.ops.object.select_all(action='DESELECT')
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #list of verticies
    vertexList = []
    #looking for objects on current layer
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                #activating object to start editing it
                scene.objects.active = object
                #clear list of vertex groups in object if it  somehow been there
                object.vertex_groups.clear()               

#debug    
def emptyAdd(list):
    context = bpy.context
    i = 0
    for elem in list:
        i += 1
        print(i, elem)
        bpy.ops.object.select_all(action='DESELECT')
        obj_empty = bpy.data.objects.new('Empty' + str(i), None)
        obj_empty.location = elem  
        context.scene.objects.link(obj_empty)
             

#debug
def listPrint(list):
    print('___print list___')
    print('VVVVVVV')
    i = 0
    for elem in list:
        i += 1
        print(i, elem)
    print('WWWWWWW')

#10. CREATE FILE WITH PIECES COORDS
def saveVertsFile(vertexDistObjCoColorList):
    #digging scene
    context = bpy.context
    scene = context.scene
    #current layer number
    layerNum = currentLayer()
    #create file if it doesnt exist
    filename = 'Wall.txt'
    file = open(filename, 'w+')
    #open file for writing
    file = open(filename, 'a')
    #list with distances to vertex from brick center
    distance = []
    #current brick color
    color = [0.0, 0.0, 0.0]
    #current brick coords
    coord = [0.0, 0.0, 0.0]
    i = 0
    for elem in vertexDistObjCoColorList:
        #middle distance
        distanceMiddle = 0
        if i == 0:
            color = elem[2]
        if color != elem[2]:
            for distElem in distance:
                distanceMiddle += distElem
            distanceMiddle /= len(distance)
            distance.clear()
            file.write(str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(coord[2]) + ' ' + str(distanceMiddle) + ' ' + str(round(color[0], 2)) + ' ' + str(round(color[1], 2)) + ' ' + str(round(color[2], 2)) + '\n')
        elif i == len(vertexDistObjCoColorList) - 1:
            for distElem in distance:
                distanceMiddle += distElem
            distanceMiddle /= len(distance)
            distance.clear()
            file.write(str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(coord[2]) + ' ' + str(distanceMiddle) + ' ' + str(round(color[0], 2)) + ' ' + str(round(color[1], 2)) + ' ' + str(round(color[2], 2)) + '\n')
        distance.append(elem[0])
        coord = elem[1]
        color = elem[2]
        i += 1
    file.close
    
def createPolyColorGroups(cont):
    bpy.ops.object.select_all(action='DESELECT')
    layerNum = currentLayer()
    #knocking to necessery scene
    context = bpy.context
    scene = context.scene
    #vertex color
    newColor = (0.0, 0.0, 0.0)
    #looking for objects on current layer
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
    bpy.ops.object.select_all(action='DESELECT')
    for object in scene.objects:
        if object.layers[layerNum]:
            if object.type == 'MESH':
                #mesh from object
                mesh = bpy.context.object.data
                for poly in mesh.polygons:
                    #here we need to pair vertex with group
                    color = []
                    for loop in poly.loop_indices:
                        color = mesh.vertex_colors.active.data[loop].color
                    #расчет a, b, c, d, color
                    threeDots = []
                    i = 0
                    for vertexIndex in poly.vertices:
                        vertex = object.data.vertices[vertexIndex]
                        vertexWorldCo = object.matrix_world * vertex.co
                        i += 1
                        threeDots.append(vertexWorldCo)
                        if i == 3:
                            X1 = threeDots[0].x
                            Y1 = threeDots[0].y
                            Z1 = threeDots[0].z
                            X2 = threeDots[1].x
                            Y2 = threeDots[1].y
                            Z2 = threeDots[1].z
                            X3 = threeDots[2].x
                            Y3 = threeDots[2].y
                            Z3 = threeDots[2].z
                            a = (Y2 - Y1)*(Z3 - Z1) - (Z2 - Z1)*(Y3 - Y1)
                            b = (Z2 - Z1)*(X3 - X1) - (X2 - X1)*(Z3 - Z1)
                            c = (X2 - X1)*(Y3 - Y1) - (Y2 - Y1)*(X3 - X1)
                            d = - X1 * a - Y1 * b - Z1 * c 
                            polyColor.append([a, b, c, d, color])
                    threeDots.clear()
                    
#11. CREATE FILE WITH POLY AND COLOR
def savePolyFile(polyColor):
    #create file if it doesnt exist
    filename = 'Wall.txt'
    file = open(filename, 'w+')
    #open file for writing
    file = open(filename, 'a')
    #current brick color
    color = [0.0, 0.0, 0.0]
    for elem in polyColor:
        color = elem[4]
        file.write(str(elem[0]) + ' ' + str(elem[1]) + ' ' + str(elem[2]) + ' ' + str(elem[3]) + ' ' + str(round(color[0], 2)) + ' ' + str(round(color[1], 2)) + ' ' + str(round(color[2], 2)) + '\n')
    file.close

    


#1. RENAME BRICKS 
rename()   
#2. REMOVING DOUBLES
removeDoubles()
#3. CORRECTING TEXTURES
textureCorrection()
#4. CREATING GROUPS OF VERTICES
objLocGroup = []
groupsCreation(objLocGroup)
#listPrint(objLocGroup)
#5. JOINING PIECES IN ONE MESH
joinPieces()
#6. MAKE PAIR OF VERTEX AND GROUP FOR COLORIZE
#array where verticies assigned to groups
groupsAndVerticies = []
#array where verticies coordinates assigned to color
vertexDistObjCoColorList = []
makePairVertexGroup(groupsAndVerticies, objLocGroup, vertexDistObjCoColorList)
#listPrint(vertexColorDistList)
#emptyAdd(vertexColorDistList)
#7. VERTEX COLORIfZE
polyColor = []
colorizeVerticies(groupsAndVerticies)
#8. NORMALS  CORRECTION
normalsCorrection()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
bpy.ops.object.select_all(action='DESELECT')
#9. CLEAR GROUPS
#clearVertexGroups()
#10. CREATE POLY COLOR GROUPS
#createPolyColorGroups(polyColor)
#11. CREATE FILE WITH PIECES COORDS
#saveVertsFile(vertexDistObjCoColorList)
#savePolyFile(polyColor)