from panda3d.core import (
    WindowProperties,
    TextNode,
    Vec4,
    Vec3,
    Vec2,
    VirtualFileSystem,
    Filename,
    Texture,
    PandaNode,
    NodePath,
    CardMaker,
    ModelPool,
    CullFaceAttrib,
    DirectionalLight,
    AntialiasAttrib
)
from direct.stdpy.file import *
from direct.gui.DirectGui import *

import Section2.Section2 as Section2

import common
from common import KeyBindings

from Ships import shipSpecs

from title_screen import TitleScreen

TAG_PREVIOUS_MENU = "predecessor"

OPTION_FILE_DIR = "."
OPTION_FILE_NAME = "options.dat"


def buildOptionsMenu(gameRef):
    gameRef.addOptionHeading("Gameplay")
    Section2.addOptions()
    gameRef.addOptionHeading("Technical")
    gameRef.addOptionSlider("Music Volume", (0, 100), 1, "musicVolume", "general", 40, gameRef.setMusicVolume)
    gameRef.addOptionSlider("Sound Volume", (0, 100), 1, "soundVolume", "general", 75, gameRef.setSoundVolume)
    gameRef.addOptionMenu("Resolution", gameRef.resolutionList, "resolution", "general", "1280 x 720", gameRef.setResolution)
    gameRef.addOptionCheck("Antialiasing (16x MSAA)\n(May have little or no effect with some systems)", "antialiasing", "general", True, gameRef.setAntialiasing)

