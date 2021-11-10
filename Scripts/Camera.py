import bge
from math import sqrt, degrees
import time 
import copy

mainScene = None

for scene in bge.logic.getSceneList():
    if scene.name == "Scene":
        mainScene = scene
        break
camContrMove = mainScene.objects['Camera Control Move']
camContrMoveMain = mainScene.objects['Camera Control Move Main']
camContrRotateMain = mainScene.objects['Camera Control Rotation Main']
camContrRotate = mainScene.objects['Camera Control Rotation']
camContrZoom = mainScene.objects['Camera Control Zoom']

camHorizSpeed = 0.2

def checkRotation():
    if camContrMoveMain.worldOrientation != camContrRotateMain.worldOrientation:
        camContrMove.removeParent()
        camContrMoveMain.worldPosition = camContrMove.worldPosition
        camContrMove.setParent(camContrMoveMain)
        camContrMoveMain.worldOrientation = camContrRotateMain.worldOrientation
    
def moveWest(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x -= camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition

def moveEast(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x += camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition
    
def moveSouth(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.y -= camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition
    
def moveNorth(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.y += camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition

#diagonal
def moveNorthWest(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x -= camHorizSpeed
        camContrMove.localPosition.y += camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition
           
def moveNorthEast(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x += camHorizSpeed
        camContrMove.localPosition.y += camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition
    
def moveSouthWest(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x -= camHorizSpeed
        camContrMove.localPosition.y -= camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition
    
def moveSouthEast(cont):
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        checkRotation(cont)
        camContrMove.localPosition.x += camHorizSpeed
        camContrMove.localPosition.y -= camHorizSpeed
        camContrRotateMain.worldPosition = camContrMove.worldPosition

def initRotateHUD(cont):
    own = cont.owner
    own['Mouse Position Prev X'] = None
    own['Mouse Position Cur X'] = None
    own['Mouse Position Prev Y'] = None
    own['Mouse Position Cur Y'] = None

camRotateHorizSpeed = 0.05
camRotateVertSpeed = 0.025

def rotate(cont):
    own = cont.owner
    sensors = cont.sensors
    for scene in bge.logic.getSceneList():
        if scene.name == 'GUI':
            cursor = scene.objects['Cursor']
            break
    if cursor.getCursorOver() != None:
        return
    own['Mouse Position Cur X'] = cursor.cursorPos[0]
    own['Mouse Position Cur Y'] = cursor.cursorPos[1]
    if own['Mouse Position Prev X'] != None:
        deltaX = own['Mouse Position Cur X'] - own['Mouse Position Prev X']
        deltaY = own['Mouse Position Cur Y'] - own['Mouse Position Prev Y']
        if abs(deltaX) > abs(deltaY):
            if deltaX > 0.0:
                tempOrient = camContrRotateMain.worldOrientation.to_euler()
                tempOrient.z += camRotateHorizSpeed
                camContrRotateMain.worldOrientation = tempOrient.to_matrix()
            elif deltaX < 0.0:
                tempOrient = camContrRotateMain.worldOrientation.to_euler()
                tempOrient.z -= camRotateHorizSpeed
                camContrRotateMain.worldOrientation = tempOrient.to_matrix()
        elif abs(deltaX)< abs(deltaY):
            if deltaY > 0.0:
                tempOrient = camContrRotate.localOrientation.to_euler()
                #Ограничение по углу, чтобы под пол не проваливались
                if degrees(tempOrient.x) > 15.0:
                    tempOrient.x -= camRotateVertSpeed
                    camContrRotate.localOrientation = tempOrient.to_matrix()
            elif deltaY < 0.0:
                tempOrient = camContrRotate.localOrientation.to_euler()
                # Ограничение по углу, чтобы под пол не проваливались
                if degrees(tempOrient.x) < 45.0:
                    tempOrient.x += camRotateVertSpeed
                    camContrRotate.localOrientation = tempOrient.to_matrix()
    own['Mouse Position Prev X'] = own['Mouse Position Cur X']
    own['Mouse Position Prev Y'] = own['Mouse Position Cur Y']

camVertSpeed = 3.0

#TODO ограничение по высоте, чтобы под пол не улетали или в космос
def moveUp(cont):
    own = cont.owner
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        # TODO сюда нужно прокинуть высоту пола самого верхнего этажа
        if own.localPosition.z < 25.0:
            own.localPosition.z += camVertSpeed
        
    
def moveDown(cont):
    own = cont.owner
    sensors = cont.sensors
    if (sensors[0].positive) and (sensors[1].positive):
        # TODO сюда нужно прокинуть высоту пола самого нижнего этажа
        if own.localPosition.z > 10.0:
            own.localPosition.z -= camVertSpeed

#перемещение камеры влево
def moveCamLeft():
    checkRotation()
    camContrMove.localPosition.x -= camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры в левый верхний угол
def moveCamLeftUp():
    checkRotation()
    camContrMove.localPosition.x -= camHorizSpeed
    camContrMove.localPosition.y += camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры в левый нижний угол    
def moveCamLeftDown():
    checkRotation()
    camContrMove.localPosition.x -= camHorizSpeed
    camContrMove.localPosition.y -= camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры наверх
def moveCamUp():
    checkRotation()
    camContrMove.localPosition.y += camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры вниз
def moveCamDown():
    checkRotation()
    camContrMove.localPosition.y -= camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры вправо
def moveCamRight():
    checkRotation()
    camContrMove.localPosition.x += camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры вправо вверх
def moveCamRightUp():
    checkRotation()
    camContrMove.localPosition.x += camHorizSpeed
    camContrMove.localPosition.y += camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
#перемещение камеры вправо вниз    
def moveCamRightDown():
    checkRotation()
    camContrMove.localPosition.x += camHorizSpeed
    camContrMove.localPosition.y -= camHorizSpeed
    camContrRotateMain.worldPosition = camContrMove.worldPosition
    

def init(cont):
    own = cont.owner
    own.setParent(own.parent)

camContrMove['prev time'] = time.clock()
camContrMove['curr time'] = time.clock()

def cursorCamPos():
    #это срамье надо убрать
    '''
    if 'GUI' not in bge.logic.getSceneList():
        return
    '''
    for scene in bge.logic.getSceneList():
        if scene.name == 'GUI':
            cursor = scene.objects['Cursor']
            break
    
    xPos = cursor.cursorPos[0]
    yPos = cursor.cursorPos[1]
    maxPos = 0.99
    minPos = 0.005
    if xPos < minPos:
        if (yPos < maxPos) and (yPos > minPos):
            moveCamLeft()
        elif yPos < minPos:
            moveCamLeftUp()
        elif yPos > maxPos:
            moveCamLeftDown()
    elif (xPos < maxPos) and (xPos > minPos):
        if yPos < minPos:
            moveCamUp()
        elif yPos > maxPos:
            moveCamDown()
    elif xPos > maxPos:
        if (yPos < maxPos) and (yPos > minPos):
            moveCamRight()
        elif yPos < minPos:
            moveCamRightUp()
        elif yPos > maxPos:
            moveCamRightDown()