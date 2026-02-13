# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Plugins.Plugin import PluginDescriptor

from .screens.main import CiefpParabolaCZMain

try:
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
except Exception:
    resolveFilename = None
    SCOPE_PLUGINS = None


def main(session, **kwargs):
    session.open(CiefpParabolaCZMain)


def Plugins(**kwargs):
    icon = None
    try:
        if resolveFilename and SCOPE_PLUGINS:
            icon = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpParabolaCZ/images/plugin.png")
    except Exception:
        icon = None

    return [
        PluginDescriptor(
            name="CiefpParabolaCZ",
            description="Parabola.cz viewer (satellites, packages, news) v1.0",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main,
            icon=icon
        ),
    ]
