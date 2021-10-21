from math import radians
import bge
import structs
import copy
def testFunc(cont):
    own = cont.owner
    #print(12, own['Interfaces'].checkTile([-0.625, 0.0, 0.0]))
    #print(22, own['Interfaces'].checkMove([0.0, 0.0, 0.0], 'px'))
    own['Interfaces'].setBridges([-0.625, 0.625, 0.0])
    
def init(cont):
    own = cont.owner
    own['Interfaces'] = BarrierCheckerInterfaces(own)
    print('--> Barrier Checker initiated!')

scene = bge.logic.getCurrentScene()
#BridgeInfo = {'Move' : False, 'Bridge To Object' : None, 'Bridge To Position' : None}
BridgesStraight = {'py' : [False, None, None], 'my' : [False, None, None], 'px' : [False, None, None], 'mx' : [False, None, None]}
BridgesDiagonal = {'pypx' : [False, None, None], 'pymx' : [False, None, None], 'mypx' : [False, None, None], 'mymx' : [False, None, None]}

class BridgeData(object):
    __slots__ = ('isBridgeDirection', 'bridgedPlayGround', 'bridgedGridPos', 'checkNearTiles')
    def __init__(self, isBridgeDirection = False, bridgedPlayGround = None, bridgedGridPos = None, checkNearTiles = None):
        self.isBridgeDirection = isBridgeDirection
        self.bridgedPlayGround = bridgedPlayGround
        self.bridgedGridPos = bridgedGridPos
        self.checkNearTiles = checkNearTiles

class BridgeDataByDirection(object):
    __slots__ = ('straightData', 'diagonalData')
    def __init__(self, straightData, diagonalData):
        self.straightData = copy.copy(straightData)
        self.diagonalData = copy.copy(diagonalData)

