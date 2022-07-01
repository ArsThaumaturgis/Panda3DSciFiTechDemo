from panda3d.core import CollisionSphere, CollisionNode, CollisionRay, CollisionSegment, CollisionHandlerQueue, CollisionTraverser
from panda3d.core import BitMask32
from panda3d.core import Vec3, Vec2
from panda3d.core import OmniBoundingVolume
from panda3d.core import Shader
from panda3d.core import TextNode
from panda3d.core import PandaNode
from direct.actor.Actor import Actor

from direct.gui.OnscreenText import OnscreenText

from Section2.Weapon import Weapon, Projectile, SeekingProjectile, ProjectileWeapon
from Section2.Explosion import Explosion

from Section2.CommonValues import *
import common

import random, math

class BlasterProjectile(Projectile):
    SOUND_FILE_NAMES = (
        "Assets/Section2/sounds/playerBlasterImpact1.ogg",
        "Assets/Section2/sounds/playerBlasterImpact2.ogg",
        "Assets/Section2/sounds/playerBlasterImpact3.ogg"
    )
    def __init__(self, model, mask, range, damage, speed, size, knockback, flinchValue,
                 aoeRadius = 0, blastModel = None,
                 pos = None, damageByTime = False):
        Projectile.__init__(self,
                            model, mask, range, damage, speed, size, knockback, flinchValue,
                             aoeRadius, blastModel,
                             pos, damageByTime)

        self.explosionSound = common.currentSection.audio3D.loadSfx(random.choice(BlasterProjectile.SOUND_FILE_NAMES))

    def impact(self, impactee):
        shaderInputs = {
            "duration" : 0.3,
            "expansionFactor" : 1,
        }

        pos = self.root.getPos(common.base.render)

        explosion = Explosion(2 + self.damage*0.2, "blasterImpact", shaderInputs, "noiseRadial", random.uniform(0, 3.152), random.uniform(0, 3.152))
        explosion.activate(Vec3(0, 0, 0), pos)
        common.currentSection.currentLevel.explosions.append(explosion)

        Projectile.impact(self, impactee)

        self.explosionSound.set3dAttributes(pos.x, pos.y, pos.z, 0, 0, 0)
        self.explosionSound.play()

class BlasterWeapon(ProjectileWeapon):
    MODELS = [
        "blasterShot_small",
        "blasterShot_med",
        "blasterShot_large",
    ]
    DAMAGE_VALUES = [
        3.5,
        7,
        12
    ]
    SOUND_SPEEDS = [
        1.25,
        1.125,
        1
    ]
    def __init__(self, powerLevel):
        modelName = BlasterWeapon.MODELS[powerLevel]
        damage = BlasterWeapon.DAMAGE_VALUES[powerLevel]
        soundSpeed = BlasterWeapon.SOUND_SPEEDS[powerLevel]
        projectile = BlasterProjectile("{0}.egg".format(modelName),
                                        MASK_INTO_ENEMY,
                                        100, damage, 75, 0.25, 0, 10, 0,
                                        "blast.egg", soundSpeed)
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 0.2
        self.firingDelayPeriod = -1

        self.energyCost = 1

        self.soundSpeed = soundSpeed

    def fire(self, owner, dt):
        if owner.energy > self.energyCost:
            proj = ProjectileWeapon.fire(self, owner, dt)
            proj.explosionSound.setPlayRate(self.soundSpeed)
            owner.alterEnergy(-self.energyCost)
            owner.attackPerformed(self)

    def triggerPressed(self, owner):
        ProjectileWeapon.triggerPressed(self, owner)

        if self.firingTimer <= 0:
            self.fire(owner, 0)

    def triggerReleased(self, owner):
        ProjectileWeapon.triggerReleased(self, owner)

    def update(self, dt, owner):
        ProjectileWeapon.update(self, dt, owner)

    def destroy(self):
        ProjectileWeapon.destroy(self)

class Rocket(SeekingProjectile):
    def __init__(self, model, mask, range, damage, speed, size, knockback, flinchValue,
                 aoeRadius = 0, blastModel = None,
                 pos = None, damageByTime = False):
        SeekingProjectile.__init__(self, model, mask, range, damage, speed, size, knockback, flinchValue,
                 aoeRadius, blastModel,
                 pos, damageByTime)

        self.acceleration = 100

        self.timer = 5

        self.explosionSound = common.currentSection.audio3D.loadSfx("Assets/Section2/sounds/playerRocketHit.ogg")

    def update(self, dt):
        SeekingProjectile.update(self, dt)

        self.timer -= dt
        if self.timer <= 0:
            self.impact(None)

    def impact(self, impactee):
        shaderInputs = {
            "duration" : 0.55,
            "expansionFactor" : 7,
            "rotationRate" : 0.2,
            "fireballBittiness" : 0.3,
            "starDuration" : 0
        }

        randomVec1 = Vec2(random.uniform(0, 1), random.uniform(0, 1))
        randomVec2 = Vec2(random.uniform(0, 1), random.uniform(0, 1))

        pos = self.root.getPos(common.base.render)

        explosion = Explosion(7, "explosion", shaderInputs, "noise", randomVec1, randomVec2)
        explosion.activate(Vec3(0, 0, 0), pos)
        common.currentSection.currentLevel.explosions.append(explosion)

        SeekingProjectile.impact(self, impactee)

        self.explosionSound.set3dAttributes(pos.x, pos.y, pos.z, 0, 0, 0)
        self.explosionSound.play()

class RocketWeapon(ProjectileWeapon):
    def __init__(self):
        projectile = Rocket("rocket.egg",
                            MASK_INTO_ENEMY,
                            None, 55, 45, 0.7, 20, 0)
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 1
        self.firingDelayPeriod = -1

        self.ammoCost = 1

    def fire(self, owner, dt):
        if owner.numMissiles >= self.ammoCost:
            proj = ProjectileWeapon.fire(self, owner, dt)
            proj.owner = owner
            owner.alterMissileCount(-self.ammoCost)
            owner.attackPerformed(self)

    def triggerPressed(self, owner):
        ProjectileWeapon.triggerPressed(self, owner)

        if self.firingTimer <= 0:
            self.fire(owner, 0)