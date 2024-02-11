from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info

metric_info["keepalived_advert_rcvd"] = {
    "title": _("Advertisements received"),
    "unit": "count",
    "color": "11/a",
}

metric_info["keepalived_advert_sent"] = {
    "title": _("Advertisements sent"),
    "unit": "count",
    "color": "12/a",
}

metric_info["keepalived_advert_interval_err"] = {
    "title": _("Advertisement interval errors"),
    "unit": "count",
    "color": "14/a",
}

metric_info["keepalived_addr_list_err"] = {
    "title": _("Address list errors"),
    "unit": "count",
    "color": "15/a",
}

metric_info["keepalived_become_master"] = {
    "title": _("Become master count"),
    "unit": "count",
    "color": "21/a",
}

metric_info["keepalived_release_master"] = {
    "title": _("Release master count"),
    "unit": "count",
    "color": "22/a",
}

metric_info["keepalived_packet_len_err"] = {
    "title": _("Packet length errors"),
    "unit": "count",
    "color": "24/a",
}

metric_info["keepalived_ip_ttl_err"] = {
    "title": _("IP TTL errors"),
    "unit": "count",
    "color": "25/a",
}

metric_info["keepalived_invalid_type_rcvd"] = {
    "title": _("Invalid type received count"),
    "unit": "count",
    "color": "31/a",
}

metric_info["keepalived_invalid_authtype"] = {
    "title": _("Invalid authtype count"),
    "unit": "count",
    "color": "32/a",
}

metric_info["keepalived_authtype_mismatch"] = {
    "title": _("Authtype mismatch count"),
    "unit": "count",
    "color": "33/a",
}

metric_info["keepalived_auth_failure"] = {
    "title": _("Authentication failures"),
    "unit": "count",
    "color": "34/a",
}

metric_info["keepalived_pri_zero_rcvd"] = {
    "title": _("Priority zero received"),
    "unit": "count",
    "color": "41/a",
}

metric_info["keepalived_pri_zero_sent"] = {
    "title": _("Priority zero sent"),
    "unit": "count",
    "color": "42/a",
}
