# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# OpenNET Inventory
# Initial revision, December 2018: Aymeric
# Changed by Bo Finnemann on 2019-01-03: Calculation of VLAN Pool changed.
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        found = False
        maxEnd=0
        for sp in root.open_net_access.inventory.sps.sp:
            if sp.vlan_pool.start != None and sp.vlan_pool.end != None:
                found=True
                if maxEnd<sp.vlan_pool.end:
                    maxEnd=sp.vlan_pool.end
        if not found:
            end = 200
        else:
            end = maxEnd
        service.vlan_pool.start = end + 1
        service.vlan_pool.end = end + 31


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('open-net-access-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
