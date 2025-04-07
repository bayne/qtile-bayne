import subprocess
from typing import List

from libqtile import layout, widget, bar, hook, log_utils, qtile
from libqtile.config import Group, Screen, Mouse, Key
from libqtile.layout.base import Layout
from libqtile.lazy import lazy
import asyncio

from bayne.default import get_default_keys, get_default_switch_group_keys, get_default_mouse
from bayne.rofi import Rofi, RofiScript
from bayne import systemd_logging
from bayne.hooks import popover, active_popup
from bayne.default import get_widget_defaults, get_default_floating, get_default_layouts

active_popup.init([
    'opensnitch-ui',
])
popover.init(restack=[
    'jetbrains-idea',
])
systemd_logging.init()

@hook.subscribe.startup_once
def startup():
    subprocess.Popen(["/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1"])
    # home dir backup
    subprocess.Popen(["/usr/bin/vorta"])
    # screenshot
    subprocess.Popen(["gtk-launch", "org.flameshot.Flameshot"])
    # egress firewall
    subprocess.Popen(["gtk-launch", "opensnitch_ui"])
    ## disabling screensaver due to issues with screen not turning back on
    # disable screensaver
    subprocess.Popen(["xset", "s", "off"])
    # disable energy star features (related to screensaver)
    subprocess.Popen(["xset", "-dpms"])

W1_GROUP = "W1"
W2_GROUP = "W2"

logger = log_utils.logger


@hook.subscribe.client_new
@hook.subscribe.client_name_updated
async def new_work_virt_viewer(client):
    if "remote-viewer" in client.get_wm_class():
        if "work (1)" in client.name:
            client.togroup(W1_GROUP)
            qtile.groups[9].toscreen(0)
            await asyncio.sleep(1.0)
            qtile.spawn(['xdotool', 'key', 'F11'])
        elif "work (2)" in client.name:
            client.togroup(W2_GROUP)

mod = "mod4"
# https://github.com/qtile/qtile/blob/master/libqtile/backend/x11/xkeysyms.py
rofi = Rofi([RofiScript(name="intellij", path="/home/bpayne/Code/mine/dotfile/rofi-scripts/intellij.py")])
keys = get_default_keys(mod, rofi)

groups = [Group(name=i, screen_affinity=0) for i in "123456789"]
groups.append(Group(name=W1_GROUP, screen_affinity=0))
groups.append(Group(name=W2_GROUP, screen_affinity=0))
keys.extend(get_default_switch_group_keys(mod, 9))
keys.extend([
    Key(['mod1', "control"], "9", lazy.group[W1_GROUP].toscreen(), desc="W1"),
    Key(['mod1', "control"], "0", lazy.group[W2_GROUP].toscreen(), desc="W2"),
    Key([mod, 'control'], 'l',
        lazy.spawn('lock'),
        desc='Lock screen',
    ),
])

layouts: List[Layout] = get_default_layouts()

widget_defaults: dict = get_widget_defaults()
extension_defaults = widget_defaults.copy()

screens: List[Screen] = [
    Screen(
        background="#555",
        top=bar.Bar(
            widgets=[
                widget.GroupBox(),
                widget.WindowName(),
                widget.Clock(format="%a %b %d %I:%M:%S %p"),
                widget.Spacer(),
                widget.Systray(),
            ],
            size=24,
            background="#222",
        ),
    )
]

# Drag floating layouts.
mouse: List[Mouse] = get_default_mouse(mod)
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_click: bool = False
floats_kept_above: bool = True
cursor_warp: bool = False
floating_layout: layout.Floating = layout.Floating(
   float_rules=[
       *layout.Floating.default_float_rules,
       *get_default_floating(),
   ]
)
auto_fullscreen: bool = True
focus_on_window_activation: bool = "smart"
reconfigure_screens: bool = True
auto_minimize = True
wmname = "LG3D"