from bge import logic
import bge
import copy
from math import sqrt
import random
import structs

scene = bge.logic.getCurrentScene()
computer = scene.objects['Computer']

def init(cont):
    own = cont.owner
    #Команда запуска физики Ragdoll
    'Global'
    #Текущая анимация
    own['Action Name'] = 'UE4standBy'
    #Индикация процесса выполнения смены позиции
    own['Changed Position'] = False
    'Private'
    #Флаг текущего состояния Ragdoll физики
    own['Ragdoll Physics'] = False
    #Action Actuator
    own['Action Actuator'] = cont.actuators["Action"]

    

def spaceKey(cont):
    own = cont.owner
    av = logic.keyboard.active_events
    if bge.events.SPACEKEY in av:
        if av[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            #own['Set Animation'] = True 
            #own['Action Name'] = 'UE4standRelaxed'
            own['Interfaces'].setRagDollPhysics()



#все фишки вызываемые по флагу
#!!! обернуть в функции
def dispetcher(cont):
    own = cont.owner
    if 'Interfaces' not in own:
        return
    #снаружи пришла команда включить анимацию
    own['Interfaces'].actionDispatecher(cont)
    #проверка переходных анимаций
    own['Interfaces'].changePostureAction(cont)
    

#Меленный диспетчер для низкоприоритетных моментов
def slowDispetcher(cont):
    own = cont.owner
    if 'Interfaces' not in own:
        return
    #own['Interfaces'].checkRagdoll(cont)


class SoldierDollInterfaces(object):
    def __init__(self, soldArm, unitController):
        """Constructor"""
        self.__soldArm = soldArm
        #флаг проигрыша анимации
        self.__animationFlag = False
        #
        self.__unitController = unitController
        #список блоково Ragdoll
        self.__ragdollBricksList = []
        #
        self.__ragDollBricksCount = 0
        self.initRagdollBricksList()
        #
        self.__actionName = None
        self.__actionMode = None
        #
        self.__ragdollPhysicsEnabled = False
        #
        self.__unitActionsDict = None
        self.setUnitActionsDict(unitController['Interfaces'].getSubUnitType())

        
        
    def setUnitActionsDict(self, subUnitType):
        self.__unitActionsDict = None#structs.AllActionDicts[subUnitType]

    
    
    #функция для смены положения тела
    def changePostureAction(self, cont):
        #проверка инициализации управляющего алгоритма
        #????
        if not 'Interfaces' in computer:
            return
        own = cont.owner
        unit = self.__unitController
        #проверка инициализации юнита
        #????
        if not 'Interfaces' in unit:
            return
        unitInterf = unit['Interfaces']
        actionName = self.__actionName
        if unitInterf.getChangePosFlag():
            act = cont.actuators["Action"]
            if act.action == actionName:
                #для ускорения анимации
                framesCount = structs.ActionFramesCount[actionName]
                if (act.frame > (framesCount - 1)) and (not(act.frame > framesCount)):
                #как-то неправильно работает условие, для двух персонажей
                    unit = computer['Interfaces'].getPlayerUnit()
                    unitInterf = unit['Interfaces']
                    unitInterf.positionChanged()
        
    #cont - нуно прокинуть иначе не фурычит. Нужен активирующий контроллер.
    def playActionControl(self, cont):
        own = cont.owner
        if self.__actionName == own['Action Actuator'].action:
            return

        own['Action Actuator'].frameStart = 1
        own['Action Actuator'].priority = 0
        own['Action Actuator'].blendIn = 3
        #временная затычка
        if self.__actionName == 'UE4reviveFront_firstFrame':
            own['Action Actuator'].action = 'UE4reviveFront'
            actionName = 'UE4reviveFront'
        else:
            own['Action Actuator'].action = self.__actionName
        own['Action Actuator'].frameEnd = structs.ActionFramesCount[self.__actionName]
        own['Action Actuator'].mode = self.__actionMode
        cont.activate(own['Action Actuator']) # start the actuator

        
        return
        if actionName == 'UE4reviveBack_firstFrame':
            own['Action Actuator'].action = 'UE4reviveBack'
            own['Action Actuator'].frameStart = 1
            own['Action Actuator'].frameEnd = 1
            own['Action Actuator'].priority = 0
            own['Action Actuator'].blendIn = 0
            own['Action Actuator'].mode = bge.logic.KX_ACTIONACT_PLAY
            cont.activate(own['Action Actuator']) # start the actuator
        elif actionName == 'UE4reviveFront_firstFrame':
            own['Action Actuator'].action = 'UE4reviveFront'
            own['Action Actuator'].frameStart = 0
            own['Action Actuator'].frameEnd = 0
            own['Action Actuator'].priority = 0
            own['Action Actuator'].blendIn = 0
            own['Action Actuator'].mode = bge.logic.KX_ACTIONACT_PLAY
            cont.activate(own['Action Actuator']) # start the actuator
        elif actionName == 'UE4armStandBy':
            own['Action Actuator'].action = actionName


    #данный список нужен, чтобы оптимально анимировать ragdoll, когда он отключен
    def initRagdollBricksList(self):
        own = self.__soldArm
        #список блоково Ragdoll
        for constraint in own.constraints:
            if ('Rag' in constraint.name) and not('_loc' in constraint.name) and not('Shoulder' in constraint.name):
                pivot = constraint.target
                pivotName = pivot.name.replace('Pivot', '')
                for child in own.children:
                    if 'Physics' in child.name:
                        boneName = child.name.replace('Physics', '')
                        if pivotName == boneName:
                            self.__ragdollBricksList.append([pivot.parent, child])
                            #через эту штуку будет включаться физика Ragdoll 
                            pivot.parent[own.name] = own
                            #флаг по которому понятно, что блок остановил движение. По сумме таких флагов останавливается  просчет физики
                            pivot.parent.suspendDynamics()
                            if 'pelvis' in child.name:
                                #Точка по которой после регдуло будет искаться ячейка
                                own['Pelvis'] = pivot.parent
            constraint.active = False
        self.__ragDollBricksCount = len(self.__ragdollBricksList)
        
    
    def getRagdollBricksList(self):
        return self.__ragdollBricksList
    
    #определение положение объекта на сетке по его координатам
    def setUnitController(self, unitController):
        self.__unitController = None
         
    #диспетче анимаций
    #cont нужен для того чтобы сработал Actuator
    def actionDispatecher(self, cont):
        if self.__animationFlag:
            self.playActionControl(cont)
            self.__animationFlag = False
    
    #анализ регдола. Включен или нет.
    def checkRagdoll(self, cont):
        own = self.__soldArm
        stopped = 0
        if self.__ragdollPhysicsEnabled:
            for brickBone in self.__ragdollBricksList:
                locAngVel = brickBone[0].getAngularVelocity(True).magnitude
                locLinVel = brickBone[0].getLinearVelocity(True).magnitude 
                if locAngVel != 0.0 or locLinVel != 0.0:
                    #print(brickBone, locAngVel, locLinVel)
                    if locAngVel < 1.0 and locLinVel < 0.8:
                        stopped += 1
        else:
            for brickBone in self.__ragdollBricksList:
                brickBone[0].worldPosition = brickBone[1].worldPosition
                brickBone[0].worldOrientation = brickBone[1].worldOrientation
        #подъем
        if self.__ragDollBricksCount == stopped:
            for brickBone in self.__ragdollBricksList:
                brickBone[0].suspendDynamics()
            #self.playActionControl(cont, 'UE4reviveFront_firstFrame')
            for constraint in own.constraints:
                constraint.active = False
                self.__ragdollPhysicsEnabled = False
            #здесь нужно по pelvis найти координаты ближайшей ячейки
            unit = self.__unitController
            unitPGinterf = unit['Interfaces'].getPGinterfaces()
            playGround = unitPGinterf.getPlayGround()
            gridPosByPelvisWorldPos = playGround['Interfaces'].objGridPosition(own['Pelvis'].worldPosition)
            
            unit['Interfaces'].setUnitWordldPositionByGrid(gridPosByPelvisWorldPos)
            self.playActionControl(cont, 'UE4reviveFront')
         
    def setRagDollPhysics(self):
        for constraint in self.__soldArm.constraints:
            constraint.target.parent.restoreDynamics()
            constraint.active = True
        self.__ragdollPhysicsEnabled = True

    def playActionNew(self, subType, weaponType, soldierState, moveTypeOrChangePosture):
        #к соалению вот так приходится изголятся. Нуен контроллер для активации Action
        #subType = 'Men' #временное решение для дебага
        self.__actionName = subType.name + ' ' + weaponType.name + ' ' + moveTypeOrChangePosture.name
        if soldierState == structs.SoldierStates.Idle:
            self.__actionName += ' Idle'
        self.__actionMode = structs.ActionModes[soldierState]
        self.__animationFlag = True



    def getUnitController(self):
        return self.__unitController
         
    #интерфейсы работы с флагом проигрыша анимации
    def getActionFlag(self):
        return self.__animationFlag
    
    def setActionFlagOff(self):
        self.__animationFlag = False