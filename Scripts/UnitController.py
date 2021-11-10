from bge import logic
from math import sqrt, radians, asin
import bge
import structs
import UnitPlayGroundInterfaces as uPgI
import copy
from SoldierArmature import SoldierDollInterfaces

scene = logic.getCurrentScene()
computer = scene.objects['Computer']



#объект для инициализация Unit Controller
#Удаляется сразу после иницилизации
def initBlock(cont):

    own = cont.owner
    if 'init' in own:
        init(own.groupObject.groupMembers['Unit Controller'])
        own.endObject()
        
#инициализация основного объекта. Unit controller    
def init(unitController):
    unitObjectsGroup = unitController.groupObject
    for member in unitObjectsGroup.groupMembers:
        #пришиваем модельку солдатика к контроллеру
        #контроллер у нас будет хранить всю игровую ифномрацию, а так же управлять моделькой
        if 'Doll' in member.name:
            armatureLocator = unitController.children['Armature Locator']
            member.groupMembers['Soldier Armature'].setParent(armatureLocator)
            unitController['Soldier Armature'] = member.groupMembers['Soldier Armature']

        if 'Rifle' in member.name:
            for member2 in member.groupMembers:
                if 'Ray Start' in member2.name:
                    unitController['Ray Start'] = member2
                elif 'Ray End' in member2.name:
                    unitController['Ray End'] = member2
                elif 'Gun Armature' in member2.name:
                    unitController['Gun Armature'] = member2
                elif 'Bullet Aim' in member2.name:
                    unitController['Bullet Aim'] = member2
        #деюажная фишка, в будущем надо будет сделать красивее
        member.setParent(unitController)
        if 'Controller' in member.name:
            unitController['Unit Controller'] = member
    unitController['init'] = True
    #следующая ячейка для перемещения
    #атакуемый юнитом объект
    unitController['Attack Object'] = None
    unitController['Interfaces'] = UnitInterfaces(unitController)
    unitController['Soldier Armature']['Interfaces'] = SoldierDollInterfaces(unitController['Soldier Armature'], unitController)
    print('---> !_[' + unitController.name + ']_! initiated!')

#включение физики Ragdoll
def setRagdoll(cont):
    own = cont.owner
    own['Soldier Armature']['Interfaces'].setRagDollPhysics()
    

def testFunc(cont):
    nearSens = cont.sensors['Near']
    seenObject = None #объект у которого уже вкдючен Ragdoll
    for object in nearSens.hitObjectList:
        if 'Ragdoll' in object.name:
            if seenObject != object.groupObject.groupObject:
                seenObject = object.groupObject.groupObject
                #unit = object['Soldier Armature'].parent
                object['Soldier Armature']['Interfaces'].setRagDollPhysics()


#проверка состояния юнита и выполнение действия в зависимости от оного       
def checkState(cont):
    own = cont.owner
    if 'Interfaces' not in own:
        return
    own['Interfaces'].moveByPath()
    return

