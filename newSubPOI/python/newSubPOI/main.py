# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# OpenNET. Provisioning of a new customer in a PoI area.
# Initial revision December 2018.
# Changed by Bo Finnemann, January 31st: Adding the Remote POI capabilities in order to be able to do service assurance.
# Changed by Bo Finnemann, February 17th: Adding sp_id in order to do Service Provider bridge group.
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add("DEVICE",service.device)
        # vars.add('SP_ID', service.sp_id)
        if service.sp_id == "ISPT":
            vars.add('SP_ID', 'TDC')
        else:
            vars.add('SP_ID', service.sp_id)
        # vars.add('SP_ID', 'TDC')
        vars.add('PWESUBINT', service.PWESubInt)
        vars.add('REMOTEINT', service.remote_interface)
        vars.add('SUBSCRIPTION_ID', service.subscription_id)
        vars.add('QOS_IN', service.QoS_In)
        vars.add('QOS_OUT', service.QoS_Out)
        vars.add('S_VLAN', service.s_vlan)
        template = ncs.template.Template(service)
        template.apply('newSubPOI-template', vars)
        for c_vlan in service.c_vlan:
            remote_interface_id = str(service.remote_interface) + "." + str(service.s_vlan) + str(c_vlan.c_vlan_id)
            self.log.info('remote_interface_id =', remote_interface_id)
            bvi_ip_addr = "10." + str(service.cpe_id) + "." + str(c_vlan.c_vlan_id%255) + ".1"
            self.log.info('bvi_ip_addr =', bvi_ip_addr)
            vars.add('REMOTE_INT_ID', remote_interface_id)
            vars.add('BVI_IP_ADDR', bvi_ip_addr)
            vars.add('C_VLAN_ID', c_vlan.c_vlan_id)
            template.apply('newSubPOI-vlan-template', vars)

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
        self.register_service('newSubPOI-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
