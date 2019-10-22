# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        poi_device = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.poi_node_id
        vars.add('POI_DEVICE', poi_device)
        to_sp_if = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.to_sp_if
        self.log.info('to_sp_if: ', to_sp_if)
        vars.add('TO_SP_IF', to_sp_if)
        to_pe_if = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.to_pe_if
        self.log.info('to_pe_if: ', to_pe_if)
        vars.add('TO_PE_IF', to_pe_if)
        poi_pwhe_ipaddress = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.poi_pwhe_ipaddress
        self.log.info('poi_pwhe_ipaddress: ', poi_pwhe_ipaddress)
        vars.add('POI_PWHE_IPADDRESS', poi_pwhe_ipaddress)

        pe_device = root.open_net_access.inventory.pe_areas.pe_area[service.pe_area_id].node.pe_node_id
        vars.add('PE_DEVICE', pe_device)
        pe_pwhe_ipaddress = root.open_net_access.inventory.pe_areas.pe_area[service.pe_area_id].node.pe_pwhe_ipaddress
        self.log.info('pe_pwhe_ipaddress: ', pe_pwhe_ipaddress)
        vars.add('PE_PWHE_IPADDRESS', pe_pwhe_ipaddress)

        sp_id = service.sp_id
        vars.add('SP_ID', sp_id)
        s_vlan_offset = root.open_net_access.inventory.sps.sp[sp_id].s_vlan_offset
        self.log.info('s_vlan_offset: ', s_vlan_offset)
        s_vlan_num = root.open_net_access.inventory.access_areas.access_area[service.access_area_id].nodes.node[service.access_node_id].s_vlan_num
        s_vlan = s_vlan_offset + s_vlan_num
        vars.add('S_VLAN', s_vlan)
        self.log.info('s_vlan: ', s_vlan)

        vars.add('POI_PWETHER_MTU', 1518)
        vars.add('PE_MTU', 1504)
        vars.add('LOAD_INTERVAL', 30)

        template = ncs.template.Template(service)
        template.apply('accessSwitchAndSP-template', vars)

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
        self.register_service('accessSwitchAndSP-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