def testFunc2(cont):
    own = cont.owner
    av = logic.keyboard.active_events
    if bge.events.LEFTCTRLKEY in av:
        if av[bge.events.LEFTCTRLKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            return
    own = cont.owner
    bge.logic.sendMessage('Shoot', 'show', own['Gun Armature'].name, '')

UnitPositions = {'Stand' : 0, 'Sit' : 1, 'Lay' : 2}

UnitSpeed = {'Run' : 0.07, 'Walk' : 0.03, 'Crouch' : 0.025, 'Prone' : 0.01, 'Barrel Jump' : 0.032}

UnitZombieSpeed = {'Run' : 0.04, 'Walk' : 0.008, 'Crouch' : 0.025, 'Prone' : 0.01, 'Barrel Jump' : 0.032}

class UnitInterfaces(object):
    def __init__(self, soldier):
        #путь
        """Constructor"""
        #юнит
        self.__unit = soldier
        #тип движения выбранный игроком
        self.__mainMoveType = structs.SoldierMoveTypes.Walk
        #текущий тип движения
        self.__currentMoveType = structs.SoldierMoveTypes.Walk
        #Флаг изменения положения тела
        self.__changingPosture = False
        #максимально возможное положение тела в данной ячейке
        self.__currentMaxMoveType = structs.SoldierMoveTypes.RunWalk
        #uPgI имя класса через as
        self.__uPgI = uPgI.UnitPlayGroundIntefaces(soldier)
        # через UnitController мы понимаем с каким типом и поддтипом юнита мы работаем
        self.__unitType = structs.selectUnitType(self.__unit['Type'])
        if self.__unitType == structs.UnitTypes.Mech:
            self.__subUnitType = structs.selectMechSubType(self.__unit['SubType'])
        elif self.__unitType == structs.UnitTypes.Soldier:
            self.__subUnitType = structs.selectSoldierSubType(self.__unit['SubType'])
        #оружее
        self.__weaponType = structs.selectWeaponType(self.__unit['Weapon'])
        #гуйня
        self.__guiControl = self.__uPgI.getGUIcontrol()
        #скорость юнита
        self.__speed = [0.0, 0.0, 0.0]
        self.__direction = None
        #номер шага в пути
        self.__stepNum = 0
        self.__nextStepNum = 0
        #Путь по которому юнит должен бует перемещеаться, содержит сам путь и нужные анимации с AP
        self.__pathAndMoveTypesAp = None
        #
        self.__currentDestination = None
        #
        self.__stepsCount = 0
        #
        self.__tracker = None
        #
        self.__moveTypeByChangePostureDict = structs.SoldierMoveTypesByChangePostureDict
        #этот флаг нужен, чтобы 10 раз не играли одну и туже анимацию
        #True
        #если дали путь или поменяли moveType
        self.__playAnimation = False

    def getUnitType(self):
        return self.__unitType
    def getSubUnitType(self):
        return self.__subUnitType
    def updateStepNum(self):
        self.__stepNum = self.__nextStepNum
        
    def updateNextStepNum(self):
        self.__nextStepNum += 1
        
    
    #данная функция проверяет дистанцию до текущей точки назначения
    def checkDistance(self):
        delta = self.__unit.worldPosition - self.__currentDestination
        distance = sqrt(delta.x * delta.x + delta.y * delta.y)
        speed = self.__speed
        modSpeed = sqrt(speed[0]*speed[0] + speed[1]*speed[1] + speed[2]*speed[2])
        #если дистанция меньше шага при текущей скорости, то returb True
        if distance - modSpeed < 0.0:
            return True
        return False
    
    def moveByPath(self):
        if self.__uPgI.getState() == structs.UnitStates['Move']:
            if self.__stepsCount > 0:
                if self.__stepNum != self.__stepsCount:
                    if self.__stepNum == self.__nextStepNum:
                        self.setUnitDirection()
                        self.updateNextStepNum()
                    else:
                        if self.__changingPosture:
                            return
                        self.moveUnit()
                        if self.checkDistance():
                            self.__unit.worldPosition = self.__currentDestination
                            self.updateStepNum()
                else:
                    if self.__stepNum == self.__stepsCount:
                        self.finalizeUnitMovement()
                        self.restorePathData()
                        self.setIdleAnimation(self.__currentMoveType)
    
    def finalizeUnitMovement(self):
        #[self.__stepNum] - номер шага
        #[0] - (playground, (y,x))
        #[0][0] - playground
        #[0][1] - (y,x)
        #[0][2] - direction
        finalStep = self.__stepNum - 1
        playGround = self.__pathAndMoveTypesAp[finalStep][0][0]
        unitGridLoc = playGround['Interfaces'].objGridPosition(self.__unit.worldPosition)
        self.__uPgI.setGridLoc(unitGridLoc)                    
        #блокировка для других юнитов текущего тайла
        playGround['Interfaces'].lockGridCoorByUnit(unitGridLoc)
        #проверка позиции
        self.__uPgI.setIdleState()
        
    def setPlayAnimation(self):
        self.__playAnimation = True

    def restorePathData(self):
        self.__pathAndMoveTypesAp = None
        self.__currentDestination = None
        self.__stepNum = 0
        self.__nextStepNum = 0
        self.__speed = [0.0, 0.0, 0.0]
        self.__stepsCount = 0
        #self.__tracker = None #трекер сам себя обнулит
        
    
    def moveUnit(self):
        self.__unit.worldPosition.x += self.__speed[0]
        self.__unit.worldPosition.y += self.__speed[1]
        self.__unit.worldPosition.z += self.__speed[2]
        
    
    #изменение положения тела в пути
    def setPosture(self, changePosture):
        self.__unit['Soldier Armature']['Interfaces'].playActionNew(self.__subUnitType,
                                                                    self.__weaponType,
                                                                    structs.SoldierStates.ChangePosture,
                                                                    changePosture)
        self.__currentMoveType = structs.SoldierMoveTypesByChangePostureDict[changePosture]
        #Лежа в стоя или сидя    
        if changePosture == structs.SoldierChangePosture.LayToStand:
            self.__currentMoveType = self.__mainMoveType
        #Сидя в стоя или лежа
        elif changePosture == structs.SoldierChangePosture.SitToStand:
            self.__currentMoveType = self.__mainMoveType
        self.__changingPosture = True
        self.__playAnimation = True
    
    #установка типа передвижения в пути
    def setCurrentMoveType(self, newMoveType):
        self.__currentMoveType = newMoveType
        # TODO анимация меха
        if self.__unitType == structs.UnitTypes.Mech:
            self.__currentMoveType = structs.SoldierMoveTypes.Walk
        if not self.__playAnimation:
            return
        self.__unit['Soldier Armature']['Interfaces'].playActionNew(self.__subUnitType,
                                                                    self.__weaponType,
                                                                    structs.SoldierStates.Move,
                                                                    self.__currentMoveType)
        self.__playAnimation = False

        
    def setIdleAnimation(self, idleMoveType):
        self.__unit['Soldier Armature']['Interfaces'].playActionNew(self.__subUnitType,
                                                                    self.__weaponType,
                                                                    structs.SoldierStates.Idle,
                                                                    idleMoveType)
        
    
    def setUnitDirection(self):
        #[self.__stepNum] - номер шага
        #[0] - (playground, (y,x))
        #[0][0] - playground
        #[0][1] - (y,x)
        #[0][2] - direction
        direction = self.__pathAndMoveTypesAp[self.__stepNum][0][2]
        self.__uPgI.setMoveDirection(direction)
        #[1] - (isChangePosture, moveType or changePosture, AP)
        #[1][0] - isChangePosture
        #[1][1] - moveType or changePosture
        #[1][2] - AP
        isChangePosture = self.__pathAndMoveTypesAp[self.__stepNum][1][0]
        if isChangePosture:
            #TODO норм нужна логика
            if self.__unitType == structs.UnitTypes.Mech:
                isChangePosture = False
                self.__stepNum += 1
        if isChangePosture:
            changePosture = self.__pathAndMoveTypesAp[self.__stepNum][1][1]
            self.setPosture(changePosture)
        else:
            currentMoveType = self.__pathAndMoveTypesAp[self.__stepNum][1][1]
            self.setCurrentMoveType(currentMoveType)
            self.setSpeed(direction)
            playGroundTo = self.__pathAndMoveTypesAp[self.__stepNum][0][0]
            self.__uPgI.setPlayGround(playGroundTo)
            self.setCurrentDestination()
            if self.__tracker != None:
                self.__tracker = self.__tracker['Interfaces'].removePathPoint()
        if self.isTrackerExist():
            ap = self.__pathAndMoveTypesAp[self.__stepNum][1][2]
            self.__tracker['Interfaces'].updateAP(ap)
    
    def isTrackerExist(self):
        if self.__tracker == None:
            return False
        return True
    
    def setCurrentDestination(self):
        #[self.__stepNum] - номер шага
        #[0] - (playground, (y,x))
        #[0][0] - playground
        #[0][1] - (y,x)
        #[0][2] - direction
        playGroundTo = self.__pathAndMoveTypesAp[self.__stepNum][0][0]
        grid = playGroundTo['Interfaces'].getGridCoor()
        destinationTileOnMap = self.__pathAndMoveTypesAp[self.__stepNum][0][1]
        yPos = destinationTileOnMap[0]
        xPos = destinationTileOnMap[1]
        self.__currentDestination = grid[yPos][xPos] 
        

    def getPGinterfaces(self):
        return self.__uPgI
        

    def getChangePosFlag(self):
        return self.__changingPosture

    #установка скорости для перемещения по пути
    def setSpeed(self, direction):
        #выбор модуля скорости
        unitSpeedDict = UnitSpeed
        if self.__subUnitType == structs.SoldierSubType.Zombie:
            unitSpeedDict = UnitZombieSpeed
        if self.__currentMoveType == structs.SoldierMoveTypes.Run:
            straightSpeed = unitSpeedDict['Run']
        elif self.__currentMoveType == structs.SoldierMoveTypes.Walk:
            straightSpeed = unitSpeedDict['Walk']
        elif self.__currentMoveType == structs.SoldierMoveTypes.Crouch:
            straightSpeed = unitSpeedDict['Crouch']
        elif self.__currentMoveType == structs.SoldierMoveTypes.Prone:
            straightSpeed = unitSpeedDict['Prone']
        elif self.__currentMoveType == structs.SoldierMoveTypes.BarrelJump:
            straightSpeed = unitSpeedDict['Barrel Jump']
        #TODO нужно сделать по нормальному для меха
        if self.__unitType == structs.UnitTypes.Mech:
            straightSpeed = structs.MechMoveSpeed[structs.MechMoveTypes.Walk]
        #выбор скорости по одной из осей
        if len(direction) == 2:
            if direction == 'py':
                self.__speed = [0.0, -straightSpeed, 0.0]
            elif direction == 'my':
                self.__speed = [0.0, straightSpeed, 0.0]
            elif direction == 'px':
                self.__speed = [straightSpeed, 0.0, 0.0]
            elif direction == 'mx':
                self.__speed = [-straightSpeed, 0.0, 0.0]
        #выбор скорости по по двум осям одновременно
        elif len(direction) == 4:
            cos45 = 0.7071067812
            diagonalSpeed = straightSpeed * cos45
            if direction == 'pypx':
                self.__speed = [diagonalSpeed, -diagonalSpeed, 0.0]
            elif direction == 'pymx':
                self.__speed = [-diagonalSpeed, -diagonalSpeed, 0.0]
            elif direction == 'mypx':
                self.__speed = [diagonalSpeed, diagonalSpeed, 0.0]
            elif direction == 'mymx':
                self.__speed = [-diagonalSpeed, diagonalSpeed, 0.0]
    
    def getMainMoveType(self):
        return self.__mainMoveType
    
    def getCurrentMoveType(self):
        return self.__currentMoveType

    def getMaxCurrentMoveType(self):
        return self.__currentMaxMoveType

    #armature
    def positionChanged(self):
        self.__changingPosture = False
        if self.__uPgI.getState() == structs.UnitStates['Move']:
            self.setPathMoveType(self.__currentMoveType)
            self.__guiControl['Interfaces'].updateMoveTypeButton()
        elif self.__uPgI.getState() == structs.UnitStates['Idle']:
            self.setIdleAnimation(self.__currentMoveType)
            self.__guiControl['Interfaces'].updateMoveTypeButton()
        self.updateStepNum()

    @staticmethod
    def get_change_posture_name(old_move_type, new_move_type):
        if (old_move_type == structs.SoldierMoveTypes.Run) or \
                (old_move_type == structs.SoldierMoveTypes.Walk):
            if new_move_type == structs.SoldierMoveTypes.Crouch:
                change_posture = structs.SoldierChangePosture.StandToSit
            elif new_move_type == structs.SoldierMoveTypes.Prone:
                change_posture = structs.SoldierChangePosture.StandToLay
        elif old_move_type == structs.SoldierMoveTypes.Crouch:
            if (new_move_type == structs.SoldierMoveTypes.Run) or \
                    (new_move_type == structs.SoldierMoveTypes.Walk):
                change_posture = structs.SoldierChangePosture.SitToStand
            elif new_move_type == structs.SoldierMoveTypes.Prone:
                change_posture = structs.SoldierChangePosture.SitToLay
        elif old_move_type == structs.SoldierMoveTypes.Prone:
            if (new_move_type == structs.SoldierMoveTypes.Run) or \
                    (new_move_type == structs.SoldierMoveTypes.Walk):
                change_posture = structs.SoldierChangePosture.LayToStand
            elif new_move_type == structs.SoldierMoveTypes.Crouch:
                change_posture = structs.SoldierChangePosture.LayToSit
        return change_posture


    def changeMoveTypeFromGUI(self, newMoveType):
        run = structs.SoldierMoveTypes.Run
        walk = structs.SoldierMoveTypes.Walk
        if newMoveType != self.__mainMoveType:
            self.__changingPosture = True
            if (self.__mainMoveType == walk) and (newMoveType == run):
                self.__changingPosture = False
            elif (self.__mainMoveType == run) and (newMoveType == walk):
                self.__changingPosture = False
            if self.__changingPosture:
                changePosture = self.get_change_posture_name(self.__mainMoveType, newMoveType)
                self.__unit['Soldier Armature']['Interfaces'].playActionNew(self.__subUnitType,
                                                                            self.__weaponType,
                                                                            structs.SoldierStates.ChangePosture,
                                                                            changePosture)
        self.__mainMoveType = newMoveType
        self.__currentMoveType = self.__mainMoveType

    #GUI    
    #помни про AP
    def setRunMainMoveType(self):
        self.changeMoveTypeFromGUI(structs.SoldierMoveTypes.Run)
    #GUI
    def setWalkMainMoveType(self):
        self.changeMoveTypeFromGUI(structs.SoldierMoveTypes.Walk)
    #GUI     
    def setCrouchMainMoveType(self):
        self.changeMoveTypeFromGUI(structs.SoldierMoveTypes.Crouch)
    #GUI     
    def setProneMainMoveType(self):
        self.changeMoveTypeFromGUI(structs.SoldierMoveTypes.Prone)
    #текущее максимальное положение 
    def setCurrentMaxMoveType(self, newMoveType):
        if newMoveType  == structs.SoldierMoveTypes.RunWalk:
            self.__currentMaxMoveType = structs.SoldierMoveTypes.RunWalk
        elif newMoveType  == structs.SoldierMoveTypes.Crouch:
            self.__currentMaxMoveType = structs.SoldierMoveTypes.Crouch
        elif newMoveType  == structs.SoldierMoveTypes.Prone:
            self.__currentMaxMoveType = structs.SoldierMoveTypes.Prone
        self.__guiControl['Interfaces'].updateMoveTypeButton()
    
    #определение текущего направления движения
    def setPathDirection(self, stepIndex, path):
        currentPlayGround = path[stepIndex][0]
        currentGridCoor = path[stepIndex][1]
        prevPlayGround = path[stepIndex - 1][0]
        prevGridCoor = path[stepIndex - 1][1]
        if currentPlayGround.name == prevPlayGround.name:
            deltaY = currentGridCoor[0] - prevGridCoor[0]
            deltaX = currentGridCoor[1] - prevGridCoor[1]
            #AP перемещения
            if (deltaY > 0) and (deltaX > 0):
                return 'pypx'                     
            elif (deltaY < 0) and (deltaX > 0):
                return 'mypx'
            elif (deltaY < 0) and (deltaX < 0):
                return 'mymx'
            elif (deltaY > 0) and (deltaX < 0):
                return 'pymx'
            elif (deltaY > 0) and (deltaX == 0):
                return 'py'
            elif (deltaY < 0) and (deltaX == 0):
                return 'my'
            elif (deltaY == 0) and (deltaX < 0):
                return 'mx'
            elif (deltaY == 0) and (deltaX > 0):
                return 'px'
        else:
            return prevPlayGround['Interfaces'].getBridgeDirection(prevGridCoor, currentPlayGround, currentGridCoor)
            
    #выбор анимации изменения move type и затрачиваемых на действие AP
    def getChangePostureAndAP(self, currentMoveType, checkMoveType):
        if currentMoveType == structs.SoldierMoveTypes.RunWalk:
            if checkMoveType == structs.SoldierMoveTypes.Crouch:
                changePosture = structs.SoldierChangePosture.StandToSit
            elif checkMoveType == structs.SoldierMoveTypes.Prone:
                changePosture =  structs.SoldierChangePosture.StandToLay
        elif currentMoveType == structs.SoldierMoveTypes.Crouch:
            if checkMoveType == structs.SoldierMoveTypes.RunWalk:
                changePosture = structs.SoldierChangePosture.SitToStand
            elif checkMoveType == structs.SoldierMoveTypes.Prone:
                changePosture = structs.SoldierChangePosture.SitToLay
        elif currentMoveType == structs.SoldierMoveTypes.Prone:
            if checkMoveType == structs.SoldierMoveTypes.RunWalk:
                changePosture = structs.SoldierChangePosture.LayToStand
            elif checkMoveType == structs.SoldierMoveTypes.Crouch:
                changePosture = structs.SoldierChangePosture.LayToSit
        actionPoints = structs.SoldierChangePostureAP[changePosture]
        isChangePosture = True
        return (isChangePosture, changePosture, actionPoints)
            
    #AP в зависиомтси от направления движения
    def getApByMoveTypeAndDirection(self, moveType, direction):
        if len(direction) == 2:
            if moveType == structs.SoldierMoveTypes.Run:
                return structs.SoldierMoveAP.RunStraight.value
            elif moveType == structs.SoldierMoveTypes.Walk:
                return structs.SoldierMoveAP.WalkStraight.value
            elif moveType == structs.SoldierMoveTypes.Crouch:
                return structs.SoldierMoveAP.CrouchStraight.value
            elif moveType == structs.SoldierMoveTypes.Prone:
                return structs.SoldierMoveAP.ProneStraight.value
            elif moveType == structs.SoldierMoveTypes.BarrelJump:
                return structs.SoldierMoveAP.BarrelJumpStraight.value
        elif len(direction) == 4:
            if moveType == structs.SoldierMoveTypes.Run:
                return structs.SoldierMoveAP.RunDiagonal.value
            elif moveType == structs.SoldierMoveTypes.Walk:
                return structs.SoldierMoveAP.WalkDiagonal.value
            elif moveType == structs.SoldierMoveTypes.Crouch:
                return structs.SoldierMoveAP.CrouchDiagonal.value
            elif moveType == structs.SoldierMoveTypes.Prone:
                return structs.SoldierMoveAP.ProneDiagonal.value
                
    #добавление к пути типа перемещения и затрачиваемые на действие AP
    def checkCurrentMoveType(self, currentMoveType, maxMoveType, playGroundAndGridCoor, isLastStepInPath):
        tempCurrentMoveType = currentMoveType
        mainMoveType = self.__mainMoveType
        if (mainMoveType == structs.SoldierMoveTypes.Run) or \
                (mainMoveType == structs.SoldierMoveTypes.Walk):
            mainMoveType = structs.SoldierMoveTypes.RunWalk
        if (currentMoveType == structs.SoldierMoveTypes.Run) or \
                (currentMoveType == structs.SoldierMoveTypes.Walk):
            tempCurrentMoveType = structs.SoldierMoveTypes.RunWalk
        if maxMoveType.value <= mainMoveType.value:
            maxMoveType = mainMoveType
        if maxMoveType != tempCurrentMoveType:
            changePostureAndAP = self.getChangePostureAndAP(tempCurrentMoveType, maxMoveType)
            self.__pathAndMoveTypesAp.append((playGroundAndGridCoor,changePostureAndAP))
            tempCurrentMoveType = maxMoveType
        if not(isLastStepInPath):
            if maxMoveType == mainMoveType:
                tempCurrentMoveType = self.__mainMoveType
            direction = playGroundAndGridCoor[2]
            apToMove = self.getApByMoveTypeAndDirection(tempCurrentMoveType, direction)
            isChangePosture = False
            moveTypeAndAP = (isChangePosture, tempCurrentMoveType, apToMove)
            self.__pathAndMoveTypesAp.append((playGroundAndGridCoor, moveTypeAndAP))  
        return tempCurrentMoveType
        
        
    #в данной функции расчитвается допустимые move type для перемещения в ячейку и move type для нахождения на ячейке
    def calcAP3(self, path, tracker):
        self.__tracker = tracker
        lastTileInPathId = len(path) - 1
        self.__pathAndMoveTypesAp = []
        isLastStepInPath = False
        currentMoveType = self.__currentMoveType
        for idg, playGroundAndGridCoor in enumerate(path):
            #пропускаем первую точку пути, т.к. на ней стоит юнит
            if idg == 0:
                continue
            playGround = playGroundAndGridCoor[0]
            pathGridCoor = playGroundAndGridCoor[1]
            maxMoveTypeMoveStay = playGround['Interfaces'].getMoveTypeByGridCoor(pathGridCoor, path[idg - 1])
            maxMoveTypeMove = maxMoveTypeMoveStay[0]
            currentMoveType = self.checkCurrentMoveType(currentMoveType, maxMoveTypeMove, playGroundAndGridCoor, isLastStepInPath)
            if idg == lastTileInPathId:
                maxMoveTypeStay = maxMoveTypeMoveStay[1]
                isLastStepInPath = True
                currentMoveType = self.checkCurrentMoveType(currentMoveType, maxMoveTypeStay, playGroundAndGridCoor, isLastStepInPath)
        #суммарное число AP
        self.__pathAndMoveTypesAp = tuple(self.__pathAndMoveTypesAp)
        '''
        print('Current path and move types')
        for id, elem in enumerate(self.__pathAndMoveTypesAp):
            print(id, elem)
        '''
        sumAP = 0
        for elem in self.__pathAndMoveTypesAp:
            sumAP += elem[1][2]
        self.__stepsCount = len(self.__pathAndMoveTypesAp)
        return sumAP

    #установка типа передвижения в пути
    def setPathMoveType(self, pathMoveType):
        self.__currentMoveType = pathMoveType
        self.__unit['Soldier Armature']['Interfaces'].playActionNew(self.__subUnitType,
                                                                    self.__weaponType,
                                                                    structs.SoldierStates.Move,
                                                                    self.__currentMoveType)


    #AP в зависиомтси от направжения двиения
    def getAPbyDirecMoveType(self, direction, moveType, pathFinal):
        if pathFinal:
            return 0
        if len(direction) == 2:
            if moveType == structs.SoldierMoveTypes.Run:
                return structs.SoldierMoveAP['Run straight']
            elif moveType == structs.SoldierMoveTypes.Walk:
                return structs.SoldierMoveAP['Walk straight']
            elif moveType == structs.SoldierMoveTypes.Crouch:
                return structs.SoldierMoveAP['Crouch straight']
            elif moveType == structs.SoldierMoveTypes.Prone:
                return structs.SoldierMoveAP['Prone straight']
            elif moveType == structs.SoldierMoveTypes.BarrelJump:
                return structs.SoldierMoveAP['Barrel Jump Straight']
        elif len(direction) == 4:
            if moveType == structs.SoldierMoveTypes.Run:
                return structs.SoldierMoveAP['Run diagonal']
            elif moveType == structs.SoldierMoveTypes.Walk:
                return structs.SoldierMoveAP['Walk diagonal']
            elif moveType == structs.SoldierMoveTypes.Crouch:
                return structs.SoldierMoveAP['Crouch diagonal']
            elif moveType == structs.SoldierMoveTypes.Prone:
                return structs.SoldierMoveAP['Prone diagonal']


    #анимирование атаки по типу перемещения
    def setAttackAnimation(self):
        if self.__currentMoveType == structs.SoldierMoveTypes.Run or \
                self.__currentMoveType == structs.SoldierMoveTypes.Walk:
            pass
            #self.__unit['Soldier Armature']['Interfaces'].playActionOld('UE4fireStand')

    #установка координат юнита
    def setUnitWordldPositionByGrid(self, gridPos):
        playGround = self.__uPgI.getPlayGround()
        grid = playGround['Interfaces'].getGridCoor()
        worldPos = grid[gridPos[0]][gridPos[1]]
        #по координатам нужно найти ближайшую свободную ячейку
        self.__unit.worldPosition.x = worldPos.x
        self.__unit.worldPosition.y = worldPos.y
        self.__uPgI.setGridLoc(gridPos)
