#!/usr/bin/env python3
from collections.abc import Iterator
from pathlib import Path
from typing import TypedDict, Literal, NotRequired

from cmk.utils.password_store import lookup_for_bakery

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
)

# Create a class that holds our config. This corresponds to the parameters set
# in the setup GUI


class HaproxyFusionBasicAuth(TypedDict):
    username: str
    password: tuple[str, str, tuple[str, str]]


class HaproxyFusionKeyAuth(TypedDict):
    key: str


class HaproxyFusionBakeryConfig(TypedDict):
    url: str
    auth: tuple[
        Literal["auth_type"], None | HaproxyFusionBasicAuth | HaproxyFusionKeyAuth
    ]
    verify: NotRequired[bool]


def get_haproxy_fusion_plugin_files(conf: HaproxyFusionBakeryConfig) -> FileGenerator:
    # The source file, specified with "source" argument, is taken from
    # ~/local/share/check_mk/agents/plugins/. It will be installed under the target name,
    # specified with "target" argument, in /usr/lib/check_mk_agent/plugins/<interval>/
    # or in /usr/lib/check_mk_agent/plugins/ (if synchronous call is requested)
    # on the target system. If the "target" argument is omitted, the "source" argument
    # will be reused as target name
    yield Plugin(
        base_os=OS.LINUX,
        source=Path("agent_haproxy_fusion"),
    )
    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_linux_cfg_lines(conf)),
        target=Path("haproxy_fusion.cfg"),
        include_header=True,
    )


def _get_linux_cfg_lines(conf: HaproxyFusionBakeryConfig) -> Iterator[str]:
    yield "[HAPROXY_FUSION]"
    for attr in ("url", "verify"):
        if attr in conf:
            yield f"{ attr } = { conf.get(attr) }"
    if "auth" in conf:
        (auth_type, auth_details) = conf.get("auth")
        yield f"auth_type = { auth_type }"
        if auth_details:
            for k, v in auth_details.items():
                if k in ("password", "key"):
                    match v:
                        case _marker, "explicit_password", (_uuid, v):
                            ...
                        case _marker, "stored_password", (pwd_id, str()):
                            v = lookup_for_bakery(pwd_id)
                        case other:
                            raise ValueError(f"Invalid password type: {other!r}")
                yield f"{ k } = { v }"


def get_haproxy_fusion_scriptlets(
    conf: HaproxyFusionBakeryConfig, # pylint: disable=unused-argument
) -> ScriptletGenerator:
    installed_lines = ['logger "Installed agent_haproxy_fusion"']
    uninstalled_lines = ['logger "Uninstalled agent_haproxy_fusion"']

    yield Scriptlet(step=DebStep.POSTINST, lines=installed_lines)
    yield Scriptlet(step=DebStep.POSTRM, lines=uninstalled_lines)
    yield Scriptlet(step=RpmStep.POST, lines=installed_lines)
    yield Scriptlet(step=RpmStep.POSTUN, lines=uninstalled_lines)


register.bakery_plugin(
    name="haproxy_fusion_agent",
    files_function=get_haproxy_fusion_plugin_files,
    scriptlets_function=get_haproxy_fusion_scriptlets,
)
