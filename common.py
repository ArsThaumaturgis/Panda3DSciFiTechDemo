from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.stdpy import threading2
from direct.filter.CommonFilters import CommonFilters
from direct.particles.ParticleEffect import ParticleEffect
import random
import array
import os
import time
import sys

load_prc_file_data("",
"""
sync-video false
fullscreen false
framebuffer-multisample 1
multisamples 4
""")


base = ShowBase()
# load a scene shader
vert_shader = "Assets/Shared/shaders/pbr_shader_v.vert"
frag_shader = "Assets/Shared/shaders/pbr_shader_f.frag"
invert_vert = "Assets/Shared/shaders/pbr_shader_v_invert.vert"
invert_frag = "Assets/Shared/shaders/pbr_shader_f_invert.frag"
metal_shader = Shader.load(Shader.SL_GLSL, invert_vert, invert_frag)
scene_shader = Shader.load(Shader.SL_GLSL, vert_shader, frag_shader)
#base.render.set_shader(scene_shader)

scene_filters = CommonFilters(base.win, base.cam)

game_start_time = time.time()

fancyFont = None
italiciseFont = False

gameController = None

currentSection = None

options = {} # Dictionary of dictionaries of option-values.
# In short: The first key indicates a section, and the section indicates the specific option.
optionCallbacks = {} # Again, a dictionary of dictionaries, this time of callback-pairs.
# The keys are the same as used in "options", above.
optionWidgets = {} # Once again, a dictionary of dictionaries, this time of UI-widgets in a list, and
# a callback ahead of them.
# The keys are the same as used in the two option-dictionaries above.

def getOption(sectionID, optionID):
    section = options.get(sectionID, None)
    if section is None:
        return None
    optionValue = section.get(optionID, None)
    return optionValue

def setOption(sectionID, optionID, newVal):
    section = options.get(sectionID, None)
    if section is None:
        return
    section[optionID] = newVal

def loadParticles(fileName):
    extension = "ptf"
    directory = "Particles/"
    if not fileName.endswith(".{0}".format(extension)):
        fileName = "{0}.{1}".format(fileName, extension)
    fileName = "{0}{1}".format(directory, fileName)

    particleEffect = ParticleEffect()
    particleEffect.loadConfig(fileName)
    return particleEffect

def create_skybox(cube_map_name):

    coords = (
        (-1., 1., -1.), (1., 1., -1.), (1., 1., 1.), (-1., 1., 1.),
        (1., -1., -1.), (-1., -1., -1.), (-1., -1., 1.), (1., -1., 1.)
    )
    pos_data = array.array("f", [])

    for coord in coords:
        pos_data.extend(coord * 2)

    idx_data = array.array("H", [
        0, 1, 2,
        0, 2, 3,
        5, 0, 3,
        5, 3, 6,
        1, 4, 7,
        1, 7, 2,
        4, 5, 6,
        4, 6, 7,
        3, 2, 7,
        3, 7, 6,
        5, 4, 1,
        5, 1, 0
    ])

    array_format = GeomVertexArrayFormat()
    array_format.add_column(InternalName.make("vertex"), 3, Geom.NT_float32, Geom.C_point)
    array_format.add_column(InternalName.make("texcoord"), 3, Geom.NT_float32, Geom.C_texcoord)
    vertex_format = GeomVertexFormat()
    vertex_format.add_array(array_format)
    vertex_format = GeomVertexFormat.register_format(vertex_format)

    v_data = GeomVertexData("side_data", vertex_format, Geom.UH_static)
    v_data.unclean_set_num_rows(8)
    view = memoryview(v_data.modify_array(0)).cast("B").cast("f")
    view[:] = pos_data

    prim = GeomTriangles(Geom.UH_static)
    idx_array = prim.modify_vertices()
    idx_array.unclean_set_num_rows(len(idx_data))
    view = memoryview(idx_array).cast("B").cast("H")
    view[:] = idx_data

    geom = Geom(v_data)
    geom.add_primitive(prim)
    node = GeomNode("sky_box")
    node.add_geom(geom)
    skybox = NodePath(node)
    skybox.set_light_off()
    skybox.set_material_off()
    skybox.set_shader_off()
    skybox.set_bin("background", 0)
    skybox.set_depth_write(False)
    skybox.set_scale(10.)
    skybox.set_texture(base.loader.load_cube_map(cube_map_name))

    return skybox


