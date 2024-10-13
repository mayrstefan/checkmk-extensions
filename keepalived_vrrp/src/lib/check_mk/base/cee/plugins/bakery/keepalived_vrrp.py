#!/usr/bin/env python3

from pathlib import Path
from typing import TypedDict, List

from .bakery_api.v1 import (
    OS,
    DebStep,
    RpmStep,
    Plugin,
    PluginConfig,
    Scriptlet,
    register,
    FileGenerator,
    ScriptletGenerator,
    quote_shell_string,
)

# Create a class that holds our config. This corresponds to the parameters set
# in the setup GUI and defines in web/plugins/wato/keepalived_vrrp_bakery.py

class keepalived_vrrpBakeryConfig(TypedDict, total=False):
    interval: int
    pidfile: str
    jsonfile: str

def get_keepalived_vrrp_plugin_files(conf: keepalived_vrrpBakeryConfig) -> FileGenerator:
    # In some cases you may want to override user input here to ensure a minimal
    # interval!
    interval = conf.get('interval')

    # The source file, specified with "source" argument, is taken from
    # ~/local/share/check_mk/agents/plugins/. It will be installed under the target name,
    # specified with "target" argument, in /usr/lib/check_mk_agent/plugins/<interval>/
    # or in /usr/lib/check_mk_agent/plugins/ (if synchronous call is requested)
    # on the target system. If the "target" argument is omitted, the "source" argument
    # will be reused as target name
    yield Plugin(
        base_os=OS.LINUX,
        source=Path('keepalived_vrrp.sh'),
        interval=interval,
    )

    yield PluginConfig(base_os=OS.LINUX,
                      lines=_get_linux_cfg_lines(conf),
                      target=Path('keepalived_vrrp.cfg'),
                      include_header=True)

def _get_linux_cfg_lines(cfg: dict) -> List[str]:
    lines = []
    if 'pidfile' in cfg and cfg['pidfile'] != '':
        lines.append('KEEPALIVED_PIDFILE="%s"' % quote_shell_string(cfg['pidfile']))
    if 'jsonfile' in cfg and cfg['jsonfile'] != '':
        lines.append('KEEPALIVED_STATUS_JSON="%s"' % quote_shell_string(cfg['jsonfile']))
    return lines

def get_keepalived_vrrp_scriptlets(conf: keepalived_vrrpBakeryConfig) -> ScriptletGenerator: # pylint: disable=unused-argument
    installed_lines = ['logger -p Checkmk_Agent "Installed keepalived_vrrp.sh"']
    uninstalled_lines = ['logger -p Checkmk_Agent "Uninstalled keepalived_vrrp.sh"']

    yield Scriptlet(step=DebStep.POSTINST, lines=installed_lines)
    yield Scriptlet(step=DebStep.POSTRM, lines=uninstalled_lines)
    yield Scriptlet(step=RpmStep.POST, lines=installed_lines)
    yield Scriptlet(step=RpmStep.POSTUN, lines=uninstalled_lines)

register.bakery_plugin(
    name="keepalived_vrrp",
    files_function=get_keepalived_vrrp_plugin_files,
    scriptlets_function=get_keepalived_vrrp_scriptlets
)
