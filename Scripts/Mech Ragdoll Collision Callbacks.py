import bge

def init(cont):
    own = cont.owner
    own = CollisionUpdate(own)

class CollisionUpdate(bge.types.KX_GameObject):
    def __init__(self, old_owner):
        self.addCollisionCallback()

    def on_collision_three(self, object, point, normal):

        return
        self.removeCollisionCallback()

    def addCollisionCallback(self):
        self.collisionCallbacks.append(self.on_collision_three)

    def removeCollisionCallback(self):
        self.collisionCallbacks.clear()


def restoreCollisionCallback(cont):
    return