class BarrierCheckerInterfaces(object):
    def __init__(self, base):
        #база чекера
        self.__base = base
        #откуда луч
        self.__rayStart = self.__base.children['Cast Ray From']
        #куда луч
        self.__rayEnd = self.__rayStart.children['Cast Ray To']
        #массив проверяемых блоков
        self.__checkBlocks = []
        #0 Стоя
        self.__checkBlocks.append(self.__base.children['Ray Move Run/Walk'])
        #1 Сидя
        self.__checkBlocks.append(self.__base.children['Ray Move Crouch'])
        #2 Лежа
        self.__checkBlocks.append(self.__base.children['Ray Move Prone'])
        #это тот блок, который скажет данные для расчет пути без использования большого силуэта. Если можно хотяб проползти, то этого хватит для расчета пути.
        #пока без прыжков, слишком сложная логика.
        self.__checkTileBlocks = []
        self.__checkTileBlocks.append(self.__base.children['Ray Tile 0'])
        self.__checkTileBlocks.append(self.__base.children['Ray Tile 1']) 
        self.__checkTileBlocks.append(self.__base.children['Ray Tile 2']) 
        self.__checkTileBlocks.append(self.__base.children['Ray Tile 3']) 
        
        #центры блоков по которым будут определяться доступные типы перемещения
        self.__checkRayBlocks = []
        for tile in self.__checkTileBlocks:
            currentTileVerticiesWorldPos  = []
            tileCenterPositionX = tile.localPosition.x
            tileCenterPositionY = tile.localPosition.y
            tileCenterPositionZ = tile.localPosition.z
            for mesh in tile.meshes:
                for material_index in range(len(mesh.materials)):
                    for vertex_index in range(mesh.getVertexArrayLength(material_index)):
                        vertex  = mesh.getVertex(material_index, vertex_index)
                        xPos = vertex.getXYZ().x + tileCenterPositionX
                        yPos = vertex.getXYZ().y + tileCenterPositionY
                        zPos = vertex.getXYZ().z + tileCenterPositionZ
                        currentTileVerticiesWorldPos.append((xPos, yPos, zPos))
            self.__checkRayBlocks.append(copy.copy(tuple(currentTileVerticiesWorldPos)))
            currentTileVerticiesWorldPos.clear()
        self.__checkRayBlocks = tuple(self.__checkRayBlocks)
        #print(self.checkTile(self.__base.worldPosition)) #DEBUG
        #на месте
        self.__idleBlock = self.__base.children['Ray Idle']
        self.__idleDistances = [1.9, 1.25, 0.64]
        #возмонжные положения
        #проверка Bridge Tile - тайлы для перехода в другую область
        self.__checkTileBridgeCenter = self.__base.children['Bridge Ray center']
        self.__checkTileBridgesStraight = []
        self.__checkTileBridgesStraight.append(self.__base.children['Bridge Ray py'])
        self.__checkTileBridgesStraight.append(self.__base.children['Bridge Ray my']) 
        self.__checkTileBridgesStraight.append(self.__base.children['Bridge Ray px']) 
        self.__checkTileBridgesStraight.append(self.__base.children['Bridge Ray mx']) 
        self.__tileBridgesStraight = copy.copy(BridgesStraight)
        self.__tileBridgesStraight2 = copy.copy(BridgesStraight)
        
        self.__checkTileBridgesDiagonal = []
        self.__checkTileBridgesDiagonal.append(self.__base.children['Bridge Ray pypx'])
        self.__checkTileBridgesDiagonal.append(self.__base.children['Bridge Ray pymx']) 
        self.__checkTileBridgesDiagonal.append(self.__base.children['Bridge Ray mypx']) 
        self.__checkTileBridgesDiagonal.append(self.__base.children['Bridge Ray mymx']) 
        self.__tileBridgesDiagonal = copy.copy(BridgesDiagonal)
        self.__tileBridgesDiagonal2 = copy.copy(BridgesDiagonal)
        #эта структура нужна для формирования флага диаганального Bridge
        self.__tileMoveStraight = copy.copy(BridgesStraight)
        self.__tileMoveStraight2 = copy.copy(BridgesStraight)
        
        
        
    
    #функция в которой будет обновлено значение Bridge для текущей ячейки
    def setCurrentBridge(self, bridgedPlayGround, checkPlayGround, bridgePosition, bridgeDirection):
        
        if len(bridgeDirection) == 2:
            if bridgedPlayGround != None:
                checkNearTiles = None
                gridPos = bridgedPlayGround['Interfaces'].objGridPosition(bridgePosition)
                self.__tileMoveStraight[bridgeDirection] = [True, bridgedPlayGround, gridPos] #old
                self.__tileMoveStraight2[bridgeDirection] = BridgeData(True, bridgedPlayGround, gridPos, checkNearTiles) #new
                if checkPlayGround.name != bridgedPlayGround.name:
                    self.__tileBridgesStraight[bridgeDirection] = [True, bridgedPlayGround, gridPos, bridgeDirection, checkNearTiles]#old
                    self.__tileBridgesStraight2[bridgeDirection] = BridgeData(True, bridgedPlayGround, gridPos, checkNearTiles)#new
                    checkPlayGround['Interfaces'].addConnectedPlayGround(bridgedPlayGround)
                    return
                self.__tileBridgesStraight[bridgeDirection] = [False, None, None]#old
                self.__tileBridgesStraight2[bridgeDirection] = BridgeData()#new
        if len(bridgeDirection) == 4:
            if bridgedPlayGround != None:
                firstTileCheck = self.__tileMoveStraight[bridgeDirection[0:2]]
                secondTileCheck = self.__tileMoveStraight[bridgeDirection[2:4]]
                if firstTileCheck[0] and secondTileCheck[0]:
                    if checkPlayGround.name != bridgedPlayGround.name:
                        checkNearTiles = (firstTileCheck[1], firstTileCheck[2]), (secondTileCheck[1], secondTileCheck[2])
                        gridPos = bridgedPlayGround['Interfaces'].objGridPosition(bridgePosition)
                        self.__tileBridgesDiagonal[bridgeDirection] = [True, bridgedPlayGround, gridPos, bridgeDirection, checkNearTiles]#old
                        self.__tileBridgesDiagonal2[bridgeDirection] = (True, bridgedPlayGround, gridPos, bridgeDirection, checkNearTiles)#new
                        checkPlayGround['Interfaces'].addConnectedPlayGround(bridgedPlayGround)
                        return
                self.__tileBridgesDiagonal[bridgeDirection] = [False, None, None]#old
                self.__tileBridgesDiagonal2[bridgeDirection] = BridgeData()#new
        
    #проверка возможности перехода в соседние области
    def setBridges(self, worldPos):
        self.__base.worldOrientation = [0.0 , 0.0, 0.0]
        self.__base.worldPosition = worldPos
        beamDistance = 0.6
        self.__rayEnd.localPosition = [0.0, 0.0, -beamDistance]
        self.__rayStart.worldPosition = self.__checkTileBridgeCenter.worldPosition
        hitObject, hitPosition, hitNormal = self.__rayStart.rayCast(self.__rayEnd, self.__rayStart, beamDistance, 'Play Ground', 0, 1)
        checkPlayGround = hitObject

        tempBridgesStraight = BridgesStraight
        #проверка прямых мостов
        self.__tileMoveStraight['py'] = [False, None, None]
        self.__tileMoveStraight['my'] = [False, None, None]
        self.__tileMoveStraight['px'] = [False, None, None]
        self.__tileMoveStraight['mx'] = [False, None, None]
        self.__tileBridgesStraight['py'] = [False, None, None]
        self.__tileBridgesStraight['my'] = [False, None, None]
        self.__tileBridgesStraight['px'] = [False, None, None]
        self.__tileBridgesStraight['mx'] = [False, None, None]
        for bridge in self.__checkTileBridgesStraight:
            
            self.__rayStart.worldPosition = bridge.worldPosition
            hitObject2, hitPosition2, hitNormal2 = self.__rayStart.rayCast(self.__rayEnd, self.__rayStart, beamDistance, 'Play Ground', 0, 1)
            
            if hitObject2!= None:
                if 'RevX' not in checkPlayGround.name: #лестница
                    if 'RevX' not in hitObject2.name: #лестница
                        if 'NonRevY' in hitObject2.name and 'my' in bridge.name:
                            sigma = 0.0001
                            delta = abs(hitPosition.z - hitPosition2.z)
                            if delta > sigma:
                                if hitPosition.z < hitPosition2.z:
                                    continue  
                        elif ('RevY' in hitObject2.name and 'NonRevY' not in hitObject2.name) and 'py' in bridge.name:
                            sigma = 0.0001
                            delta = abs(hitPosition.z - hitPosition2.z)
                            if delta > sigma:
                                if hitPosition.z < hitPosition2.z:
                                    continue  
                        if 'py' in bridge.name:
                            self.setCurrentBridge(hitObject2, checkPlayGround, hitPosition2, 'py')
                        elif 'my' in bridge.name:
                            self.setCurrentBridge(hitObject2, checkPlayGround, hitPosition2, 'my')
                if 'RevY' not in checkPlayGround.name:
                    if 'RevY' not in hitObject2.name: #лестница
                        if 'NonRevX' in hitObject2.name and 'mx' in bridge.name:
                            sigma = 0.0001
                            delta = abs(hitPosition.z - hitPosition2.z)
                            if delta > sigma:
                                if hitPosition.z < hitPosition2.z:
                                    continue
                        elif ('RevX' in hitObject2.name and 'NonRevX' not in hitObject2.name) and 'px' in bridge.name:
                            sigma = 0.0001
                            delta = abs(hitPosition.z - hitPosition2.z)
                            if delta > sigma:
                                if hitPosition.z < hitPosition2.z:
                                    continue  
                        if 'px' in bridge.name:
                            self.setCurrentBridge(hitObject2, checkPlayGround, hitPosition2, 'px')
                        elif 'mx' in bridge.name:
                            self.setCurrentBridge(hitObject2, checkPlayGround, hitPosition2, 'mx')
        #проверка диагональных мостов
        self.__tileBridgesDiagonal['pypx'] = [False, None, None]
        self.__tileBridgesDiagonal['pymx'] = [False, None, None]
        self.__tileBridgesDiagonal['mypx'] = [False, None, None]
        self.__tileBridgesDiagonal['mymx'] = [False, None, None]
        for bridge in self.__checkTileBridgesDiagonal:
            self.__rayStart.worldPosition = bridge.worldPosition
            hitObject3, hitPosition3, hitNormal3 = self.__rayStart.rayCast(self.__rayEnd, self.__rayStart, beamDistance, 'Play Ground', 0, 1)
            if hitObject3 != None:
                if 'Ladder' in hitObject3.name:
                    continue
            if 'pypx' in bridge.name:
                self.setCurrentBridge(hitObject3, checkPlayGround, hitPosition3, 'pypx')
            elif 'pymx' in bridge.name:
                self.setCurrentBridge(hitObject3, checkPlayGround, hitPosition3, 'pymx')
            elif 'mypx' in bridge.name:
                self.setCurrentBridge(hitObject3, checkPlayGround, hitPosition3, 'mypx')
            elif 'mymx' in bridge.name:
                self.setCurrentBridge(hitObject3, checkPlayGround, hitPosition3, 'mymx')

    #проверяем ячейку на доступность перемещения
    def checkTile(self, worldPos):
        checkPosturesResult = self.checkPostures(worldPos)
        #настройка мостов между Play Ground
        self.setBridges(worldPos)
        bridgeDataByDirection = BridgeDataByDirection(self.__tileBridgesStraight, self.__tileBridgesDiagonal)
        return checkPosturesResult, bridgeDataByDirection
           
    def checkHeight(self, height):
        proneHeight = 0.66
        crouchHeight = 1.4
        walkRunHeight  = 1.85
        if height < proneHeight:
            return structs.SoldierMoveTypes.NoMove
        elif (proneHeight < height) and (height < crouchHeight) :
            return structs.SoldierMoveTypes.Prone
        elif (crouchHeight < height) and (height < walkRunHeight) :
            return structs.SoldierMoveTypes.Crouch
        elif walkRunHeight <= height:
            return structs.SoldierMoveTypes.RunWalk
            
    
    def checkPostures(self, worldPos):
        beamDistances = 2.0
        currentTileMoveTypes = []
        hit = False
        for block in self.__checkRayBlocks: # этот момент лишний, т.к. его можно убрать в координаты vertex
            for vertexPos in block:
                rayStartPosX = vertexPos[0] + worldPos.x
                rayStartPosY = vertexPos[1] + worldPos.y
                rayStartPosZ = vertexPos[2] + worldPos.z
                rayStartPos = (rayStartPosX, rayStartPosY, rayStartPosZ)
                rayEndPosZ = rayStartPosZ + beamDistances
                rayEndPos = (rayStartPosX, rayStartPosY, rayEndPosZ)
                hitObject, hitPosition, hitNormal = self.__base.rayCast(rayEndPos, rayStartPos, beamDistances, 'Barrier', 0, 1)
                if hitObject != None:
                    heght = hitPosition.z - rayStartPos[2]
                    maxMoveType = self.checkHeight(heght)
                    currentTileMoveTypes.append(maxMoveType)
                    hit = True
                    break
            if not(hit):
                currentTileMoveTypes.append(structs.SoldierMoveTypes.RunWalk)
            hit = False
        currentTileMoveTypes = tuple(currentTileMoveTypes)
        return currentTileMoveTypes



            
    