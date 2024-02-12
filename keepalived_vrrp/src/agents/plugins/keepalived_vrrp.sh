#!/bin/bash
CMK_VERSION="2.2.0p17"

# Default configuration
declare KEEPALIVED_PIDFILE="/var/run/keepalived.pid"
declare KEEPALIVED_STATUS_JSON="/tmp/keepalived.json"
declare -r KEEPALIVED_PLUGIN_CFG="${MK_CONFDIR}/keepalived_vrrp.cfg"

# read external configuration
if [ -e "${KEEPALIVED_PLUGIN_CFG}" ]; then
	source "${KEEPALIVED_PLUGIN_CFG}"
fi

# abort if we don't have a pidfile
if [ ! -e "${KEEPALIVED_PIDFILE}" ]; then
	exit 0
fi
# send signal to keepalived
kill -s $(keepalived --signum=JSON) $(<${KEEPALIVED_PIDFILE})
# most of the times we need to wait a little bit until the json status file is created
for i in {1..10}; do
        if [ -e "${KEEPALIVED_STATUS_JSON}" ]; then
                break
        else
                sleep 0.1
        fi
done
# output section if we have the status json file
if [ -e "${KEEPALIVED_STATUS_JSON}" ]; then
	echo "<<<keepalived_vrrp:sep(0)>>>"
	echo "$(<"${KEEPALIVED_STATUS_JSON}")"
	rm "${KEEPALIVED_STATUS_JSON}"
fi
