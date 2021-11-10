import PlayGround
import copy
import bge
from math import sqrt
import time
import os



def BinarySearch(lys, val):
    first = 0
    last = len(lys) - 1
    index = -1
    sigma = 0.0000000001 #модификация оригинала
    while (first <= last) and (index == -1):
        mid = (first + last) // 2
        #if lys[mid] == val:
        if abs(lys[mid][0] - val) < sigma:  #модификация оригинала
            index = mid
        else:
            if val < lys[mid][0]:
                last = mid - 1
            else:
                first = mid + 1
    return index

class DestructibleObjectInterfaces(object):
    #__slots__ = ('object', 'bricksByColor', 'mesh', 'currentColor', 'damagedBlocks')
    def __init__(self, object):
        self.object = object
        self.bricksByColor = [] #здесь хранятся пара [модулб цвета, [индексы вершин из self.verticies]]
        self.mesh = self.object.meshes[0]
        self.material_index = 0
        self.verticies = [] #вершины
        for material_index in range(len(self.mesh.materials)):
            for vertex_index in range(self.mesh.getVertexArrayLength(material_index)):
                vertex = self.mesh.getVertex(material_index, vertex_index)
                self.verticies.append(vertex)

        #path = "D:/Imagination/{3d}/{Blender}/{BGEforever}/[Silent Souls]current/Project Assembly/"
        #os.makedirs(path, exist_ok=True)
        #filename = path + self.object.name + '.txt'
        #self.file = open(filename, 'w')

        self.initBricksByColor()
        self.colorMagn = None
        self.thread2 = None
        print(self.object, 'DestructibleObjectInterfaces' )

        if 'Floor Floor' in object.name:
            return
            object.endObject()

    #инициализация нового блока по цвету. добавление его в массив. сортировка массива по модулю цвета.
    def initNewVertexListByColor(self, colorMagn, vertex_index):
        newVertexList = []
        newVertexList.append(vertex_index)
        newPair = [colorMagn, newVertexList]
        self.bricksByColor.append(newPair)
        # сортировка по модулю цвета
        self.bricksByColor = sorted(self.bricksByColor, key=lambda colorVerticies: colorVerticies[0])

    #обновление массива блоков по цвету
    def updateColorsAndVertexList(self, vertex_index):
        vertex = self.verticies[vertex_index]
        colorMagn = vertex.color.length
        #self.file.write( str(colorMagn) + ' ' + str(vertex.color) + '\n')
        #условие инициализации списка цветов с вертексами
        if len(self.bricksByColor) == 0:
            self.initNewVertexListByColor(colorMagn, vertex_index)
            return
        index = BinarySearch(self.bricksByColor, colorMagn)
        if index >= 0:
            self.bricksByColor[index][1].append(vertex_index)
            return

        self.initNewVertexListByColor(colorMagn, vertex_index)

    #инициализация массива блоков по цвету
    def initBricksByColor(self):
        for vertex_index, vertex in enumerate(self.verticies):
            self.updateColorsAndVertexList(vertex_index)

    #удаление блока по цвету
    def removeBrickByColor(self, thread, colorMagn):
        index = BinarySearch(self.bricksByColor, colorMagn)
        if index >= 0:
            for vertex_index in self.bricksByColor[index][1]:
                vertex = self.verticies[vertex_index]
                vertex.XYZ = (0.0, 0.0, 0.0)
            #del self.bricksByColor[index]
            #thread.setProcessingFlagOn(self.updatePhysicsAndCollision)
            thread.addFuncToCall(self.updatePhysicsAndCollision, self.object)

    def removeBrickByColor2(self, thread1, thread2, colorMagn):
        self.colorMagn = colorMagn
        self.thread2 = thread2
        thread1.addFuncToCall(self.removeBrickByColor22, self.colorMagn)

    def removeBrickByColor22(self):
        index = BinarySearch(self.bricksByColor, self.colorMagn)
        if index >= 0:
            for vertex_index in self.bricksByColor[index][1]:
                vertex = self.verticies[vertex_index]
                vertex.XYZ = (0.0, 0.0, 0.0)
            self.thread2.addFuncToCall(self.updatePhysicsAndCollision, self.object)




    #перемещение вершин удаляемого блока
    def moveVerticiesByColor(self, colorMagn):
        index = BinarySearch(self.bricksByColor, colorMagn)
        if index >= 0:
            for vertex_index in self.bricksByColor[index][1]:
                vertex = self.verticies[vertex_index]
                vertex.XYZ = (0.0, 0.0, 0.0)
            del self.bricksByColor[index]

    def updatePhysicsAndCollision(self):
        self.object.reinstancePhysicsMesh()
        #self.object.addCollisionCallback()



