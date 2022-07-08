from setuptools import setup

setup(
    name = "Captain Panda--Across the Night",
    version = "1.0.0",
    options = {
        "build_apps" : {
            "include_patterns" : [
                "**/*.png",
                "**/*.ogg",
                "**/*.txt",
                "**/*.egg",
                "**/*.egg.pz",
                "**/*.bam",
                "**/*.gltf",
                "**/*.dat",
                "**/*.cur",
                "**/*.ttf",
                "**/*.glsl",
                "**/*.vert",
                "**/*.frag",
                "Assets/Shared/fonts/*",
                "Assets/Section2/levels/scripts/*"
            ],
			"exclude_patterns" : [
                "ModelViewer/*",
                "build/*",
                "dist/*",
                ".git/*",
                "*__pychache__*",
                "README.md"
            ],
            "gui_apps" : {
                "Captain Panda--Across the Night" : "Game.py"
            },
            "icons" : {
                "Captain Panda--Across the Night" : [
                    "icon/icon512.png"
                ]
            },
            "plugins" : [
                "pandagl",
                "p3openal_audio",
            ],
            "platforms" : [
                "manylinux1_x86_64",
                #"macosx_10_6_x86_64",
                "win_amd64"
            ],
            "log_filename" : "$USER_APPDATA/CptPanda_AcrossNight/output.log",
            "log_append" : False
        }
    }
)
