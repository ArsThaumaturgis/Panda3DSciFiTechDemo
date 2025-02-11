from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionSphere, CollisionTube, CollisionNode
from panda3d.core import Vec4, Vec3, Vec2
from panda3d.core import WindowProperties
from panda3d.core import Shader
from panda3d.core import ClockObject
from panda3d.core import AmbientLight
from panda3d.core import CompassEffect
from panda3d.core import OmniBoundingVolume
from panda3d.core import AudioSound
from direct.showbase import Audio3DManager

from direct.gui.DirectGui import *

from Section2.GameObject import *
from Section2.Player import *
from Section2.Enemy import *
from Section2.SpaceLevel import SpaceLevel
from Section2.EndPortal import SphericalPortalSystem

import common
from common import KeyBindings

import random

section2Models = common.models["section2"]


class Section2():
    STATE_PLAYING = 0
    STATE_DEATH_CUTSCENE = 1
    STATE_GAME_OVER = 2

    def __init__(self, actionMusic, peaceMusic):
        common.currentSection = self

        cube_map_name = 'Assets/Section2/tex/main_skybox_#.png'
        self.skybox = common.create_skybox(cube_map_name)
        self.skybox.reparentTo(common.base.render)
        self.skybox.setEffect(CompassEffect.make(common.base.camera, CompassEffect.P_pos))
        self.skybox.node().setBounds(OmniBoundingVolume())
        self.skybox.node().setFinal(True)

        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False,
            "shootSecondary" : False
        }

        KeyBindings.setHandler("moveUp", lambda: self.updateKeyMap("up", True), "section2")
        KeyBindings.setHandler("moveUpDone", lambda: self.updateKeyMap("up", False), "section2")
        KeyBindings.setHandler("moveDown", lambda: self.updateKeyMap("down", True), "section2")
        KeyBindings.setHandler("moveDownDone", lambda: self.updateKeyMap("down", False), "section2")
        KeyBindings.setHandler("shoot", lambda: self.updateKeyMap("shoot", True), "section2")
        KeyBindings.setHandler("shootDone", lambda: self.updateKeyMap("shoot", False), "section2")
        KeyBindings.setHandler("shootSecondary", lambda: self.updateKeyMap("shootSecondary", True), "section2")
        KeyBindings.setHandler("shootSecondaryDone", lambda: self.updateKeyMap("shootSecondary", False), "section2")

        KeyBindings.setHandler("openPauseMenu", common.gameController.openPauseMenu, "section2")
        KeyBindings.setHandler("toggleThirdPerson", self.toggleThirdPerson, "section2")

        self.audio3D = Audio3DManager.Audio3DManager(common.base.sfxManagerList[0], common.base.render)
        self.audio3D.setDropOffFactor(0.04)

        self.pusher = CollisionHandlerPusher()
        self.traverser = CollisionTraverser()
        self.traverser.setRespectPrevTransform(True)

        self.pusher.add_in_pattern("%fn-into-%in")
        self.pusher.add_in_pattern("%fn-into")
        self.pusher.add_again_pattern("%fn-again-into")
        common.base.accept("projectile-into", self.projectileImpact)
        common.base.accept("projectile-again-into", self.projectileImpact)
        common.base.accept("player-into", self.gameObjectPhysicalImpact)
        common.base.accept("enemy-into", self.gameObjectPhysicalImpact)
        common.base.accept("playerTriggerDetector-into-trigger", self.triggerActivated)

        self.updateTask = common.base.taskMgr.add(self.update, "update")

        self.player = None
        self.currentLevel = None
        self.shipSpec = None

        self.playState = Section2.STATE_PLAYING

        self.paused = False

        self.peaceMusic = common.base.loader.loadMusic(peaceMusic)
        self.actionMusic = common.base.loader.loadMusic(actionMusic)

        self.peaceMusic.setLoop(True)
        self.actionMusic.setLoop(True)

        self.startedPeaceMusic = False

        self.peaceMusic.setVolume(0)
        self.actionMusic.setVolume(0)

        self.actionMusic.play()

        self.musicFadeSpeedToAction = 1.5
        self.musicFadeSpeedToPeace = 0.5

        # controller info text
        events = KeyBindings.events["section2"]
        cam_toggle_key = events["toggleThirdPerson"].key_str
        forward_key = events["moveUp"].key_str
        backward_key = events["moveDown"].key_str
        prim_weapon_key = events["shoot"].key_str
        sec_weapon_key = events["shootSecondary"].key_str
        events = KeyBindings.events["text"]
        help_toggle_key = events["toggle_help"].key_str
        controller_text = '\n'.join((
            f'Toggle Third-Person Mode: \1key\1{cam_toggle_key.title()}\2',
            f'\nForward: \1key\1{forward_key.title()}\2',
            f'Backward: \1key\1{backward_key.title()}\2',
            'Orientation: \1key\1Mouse Movement\2',
            f'\nFire Energy Weapon: \1key\1{prim_weapon_key.title()}\2 (hold)',
            f'Fire Missile: \1key\1{sec_weapon_key.title()}\2 (hold)',
            f'\nToggle This Help: \1key\1{help_toggle_key.title()}\2'
        ))
        common.TextManager.addText("context_help", controller_text)

    def windowUpdated(self, window):
        if self.player is not None:
            self.player.updateCameraLens()

    def toggleThirdPerson(self):
        self.player.toggleThirdPerson()

    def startGame(self, shipSpec):
        xSize = common.base.win.getXSize()
        ySize = common.base.win.getYSize()

        common.base.win.movePointer(0, xSize//2, ySize//2)

        self.cleanupLevel()

        self.shipSpec = shipSpec

        self.currentLevel = SpaceLevel()

        self.player = Player(shipSpec)
        self.player.root.setPos(self.currentLevel.playerSpawnPoint)
        self.player.forceCameraPosition()

        exit_sphere = self.currentLevel.geometry.find("**/=exit").find("**/+GeomNode")
        pos = exit_sphere.get_pos(self.currentLevel.geometry)
        exit_sphere.detach_node()
        lights = [self.currentLevel.lightNP, self.player.lightNP]
        self.portalSys = SphericalPortalSystem(self.currentLevel.geometry, lights, pos)

        shieldModel = section2Models["bigShield.egg"]
        shieldModel.setTransparency(True)
        shieldModel.setBin("unsorted", 0)
        shieldModel.reparentTo(self.currentLevel.geometry)
        shieldModel.setPos(pos)
        shieldModel.setHpr(-90, -40, 0)

        shader = Shader.load(Shader.SL_GLSL,
                             "Assets/Section2/shaders/bigShieldVertex.glsl",
                             "Assets/Section2/shaders/bigShieldFragment.glsl")
        shieldModel.setShader(shader)

        shieldModel.setShaderInput("player", self.player.root)

        self.playState = Section2.STATE_PLAYING

        self.activated()

    def resumeGame(self):
        self.activated()
        self.paused = False

        self.conditionallyPlayPeaceMusic()
        self.actionMusic.play()
        KeyBindings.activateAll("section2")
        KeyBindings.activateAll("text")

    def pauseGame(self):
        self.paused = True

        self.peaceMusic.stop()
        self.actionMusic.stop()
        KeyBindings.deactivateAll("section2")
        KeyBindings.deactivateAll("text")

    def conditionallyPlayPeaceMusic(self):
        if self.player.root.getY(common.base.render) > -840 or self.startedPeaceMusic:
            self.startedPeaceMusic = True
            if self.peaceMusic.status() != AudioSound.PLAYING:
                    self.peaceMusic.play()

    def activated(self):
        properties = WindowProperties()
        properties.setMouseMode(WindowProperties.M_confined)
        properties.setCursorHidden(True)
        #properties.setCursorFilename("Assets/Section2/tex/shipCursor.cur")
        common.base.win.requestProperties(properties)

    def updateKeyMap(self, controlName, controlState, callback = None):
        self.keyMap[controlName] = controlState

        if callback is not None:
            callback(controlName, controlState)

    def update(self, task):
        dt = globalClock.getDt()

        if self.paused:
            return Task.cont

        if self.currentLevel is not None:
            self.currentLevel.update(self.player, self.keyMap, dt)

            if self.player is not None and self.player.health <= 0:
                if self.playState == Section2.STATE_PLAYING:
                    self.playState = Section2.STATE_DEATH_CUTSCENE
                    self.deathTimer = 4.5
                elif self.playState == Section2.STATE_DEATH_CUTSCENE:
                    self.deathTimer -= dt
                    if self.deathTimer <= 0:
                        self.peaceMusic.stop()
                        self.actionMusic.stop()
                        self.playState = Section2.STATE_GAME_OVER
                        common.gameController.gameOver()
                        return Task.done
                return Task.cont

            if len(self.currentLevel.enemies) == 0:
                self.conditionallyPlayPeaceMusic()
                if self.startedPeaceMusic:
                    newVolume = self.peaceMusic.getVolume()
                    newVolume += dt*self.musicFadeSpeedToPeace
                    if newVolume > 1:
                        newVolume = 1
                    self.peaceMusic.setVolume(newVolume)

                newVolume = self.actionMusic.getVolume()
                newVolume -= dt*self.musicFadeSpeedToPeace
                if newVolume < 0:
                    newVolume = 0
                    if self.actionMusic.status() == AudioSound.PLAYING:
                        self.actionMusic.stop()
                self.actionMusic.setVolume(newVolume)
            else:
                newVolume = self.peaceMusic.getVolume()
                newVolume -= dt*self.musicFadeSpeedToAction
                if newVolume < 0:
                    newVolume = 0
                    if self.peaceMusic.status() == AudioSound.PLAYING:
                        self.peaceMusic.stop()
                self.peaceMusic.setVolume(newVolume)

                if self.actionMusic.status() != AudioSound.PLAYING:
                    self.actionMusic.play()
                newVolume = self.actionMusic.getVolume()
                newVolume += dt*self.musicFadeSpeedToAction
                if newVolume > 1:
                    newVolume = 1
                self.actionMusic.setVolume(newVolume)

            self.traverser.traverse(common.base.render)

            if self.player is not None and self.player.health > 0:
                self.player.postTraversalUpdate(dt)

        return Task.cont

    def projectileImpact(self, entry):
        fromNP = entry.getFromNodePath()
        proj = fromNP.getPythonTag(TAG_OWNER)

        intoNP = entry.getIntoNodePath()
        if intoNP.hasPythonTag(TAG_OWNER):
            intoObj = intoNP.getPythonTag(TAG_OWNER)
            proj.impact(intoObj)
        else:
            proj.impact(None)

    def gameObjectPhysicalImpact(self, entry):
        fromNP = entry.getFromNodePath()
        if fromNP.hasPythonTag(TAG_OWNER):
            fromNP.getPythonTag(TAG_OWNER).physicalImpact(entry.getSurfaceNormal(common.base.render))

    def triggerActivated(self, entry):
        intoNP = entry.getIntoNodePath()
        trigger = intoNP.getPythonTag(TAG_OWNER)

        if self.currentLevel is not None:
            self.currentLevel.triggerActivated(trigger)

    def exitTriggered(self):
        common.gameController.showEndCutscene()

    def cleanupLevel(self):
        if self.player is not None:
            self.player.destroy()
            self.player = None

        if self.currentLevel is not None:
            self.currentLevel.destroy()
            self.currentLevel = None

    def destroy(self):
        if self.peaceMusic is not None:
            self.peaceMusic.stop()
            self.peaceMusic = None
        if self.actionMusic is not None:
            self.actionMusic.stop()
            self.actionMusic = None

        if self.skybox is not None:
            self.skybox.removeNode()
            self.skybox = None

        common.TextManager.removeText()

        KeyBindings.deactivateAll("section2")

        common.base.ignore("projectile-into")
        common.base.ignore("projectile-again-into")
        common.base.ignore("player-into")
        common.base.ignore("enemy-into")

        self.cleanupLevel()
        self.portalSys.destroy()
        self.portalSys = None
        common.base.taskMgr.remove(self.updateTask)
        self.updateTask = None

        section2Models.clear()
        common.currentSection = None

def initialise(shipSpec):
    game = Section2("Assets/Section2/music/space_tech_break.ogg",
                    "Assets/Section2/music/space_tech_interlude_full.ogg")
    game.startGame(shipSpec)
    KeyBindings.activateAll("section2")
    KeyBindings.activateAll("text")
    return game

def addOptions():
    gameController = common.gameController

    gameController.addOptionCheck("Use Semi-Newtonian Flight", "useNewtonianFlight", "section2", True)

# define key map
KeyBindings.add("moveUp", "w", "section2")
KeyBindings.add("moveUpDone", "w-up", "section2")
KeyBindings.add("moveDown", "s", "section2")
KeyBindings.add("moveDownDone", "s-up", "section2")
KeyBindings.add("shoot", "mouse1", "section2")
KeyBindings.add("shootDone", "mouse1-up", "section2")
KeyBindings.add("shootSecondary", "mouse3", "section2")
KeyBindings.add("shootSecondaryDone", "mouse3-up", "section2")
KeyBindings.add("openPauseMenu", "escape", "section2")
KeyBindings.add("toggleThirdPerson", "tab", "section2")
