#!/usr/bin/env python3
# Shebang needed only for editors

from cmk.server_side_calls.v1 import (
    noop_parser,
    SpecialAgentConfig,
    SpecialAgentCommand,
)


def _agent_arguments(params, host_config):
    # pylint: disable=unused-argument
    args = ["--auth-type"]
    auth_type, auth_details = params["auth"]
    match auth_type:
        case "none":
            args.extend(["none"])
        case "basic":
            args.extend(
                [
                    "basic",
                    "--username",
                    str(auth_details["username"]),
                    "--password",
                    auth_details["password"].unsafe(),
                ]
            )
        case "apikey":
            args.extend(["apikey", "--key", auth_details["key"].unsafe()])
        case "x_api_key":
            args.extend(["x-api-key", "--key", auth_details["key"].unsafe()])
        case "x_fusion_apikey":
            args.extend(["x-fusion-apikey", "--key", auth_details["key"].unsafe()])
    args.extend(["--url", str(params["url"])])
    if "verify" in params:
        args.extend(["--verify", str(params["verify"])])
    yield SpecialAgentCommand(command_arguments=args)


special_agent_haproxy_fusion = SpecialAgentConfig(
    name="haproxy_fusion",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments,
)
