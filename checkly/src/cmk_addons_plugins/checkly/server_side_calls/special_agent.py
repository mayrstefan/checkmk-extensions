#!/usr/bin/env python3
# Shebang needed only for editors

from collections.abc import Iterator
from pydantic import BaseModel
from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentConfig,
    SpecialAgentCommand,
)


# pylint: disable=too-few-public-methods
class ChecklyParams(BaseModel):
    account: str
    token: Secret


def _agent_arguments(
    params: ChecklyParams, _host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    args = ["--account", str(params.account), "--token", params.token.unsafe()]
    yield SpecialAgentCommand(command_arguments=args)


special_agent_checkly = SpecialAgentConfig(
    name="checkly",
    parameter_parser=ChecklyParams.model_validate,
    commands_function=_agent_arguments,
)
