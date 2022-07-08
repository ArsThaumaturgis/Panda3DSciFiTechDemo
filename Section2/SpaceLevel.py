
from Section2.Level import Level

import common

class SpaceLevel(Level):
    def __init__(self):
        Level.__init__(self, "spaceLevel")

    def spawnWave1(self):
        self.activateSpawnerGroup("wave1")

    def spawnWave2(self):
        self.activateSpawnerGroup("wave2")

    def spawnWave3(self):
        self.activateSpawnerGroup("wave3")

    def spawnWave4(self):
        self.activateSpawnerGroup("wave4")

    def spawnWave5(self):
        self.activateSpawnerGroup("wave5")

    def exitTriggered(self):
        common.currentSection.exitTriggered()