# Keepalived check
This check is an agent based check to monitor keepalived VRRP instances

The agent sends a signal to keepalived and waits up to 5 seconds for the json status file to appear.

## Agent configuration
In /etc/checkmk/keepalived_vrrp.cfg the paths to the keepalived pidfile and the output json can be configured
```
KEEPALIVED_PIDFILE="/var/run/keepalived.pid"
KEEPALIVED_STATUS_JSON="/tmp/keepalived.json"
```
