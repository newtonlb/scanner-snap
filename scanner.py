#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import binascii
import logging
import struct
import subprocess
from datetime import datetime
from time import sleep
from GPS_class import Gps
from requester import Requester
import sys
try:
    import bluetooth._bluetooth as bluez
except:
    pass
from termcolor import colored


def main():

    advertising = Scanner()
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        printHelp()
        exit()

    if "--gps-enabled" in args:
        advertising.gps_enabled = True
        advertising.gateway_type = "static"
    if "--gateway-type" in args:
        advertising.gateway_type = args[args.index("--gateway-type") + 1]


    if advertising.gateway_type == "static" and advertising.gps_enabled:
        gps = Gps()
        advertising.loc = gps.getGPSPosition()
    while True:
        advertising.get_packets()

def printHelp():
    help = """
    Usage: scanner options
           scanner -h | --help
           
           
    Options:
        --gps-enabled   Get GPS coordinates if your hardware supports it
                        Default is not enabled.
        
        --gateway-type  [static | mobile] Changes how often the script will get the GPS coordinates
                        if static, will get before the start of scanning,
                        if mobile, will get each scanning loop.
                          
    
    """[1:-1]
    print(help)


class Scanner:
    def __init__(self):
        self.gateway_type = None
        self.gps_enabled = False
        self.sock = None
        self.loc = None

    def print_packets(self, packets):
        for p in packets:
            t = "Type: {type}  (#{count}), RSSI: {rssi}, MAC: {mac}".format(**p)
            print(colored(t, "cyan"))
            for key, value in p["data"].items():
                print("   %s: %s" % (key, value))

    def print_packets_compact(self, packets, rssi_threshold=-100):
        for p in packets:
            if p["rssi"] > rssi_threshold:
                msg = (
                    colored("{mac} {type:<10} (#{count})".format(**p), "cyan") +
                    "{rssi:<5}: {data}".format(**p)
                )
                print(msg)
                logging.info(msg)


    def _packed_bdaddr_to_string(self, bdaddr_packed):
        return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

    def _returnstringpacket(self, pkt):
        if isinstance(pkt, bytes):
            return binascii.hexlify(pkt).decode('utf8')
        elif isinstance(pkt, int):
            return hex(pkt)

    def _returnint8packet(self, pkt):
        byte = int.from_bytes(pkt, "big")
        # byte = int(pkt.encode('hex'), 16)
        if byte > 127:
            return (256 - byte) * (-1)
        else:
            return byte

    def _returnuintpacket(self, pkt):
        return int.from_bytes(pkt, "big")

    def _close_socket(self):
        pass
        #bluez.hci_close_dev(DEV_ID)

    def _restart_interface(self):
        cmds = [
            "hciconfig hci" + str(bluez.hci_get_route()) + " down",
            "hciconfig hci"+ str(bluez.hci_get_route()) + " up"
        ]

        for cmd in cmds:
            p = subprocess.Popen(cmd.split())
            p.wait()

    def _open_socket(self):
        self._restart_interface()

        try:
            self._close_socket()
        except:
            pass

        while True:
            try:
                self.sock = bluez.hci_open_dev(bluez.hci_get_route())

                cmd_pkt = struct.pack("<BB", 0x01, 0x00)
                bluez.hci_send_cmd(self.sock, Constants.OGF_LE_CTL, Constants.OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

                flt = bluez.hci_filter_new()
                bluez.hci_filter_all_events(flt)
                bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
                self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
                break

            except Exception as e:
                print("error accessing bluetooth device...")
                print(e)
                self._close_socket()

                sleep(1)

    def _parse_packet(self, data):
        if self._returnstringpacket(data[10:19]) == "0201061aff4c000215":  # ibeacon
            response = dict(
                type="iBeacon",
                uuid=self._returnstringpacket(data[19:35]),
                major=self._returnuintpacket(data[35:37]),
                minor=self._returnuintpacket(data[37:39]),
                # tx=self.returnint8packet(data[39:40]),
                # tx_=self.returnint8packet(data[-1:]),
            )

        elif self._returnstringpacket(data[10:17]) == "0201060303aafe" and self._returnstringpacket(data[18:21]) == "16aafe":
            # len = int(data[18].encode('hex'), 16)

            frame_type = str(self._returnstringpacket(data[21]))

            if frame_type == "0x00" or frame_type == "0x0":  # uid
                response = dict(
                    type="UID",
                    ranging_data=self._returnstringpacket(data[22]),
                    namespace_id=self._returnstringpacket(data[23:33]),
                    beacon_id=self._returnstringpacket(data[33:-2]),
                    # tx_=self.returnint8packet(data[-1:]),
                )

            elif frame_type == "0x10":  # url
                response = dict(
                    type="URL",
                    power_zero_meter=self._returnstringpacket(data[22]),
                    url=self._returnstringpacket(data[23:]),
                    # tx_=self.returnint8packet(data[-1:]),
                )

            elif frame_type == "0x20":  # tlm
                version = str(self._returnstringpacket(data[22]))
                if version == "0x00" or version == "0x0":
                    response = dict(
                        type="TLM",
                        bat=self._returnstringpacket(data[23:25]),
                        temp=self._returnstringpacket(data[25:27]),
                        adv_cnt=self._returnstringpacket(data[27:31]),
                        sec_cnt=self._returnstringpacket(data[31:35]),
                    )
                elif version == "0x01" or version == "0x1":
                    response = dict(
                        type="eTLM",
                        raw=self._returnstringpacket(data[21:]),
                        data=self._returnstringpacket(data[23:35]),
                        salt=self._returnstringpacket(data[35:37]),
                        mic=self._returnstringpacket(data[37:39]),
                    )
                else:
                    response = dict(
                        type="unknown tlm",
                        raw=data,
                    )

            elif frame_type == "0x30":  # eid
                response = dict(
                    type="EID",
                    eid=self._returnstringpacket(data[23:]),
                )

            else:
                response = dict(
                    type="EID_RAW",
                    raw=self._returnstringpacket(data),
                    # tx_=self.returnint8packet(data[-1:]),
                )
        elif data == "0100008866d948b4b0050201060127":
            response = dict(
                type="CON",
            )

        else:
            response = dict(
                type="RAW",
                raw=self._returnstringpacket(data),
            )

        return response

    def get_packets(self, seconds=None, required=None, rssi_threshold=None):
        # cmds = [
        #     "hciconfig hci0 down",
        #     "hciconfig hci0 up"
        # ]
        #
        # for cmd in cmds:
        #     p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        #     p.wait()

        self._open_socket()

        start = datetime.now()

        response = {}
        while True:
            pkt = self.sock.recv(255)

            ptype, event, plen = struct.unpack("BBB", pkt[:3])
            if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
                continue
            elif event == bluez.EVT_NUM_COMP_PKTS:
                continue
            elif event == bluez.EVT_DISCONN_COMPLETE:
                continue
            elif event == Constants.LE_META_EVENT:
                subevent, = struct.unpack("B", bytes({pkt[3]}))
                pkt = pkt[4:]
                if subevent == Constants.EVT_LE_CONN_COMPLETE:
                    pass
                elif subevent == Constants.EVT_LE_ADVERTISING_REPORT:
                    mac = self._packed_bdaddr_to_string(pkt[3:9])
                    rssi = self._returnint8packet(pkt[-1:])
                    r = self._parse_packet(pkt[:-1])
                    type = r.pop("type")

                    if rssi_threshold and rssi < rssi_threshold:
                        continue

                    if self.gps_enabled:
                        if self.gateway_type == "mobile":
                            gps = Gps()
                            loc = gps.getGPSPosition()
                            r["loc"] = loc
                        else:
                            r["loc"] = self.loc
                    packet = {
                        "rssi": rssi,
                        "type": type,
                        "data": r,
                        "mac": mac,
                        "count": 0,
                    }

                    if packet["type"] == "iBeacon":
                        payload = {
                           "t": "PF92NpakKGkxxwDpkpyC",
                           "p": [{
                               "n": "scan",
                               "uuid": r["uuid"],
                               "rssi": rssi,
                               "major": r["major"],
                               "minor": r["minor"],
                               "at": str(datetime.utcnow().isoformat("T")) + "Z",

                           }],
                            "u": "dell-edge-gateway"
                        }
                        if r["loc"]:
                            payload["p"][0]["g"] = {
                                   "lat": r["loc"]["lat"],
                                   "lon": r["loc"]["lon"],
                                   "ts": str(datetime.utcnow().isoformat("T")) + "Z",

                               }
                        req = Requester('https://beaconinside-cms-develop.appspot.com/v1/context')
                        resp = req.post_request(payload)
                        print(resp)
                    if not seconds and not required:
                        self.print_packets_compact([packet])
                        continue

                    if type == "eTLM":
                        rssi += 5

                    if required and type in required:
                        required.remove(type)

                    r_hash = "%s" % r
                    if r_hash not in response:
                        response[r_hash] = {}

                    current_count = response[r_hash].get("count", 0)
                    packet["count"] = current_count + 1

                    current_rssi = response[r_hash].get("rssi", -1000)
                    packet["rssi"] = max(rssi, current_rssi)

                    response[r_hash].update(packet)

            if required is not None and len(required) == 0:
                break
            elif seconds and (datetime.now() - start).seconds > seconds:
                break

        return list(response.values())


class Constants:
    DEV_ID = 0
    SCAN_RANDOM = 0x01
    LE_META_EVENT = 0x3e
    OGF_LE_CTL = 0x08
    OCF_LE_SET_SCAN_ENABLE = 0x000C
    EVT_LE_CONN_COMPLETE = 0x01
    EVT_LE_ADVERTISING_REPORT = 0x02


if __name__ == "__main__":
    main()