def init(building):
    building['Interfaces'] = BuildingInterfaces(building)

class BuildingInterfaces(object):
    def __init__(self, building):
        self.__building = building
        
        #создание списка с этажами
        floorsNames = []
        for member in building.groupMembers:
            floorsNames.append(member.name)
        floorsNames.sort()
        self.__floors = []
        for floorName in floorsNames:
            self.__floors.append(building.groupMembers[floorName])
            
        self.__playGroundsList = []
        self.initPlayGround()
        
        self.initCollisionCallbacks()
        
        self.initDestructableObjects()

        self.__verticiesByColors = []




    #инициализация play ground
    def initPlayGround(self):
        for floor in self.__floors:
            for member in floor.groupMembers:
                if 'Play Ground' in member.name:
                    self.__playGroundsList.append(member)
                    if ('Ladder' in member.name):
                        PlayGround.init_ladder(member)
                    else:
                        PlayGround.init(member)
        
    

        
    def initDestructableObjects(self):
        for floor in self.__floors:
            for member in floor.groupMembers:
                if 'Play Ground' not in member.name:
                    member['Interfaces'] = DestructibleObjectInterfaces(member)
        print(self.__building, '---> Destructable objects initiated!')
        
    
    def getFloorsList(self):
        return self.__floors
        
        
    def getPlayGroundsList(self):
        return self.__playGroundsList
            
    def showFloor(self, number):
        for member in self.__floors[number].groupMembers:
            if 'Play Ground' in member.name:
                member['Play Ground'] = True
                continue
            member.color = [1.0,1.0,1.0,1.0]
                        
    def hideFloor(self, number):
        if number > (len(self.__floors) - 1):
            return
        for member in self.__floors[number].groupMembers:
            if 'Play Ground' in member.name:
                del member['Play Ground']
                continue
            member.color = [1.0,1.0,1.0, 0.0]

    # функция которая должна быть добавлена к объекту для обоработки столкновений
    def initCollisionCallbacks(self):
        for floor in self.__floors:
            for member in floor.groupMembers:
                if 'Play Ground' not in member.name:
                    member = CollisionUpdate(member)
        print(self.__building, '---> Collision Callbacks initiated!')


# Method form
class CollisionUpdate(bge.types.KX_GameObject):
    def __init__(self, old_owner):
        self.object = None
        self.addCollisionCallback()
        # TODO нужно через инициализацию прокинуть сюда этот алгоритм
        scene = bge.logic.getCurrentScene()
        self.computer = scene.objects['Computer']



    def on_collision_three(self, object, point, normal):
        #self.removeCollisionCallback()
        object.removeCollisionCallback()
        self.object = object
        self.computer['Interfaces'].mechDamageObject(self, point, normal)
        #print(self, 'Hit by %r at %s with normal %s' % (object.name, point, normal))

    def addCollisionCallback(self):
        self.collisionCallbacks.append(self.on_collision_three)
        if self.object != None:
            self.object.addCollisionCallback()

    def removeCollisionCallback(self):
        self.collisionCallbacks.clear()





