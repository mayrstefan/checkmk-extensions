#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit, StrictPrecision

metric_keepalived_vrrp_advert_rcvd = Metric(
    name = "keepalived_advert_rcvd",
    title = Title("Advertisements received"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.YELLOW,
)

metric_keepalived_vrrp_advert_sent = Metric(
    name = "keepalived_advert_sent",
    title = Title("Advertisements sent"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.ORANGE,
)

metric_keepalived_vrrp_advert_interval_err = Metric(
    name = "keepalived_advert_interval_err",
    title = Title("Advertisement interval errors"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.RED,
)

graph_keepalived_vrrp_advert_combined = Graph(
    name = "keepalived_advert_combined",
    title = Title("Advertisements sent, received and interval errors"),
    simple_lines = [ "keepalived_advert_sent", "keepalived_advert_rcvd", "keepalived_advert_interval_err"],
    minimal_range = MinimalRange(0,1)
)

metric_keepalived_vrrp_addr_list_err = Metric(
    name = "keepalived_addr_list_err",
    title = Title("Address list errors"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.ORANGE,
)

metric_keepalived_vrrp_become_master = Metric(
    name = "keepalived_become_master",
    title = Title("Become master count"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.LIGHT_YELLOW,
)

metric_keepalived_vrrp_release_master = Metric(
    name = "keepalived_release_master",
    title = Title("Release master count"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.DARK_YELLOW,
)

metric_keepalived_vrrp_packet_len_err = Metric(
    name = "keepalived_packet_len_err",
    title = Title("Packet length errors"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.LIGHT_GREEN,
)

metric_keepalived_vrrp_ip_ttl_err = Metric(
    name = "keepalived_ip_ttl_err",
    title = Title("IP TTL errors"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.GREEN,
)

metric_keepalived_vrrp_invalid_type_rcvd = Metric(
    name = "keepalived_invalid_type_rcvd",
    title = Title("Invalid type received count"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.BLUE,
)

metric_keepalived_vrrp_invalid_authtype = Metric(
    name = "keepalived_invalid_authtype",
    title = Title("Invalid authtype count"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.LIGHT_PURPLE,
)

metric_keepalived_vrrp_authtype_mismatch = Metric(
    name = "keepalived_authtype_mismatch",
    title = Title("Authtype mismatch count"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.PURPLE,
)

metric_keepalived_vrrp_auth_failure = Metric(
    name = "keepalived_auth_failure",
    title = Title("Authentication failures"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.DARK_PURPLE,
)

metric_keepalived_vrrp_pri_zero_rcvd = Metric(
    name = "keepalived_pri_zero_rcvd",
    title = Title("Priority zero received"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.CYAN,
)

metric_keepalived_vrrp_pri_zero_sent = Metric(
    name = "keepalived_pri_zero_sent",
    title = Title("Priority zero sent"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.DARK_CYAN,
)

graph_keepalived_vrrp_pri_zero_combined = Graph(
    name = "keepalived_pri_zero_combined",
    title = Title("Priority zero sent and received"),
    simple_lines = [ "keepalived_pri_zero_sent", "keepalived_pri_zero_rcvd"],
    minimal_range = MinimalRange(0,1)
)
