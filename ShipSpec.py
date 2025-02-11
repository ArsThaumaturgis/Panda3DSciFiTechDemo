
from panda3d.core import Vec3

class ShipSpec():
    def __init__(self):
        self.gunPositions = []
        self.missilePositions = []
        self.enginePositions = []
        self.numMissiles = 1
        self.maxEnergy = 10
        self.maxShields = 100
        self.energyRechargeRate = 1
        self.shieldRechargeRate = 1
        self.maxSpeed = 1
        self.turnRate = 1
        self.acceleration = 1
        self.cockpitModelFile = ""
        self.cockpitEyePos = Vec3(0, 0, 0)
        self.shipModelFileHighPoly = ""
        self.shipModelFileLowPoly = ""
        self.shipModelScalar = 1
        self.shipModelRotation = 0
        self.shipModelOffset = Vec3(0, 0, 0)
        self.weaponSoundBlastersFileName = ""
        self.name = ""