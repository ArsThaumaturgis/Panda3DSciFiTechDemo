
from panda3d.core import Vec4, Vec3, Vec2, Plane, Point3, BitMask32
from panda3d.core import CollisionSphere, CollisionNode, CollisionRay, CollisionSegment, CollisionHandlerQueue, CollisionTraverser

from Section2.GameObject import GameObject, ArmedObject, ShieldedObject, FRICTION
from Section2.Weapon import ProjectileWeapon, Projectile
from Section2.Explosion import Explosion
from Section2.CommonValues import *
import common

import random, math

class BasicEnemyBlaster(ProjectileWeapon):
    def __init__(self):
        projectile = Projectile("blasterShotEnemy.egg",
                                MASK_INTO_PLAYER,
                                100, 7, 60, 0.5, 0, 0,
                                0, "blast.egg")
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 0.5
        self.firingDelayPeriod = -1
        
        audio3D = common.currentSection.audio3D
        self.sounds = [
            audio3D.loadSfx("Assets/Section2/sounds/enemyShot1.ogg"),
            audio3D.loadSfx("Assets/Section2/sounds/enemyShot2.ogg"),
            audio3D.loadSfx("Assets/Section2/sounds/enemyShot3.ogg"),
        ]
        self.lastSound = None

    def fire(self, owner, dt):
        ProjectileWeapon.fire(self, owner, dt)
        sound = random.choice([snd for snd in self.sounds if snd is not self.lastSound])
        pos = owner.root.getPos(common.base.render)
        sound.set3dAttributes(pos.x, pos.y, pos.z, 0, 0, 0)
        sound.play()
        self.lastSound = sound

class Enemy(GameObject, ArmedObject, ShieldedObject):
    def __init__(self, pos, modelName, maxHealth, maxSpeed, colliderName, size):
        GameObject.__init__(self, pos, modelName, None, maxHealth, maxSpeed, colliderName,
                            MASK_INTO_ENEMY | MASK_FROM_PLAYER | MASK_FROM_ENEMY, size)
        ArmedObject.__init__(self)
        ShieldedObject.__init__(self, self.root, Vec4(0.2, 1, 0.3, 1))

        self.colliderNP.node().setFromCollideMask(MASK_WALLS | MASK_FROM_ENEMY)

        common.currentSection.pusher.addCollider(self.colliderNP, self.root)
        common.currentSection.traverser.addCollider(self.colliderNP, common.currentSection.pusher)

        colliderNode = CollisionNode("lock sphere")
        solid = CollisionSphere(0, 0, 0, size*2)
        solid.setTangible(False)
        colliderNode.addSolid(solid)
        self.lockColliderNP = self.root.attachNewNode(colliderNode)
        self.lockColliderNP.setPythonTag(TAG_OWNER, self)
        colliderNode.setFromCollideMask(0)
        colliderNode.setIntoCollideMask(MASK_ENEMY_LOCK_SPHERE)

        self.setFlinchPool(10, 15)

        self.attackAnimsPerWeapon = {}

        self.flinchAnims = []
        self.flinchTimer = 0

        self.hurtSound = []
        self.lastHurtSound = None

        self.movementNames = ["walk"]

        self.setupExplosion()

    def setupExplosion(self):
        self.explosion = None

    def setFlinchPool(self, minVal, maxVal):
        self.flinchPoolMin = minVal
        self.flinchPoolMax = maxVal

        self.resetFlinchCounter()

    def resetFlinchCounter(self):
        self.flinchCounter = random.uniform(self.flinchPoolMin, self.flinchPoolMax)

    def alterHealth(self, dHealth, incomingImpulse, knockback, flinchValue, overcharge = False):
        GameObject.alterHealth(self, dHealth, incomingImpulse, knockback, flinchValue, overcharge)
        ShieldedObject.alterHealth(self, dHealth, incomingImpulse, knockback, flinchValue, overcharge)

        self.flinchCounter -= flinchValue
        if self.flinchCounter <= 0:
            self.resetFlinchCounter()
            self.flinch()

        if dHealth < 0:
            sound = random.choice([snd for snd in self.hurtSound if snd is not self.lastHurtSound])
            sound.play()
            self.lastHurtSound = sound

    def flinch(self):
        if len(self.flinchAnims) > 0 and self.flinchTimer <= 0:
            anim = random.choice(self.flinchAnims)
            if self.inControl:
                self.velocity.set(0, 0, 0)
            self.inControl = False
            self.walking = False
            self.flinchTimer = 2

    def update(self, player, dt):
        GameObject.update(self, dt)
        ArmedObject.update(self, dt)
        ShieldedObject.update(self, dt)

        if self.flinchTimer > 0:
            self.flinchTimer -= dt

        if self.inControl and self.flinchTimer <= 0:
            self.runLogic(player, dt)

    def runLogic(self, player, dt):
        pass

    def attackPerformed(self, weapon):
        ArmedObject.attackPerformed(self, weapon)

    def onDeath(self):
        explosion = self.explosion
        self.explosion = None
        explosion.activate(self.velocity, self.root.getPos(common.base.render))
        common.currentSection.currentLevel.explosions.append(explosion)
        self.walking = False

    def destroy(self):
        self.lockColliderNP.clearPythonTag(TAG_OWNER)
        ArmedObject.destroy(self)
        GameObject.destroy(self)
        ShieldedObject.destroy(self)

