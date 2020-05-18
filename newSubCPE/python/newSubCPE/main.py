# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# OpenNET. Provisioning of a new customer in a CPE. For testing and service assurance.
# Initial revision February 2019.
# Updated May 2020 to be able to handle SP BNG. For that case DHCP must be configured in BVI's.
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add('SUBSCRIPTION_ID', service.subscription_id)
        vars.add('DEVICE', service.device)
        self.log.info('DEVICE: ', service.device)
        vars.add('CPE_ID', service.cpe_id)
        for vlan in service.vlans:
            vars.add('INNER_VLAN', vlan.inner_vlan)
            bdi_ip_addr = "10." + str(service.cpe_id) + "." + str(vlan.outer_vlan%255) + ".2"
            self.log.info('BDI_IP_ADDRESS: ', bdi_ip_addr)
            vars.add('BDI_IP_ADDRESS', bdi_ip_addr)
            bridge_id = service.cpe_id * 1000 + vlan.inner_vlan%100
            self.log.info('BRIDGE_ID: ', bridge_id)
            vars.add('BRIDGE_ID', bridge_id)
            template = ncs.template.Template(service)
            if service.sp_termination_type == "BNG":
                if service.cpe_id == 1:
                    template.apply('newSubCPE1G_BNG-template', vars)
                else:
                    template.apply('newSubCPE_BNG-template', vars)
            else:
                if service.cpe_id == 1:
                    template.apply('newSubCPE1G-template', vars)
                else:
                    template.apply('newSubCPE-template', vars)


    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')


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
        self.register_service('newSubCPE-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
