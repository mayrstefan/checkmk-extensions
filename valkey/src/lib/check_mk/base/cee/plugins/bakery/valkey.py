#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterator, Sequence
from pathlib import Path
from shlex import quote
from typing import Literal, TypedDict

from .bakery_api.v1 import (
    FileGenerator,
    OS,
    password_store,
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
        | tuple[Literal["unix-socket"], ConnectionParamsSocket]
    )
    password: password_store.PasswordId | str | None


ValkeyConfig = Literal["autodetect"] | tuple[Literal["static"], Sequence[ValkeyInstance]]


def get_valkey_files(conf: ValkeyConfig) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("valkey"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_valkey_config(conf)),
        target=Path("valkey.cfg"),
        include_header=True,
    )


def _get_valkey_config(conf: ValkeyConfig) -> Iterator[str]:
    if conf == "autodetect":
        yield "# Autodetect instances"
        return

    for valkey_instance in conf[1]:
        instance = valkey_instance["instance"]
        connection = valkey_instance["connection"]
        port: str | int
        if connection[0] == "tcp":
            host = connection[1]["host"]
            port = connection[1]["port"]
        else:
            assert connection[0] == "unix-socket"
            host = connection[1]["socket"]
            port = "unix-socket"
        password = valkey_instance["password"]

        yield f"VALKEY_HOST_{instance}={quote(host)}"
        yield f"VALKEY_PORT_{instance}={quote(str(port))}"
        if password is not None:
            yield f"VALKEY_PASSWORD_{instance}={quote(password_store.extract(password))}"

    yield "VALKEY_INSTANCES=(%s)" % " ".join(e["instance"] for e in conf[1])


register.bakery_plugin(
    name="valkey",
    files_function=get_valkey_files,
)
