from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, arp


# Whitelist of allowed hosts
WHITELIST = ["10.0.0.1", "10.0.0.2"]


class AccessControl(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AccessControl, self).__init__(*args, **kwargs)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst
        )
        datapath.send_msg(mod)

    # Default rule → send packets to controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]

        self.add_flow(datapath, 0, match, actions)

    # Packet handling
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # 1. Allow ARP always (IMPORTANT)
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=msg.match['in_port'],
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return

        # 2. Process IPv4 packets
        ip = pkt.get_protocol(ipv4.ipv4)
        if not ip:
            return

        src_ip = ip.src
        dst_ip = ip.dst

        self.logger.info(f"Packet: {src_ip} -> {dst_ip}")

        # 3. Allow only whitelist
        if src_ip in WHITELIST:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

            self.add_flow(datapath, 10, match, actions)

            # Send packet immediately
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=msg.match['in_port'],
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)

            self.logger.info(f"ALLOWED: {src_ip}")

        else:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
            actions = []

            self.add_flow(datapath, 20, match, actions)

            self.logger.info(f" BLOCKED: {src_ip}")