class Game():
    BUTTON_SIZE_LARGE = 0
    BUTTON_SIZE_SMALL = 1
    BUTTON_SIZE_MED = 2

    @staticmethod
    def makeButton(text, command, menu, size, extraArgs = None, leftAligned = True, textScale = 1):
        if size == Game.BUTTON_SIZE_LARGE:
            width = 20
        elif size == Game.BUTTON_SIZE_SMALL:
            width = 10
        elif size == Game.BUTTON_SIZE_MED:
            width = 10
        height = 2.5

        if leftAligned:
            frame = (0, width, -height*0.5, height*0.5)
            alignment = TextNode.ALeft
            textPos = (0.9, -0.2)
            if size == Game.BUTTON_SIZE_LARGE:
                button = ""
            elif size == Game.BUTTON_SIZE_MED:
                button = "Med"
            else:
                button = "Small"
        else:
            frame = (-width*0.5 , width*0.5, -height*0.5, height*0.5)
            alignment = TextNode.ACenter
            textPos = (0, -0.2)
            if size == Game.BUTTON_SIZE_LARGE:
                button = "SmallCentred"
            elif size == Game.BUTTON_SIZE_MED:
                button = "MedCentred"
            else:
                button = "SmallCentred"

        btn = DirectButton(text = text,
                           command = command,
                           scale = 0.1,
                           parent = menu,
                           text_align = alignment,
                           text_font = common.fancyFont,
                           text_scale = textScale,
                           frameSize = frame,
                           frameColor = (1, 1, 1, 1),
                           pressEffect = False,
                           text_pos = textPos,
                           relief = DGG.FLAT,
                           frameTexture = (
                                        "Assets/Shared/tex/mainMenuBtn{0}Normal.png".format(button),
                                        "Assets/Shared/tex/mainMenuBtn{0}Click.png".format(button),
                                        "Assets/Shared/tex/mainMenuBtn{0}Highlight.png".format(button),
                                        "Assets/Shared/tex/mainMenuBtn{0}Normal.png".format(button),
                                      ),
                           rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                           clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonPressed.ogg")
                           )
        if common.italiciseFont:
            btn.setShear((0, 0.1, 0))
        btn.setTransparency(True)
        if extraArgs is not None:
            btn["extraArgs"] = extraArgs
        return btn

    def __init__(self):
        properties = WindowProperties()
        properties.setCursorFilename("Assets/Shared/tex/cursor.cur")
        common.base.win.requestProperties(properties)

        common.gameController = self

        common.fancyFont = common.base.loader.loadFont("Assets/Shared/fonts/cinema-gothic-nbp-font/CinemaGothicNbpItalic-1ew2.ttf",
                                                       pointSize = 8, lineHeight = 1, pixelsPerUnit = 150)

        common.base.win.setClearColor(Vec4(0, 0, 0, 1))

        common.base.render.set_shader(common.scene_shader)

        common.base.disableMouse()

        common.base.exitFunc = self.destroy

        common.base.accept("window-event", self.windowUpdated)

        self.currentMenu = None

        ### Main Menu

        self.mainMenuMusic = common.base.loader.loadMusic("Assets/Section2/music/space_tech_next_short.ogg")
        self.mainMenuMusic.setVolume(0.75)
        self.mainMenuMusic.setLoop(True)
        self.mainMenuMusic.setTime(11)

        self.mainMenuBackdrop = DirectFrame(
            frameSize=(-1/common.base.aspect2d.getSx(), 1/common.base.aspect2d.getSx(), -1, 1),
            frameColor = (0, 0, 0, 0)
        )
        self.mainMenuBackdrop.setTransparency(True)

        self.titleHolder = self.mainMenuBackdrop.attachNewNode(PandaNode("title holder"))
        self.titleHolder.setPos(0, 0, 0.6)

        self.underline = DirectLabel(frameTexture = "Assets/Shared/tex/underline.png",
                                     parent = self.titleHolder,
                                     relief = DGG.FLAT,
                                     frameSize = (-1.778, 2.122, -0.0609, 0.0609),
                                     frameColor = (1, 1, 1, 1),
                                     pos = (0, 0, 0),
                                     scale = -1)
        self.underline.setTransparency(True)

        self.title1 = DirectLabel(text = "CAPTAIN PANDA",
                                 parent = self.titleHolder,
                                 scale = 0.1,
                                 text_font = common.fancyFont,
                                 text_fg = (0.8, 0.9, 1, 1),
                                 relief = None,
                                 pos = (0, 0, 0.225),
                                 text_align = TextNode.ALeft)
        self.title2 = DirectLabel(text = "and the",
                                 parent = self.titleHolder,
                                 scale = 0.07,
                                 text_font = common.fancyFont,
                                 text_fg = (0.8, 0.9, 1, 1),
                                 relief = None,
                                 pos = (0, 0, 0.1675),
                                 text_align = TextNode.ALeft)
        self.title3 = DirectLabel(text = "INVASION OF THE MECHANOIDS!",
                                 parent = self.titleHolder,
                                 scale = 0.125,
                                 text_font = common.fancyFont,
                                 text_fg = (0.8, 0.9, 1, 1),
                                 relief = None,
                                 pos = (0, 0, 0.0625),
                                 text_align = TextNode.ALeft)

        if common.italiciseFont:
            self.title1.setShear((0, 0.1, 0))
            self.title2.setShear((0, 0.1, 0))
            self.title3.setShear((0, 0.1, 0))

        self.mainMenuPanel = DirectFrame(
                                    frameSize = (0, 1.25, -1, 1),
                                    frameColor = (0, 0, 0, 0)
                                   )

        buttons = []

        btn = Game.makeButton("New Game", self.startGame, self.mainMenuPanel, Game.BUTTON_SIZE_LARGE)
        buttons.append(btn)

        btn = Game.makeButton("Help", self.openHelp, self.mainMenuPanel, Game.BUTTON_SIZE_LARGE)
        buttons.append(btn)

        btn = Game.makeButton("Options", self.openOptions, self.mainMenuPanel, Game.BUTTON_SIZE_LARGE)
        buttons.append(btn)

        btn = Game.makeButton("Quit", self.quit, self.mainMenuPanel, Game.BUTTON_SIZE_LARGE)
        buttons.append(btn)

        buttonSpacing = 0.2125
        buttonY = (len(buttons) - 1)*0.5*buttonSpacing
        for btn in buttons:
            btn.setPos(0.1, 0, buttonY)
            buttonY -= buttonSpacing

        cubeMapFileBase = "Assets/Section2/tex/main_skybox_#.png"
        self.skyBox = common.create_skybox(cubeMapFileBase)
        self.skyBox.reparentTo(render)
        self.skyBox.setDepthTest(True)
        self.skyBox.setDepthWrite(True)
        self.skyBox.setR(90)
        self.skyBox.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        #self.skyBox.hide()

        ### A gradient for sub-menu backgrounds

        gradient = loader.loadTexture("Assets/Shared/tex/menuBackCentred.png")
        gradient.setWrapU(Texture.WMClamp)
        gradient.setWrapV(Texture.WMClamp)


        ### Help Menu

        self.helpMenu = DirectDialog(
                                        frameSize = (-1, 1, -0.85, 0.85),
                                        frameColor = (1, 1, 1, 0.75),
                                        frameTexture="Assets/Shared/tex/menuBackCentred.png",
                                        fadeScreen = 0.5,
                                        pos = (0, 0, 0),
                                        relief = DGG.FLAT
                                       )
        self.helpMenu.hide()

        label = DirectLabel(text = "Help",
                            parent = self.helpMenu,
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT,
                            scale = 0.1,
                            pos = (0, 0, 0.65)
                            )
        if common.italiciseFont:
            label.setShear((0, 0.1, 0))

        helpText = VirtualFileSystem.getGlobalPtr().readFile(Filename("help.txt"), False)
        helpText = helpText.decode("utf-8")
        newHelpText = helpText.replace("\r", "")
        label = DirectLabel(text = newHelpText,
                            parent = self.helpMenu,
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            text_wordwrap = 27,
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT,
                            scale = 0.06,
                            text_align = TextNode.ALeft,
                            pos = (-27*0.06*0.5, 0, 0.45)
                            )
        if common.italiciseFont:
            label.setShear((0, 0.1, 0))

        btn = Game.makeButton("Back", self.closeCurrentMenu, self.helpMenu, Game.BUTTON_SIZE_SMALL, leftAligned = False)
        btn.setPos(0, 0, -0.7)


        ### Options Menu

        self.resolutionList = []
        tempList = []
        displayInformation = common.base.pipe.getDisplayInformation()
        for index in range(displayInformation.getTotalDisplayModes()):
            w = displayInformation.getDisplayModeWidth(index)
            h = displayInformation.getDisplayModeHeight(index)
            tempList.append((w, h))
        for res in tempList:
            if res not in self.resolutionList:
                self.resolutionList.append(res)
        self.resolutionList.sort(key = lambda x: x[0] * 10000 + x[1], reverse = True)
        self.resolutionList = ["{0} x {1}".format(w, h) for (w, h) in self.resolutionList]

        self.optionsTop = 0.35
        self.currentOptionsZ = self.optionsTop
        self.optionSpacingHeading = 0.2
        self.optionCheckSpacing = 0.25
        self.optionSliderSpacing = 0.25
        self.optionMenuSpacing = 0.7

        self.optionsMenu = DirectDialog(
                                        frameSize = (-1, 1, -0.85, 0.85),
                                        frameColor = (1, 1, 1, 0.75),
                                        frameTexture="Assets/Shared/tex/menuBackCentred.png",
                                        fadeScreen = 0.5,
                                        pos = (0, 0, 0),
                                        relief = DGG.FLAT
                                       )
        self.optionsMenu.hide()

        label = DirectLabel(text = "Options",
                            parent = self.optionsMenu,
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT,
                            scale = 0.1,
                            pos = (0, 0, 0.65)
                            )
        if common.italiciseFont:
            label.setShear((0, 0.1, 0))

        self.optionsScroller = DirectScrolledFrame(
                                        parent = self.optionsMenu,
                                        relief = DGG.SUNKEN,
                                        scrollBarWidth = 0.1,
                                        frameSize = (-0.85, 0.95, -0.5, 0.5),
                                        frameColor = (0.225, 0.325, 0.5, 0.75),
                                        canvasSize = (-0.8, 0.8, -0.4, 0.5),
                                        frameTexture = gradient,
                                        autoHideScrollBars = False,
                                        verticalScroll_frameColor = (0.225*0.05, 0.325*0.1, 0.5*0.3, 0.75),
                                        verticalScroll_incButton_frameTexture = "Assets/Shared/tex/mainMenuScrollerDown.png",
                                        verticalScroll_incButton_pressEffect = False,
                                        verticalScroll_incButton_relief = DGG.FLAT,
                                        verticalScroll_incButton_frameColor = (1, 1, 1, 1),
                                        verticalScroll_decButton_frameTexture = "Assets/Shared/tex/mainMenuScrollerUp.png",
                                        verticalScroll_decButton_pressEffect = False,
                                        verticalScroll_decButton_relief = DGG.FLAT,
                                        verticalScroll_decButton_frameColor = (1, 1, 1, 1),
                                        verticalScroll_thumb_frameTexture = "Assets/Shared/tex/mainMenuScrollerThumb.png",
                                        verticalScroll_thumb_pressEffect = False,
                                        verticalScroll_thumb_relief = DGG.FLAT,
                                        verticalScroll_thumb_frameColor = (1, 1, 1, 1),
                                        verticalScroll_incButton_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                        verticalScroll_incButton_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg"),
                                        verticalScroll_decButton_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                        verticalScroll_decButton_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg"),
                                        verticalScroll_thumb_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                        verticalScroll_thumb_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg")
                                    )
        self.optionsScroller.verticalScroll.setTransparency(True)
        self.optionsScroller.horizontalScroll.hide()

        buildOptionsMenu(self)

        self.readOptions()

        btn = Game.makeButton("Back", self.closeOptionsMenu, self.optionsMenu, Game.BUTTON_SIZE_SMALL, leftAligned = False)
        btn.setPos(0, 0, -0.7)

        ### Game-over menu

        self.gameOverScreen = DirectDialog(frameSize = (-0.5, 0.5, -0.7, 0.7),
                                           frameColor = (0.225, 0.325, 0.5, 0.75),
                                           fadeScreen = 0.4,
                                           relief = DGG.FLAT,
                                           frameTexture = gradient)
        self.gameOverScreen.hide()

        label = DirectLabel(text = "Game Over!",
                            parent = self.gameOverScreen,
                            scale = 0.1,
                            pos = (0, 0, 0.55),
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT)

        btn = Game.makeButton("Retry", self.restartCurrentSection, self.gameOverScreen, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, 0.25)
        btn.setTransparency(True)

        btn = Game.makeButton("Return to Menu", self.openMenu, self.gameOverScreen, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, 0)
        btn.setTransparency(True)

        btn = Game.makeButton("Quit", self.quit, self.gameOverScreen, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, -0.25)
        btn.setTransparency(True)

        ### Pause menu

        self.pauseMenu = DirectDialog(frameSize = (-0.5, 0.5, -0.7, 0.7),
                                      frameColor = (1, 1, 1, 0.75),
                                      frameTexture="Assets/Shared/tex/menuBackCentred.png",
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT)
        self.pauseMenu.hide()

        label = DirectLabel(text = "Paused...",
                            parent = self.pauseMenu,
                            scale = 0.1,
                            pos = (0, 0, 0.55),
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT)

        btn = Game.makeButton("Resume", self.returnToGame, self.pauseMenu, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, 0.25)
        btn.setTransparency(True)

        btn = Game.makeButton("Return to Menu", self.openMenu, self.pauseMenu, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, 0)
        btn.setTransparency(True)

        btn = Game.makeButton("Quit", self.quit, self.pauseMenu, Game.BUTTON_SIZE_MED, leftAligned = False)
        btn.setPos(0, 0, -0.25)
        btn.setTransparency(True)

        ### Section 2 ship-selection menu

        buttons = []

        self.shipSelectionMenu = DirectDialog(
                                              frameSize = (-1.5, 1.5, -0.85, 0.85),
                                              fadeScreen = 0.5,
                                              frameColor = (1, 1, 1, 0.75),
                                              frameTexture="Assets/Shared/tex/mainMenuBack.png",
                                              relief = DGG.FLAT,
                                             )
        self.shipSelectionMenu.hide()

        frame = DirectFrame(frameSize = (-0.575, 0.575, -0.7, 0.7),
                            relief = DGG.FLAT,
                            frameTexture = gradient,
                            frameColor = (0.056, 0.081, 0.125, 0.75),
                            parent = self.shipSelectionMenu,
                            pos = (0.8, 0, 0))

        self.shipTurntable = NodePath(PandaNode("turnTable"))
        self.shipTurntable.reparentTo(frame)
        self.shipTurntable.setTwoSided(False, 0)
        self.shipTurntable.setDepthTest(True)
        self.shipTurntable.setDepthWrite(True)
        self.shipTurntable.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        self.shipTurntable.setPos(0, 0, 0.2)
        self.shipTurntable.setP(30)
        self.shipTurntable.setShader(common.metal_shader)

        light = DirectionalLight("directional light")
        light.setColor(Vec4(1, 1, 1, 1))
        self.lightNP = frame.attachNewNode(light)
        self.lightNP.setScale(render, 1)
        self.lightNP.setHpr(render, 0, -25, 0)
        self.shipTurntable.setLight(self.lightNP)

        light2 = DirectionalLight("directional light")
        light2.setColor(Vec4(0.45, 0.5, 0.6, 1))
        self.light2NP = frame.attachNewNode(light2)
        self.light2NP.setScale(render, 1)
        self.light2NP.setHpr(render, 90, -45, 0)
        self.shipTurntable.setLight(self.light2NP)

        light3 = DirectionalLight("directional light")
        light3.setColor(Vec4(0.45, 0.5, 0.6, 1))
        self.light3NP = frame.attachNewNode(light3)
        self.light3NP.setScale(render, 1)
        self.light3NP.setHpr(render, -45, -45, 0)
        self.shipTurntable.setLight(self.light3NP)

        self.shipNameLabel = DirectLabel(text = " ",
                                         parent = frame,
                                         scale = 0.075,
                                         text_font = common.fancyFont,
                                         text_fg = (0.8, 0.9, 1, 1),
                                         relief = None,
                                         pos = (-0.525, 0, 0.6),
                                         text_align = TextNode.ALeft)

        self.shipSpeedLabel = DirectLabel(text = " ",
                                         parent = frame,
                                         scale = 0.075,
                                         text_font = common.fancyFont,
                                         text_fg = (0.8, 0.9, 1, 1),
                                         relief = None,
                                         pos = (-0.525, 0, -0.3),
                                         text_align = TextNode.ALeft)
        self.shipBlasterLabel = DirectLabel(text = " ",
                                         parent = frame,
                                         scale = 0.075,
                                         text_font = common.fancyFont,
                                         text_fg = (0.8, 0.9, 1, 1),
                                         relief = None,
                                         pos = (-0.525, 0, -0.4),
                                         text_align = TextNode.ALeft)
        self.shipMissileLabel = DirectLabel(text = " ",
                                         parent = frame,
                                         scale = 0.075,
                                         text_font = common.fancyFont,
                                         text_fg = (0.8, 0.9, 1, 1),
                                         relief = None,
                                         pos = (-0.525, 0, -0.5),
                                         text_align = TextNode.ALeft)
        self.shipShieldLabel = DirectLabel(text = " ",
                                         parent = frame,
                                         scale = 0.075,
                                         text_font = common.fancyFont,
                                         text_fg = (0.8, 0.9, 1, 1),
                                         relief = None,
                                         pos = (-0.525, 0, -0.6),
                                         text_align = TextNode.ALeft)

        self.updateShipView(None)

        label = DirectLabel(text = "Select a Ship:",
                            parent = self.shipSelectionMenu,
                            scale = 0.1,
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.9, 0.3),
                            relief = DGG.FLAT,
                            pos = (-1.5 + 0.1925, 0, 0.65),
                            text_align = TextNode.ALeft)
        if common.italiciseFont:
            label.setShear((0, 0.1, 0))

        btn = Game.makeButton("Light fighter", self.sectionSpecificMenuDone, self.shipSelectionMenu, Game.BUTTON_SIZE_LARGE,
                              textScale = 0.9,
                              extraArgs = [self.shipSelectionMenu, 0, shipSpecs[0]])
        btn.bind(DGG.ENTER, self.updateShipView, extraArgs = [shipSpecs[0]])
        buttons.append(btn)

        btn = Game.makeButton("Medium Interceptor", self.sectionSpecificMenuDone, self.shipSelectionMenu, Game.BUTTON_SIZE_LARGE,
                              textScale = 0.9,
                              extraArgs = [self.shipSelectionMenu, 0, shipSpecs[1]])
        btn.bind(DGG.ENTER, self.updateShipView, extraArgs = [shipSpecs[1]])
        buttons.append(btn)

        btn = Game.makeButton("Heavy Bombardment Platform", self.sectionSpecificMenuDone, self.shipSelectionMenu, Game.BUTTON_SIZE_LARGE,
                              textScale = 0.9,
                              extraArgs = [self.shipSelectionMenu, 0, shipSpecs[2]])
        btn.bind(DGG.ENTER, self.updateShipView, extraArgs = [shipSpecs[2]])
        buttons.append(btn)

        buttonY = (len(buttons) - 1)*0.5*buttonSpacing
        for btn in buttons:
            btn.setPos(-1.5 + 0.1, 0, buttonY)
            buttonY -= buttonSpacing

        btn = Game.makeButton("Back", self.closeCurrentMenu, self.shipSelectionMenu, Game.BUTTON_SIZE_SMALL)
        btn.setPos(-1.5 + 0.1, 0, -0.7)

        self.updateTask = common.base.taskMgr.add(self.updateMenuAnimation, "update menu animation")

        ### Loading screen

        self.loading_screen = None
        model = common.base.loader.loadModel("Assets/Section2/models/enemyFighter")
        model.setDepthTest(True)
        model.setDepthWrite(True)
        model.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
        model.setShader(common.metal_shader)
        model.setScale(0.075)
        self.loadingModel = model

        ### End-of-game "cutscene"

        cm = CardMaker("end cutscene")
        cm.set_frame_fullscreen_quad()
        self.endCutscene = common.base.render2d.attach_new_node(cm.generate())
        tex = common.base.loader.load_texture("Assets/Shared/tex/cutscene_screen.png")
        self.endCutscene.set_texture(tex)
        self.endCutscene.hide()

        text = TextNode("heading")
        text.setText("Conclusion")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)

        textNP = self.endCutscene.attachNewNode(text)
        textNP.setPos(0, 0, 0.85)
        textNP.setPythonTag("scale", 0.1)

        text = TextNode("cutscene text")
        text.setText("You boost through the portal, one space slipping behind as a new space envelops you. At last you are free of the harrying of the the Mechanoid rocket-ships.\n\nIn the dark ahead drifts a space station: once a hub of activity, now devastated by the Mechanoid attack.\n\nThe journey there is almost done. Can you best the Mechanoid forces within...?")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)
        text.setWordwrap(30)

        textNP = self.endCutscene.attachNewNode(text)
        textNP.setPos(0, 0, 0.5)
        textNP.setPythonTag("scale", 0.075)

        text = TextNode("prompt")
        text.setText("Press \"Escape\" to return to the menu...")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)

        textNP = self.endCutscene.attachNewNode(text)
        textNP.setPos(0, 0, -0.9125)
        textNP.setPythonTag("scale", 0.05)

        ### Section-data

        self.currentSectionIndex = 0
        self.currentSectionData = None
        self.currentSectionObject = None

        # Stores section-modules and the menu, if any, that's to be
        # shown if they're loaded without the preceding section
        # being run
        self.sections = [
            (Section2, self.shipSelectionMenu),
        ]

        ### Utility

        common.base.accept("f", self.toggleFrameRateMeter)
        self.showFrameRateMeter = False

    def updateMenuAnimation(self, task):

        self.shipTurntable.setH(self.shipTurntable, 20 * common.base.clock.getDt())

        self.skyBox.setP(self.skyBox, 2 * common.base.clock.getDt())

        return task.cont

    def updateShipView(self, ship, pos = None):
        for child in self.shipTurntable.getChildren():
            child.removeNode()

        if ship is not None:
            model = common.models["shared"][ship.shipModelFileLowPoly].copyTo(self.shipTurntable)
            model.setScale(0.05 * ship.shipModelScalar)

        self.shipTurntable.setHpr(180, -30, 0)

        textString = "Ship: "
        if ship is not None:
            textString += ship.name
        else:
            textString += "-"
        self.shipNameLabel["text"] = textString
        self.shipNameLabel.setText()
        self.shipNameLabel.resetFrameSize()

        textString = "Speed: "
        if ship is not None:
            textString += str(ship.maxSpeed * 2)
        else:
            textString += "-"
        self.shipSpeedLabel["text"] = textString
        self.shipSpeedLabel.setText()
        self.shipSpeedLabel.resetFrameSize()

        gunDescriptors = ["Light", "Medium", "Heavy"]
        textString = "Blasters: "
        if ship is not None:
            textString += str(len(ship.gunPositions)) + ", " + gunDescriptors[ship.gunPositions[0][1]]
        else:
            textString += "-"
        self.shipBlasterLabel["text"] = textString
        self.shipBlasterLabel.setText()
        self.shipBlasterLabel.resetFrameSize()

        textString = "Missile Loadout: "
        if ship is not None:
            textString += str(ship.numMissiles)
        else:
            textString += "-"
        self.shipMissileLabel["text"] = textString
        self.shipMissileLabel.setText()
        self.shipMissileLabel.resetFrameSize()

        textString = "Shield Strength: "
        if ship is not None:
            textString += str(ship.maxShields)
        else:
            textString += "-"
        self.shipShieldLabel["text"] = textString
        self.shipShieldLabel.setText()
        self.shipShieldLabel.resetFrameSize()

    def readOptions(self):
        try:
            fileObj = open(Filename("{0}/{1}".format(OPTION_FILE_DIR, OPTION_FILE_NAME)).toOsSpecific(), "r")
            for line in fileObj:
                sectionID, optionID, optionValueStr = line.split("|")
                sectionID = sectionID.strip()
                optionID = optionID.strip()
                optionValueStr = optionValueStr.strip()
                optionValue = self.parseOptionVal(optionValueStr)
                common.options[sectionID][optionID] = optionValue
                setter = common.optionWidgets[sectionID][optionID][0]
                setter(optionID, sectionID, optionValue)
                #self.setOptionValue(optionValue, optionID, sectionID)
            fileObj.close()
        except FileNotFoundError as e:
            pass

    def updateSlider(self, optionID, sectionID, value):
        slider = common.optionWidgets[sectionID][optionID][1]
        slider["value"] = value

    def updateCheck(self, optionID, sectionID, value):
        check = common.optionWidgets[sectionID][optionID][1]
        check["indicatorValue"] = value
        check.setIndicatorValue()

    def updateMenu(self, optionID, sectionID, value):
        menu = common.optionWidgets[sectionID][optionID][1]
        for index, btn in enumerate(menu.getPythonTag("items")):
            if btn["text"] == value:
                btn.commandFunc(None)
                #menu.selectListItem(btn)
                #menu.scrollTo(index)
        #menu.selectListItem(value)

    def parseOptionVal(self, valueStr):
        result = 0
        if "," in valueStr:
            valueList = valueStr.split(",")
            valueList = [self.parseOptionVal(subStr) for subStr in valueList]
            if len(valueList) == 4:
                result = Vec4(*valueList)
            elif len(valueList) == 3:
                result = Vec3(*valueList)
            elif len(valueList) == 2:
                result = Vec2(*valueList)
            else:
                result = None
        elif valueStr.lower() == "true":
            result = True
        elif valueStr.lower() == "false":
            result = False
        else:
            try:
                result = int(valueStr)
            except ValueError:
                try:
                    result = float(valueStr)
                except ValueError:
                    result = valueStr

        return result

    def getOptionValueString(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, Vec4):
            return "{0}, {1}, {2}, {3}".format(value.x, value.y, value.z, value.w)
        if isinstance(value, Vec3):
            return "{0}, {1}, {2}".format(value.x, value.y, value.z)
        if isinstance(value, Vec2):
            return "{0}, {1}".format(value.x, value.y)
        return str(value)

    def writeOptions(self):
        fileObj = open(Filename("{0}/{1}".format(OPTION_FILE_DIR, OPTION_FILE_NAME)).toOsSpecific(), "w")
        for sectionKey, section in common.options.items():
            for optionKey, option in section.items():
                fileObj.write("{0} | {1} | {2}\n".format(sectionKey, optionKey, self.getOptionValueString(option)))
        fileObj.close()

    def setOptionData(self, optionID, sectionID, defaultValue, setCallback = None):
        if not sectionID in common.optionCallbacks:
            common.optionCallbacks[sectionID] = {}
        common.optionCallbacks[sectionID][optionID] = setCallback

        if not sectionID in common.options:
            common.options[sectionID] = {}
        common.options[sectionID][optionID] = defaultValue

    def setOptionWidgets(self, optionID, sectionID, widgetList):
        if not sectionID in common.optionWidgets:
            common.optionWidgets[sectionID] = {}
        common.optionWidgets[sectionID][optionID] = widgetList

    def setOptionValue(self, value, optionID, sectionID):
        common.options[sectionID][optionID] = value

        setCallback = common.optionCallbacks[sectionID][optionID]
        if setCallback is not None:
            setCallback(value)

    def setOptionValueFromSlider(self, args):
        optionID, sectionID, slider = args
        val = slider.getValue()

        self.setOptionValue(val, optionID, sectionID)

    def setOptionValueFromMenu(self, val, optionID, sectionID, menu):
        self.setOptionValue(val, optionID, sectionID)

        markerLeft, markerRight = menu.getPythonTag("markers")

        for index, btn in enumerate(menu.getPythonTag("items")):
            if btn["text"] == val:
                markerLeft.show()
                markerLeft.setZ(btn.getZ())
                markerRight.show()
                markerRight.setZ(btn.getZ())

    def addOptionSlider(self, text, rangeTuple, pageSize, optionID, sectionID, defaultValue, setCallback = None):
        self.setOptionData(optionID, sectionID, defaultValue, setCallback)

        self.currentOptionsZ -= 0.0775

        slider = DirectSlider(text = text,
                              parent = self.optionsScroller.getCanvas(),
                              scale = 0.65,
                              text_pos = (0, 0.125),
                              text_scale = 0.1,
                              text_font = common.fancyFont,
                              text_fg = (0.8, 0.9, 1, 1),
                              pos = (0, 0, self.currentOptionsZ),
                              command = self.setOptionValueFromSlider,
                              thumb_image = (
                                  "Assets/Shared/tex/mainMenuSliderThumbNormal.png",
                                  "Assets/Shared/tex/mainMenuSliderThumbClick.png",
                                  "Assets/Shared/tex/mainMenuSliderThumbHighlight.png",
                                  "Assets/Shared/tex/mainMenuSliderThumbNormal.png"
                              ),
                              thumb_image_scale = 0.1125,
                              thumb_frameSize = (-0.06, 0.06, -0.09, 0.09),
                              thumb_frameColor = (1, 1, 1, 1),
                              thumb_relief = None,
                              thumb_pressEffect = False,
                              thumb_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                              thumb_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg"),
                              value = defaultValue,
                              range = rangeTuple,
                              frameColor = (0.05, 0.05, 0.125, 1),
                              pageSize = pageSize,
                              orientation = DGG.HORIZONTAL)
        slider["extraArgs"] = [optionID, sectionID, slider],
        slider.setTransparency(True)
        label1 = DirectLabel(text = str(rangeTuple[0]),
                             scale = 0.06,
                             text_font = common.fancyFont,
                             text_fg = (0.8, 0.9, 1, 1),
                             frameTexture = "Assets/Shared/tex/mainMenuSliderCapLeft.png",
                             frameSize = (-1.15, 0.85, -1, 1),
                             pos = (-0.7, 0, self.currentOptionsZ),
                             text_pos = (0, 0.8),
                             parent = self.optionsScroller.getCanvas())
        label1.setTransparency(True)
        label2 = DirectLabel(text = str(rangeTuple[1]),
                             scale = 0.06,
                             text_font = common.fancyFont,
                             text_fg = (0.8, 0.9, 1, 1),
                             frameTexture = "Assets/Shared/tex/mainMenuSliderCapRight.png",
                             frameSize = (-0.85, 1.15, -1, 1),
                             pos = (0.7, 0, self.currentOptionsZ),
                             text_pos = (0, 0.8),
                             parent = self.optionsScroller.getCanvas())
        label2.setTransparency(True)
        self.setOptionWidgets(optionID, sectionID, [self.updateSlider, slider, label1, label2])

        self.currentOptionsZ -= self.optionSliderSpacing
        self.updateOptionsCanvasSize()

    def addOptionCheck(self, text, optionID, sectionID, defaultValue, setCallback = None):
        self.setOptionData(optionID, sectionID, defaultValue, setCallback)

        check = DirectCheckButton(text = text,
                                  scale = 0.075,
                                  text_align = TextNode.ACenter,
                                  parent = self.optionsScroller.getCanvas(),
                                  pos = (0, 0, self.currentOptionsZ),
                                  command = self.setOptionValue,
                                  text_font = common.fancyFont,
                                  text_fg = (0.8, 0.9, 1, 1),
                                  boxPlacement = "below",
                                  boxRelief = None,
                                  boxImageScale = (4, 1, 1),
                                  pressEffect = False,
                                  boxImage = ("Assets/Shared/tex/mainMenuCheckEmpty.png", "Assets/Shared/tex/mainMenuCheckFull.png", None),
                                  relief = None,
                                  extraArgs = [optionID, sectionID],
                                  indicatorValue = defaultValue,
                                  rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                  clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonPressed.ogg"))
        check.indicator.setTransparency(True)

        self.setOptionWidgets(optionID, sectionID, [self.updateCheck, check])

        self.currentOptionsZ -= self.optionCheckSpacing
        self.updateOptionsCanvasSize()

    def addOptionRadioSet(self, text, buttonLabels, optionID, sectionID, defaultValue, setCallback = None):
        self.setOptionData(optionID, sectionID, defaultValue, setCallback)

    def addOptionMenu(self, text, menuItems, optionID, sectionID, defaultValue, setCallback = None):
        self.setOptionData(optionID, sectionID, defaultValue, setCallback)

        label = DirectLabel(parent = self.optionsScroller.getCanvas(),
                            text = text,
                            scale = 0.075,
                            relief = None,
                            pos = (0, 0, self.currentOptionsZ),
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),)
        menu = DirectScrolledFrame(parent = self.optionsScroller.getCanvas(),
                                   pos = (0, 0, self.currentOptionsZ - 0.125),
                                   frameSize = (-0.5, 0.58, -0.4, 0.075),
                                   autoHideScrollBars = False,
                                   relief = DGG.SUNKEN,
                                   frameColor = (0.225*0.05, 0.325*0.1, 0.5*0.3, 0.75),
                                   verticalScroll_frameColor = (0.225*0.05, 0.325*0.1, 0.5*0.3, 0.75),
                                   verticalScroll_incButton_frameTexture = "Assets/Shared/tex/mainMenuScrollerDown.png",
                                   verticalScroll_incButton_pressEffect = False,
                                   verticalScroll_incButton_relief = DGG.FLAT,
                                   verticalScroll_incButton_frameColor = (1, 1, 1, 1),
                                   verticalScroll_decButton_frameTexture = "Assets/Shared/tex/mainMenuScrollerUp.png",
                                   verticalScroll_decButton_pressEffect = False,
                                   verticalScroll_decButton_relief = DGG.FLAT,
                                   verticalScroll_decButton_frameColor = (1, 1, 1, 1),
                                   verticalScroll_thumb_frameTexture = "Assets/Shared/tex/mainMenuScrollerThumb.png",
                                   verticalScroll_thumb_pressEffect = False,
                                   verticalScroll_thumb_relief = DGG.FLAT,
                                   verticalScroll_thumb_frameColor = (1, 1, 1, 1),
                                   verticalScroll_incButton_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                   verticalScroll_incButton_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg"),
                                   verticalScroll_decButton_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                   verticalScroll_decButton_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg"),
                                   verticalScroll_thumb_rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                                   verticalScroll_thumb_clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/scrollButtonPressed.ogg")
                                  )
        menu.verticalScroll.setTransparency(True)
        menu.horizontalScroll.hide()

        btnList = []

        for index, item in enumerate(menuItems):
            btn = DirectButton(text = item,
                               text_scale = 0.06,
                               text_pos = (0, -0.015),
                               text_font = common.fancyFont,
                               command = self.setOptionValueFromMenu,
                               extraArgs = [item, optionID, sectionID, menu],
                               parent = menu.getCanvas(),
                               pos = (0, 0, -index*0.08),
                               frameSize = (-0.3, 0.3, -0.0375, 0.0375),
                               frameTexture = (
                                        "Assets/Shared/tex/mainMenuBtnMenuItemNormal.png",
                                        "Assets/Shared/tex/mainMenuBtnMenuItemClick.png",
                                        "Assets/Shared/tex/mainMenuBtnMenuItemHighlight.png",
                                        "Assets/Shared/tex/mainMenuBtnMenuItemNormal.png",
                                      ),
                               relief = DGG.FLAT,
                               pressEffect = False,
                               rolloverSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonHighlighted.ogg"),
                               clickSound = common.base.loader.loadSfx("Assets/Shared/sounds/buttonPressed.ogg"))
            btn.setTransparency(True)
            btnList.append(btn)
        menu["canvasSize"] = (-0.5, 0.5, -len(menuItems)*0.08, 0.075)
        menu.setPythonTag("items", btnList)

        markerLeft = DirectLabel(parent = menu.getCanvas(),
                                 frameSize = (-0.0375, 0.0375, -0.0375, 0.0375),
                                 pos = (-0.325, 0, 0),
                                 relief = DGG.FLAT,
                                 frameTexture = "Assets/Shared/tex/mainMenuMarkerLeft.png")
        markerLeft.setTransparency(True)
        markerLeft.hide()
        markerRight = DirectLabel(parent = menu.getCanvas(),
                                 frameSize = (-0.0375, 0.0375, -0.0375, 0.0375),
                                  pos = (0.325, 0, 0),
                                 relief = DGG.FLAT,
                                 frameTexture = "Assets/Shared/tex/mainMenuMarkerRight.png")
        markerRight.hide()
        markerRight.setTransparency(True)
        menu.setPythonTag("markers", (markerLeft, markerRight))

        self.setOptionWidgets(optionID, sectionID, [self.updateMenu, menu])

        self.currentOptionsZ -= self.optionMenuSpacing
        self.updateOptionsCanvasSize()

    def addOptionHeading(self, text):
        self.currentOptionsZ -= self.optionSpacingHeading*0.5
        label = DirectLabel(text = text,
                            text_align = TextNode.ACenter,
                            text_font = common.fancyFont,
                            text_fg = (0.8, 0.9, 1, 1),
                            scale = 0.1,
                            frameColor = (0, 0, 0.225, 1),
                            pad = (0.7, 0.2),
                            relief = DGG.FLAT,
                            parent = self.optionsScroller.getCanvas(),
                            pos = (0, 0, self.currentOptionsZ))
        if common.italiciseFont:
            label.setShear((0, 0.1, 0))
        self.currentOptionsZ -= self.optionSpacingHeading
        self.updateOptionsCanvasSize()

    def updateOptionsCanvasSize(self):
        self.optionsScroller["canvasSize"] = (-0.85, 0.85, self.currentOptionsZ, 0.5)

    def setMusicVolume(self, vol):
        common.base.musicManager.setVolume(vol/100)

    def setSoundVolume(self, vol):
        common.base.sfxManagerList[0].setVolume(vol/100)

    def setResolution(self, res):
        w, h = res.split(" x ")
        w = self.parseOptionVal(w)
        h = self.parseOptionVal(h)
        properties = WindowProperties()
        properties.setSize(w, h)
        common.base.win.requestProperties(properties)

        self.updateTitleForWindowSize(w, h)

    def setAntialiasing(self, antialias):
        common.base.render.clearAntialias()
        if antialias:
            common.base.render.setAntialias(AntialiasAttrib.MMultisample)
        else:
            common.base.render.setAntialias(AntialiasAttrib.MNone)

    def updateTitleForWindowSize(self, w, h):
        ratio = w / h
        ratio = ratio / 1.777777777778
        if ratio > 1:
            self.titleHolder.setX(1/aspect2d.getSx() - 1.777777)
            ratio = 1
        else:
            self.titleHolder.setX(0)
        self.titleHolder.setScale(ratio)
        self.titleHolder.setZ(0.6 + 0.4 - 0.4*ratio)

    def toggleFrameRateMeter(self):
        self.showFrameRateMeter = not self.showFrameRateMeter

        common.base.setFrameRateMeter(self.showFrameRateMeter)

    def windowUpdated(self, window):
        common.base.windowEvent(window)
        self.mainMenuBackdrop["frameSize"] = (-1/common.base.aspect2d.getSx(), 1/common.base.aspect2d.getSx(),
                                              -1/common.base.aspect2d.getSz(), 1/common.base.aspect2d.getSz())
        self.mainMenuPanel.setX(common.base.render2d, -1)
        self.mainMenuPanel["frameSize"] = (0, 1.25, -1/common.base.aspect2d.getSz(), 1/common.base.aspect2d.getSz())
        perc = min(1, common.base.camLens.getAspectRatio() / 1.6)
        self.shipSelectionMenu.setScale(perc)

        if window.hasSize():
            size = window.getSize()
            self.updateTitleForWindowSize(size[0], size[1])

        if self.currentSectionObject is not None and hasattr(self.currentSectionObject, "windowUpdated"):
            self.currentSectionObject.windowUpdated(window)

    def openMenu(self):
        self.cleanupCurrentSection()

        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setCursorFilename("Assets/Shared/tex/cursor.cur")
        common.base.win.requestProperties(properties)

        self.currentSectionIndex = 0
        self.currentSectionData = None

        self.gameOverScreen.hide()
        self.pauseMenu.hide()
        self.mainMenuBackdrop.show()
        self.mainMenuPanel.show()
        self.mainMenuMusic.setTime(11)
        self.mainMenuMusic.play()

        self.currentMenu = None

        ModelPool.list_contents()
        c = ModelPool.garbage_collect()
        print("Released models:", c)

        self.skyBox.reparentTo(render)
        common.base.camera.reparentTo(render)
        common.base.camera.setPos(0, 0, 0)
        common.base.camera.setHpr(0, 0, 0)

    def openOptions(self):
        self.optionsMenu.show()
        self.currentMenu = self.optionsMenu

    def openHelp(self):
        self.helpMenu.show()
        self.currentMenu = self.helpMenu

    def openPauseMenu(self):
        if self.endCutscene.isHidden():
            properties = WindowProperties()
            properties.setCursorHidden(False)
            properties.setCursorFilename("Assets/Shared/tex/cursor.cur")
            common.base.win.requestProperties(properties)

            self.pauseMenu.show()

            if self.currentSectionObject is not None:
                self.currentSectionObject.pauseGame()
        else:
            print ("mew")
            KeyBindings.deactivateAll("endCutscene")
            self.endCutscene.hide()
            self.openMenu()

    def returnToGame(self):
        self.pauseMenu.hide()
        if self.currentSectionObject is not None:
            self.currentSectionObject.resumeGame()

    def startGame(self):
        self.startSection(0)

    def startSection(self, index, data = None):
        specificMenu = self.sections[index][1]
        if specificMenu is not None and data is None:
            specificMenu.show()
            self.currentMenu = specificMenu

    def sectionSpecificMenuDone(self, menu, sectionIndex, data):
        menu.hide()
        self.startSectionInternal(sectionIndex, data)

    def startSectionInternal(self, index, data):
        self.cleanupCurrentSection()

        self.skyBox.detachNode()

        self.mainMenuPanel.hide()
        self.mainMenuBackdrop.hide()
        self.mainMenuMusic.stop()
        self.currentMenu = None

        self.currentSectionIndex = index
        self.currentSectionData = data

        self.cleanupLoadingScreen()
        cm = CardMaker("loading_screen")
        cm.set_frame_fullscreen_quad()
        self.loading_screen = base.render2d.attach_new_node(cm.generate())
        tex = base.loader.load_texture("Assets/Shared/tex/loading_screen.png")
        self.loading_screen.set_texture(tex)
        model = self.loadingModel

        light = DirectionalLight("directional light")
        light.setColor(Vec4(1, 1, 1, 1))
        lightNP = self.loading_screen.attachNewNode(light)
        lightNP.setScale(render, 1)
        lightNP.setHpr(render, 0, -45, 0)
        model.setLight(lightNP)

        light2 = DirectionalLight("directional light")
        light2.setColor(Vec4(0.3, 0.3, 0.6, 1))
        light2NP = self.loading_screen.attachNewNode(light2)
        light2NP.setScale(render, 0.8)
        light2NP.setHpr(render, -45, 45, 0)
        model.setLight(light2NP)

        light2 = DirectionalLight("directional light")
        light2.setColor(Vec4(0.3, 0.3, 0.6, 1))
        light2NP = self.loading_screen.attachNewNode(light2)
        light2NP.setScale(render, 0.8)
        light2NP.setHpr(render, 0, 45, 0)
        model.setLight(light2NP)

        ship1 = model.instanceUnderNode(self.loading_screen, "ship1")
        ship1.setX(aspect2d, -1.25)
        ship1.setScale(aspect2d, 1)

        ship2 = model.instanceUnderNode(self.loading_screen, "ship2")
        ship2.setX(aspect2d, 1.25)
        ship2.setH(180)
        ship2.setScale(aspect2d, 1)

        ship3 = model.instanceUnderNode(self.loading_screen, "ship3")
        ship3.setX(0)
        ship3.setH(90)
        ship3.setScale(aspect2d, 1)

        text = TextNode("ship label")
        text.setText("Mechanoid Rocketship")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)

        textNP = self.loading_screen.attachNewNode(text)
        textNP.setPos(0, 0, -0.4)
        textNP.setScale(aspect2d, 0.05)

        text = TextNode("heading")
        text.setText("\"Across the Night\"")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)

        textNP = self.loading_screen.attachNewNode(text)
        textNP.setPos(0, 0, 0.55)
        textNP.setScale(aspect2d, 0.2)

        text = TextNode("loading notice")
        text.setText("Loading...")
        text.setTextColor(Vec4(0.8, 0.9, 1, 1))
        text.setFont(common.fancyFont)
        text.setAlign(TextNode.ACenter)

        textNP = self.loading_screen.attachNewNode(text)
        textNP.setPos(0, 0, -0.9)
        textNP.setScale(aspect2d, 0.05)

        with open("Section2/models.txt") as model_path_file:
            model_paths = [path.replace("\r", "").replace("\n", "") for path in model_path_file]
        common.preload_models(model_paths, self.startSectionFinal)

    def startSectionFinal(self):
        self.cleanupLoadingScreen()

        sectionModule = self.sections[self.currentSectionIndex][0]

        if hasattr(sectionModule, "initialise"):
            initialisationMethod = sectionModule.initialise
        elif hasattr(sectionModule, "initialize"):
            initialisationMethod = sectionModule.initialize

        self.currentSectionObject = initialisationMethod(self.currentSectionData)

    def restartCurrentSection(self):
        self.gameOverScreen.hide()
        self.pauseMenu.hide()
        self.startSectionInternal(self.currentSectionIndex, self.currentSectionData)

    def gameOver(self):
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setCursorFilename("Assets/Shared/tex/cursor.cur")
        common.base.win.requestProperties(properties)

        if self.gameOverScreen.isHidden():
            self.gameOverScreen.show()

    def showEndCutscene(self):
        for np in self.endCutscene.getChildren():
            if np.hasPythonTag("scale"):
                np.setScale(common.base.aspect2d, np.getPythonTag("scale"))
            if np.getName() == "cutscene text":
                textNode = np.node()
                textNode.setWordwrap(16.8 / aspect2d.getSx())
        self.endCutscene.show()
        self.cleanupCurrentSection()
        self.skyBox.detachNode()

        KeyBindings.add("openPauseMenu", "escape", "endCutscene")
        KeyBindings.setHandler("openPauseMenu", common.gameController.openPauseMenu, "endCutscene")
        KeyBindings.activateAll("endCutscene")

    def closeOptionsMenu(self):
        self.writeOptions()
        self.closeCurrentMenu()

    def closeCurrentMenu(self):
        if self.currentMenu is not None:
            self.currentMenu.hide()
            if self.currentMenu.hasPythonTag(TAG_PREVIOUS_MENU):
                otherMenu = self.currentMenu.getPythonTag(TAG_PREVIOUS_MENU)
                otherMenu.show()
                self.currentMenu = otherMenu
            else:
                self.currentMenu = None

    def cleanupCurrentSection(self):
        import sys
        if self.currentSectionObject is not None:
            self.currentSectionObject.destroy()
            print("\n\n****** currentSectionObject ref. count:", sys.getrefcount(self.currentSectionObject) - 2)
            self.currentSectionObject = None

    def cleanupLoadingScreen(self):
        if self.loading_screen is not None:
            self.loading_screen.detach_node()
            self.loading_screen = None

    def destroy(self):
        self.cleanupCurrentSection()

        self.cleanupLoadingScreen()

        self.shipSelectionMenu.clearPythonTag(TAG_PREVIOUS_MENU)

        for section in common.optionWidgets.values():
            for key, widgetList in section.items():
                for widget in widgetList[1:]:
                    if "extraArgs" in [optTuple[0] for optTuple in widget.options()]:
                        widget["extraArgs"] = []
                    if widget.hasPythonTag("items"):
                        widget.clearPythonTag("items")
                    if widget.hasPythonTag("markers"):
                        widget.clearPythonTag("markers")
        common.options = {}
        common.optionWidgets = {}
        common.optionCallbacks = {}

    def quit(self):
        self.destroy()

        common.base.userExit()

TitleScreen(Game, Game.windowUpdated, OPTION_FILE_DIR, OPTION_FILE_NAME)
common.base.run()
