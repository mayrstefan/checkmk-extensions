#!/bin/bash
CMK_VERSION="2.2.0p17"

# Default-Konfiguration
declare KEEPALIVED_PIDFILE="/var/run/keepalived.pid"
declare KEEPALIVED_STATUS_JSON="/tmp/keepalived.json"
declare -r KEEPALIVED_PLUGIN_CFG="${MK_CONFDIR}/keepalived_vrrp.cfg"

# Externe Konfiguration einlesen wenn vorhanden
if [ -e "${KEEPALIVED_PLUGIN_CFG}" ]; then
	source "${KEEPALIVED_PLUGIN_CFG}"
fi

# Frühzeitiges Ende wenn wir kein Pidfile haben
if [ ! -e "${KEEPALIVED_PIDFILE}" ]; then
	exit 0
fi
# JSON-Status erzeugen und ausgeben
kill -s $(keepalived --signum=JSON) $(<${KEEPALIVED_PIDFILE})
if [ -e "${KEEPALIVED_STATUS_JSON}" ]; then
	echo "<<<keepalived_vrrp:sep(0)>>>"
	echo "$(<"${KEEPALIVED_STATUS_JSON}")"
	rm "${KEEPALIVED_STATUS_JSON}"
fi
