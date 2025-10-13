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
# in the setup GUI and defines in web/plugins/wato/pgbouncer_bakery.py

class pgbouncerBakeryConfig(TypedDict, total=False):
    interval: int
    dbuser: str
    pghost: str
    pgport: str

def get_pgbouncer_plugin_files(conf: pgbouncerBakeryConfig) -> FileGenerator:
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
        source=Path('pgbouncer.py'),
        interval=interval,
    )

    yield PluginConfig(base_os=OS.LINUX,
                      lines=_get_linux_cfg_lines(conf),
                      target=Path('pgbouncer.cfg'),
                      include_header=True)

def _get_linux_cfg_lines(cfg: dict) -> List[str]:
    lines = []
    for option in ('dbuser', 'pghost', 'pgport'):
        if option in cfg and cfg[option] != '':
            lines.append('%s=%s' % (option.upper(), quote_shell_string(cfg[option])))
    return lines

def get_pgbouncer_scriptlets(conf: pgbouncerBakeryConfig) -> ScriptletGenerator: # pylint: disable=unused-argument
    installed_lines = ['logger "Installed pgbouncer.py"']
    uninstalled_lines = ['logger "Uninstalled pgbouncer.py"']

    yield Scriptlet(step=DebStep.POSTINST, lines=installed_lines)
    yield Scriptlet(step=DebStep.POSTRM, lines=uninstalled_lines)
    yield Scriptlet(step=RpmStep.POST, lines=installed_lines)
    yield Scriptlet(step=RpmStep.POSTUN, lines=uninstalled_lines)

register.bakery_plugin(
    name="pgbouncer",
    files_function=get_pgbouncer_plugin_files,
    scriptlets_function=get_pgbouncer_scriptlets
)
