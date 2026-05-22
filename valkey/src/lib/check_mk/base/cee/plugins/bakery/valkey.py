#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterator, Sequence
from pathlib import Path
from shlex import quote
from typing import Literal, NotRequired, TypedDict

from cmk.utils.password_store import lookup_for_bakery

from .bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    PluginConfig,
    register,
)


class ConnectionParamsTcp(TypedDict):
    host: str
    port: int


class ConnectionParamsSocket(TypedDict):
    socket: str


class ValkeyInstance(TypedDict):
    instance: str
    connection: (
        tuple[Literal["tcp"], ConnectionParamsTcp]
        | tuple[Literal["unixsocket"], ConnectionParamsSocket]
    )
    password: tuple[str, str, tuple[str, str]]


class ValkeyConfig(TypedDict):
    deployment: NotRequired[
        tuple[Literal["autodetect"], None]
        | tuple[Literal["static"], Sequence[ValkeyInstance]]
        | tuple[Literal["do_not_deploy"], None]
    ]


def get_valkey_files(conf: ValkeyConfig) -> FileGenerator:
    deployment = conf.get("deployment", ("autodetect", None))
    # do not package any file if do_not_deploy was selected
    match deployment:
        case "do_not_deploy", _:
            return
    # add plugin file
    yield Plugin(base_os=OS.LINUX, source=Path("valkey"))
    # generate configuration file
    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_valkey_config(conf)),
        target=Path("valkey.cfg"),
        include_header=True,
    )


def _get_valkey_config(conf: ValkeyConfig) -> Iterator[str]:
    deployment = conf.get("deployment", ("autodetect", None))
    match deployment:
        case "do_not_deploy", _:
            return
        case "autodetect", _:
            yield "# Autodetect instances"
            return
        case "static", list() as instances:
            for valkey_instance in instances:
                instance = valkey_instance["instance"]
                connection = valkey_instance["connection"]
                port: str | int
                if connection[0] == "tcp":
                    host = connection[1]["host"]
                    port = connection[1]["port"]
                else:
                    assert connection[0] == "unixsocket"
                    host = connection[1]["socket"]
                    port = "unix-socket"
                match valkey_instance["password"]:
                    case _marker, "explicit_password", (_uuid, password):
                        ...
                    case _marker, "stored_password", (pwd_id, str()):
                        password = lookup_for_bakery(pwd_id)
                    case other:
                        raise ValueError(f"Invalid password type: {other!r}")

                yield f"VALKEY_HOST_{instance}={quote(host)}"
                yield f"VALKEY_PORT_{instance}={quote(str(port))}"
                if password is not None:
                    yield f"VALKEY_PASSWORD_{instance}={quote(password)}"

            yield "VALKEY_INSTANCES=(%s)" % " ".join(e["instance"] for e in instances)


register.bakery_plugin(
    name="valkey",
    files_function=get_valkey_files,
)
