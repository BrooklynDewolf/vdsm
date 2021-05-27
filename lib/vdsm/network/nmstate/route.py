# Copyright 2020 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

from vdsm.network.common.switch_util import SwitchType

from .schema import Route

DEFAULT_TABLE_ID = 254


class Family(object):
    IPV4 = 4
    IPV6 = 6


class DefaultRouteDestination(object):
    IPV4 = '0.0.0.0/0'
    IPV6 = '::/0'

    @staticmethod
    def get_by_family(family):
        if family == Family.IPV4:
            return DefaultRouteDestination.IPV4
        if family == Family.IPV6:
            return DefaultRouteDestination.IPV6
        return None


class Routes(object):
    def __init__(self, netconf, runconf):
        self._netconf = netconf
        self._runconf = runconf
        self._state = self._create_routes()

    @property
    def state(self):
        return self._state

    def _create_routes(self):
        routes = []
        next_hop = _get_next_hop_interface(self._netconf)
        for family in (Family.IPV4, Family.IPV6):
            gateway = _get_gateway_by_ip_family(self._netconf, family)
            runconf_gateway = _get_gateway_by_ip_family(self._runconf, family)
            if gateway:
                routes.append(self._create_route(next_hop, gateway, family))
                if (
                    _gateway_has_changed(runconf_gateway, gateway)
                    and runconf_gateway
                ):
                    routes.append(
                        self._create_remove_default_route(
                            next_hop, runconf_gateway, family
                        )
                    )
            elif self._should_remove_def_route(family):
                routes.append(
                    self._create_remove_default_route(
                        next_hop, runconf_gateway, family
                    )
                )

        return routes

    def _create_route(self, next_hop, gateway, family):
        if self._netconf.default_route:
            return self._create_add_default_route(next_hop, gateway, family)
        else:
            return self._create_remove_default_route(next_hop, gateway, family)

    def _should_remove_def_route(self, family):
        dhcp = (
            self._netconf.dhcpv4
            if family == Family.IPV4
            else self._netconf.dhcpv6
        )
        return (
            not self._netconf.remove
            and _get_gateway_by_ip_family(self._runconf, family)
            and self._runconf.default_route
            and (dhcp or not self._netconf.default_route)
        )

    @staticmethod
    def _create_add_default_route(next_hop_interface, gateway, family):
        return _create_route_state(
            next_hop_interface,
            gateway,
            DefaultRouteDestination.get_by_family(family),
        )

    @staticmethod
    def _create_remove_default_route(next_hop_interface, gateway, family):
        return _create_route_state(
            next_hop_interface,
            gateway,
            DefaultRouteDestination.get_by_family(family),
            absent=True,
        )


def _gateway_has_changed(runconf_gateway, netconf_gateway):
    return runconf_gateway != netconf_gateway


def _get_next_hop_interface(source):
    if source.switch == SwitchType.OVS or source.bridged:
        return source.name

    return source.vlan_iface or source.base_iface


def _get_gateway_by_ip_family(source, family):
    return source.gateway if family == Family.IPV4 else source.ipv6gateway


def _create_route_state(
    next_hop_interface,
    gateway,
    destination,
    absent=False,
    table_id=Route.USE_DEFAULT_ROUTE_TABLE,
):
    state = {
        Route.NEXT_HOP_ADDRESS: gateway,
        Route.NEXT_HOP_INTERFACE: next_hop_interface,
        Route.DESTINATION: destination,
        Route.TABLE_ID: table_id,
    }
    if absent:
        state[Route.STATE] = Route.STATE_ABSENT

    return state
