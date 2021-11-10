import bge
from enum import Enum

# виды перемещения юнита
class SoldierMoveTypes(Enum):
    RunWalk = -1
    Run = 0
    Walk = 1
    Crouch = 2
    Prone = 3
    BarrelJump = 4
    NoMove = 99

# виды перемещения юнита
class MechMoveTypes(Enum):
    Walk = 1
    NoMove = 99
#скорость меха
MechMoveSpeed = {
    MechMoveTypes.Walk : 0.06,
}

#виды оружия
class WeaponTypes(Enum):
    Rifle = 0
    Hands = 1

#выбор под типы пеших юнитов по признаку
def selectWeaponType(weaponName):
    if 'Rifle' == weaponName:
        return WeaponTypes.Rifle
    elif 'Hands' == weaponName:
        return WeaponTypes.Hands

#под типы пеших юнитов
class SoldierSubType(Enum):
    Men = 0
    Girl = 1
    Zombie = 2

# выбор под типы пеших юнитов по признаку
def selectSoldierSubType(subTypeName):
    if 'Men' == subTypeName:
        return SoldierSubType.Men
    elif 'Girl' == subTypeName:
        return SoldierSubType.Girl
    elif 'Zombie' == subTypeName:
        return SoldierSubType.Zombie

#типы юнитов
class UnitTypes(Enum):
    Mech = 0
    Soldier = 1

def selectUnitType(unitTypeName):
    if 'Mech' == unitTypeName:
        return UnitTypes.Mech
    elif 'Soldier' == unitTypeName:
        return UnitTypes.Soldier

#типы больших юнитов
class MechSubType(Enum):
    Mech = 0
    Monster = 1

#выбор под типы пеших юнитов по признаку
def selectMechSubType(subTypeName):
    if 'Mech' == subTypeName:
        return MechSubType.Mech
    elif 'Monster' == subTypeName:
        return MechSubType.Monster




# ID анимаций смены типы перещения
class SoldierChangePosture(Enum):
    StandToLay = 0
    StandToSit = 1
    SitToStand = 2
    SitToLay = 3
    LayToStand = 4
    LayToSit = 5

#число АР затрачиваемых на действие
class SoldierMoveAP(Enum):
    RunStraight = 4
    RunDiagonal = 6
    WalkStraight = 6
    WalkDiagonal = 9
    CrouchStraight = 8
    CrouchDiagonal = 12
    ProneStraight = 10
    ProneDiagonal = 15
    BarrelJumpStraight = 8

# Id групп анимаций
class SoldierStates(Enum):
    Move = 0
    Idle = 1
    ChangePosture = 2
    Attack = 3

class UnitSide(Enum):
    Player = 0
    Ally = 1
    Enemy = 2


# способ проигрывания анимации
ActionModes = {
    SoldierStates.Idle: bge.logic.KX_ACTIONACT_LOOPEND,
    SoldierStates.ChangePosture: bge.logic.KX_ACTIONACT_PLAY,
    SoldierStates.Attack: bge.logic.KX_ACTIONACT_PLAY,
    SoldierStates.Move: bge.logic.KX_ACTIONACT_LOOPEND,
}

SoldierMoveTypesByChangePostureDict = {
    SoldierChangePosture.LayToSit: SoldierMoveTypes.Crouch,
    SoldierChangePosture.LayToStand: None,
    SoldierChangePosture.SitToLay: SoldierMoveTypes.Prone,
    SoldierChangePosture.SitToStand: None,
    SoldierChangePosture.StandToLay: SoldierMoveTypes.Prone,
    SoldierChangePosture.StandToSit: SoldierMoveTypes.Crouch
}
# виды атаки
UnitAttackTypes = {'Shoot': 0, 'Melee': 1}
# текущее управление
# ControlType = {'Player' : 0, 'AI' : 1, 'None': 101}
# возможные состояния юнита
UnitStates = {'Idle': 0, 'Move': 1, 'Attack': 2}
#
UnitType = {'Soldier': 0, 'Mech': 1}

# комп или игрок
UnitControlType = {'Player': 0, 'AI': 1, 'None': 101}
# сторона
#UnitSide = {'Ally': 0, 'Enemy': 1}
# анимации

# AP на пермещение
SoldierChangePostureAP = {SoldierChangePosture.StandToSit: 4,
                          SoldierChangePosture.StandToLay: 8,
                          SoldierChangePosture.SitToStand: 4,
                          SoldierChangePosture.SitToLay: 4,
                          SoldierChangePosture.LayToStand: 8,
                          SoldierChangePosture.LayToSit: 4,
                          }



# число кадров в анимации
# анимации
ActionFramesCount = {'Men Rifle Run Idle': 101,
                    'Men Rifle Walk Idle': 101,
                    'Men Rifle Run': 17,
                    'Men Rifle Walk': 25,
                    'Men Rifle Crouch': 23,
                    'Men Rifle Crouch Idle': 302,
                    'Men Rifle Prone': 51,
                    'Men Rifle Prone Idle': 61,
                    'Men Rifle SitToStand': 26,
                    'Men Rifle LayToStand': 67,
                    'Men Rifle StandToSit': 18,
                    'Men Rifle StandToLay': 70,
                    'Men Rifle LayToSit': 40,
                    'Men Rifle SitToLay': 37,
                    'UE4fireStand': 15,
                    'UE4runJump': 21,
                    'UE4reviveBack': 108,
                    'UE4reviveFront': 108,


                    'Girl Rifle Run Idle': 351,
                    'Girl Rifle Walk Idle': 351,
                    'Girl Rifle Run': 17,
                    'Girl Rifle Walk': 25,
                    'Girl Rifle Crouch': 26,
                    'Girl Rifle Crouch Idle': 165,
                    'Girl Rifle Prone': 51,
                    'Girl Rifle Prone Idle': 61,
                    'Girl Rifle SitToStand': 17,
                    'Girl Rifle LayToStand': 67,
                    'Girl Rifle StandToSit': 23,
                    'Girl Rifle StandToLay': 70,
                    'Girl Rifle LayToSit': 40,
                    'Girl Rifle SitToLay': 37,

                    'Zombie Hands Run Idle': 91,
                    'Zombie Hands Walk Idle': 91,
                    'Zombie Hands Run': 26,
                    'Zombie Hands Walk': 51,

                    'Mech Hands Walk Idle': 125,
                    'Mech Hands Walk': 27
                     }