# The following class keeps track of key-bindings, such that they can easily be
# suppressed and restored (e.g. when pausing and resuming the demo, respectively).
# A dedicated DirectObject can be used to listen for key events instead of ShowBase
# by assigning it to `KeyBindings.listener`.
# Key-bindings can be divided into groups for convenience. If no group ID is
# specified in the calls to the class methods, a default ID ("") is used.
class KeyBindings:

    listener = base
    bindings = {}

    @classmethod
    def add(cls, key, handler, group="", activate=True):
        cls.bindings.setdefault(group, {})[key] = handler

        if activate:
            cls.listener.accept(key, handler)

    @classmethod
    def remove(cls, key, group="", deactivate=True):
        if deactivate:
            cls.listener.ignore(key)

        del cls.bindings[group][key]

        if not cls.bindings[group]:
            del cls.bindings[group]

    @classmethod
    def clear(cls, group="", deactivate=True):
        if deactivate:
            cls.deactivate_all(group)

        del cls.bindings[group]

    @classmethod
    def activate(cls, key, group="", once=False):
        handler = cls.bindings.get(group, {}).get(key, lambda: None)

        if once:
            cls.listener.accept_once(key, handler)
        else:
            cls.listener.accept(key, handler)

    @classmethod
    def activate_all(cls, group="", once=False):
        if once:
            for key, handler in cls.bindings.get(group, {}).items():
                cls.listener.accept_once(key, handler)
        else:
            for key, handler in cls.bindings.get(group, {}).items():
                cls.listener.accept(key, handler)

    @classmethod
    def deactivate(cls, key):
        cls.listener.ignore(key)

    @classmethod
    def deactivate_all(cls, group=""):
        if group is None:  # not recommended if cls.listener == base!!!
            cls.listener.ignore_all()
        else:
            for key in cls.bindings.get(group, {}):
                cls.listener.ignore(key)


# The following class is a modification of PythonTask. Its purpose is to
# allow resuming (re-adding) a previously paused (removed) task without its
# internal timers being reset.
# Specifically, since `Task.time` is reset to zero when the task is re-added,
# a new `cont_time` variable adds the previous task duration to this value.
# This variable should therefore be used instead of `Task.time` for code that
# expects the elapsed time to continue increasing from where it left off when
# pausing the task.
# For delayed tasks, no changes to existing code need to be made, as it can
# rely on `Task.delay_time` being decreased by the previously elapsed task time
# upon resumption, as expected.
class ResumableTask(PythonTask):

    def __init__(self, task_func, task_id, delay=None, sort=0, priority=0, uponDeath=None, clock=None):
        def extended_func(task):
            return task_func(self)

        PythonTask.__init__(self, extended_func, task_id)

        self.clock = globalClock if clock is None else clock
        self.delay_time = delay
        self.sort = sort
        self.priority = priority
        self.set_upon_death(uponDeath if uponDeath else lambda task: None)
        self.paused_time = 0.
        self.paused_delay_time = 0.
        self.tmp_time = self.clock.get_real_time()
        self.is_paused = False

    def pause(self):
        if self.is_paused:
            return

        self.paused_time += self.time
        base.task_mgr.remove(self)

        if self.delay_time is None:
            self.paused_delay_time = 0.
        else:
            dt = self.clock.get_real_time() - self.tmp_time
            self.paused_delay_time = max(0., self.delay_time - dt)

        self.is_paused = True

    def resume(self):
        if not self.is_paused:
            return

        if self.delay_time is not None:
            self.delay_time = self.paused_delay_time

        base.task_mgr.add(self)
        self.tmp_time = self.clock.get_real_time()

        self.is_paused = False

    @property
    def cont_time(self):
        return self.time + self.paused_time
