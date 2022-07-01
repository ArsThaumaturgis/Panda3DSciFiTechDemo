
from panda3d.core import Vec3

from ShipSpec import ShipSpec

shipSpecs = []

# Light fighter
shipSpec = ShipSpec()
shipSpec.gunPositions = [
    (Vec3(3.6, 1.2, 2.25), 2),
    (Vec3(3.6, 1.2, -2.25), 2),
    (Vec3(-3.6, 1.2, 2.25), 2),
    (Vec3(-3.6, 1.2, -2.25), 2),
]
shipSpec.missilePositions = [
    Vec3(0, -1.28, 2.753),
    Vec3(0, -1.28, -2.753),
    Vec3(2.753, -1.28, 0),
    Vec3(-2.753, -1.28, 0),
]
shipSpec.enginePositions = [
    (Vec3(0, -8.2, 0), 3.5),
    (Vec3(-1.65, -8.5, 1.493), 0.5),
    (Vec3(1.65, -8.5, 1.493), 0.5),
    (Vec3(-1.65, -8.5, -1.493), 0.5),
    (Vec3(1.65, -8.5, -1.493), 0.5)
]
shipSpec.maxEnergy = 200
shipSpec.shieldRechargeRate = 7
shipSpec.energyRechargeRate = 20
shipSpec.maxShields = 50
shipSpec.numMissiles = 8
shipSpec.maxSpeed = 25
shipSpec.turnRate = 200
shipSpec.acceleration = 60
shipSpec.cockpitModelFile = "playerShip_light_cockpit.egg"
shipSpec.cockpitEyePos = Vec3(0, 2.56, 0.75)
shipSpec.shipModelFileLowPoly = "playerShip_light.egg"
shipSpec.shipModelScalar = 0.75
shipSpec.shipModelRotation = 0
shipSpec.shipModelOffset = Vec3(0, 0, -4)
shipSpec.weaponSoundBlastersFileName = "Assets/Section2/sounds/playerAttackBlastersMany"
shipSpec.name = "Serpent"

shipSpecs.append(shipSpec)

# Medium fighter
shipSpec = ShipSpec()
shipSpec.gunPositions = [
    (Vec3(5.65, -2, 2.4), 1),
    (Vec3(-5.65, -2, 2.4), 1),
    (Vec3(0, -2.5, 4.475), 1)
]
shipSpec.missilePositions = [
    Vec3(3.45, -2.65, 3.4),
    Vec3(-3.45, -2.65, 3.4),
]
shipSpec.enginePositions = [
    (Vec3(0, -9.6, 1.25), 1.25),
    (Vec3(-2.8, -9.5, 1.14), 0.85),
    (Vec3(2.8, -9.5, 1.14), 0.85),
]
shipSpec.maxEnergy = 100
shipSpec.shieldRechargeRate = 10
shipSpec.energyRechargeRate = 15
shipSpec.maxShields = 100
shipSpec.numMissiles = 20
shipSpec.maxSpeed = 18
shipSpec.turnRate = 150
shipSpec.acceleration = 40
shipSpec.cockpitModelFile = "playerShip_med_cockpit.egg"
shipSpec.cockpitEyePos = Vec3(0, -3.5, 2.5)
shipSpec.shipModelFileLowPoly = "playerShip_med.egg"
shipSpec.shipModelScalar = 0.75
shipSpec.shipModelRotation = 0
shipSpec.shipModelOffset = Vec3(0, 0, -4)
shipSpec.weaponSoundBlastersFileName = "Assets/Section2/sounds/playerAttackBlastersSome"
shipSpec.name = "Wyvern"

shipSpecs.append(shipSpec)

# Heavy missile-platform
shipSpec = ShipSpec()
shipSpec.gunPositions = [
    (Vec3(1.19, 7.45, -2.33), 0),
    (Vec3(-1.19, 7.45, -2.33), 0),
]
shipSpec.missilePositions = [
    Vec3(3.94, 4.5, 4.45),
    Vec3(3.94, 4.5, 1.468),
    Vec3(3.94, 4.5, -1.514),
    Vec3(3.94, 4.5, -4.496),

    Vec3(6.64, 4.5, 2.95),
    Vec3(6.64, 4.5, -0.018),
    Vec3(6.64, 4.5, -2.986),

    Vec3(-3.94, 4.5, 4.45),
    Vec3(-3.94, 4.5, 1.468),
    Vec3(-3.94, 4.5, -1.514),
    Vec3(-3.94, 4.5, -4.496),

    Vec3(-6.64, 4.5, 2.95),
    Vec3(-6.64, 4.5, -0.018),
    Vec3(-6.64, 4.5, -2.986)

]
shipSpec.enginePositions = [
    (Vec3(0, -9.4, 2.96), 0.6),
    (Vec3(2.56, -9.4, 1.48), 0.6),
    (Vec3(2.56, -9.4, -1.48), 0.6),
    (Vec3(0, -9.4, -2.96), 0.6),
    (Vec3(-2.56, -9.4, 1.48), 0.6),
    (Vec3(-2.56, -9.4, -1.48), 0.6),
]
shipSpec.maxEnergy = 50
shipSpec.shieldRechargeRate = 20
shipSpec.energyRechargeRate = 7
shipSpec.maxShields = 200
shipSpec.numMissiles = 400
shipSpec.maxSpeed = 14
shipSpec.turnRate = 100
shipSpec.acceleration = 20
shipSpec.cockpitModelFile = "playerShip_heavy_cockpit.egg"
shipSpec.cockpitEyePos = Vec3(0, 4.2, 1.75)
shipSpec.shipModelFileLowPoly = "playerShip_heavy.egg"
shipSpec.shipModelScalar = 0.9
shipSpec.shipModelRotation = 0
shipSpec.shipModelOffset = Vec3(0, 0, -4)
shipSpec.weaponSoundBlastersFileName = "Assets/Section2/sounds/playerAttackBlastersOne"
shipSpec.name = "Manticore"

shipSpecs.append(shipSpec)