class BasicEnemy(Enemy):
    STATE_ATTACK = 0
    STATE_BREAK_AWAY = 1
    STATE_FLEE = 2
    
    def __init__(self):
        Enemy.__init__(self, Vec3(0, 0, 0),
                       "enemyFighter.egg",
                              100,
                              20,
                              "enemy",
                              4)
        self.actor.setScale(0.5)
        
        self.acceleration = 100.0

        self.turnRate = 300.0

        self.yVector = Vec2(0, 1)

        self.steeringRayNPs = []

        self.steeringQueue = CollisionHandlerQueue()
        self.steeringTraverser = CollisionTraverser()

        self.steeringDistance = 80

        self.state = BasicEnemy.STATE_ATTACK
        self.breakAwayTimer = 0
        self.breakAwayMaxDuration = 5

        self.evasionDuration = 2
        self.evasionDurationVariability = 0.2
        self.evasionTimer = 0
        self.evasionDirection = (0, 0)

        steeringNode = CollisionNode("steering")

        sphere = CollisionSphere(0, 0, 0, self.steeringDistance)
        steeringNode.addSolid(sphere)

        steeringNode.setFromCollideMask(MASK_WALLS)
        steeringNode.setIntoCollideMask(0)

        steeringNodeNodePath = self.actor.attachNewNode(steeringNode)

        #steeringNodeNodePath.show()

        self.steeringRayNPs.append(steeringNodeNodePath)

        self.steeringTraverser.addCollider(steeringNodeNodePath, self.steeringQueue)
        
        audio3D = common.currentSection.audio3D
        self.hurtSound = [
                audio3D.loadSfx("Assets/Section2/sounds/enemyHit1.ogg"),
                audio3D.loadSfx("Assets/Section2/sounds/enemyHit2.ogg"),
                audio3D.loadSfx("Assets/Section2/sounds/enemyHit3.ogg"),
                audio3D.loadSfx("Assets/Section2/sounds/enemyHit4.ogg")
            ]
        for sound in self.hurtSound:
            sound.setVolume(3)
            audio3D.attachSoundToObject(sound, self.root)

        self.deathSound = audio3D.loadSfx("Assets/Section2/sounds/enemyDie.ogg")
        self.deathSound.setVolume(5)
        self.deathSoundIs3D = True

        weaponPoint = self.actor.find("**/weaponPoint")
        gun = BasicEnemyBlaster()
        self.addWeapon(gun, 0, weaponPoint)

        engineNPs = self.actor.findAllMatches("**/engineFlame*")
        self.engineData = []
        for np in engineNPs:
            scale = np.getScale().x
            np.setScale(1)
            pos = np.getPos()
            np.removeNode()

            flame = common.models["shared"]["shipEngineFlame.egg"].copy_to(self.actor)
            flame.setPos(pos)
            glow = flame.find("**/glow")
            glow.setScale(scale, 1, scale)
            common.make_engine_flame(flame, Vec3(1, 0.75, 0.2), Vec4(1, 0.4, 0.1, 1))

            self.engineData.append((flame, scale))

        landingGearNPs = self.actor.findAllMatches("**/landingGear*")
        for np in landingGearNPs:
            np.hide()

        #self.colliderNP.show()

    def setupExplosion(self):
        shaderInputs = {
            "duration" : 1.25,
            "expansionFactor" : 7,
            "rotationRate" : 0.2,
            "fireballBittiness" : 1.8,
            "starDuration" : 0.4
        }

        randomVec1 = Vec2(random.uniform(0, 1), random.uniform(0, 1))
        randomVec2 = Vec2(random.uniform(0, 1), random.uniform(0, 1))

        self.explosion = Explosion(25, "explosion", shaderInputs, "noise", randomVec1, randomVec2)

    def update(self, player, dt):
        Enemy.update(self, player, dt)
        diff = -self.actor.getQuat(render).getForward()
        #diff = fire.getRelativeVector(render, diff)
        for engineFlame, enginePower in self.engineData:
            fire = engineFlame.find("**/flame")
            common.update_engine_flame(fire, diff, enginePower)

    def runLogic(self, player, dt):
        Enemy.runLogic(self, player, dt)
        
        selfPos = self.root.getPos(common.base.render)
        playerPos = player.root.getPos()
        playerVel = player.velocity
        playerQuat = player.root.getQuat(common.base.render)
        playerForward = playerQuat.getForward()
        playerUp = playerQuat.getUp()
        playerRight = playerQuat.getRight()

        testWeapon = self.weaponSets[0][0]

        ### With thanks to a post on GameDev.net for this algorithm.
        ### Specifically, the post was by "alvaro", and at time of
        ### writing should be found here:
        ### https://www.gamedev.net/forums/topic/401165-target-prediction-system-target-leading/3662508/
        shotSpeed = testWeapon.projectileTemplate.maxSpeed

        vectorToPlayer = playerPos - selfPos

        quadraticA = shotSpeed*shotSpeed - playerVel.lengthSquared()
        if quadraticA <= 0:
            quadraticA = playerVel.lengthSquared()*1.25
        quadraticB = -2*playerVel.dot(vectorToPlayer)
        quadraticC = -vectorToPlayer.lengthSquared()

        innerSquare = quadraticB*quadraticB - 4*quadraticA*quadraticC

        if innerSquare < 0:
            targetPt = playerPos
        else:
            quadraticResult = (quadraticB + math.sqrt(innerSquare)) / (2*quadraticA)

            targetPt = playerPos + playerVel*quadraticResult

        ### End of GameDev.net algorithm

        vectorToTargetPt = targetPt - selfPos

        distanceToPlayer = vectorToTargetPt.length()

        quat = self.root.getQuat(common.base.render)
        forward = quat.getForward()
        up = quat.getUp()
        right = quat.getRight()

        angleToPlayer = forward.angleDeg(vectorToTargetPt.normalized())
        angleFromPlayer = playerForward.angleDeg(vectorToPlayer.normalized())

        fireWeapon = False
        if len(self.weaponSets) > 0:
            if distanceToPlayer < testWeapon.desiredRange:
                if angleToPlayer < 30:
                    fireWeapon = True

        if fireWeapon:
            self.startFiringSet(0)
        else:
            self.ceaseFiringSet(0)

        if self.inControl:
            self.walking = True

            turned = False

            if self.state == BasicEnemy.STATE_ATTACK:
                if distanceToPlayer < testWeapon.desiredRange*0.3:
                    self.state = BasicEnemy.STATE_BREAK_AWAY
                    self.breakAwayTimer = self.breakAwayMaxDuration
                else:
                    self.turnTowards(targetPt, 2, dt)
                    turned = True
            elif self.state == BasicEnemy.STATE_BREAK_AWAY:
                self.evasionTimer -= dt
                if self.evasionTimer <= 0:
                    self.evasionTimer = self.evasionDuration + random.uniform(-self.evasionDurationVariability, self.evasionDurationVariability)
                    self.evasionDirection = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.breakAwayTimer -= dt
                if angleFromPlayer > 150:
                    self.turnTowards(selfPos + playerRight*self.evasionDirection[0] + playerUp*self.evasionDirection[1], 2, dt)
                    turned = True
                elif angleToPlayer < 120:
                    self.turnTowards(selfPos - vectorToPlayer, 2, dt)
                    turned = True
                if distanceToPlayer > testWeapon.desiredRange*7 or self.breakAwayTimer <= 0:
                    self.state = BasicEnemy.STATE_ATTACK
            elif self.state == BasicEnemy.STATE_FLEE:
                pass

            self.steeringTraverser.traverse(common.base.render)

            if self.steeringQueue.getNumEntries() > 0:
                for hit in self.steeringQueue.getEntries():
                    np = hit.getIntoNodePath()
                    diff = hit.getSurfacePoint(common.base.render) - selfPos
                    dist = max(0.0001, diff.length())
                    r = diff.project(right)
                    u = diff.project(up)
                    offset = r + u
                    offset.normalize()
                    self.turnTowards(selfPos - offset, 15 * (1.0 - dist / self.steeringDistance) * max(0, (diff.normalized().dot(forward))), dt)
                    turned = True

            if not turned:
                self.turnTowards(self.root.getPos(common.base.render) + self.root.getQuat(common.base.render).getForward(), 0.1, dt)

            self.velocity += forward*self.acceleration*dt

    def destroy(self):
        Enemy.destroy(self)
        
        if self.explosion is not None:
            self.explosion.destroy()
            self.explosion = None

        for np in self.steeringRayNPs:
            common.currentSection.traverser.removeCollider(np)
            np.removeNode()
        self.steeringRayNPs = []
        self.steeringQueue = None
        Enemy.destroy(self)