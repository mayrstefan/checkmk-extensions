#!/usr/bin/env python3
# Generic Bulk Wrapper
# Bulk: yes

import os
import re
import sys
import subprocess
from typing import NoReturn
from cmk.utils.paths import omd_root
from cmk.notification_plugins import utils

OPT_DEBUG = "-d" in sys.argv
BULK_MODE = "--bulk" in sys.argv

env_base = os.environ
env_base['PATH'] += f':{ omd_root }/local/share/check_mk/notifications'

def call_script(script_env: dict[str, str]) -> NoReturn:
    """Call regular notification script in normal (non-bulk) mode."""
    # check if a script name was given or exit
    if 'NOTIFY_PARAMETER_1' not in script_env:
        sys.stderr.write('First parameter must be the notification script to call: ' \
            'parameter is empty')
        sys.exit(1)

    # because we are a wrapper we have to shift parameters:
    #   NOTIFY_PARAMETER_1 -> script to call
    #   NOTIFY_PARAMETER_2 -> NOTIFY_PARAMETER_1
    #   NOTIFY_PARAMETER_n+1 -> NOTIFY_PARAMETER_n
    script_name = script_env['NOTIFY_PARAMETER_1']
    param_re = re.compile('^NOTIFY_PARAMETER_[0-9]+$')
    param_count = len(list(filter(lambda k: param_re.match(k), script_env)))
    # shift all parameters one position
    for i in range(1, param_count):
        script_env[f'NOTIFY_PARAMETER_{i}'] = script_env[f'NOTIFY_PARAMETER_{i+1}']
    # delete last parameter
    del script_env[f'NOTIFY_PARAMETER_{param_count}']
    # remove script name from parameters
    script_env['NOTIFY_PARAMETERS'] = script_env['NOTIFY_PARAMETERS'][len(script_name):].lstrip()

    # call script with processes environment
    if OPT_DEBUG:
        sys.stderr.write(f'call {script_name} with env: { script_env}\n')
    process = subprocess.run(script_name, env=script_env, check=False)
    if not BULK_MODE:
        sys.exit(process.returncode)

if __name__ == "__main__":
    if OPT_DEBUG:
        sys.stderr.write('started generic bulk wrapper\n')
    # normal mode: pass through the environment to call the script
    if not BULK_MODE:
        call_script(env_base)
    else:
        # Bulkmode: read contexts from stdin
        (parameters, contexts) = utils.read_bulk_contexts()
        if OPT_DEBUG:
            sys.stderr.write(f'{ len(parameters) } parameters: { parameters }\n')
            sys.stderr.write(f'{ len(contexts) } contexts: { contexts }\n')
        env_base |= { f'NOTIFY_{ k }': v for k, v in parameters.items() }
        for context in contexts:
            env_context = {
                f'NOTIFY_{ k }': v for k, v in context.items() if not k.startswith('OMD_')
            }
            call_script(env_base | env_context)
    if OPT_DEBUG:
        sys.stderr.write('finished generic bulk wrapper\n')
