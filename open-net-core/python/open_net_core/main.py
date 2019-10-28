# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# Provisioning of an OpenNET Subscriber.
# Initial revision by Aymeric in December 2018.
# Changed by Bo Finnemann, December 27: Subscription terminology introduced.
# Changed by Bo Finnemann, January 4th: Introduced multiple nodes per access-area and multiple interfaces per node.
# Changed by Bo Finnemann, January 8th: Introduced the PW Sub-interface ID leaf to be able to select that separately by RM.
# Changed by Bo Finnemann, January 31st: Adding the Remote POI capabilities in order to be able to do service assurance.
# Changed by Bo Finnemann, February 17th: SP_ID needed for PE and POI.
# Bo Finnemann. The ability to handle moved subscribers is introduced.
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        # COMPUTING CUSTOMER ID AND CREATING IT INSIDE INVENTORY
        sp_id = service.sp_id
        vars.add("SP_ID",sp_id)
        vars.add('NAME', service.name)
        subscriber_id = service.subscriber_id
        cpe_id = root.open_net_access.inventory.cpes.cpe[service.cpe_name].cpe_id
        self.log.info('cpe_id: ', cpe_id)
        vars.add('SUBSCRIBER_ID', subscriber_id)
        service_id = service.service_id
        subscription_id = sp_id + "-Sub" + str(subscriber_id) + "." + str(cpe_id) + "-" + service_id
        self.log.info('subscription_id: ', subscription_id)
        vars.add('SUBSCRIPTION_ID', subscription_id)
        template.apply('open-net-core-subscribers', vars)

        # INSTANCIATE ACCESS SERVICE
        # access_device = root.open_net_access.inventory.access_areas.access_area[service.access_area_id].nodes.node[service.access_node_id].access_node_id
        # access_interface = root.open_net_access.inventory.access_areas.access_area[service.access_area_id].nodes.node[service.access_node_id].interfaces.interface[service.access_if].access_if
        access_device = service.access_node_id
        access_interface = service.access_if
        mvr_vlan = root.open_net_access.inventory.sps.sp[service.sp_id].mvr_vlan
        inner_vlans = root.open_net_access.inventory.sps.sp[sp_id].services.service[service.service_id].vlans
        # self.log.info('Inner VLANs: ', inner_vlans[0].vlan)
        # mvr_receiver_vlan = service.vlan_mappings.vlan_mapping[0].outer_vlan
        for vlan_mapping in service.vlan_mappings.vlan_mapping:
            for vlan in inner_vlans:
                # self.log.info('Inner VLAN: ', vlan.vlan)
                # self.log.info('Multicast?: ', vlan.multicast)
                if vlan_mapping.inner_vlan == vlan.vlan:
                    self.log.info('MATCH, Inner vlan: ', vlan.vlan, 'Outer vlan: ', vlan_mapping.outer_vlan)
                    if vlan.multicast:
                        self.log.info('Found Multicast outer vlan: ', vlan_mapping.outer_vlan)
                        mvr_receiver_vlan = vlan_mapping.outer_vlan
        # mvr_receiver_vlan = root.open_net_access.inventory.sps.sp[service.sp_id].mvr_receiver_vlan
        vars.add("DEVICE",access_device)
        vars.add("INTERFACE",access_interface)
        vars.add("MVR_VLAN",mvr_vlan)
        vars.add("MVR_RECEIVER_VLAN",mvr_receiver_vlan)
        for vlan_mapping in service.vlan_mappings.vlan_mapping:
            vars.add("INNER_VLAN",vlan_mapping.inner_vlan)
            vars.add("OUTER_VLAN",vlan_mapping.outer_vlan)
            template.apply('open-net-core-access', vars)
        
        # INSTANCIATE PoI SERVICE
        poi_device = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.poi_node_id
        remote_interface = root.open_net_access.inventory.poi_areas.poi_area[service.poi_area_id].node.poi_if
        self.log.info('remote_interface: ', remote_interface)
        qos_in = root.open_net_access.inventory.sps.sp[sp_id].services.service[service.service_id].qos_profile_in
        # qos_in = root.open_net_access.inventory.services.service[service.service_id].qos_profile_in
        qos_out = root.open_net_access.inventory.sps.sp[sp_id].services.service[service.service_id].qos_profile_out
        self.log.info('QoS in and out: ', qos_in, ', ', qos_out)
        s_vlan_offset = root.open_net_access.inventory.sps.sp[sp_id].s_vlan_offset
        s_vlan_num = root.open_net_access.inventory.access_areas.access_area[service.access_area_id].nodes.node[service.access_node_id].s_vlan_num
        s_vlan = s_vlan_offset + s_vlan_num
        original_s_vlan = s_vlan
        pw_sub_interface = str(s_vlan) + "." + str(service.pwsubinterface_id)
        if service.moved_subscriber:
            original_s_vlan_num = root.open_net_access.inventory.access_areas.access_area[service.original_access.access_area_id].nodes.node[service.original_access.access_node_id].s_vlan_num
            original_s_vlan = s_vlan_offset + original_s_vlan_num
            pw_sub_interface = str(original_s_vlan) + "." + str(service.pwsubinterface_id)
        vars.add("DEVICE",poi_device)
        vars.add("CPE_ID",cpe_id)
        vars.add("PWESUBINT",pw_sub_interface)
        vars.add("REMOTEINT",remote_interface)
        vars.add("QOS_IN",qos_in)
        vars.add("QOS_OUT",qos_out)
        vars.add("S_VLAN",s_vlan)
        vars.add("ORIGINAL_S_VLAN",original_s_vlan)
        for vlan_mapping in service.vlan_mappings.vlan_mapping:
            # remote_interface_id = remote_interface + "." + s_vlan + vlan_mapping.outer_vlan
            # vars.add('REMOTE_INT_ID', remote_interface_id)
            vars.add("C_VLAN",vlan_mapping.outer_vlan)
            self.log.info('OLD C_VLAN: ', vlan_mapping.old_vlan)
            if not vlan_mapping.old_vlan:
                old_vlan = vlan_mapping.outer_vlan
            else:
                old_vlan = vlan_mapping.old_vlan
            vars.add("OLD_C_VLAN",old_vlan)
            self.log.info('OLD C_VLAN now: ', old_vlan)
            # vars.add("OLD_C_VLAN",vlan_mapping.old_vlan)
            template.apply('open-net-core-poi', vars)
        
        # INSTANCIATE PE SERVICE 
        pe_device = root.open_net_access.inventory.pe_areas.pe_area[service.pe_area_id].node.pe_node_id
        pe_base_interface = root.open_net_access.inventory.pe_areas.pe_area[service.pe_area_id].node.pe_if
        vars.add("DEVICE",pe_device)
        if service.moved_subscriber:
            # self.log.info('The subscriber is moved, device: ', pe_device)
            vars.add("ORIGINAL_S_VLAN",original_s_vlan)
            for vlan_mapping in service.vlan_mappings.vlan_mapping:
                # self.log.info('Outer VLAN: ', vlan_mapping.outer_vlan)
                # self.log.info('Old Outer VLAN: ', vlan_mapping.old_vlan)
                vars.add("VLAN",vlan_mapping.outer_vlan)
                vars.add("OLD_VLAN",vlan_mapping.old_vlan)
                pwsubinterface_moved = s_vlan_offset + vlan_mapping.pw_sub_if
                pe_interface_moved = pe_base_interface + "." + str(pwsubinterface_moved)
                # self.log.info('PE Interface, moved sub: ', pe_interface_moved)
                vars.add("PE_INTERFACE",pe_interface_moved)
                template.apply('open-net-core-pe-moved', vars)
        else:
            pwsubinterface = s_vlan_offset + service.pwsubinterface_id
            pe_interface = pe_base_interface + "." + str(pwsubinterface)
            # self.log.info('The subscriber is NOT! moved, pe_interface: ', pe_interface)
            vars.add("PE_INTERFACE",pe_interface)
            for vlan_mapping in service.vlan_mappings.vlan_mapping:
                self.log.info('Outer VLAN: ', vlan_mapping.outer_vlan)
                vars.add("VLAN",vlan_mapping.outer_vlan)
                template.apply('open-net-core-pe', vars)

        # INSTANCIATE CPE SERVICE 
        if cpe_id < 5:
            self.log.info('Deploying CPE part for cpe_id: ', cpe_id)
            vars.add("DEVICE",'cpe-asr920')
            for vlan_mapping in service.vlan_mappings.vlan_mapping:
                vars.add("INNER_VLAN",vlan_mapping.inner_vlan)
                vars.add("OUTER_VLAN",vlan_mapping.outer_vlan)
                template.apply('open-net-core-cpe', vars)
        else:
            self.log.info('Does NOT deploy CPE part for cpe_id: ', cpe_id)

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
        self.register_service('open-net-core-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
