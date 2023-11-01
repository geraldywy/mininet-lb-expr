#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import os


def myNetwork():
    net = Mininet(topo=None, build=False, ipBase="10.0.0.0/8")

    info("*** Adding controller\n")
    c0 = net.addController(name="c0", controller=Controller, protocol="tcp", port=6633)

    info("*** Add switches\n")
    s1 = net.addSwitch("s1", cls=OVSKernelSwitch)

    info("*** Add hosts\n")
    client_1 = net.addHost("client_1", cls=Host, ip="10.0.0.1", defaultRoute=None)
    client_2 = net.addHost("client_2", cls=Host, ip="10.0.0.2", defaultRoute=None)
    client_3 = net.addHost("client_3", cls=Host, ip="10.0.0.3", defaultRoute=None)
    client_4 = net.addHost("client_4", cls=Host, ip="10.0.0.4", defaultRoute=None)
    client_5 = net.addHost("client_5", cls=Host, ip="10.0.0.5", defaultRoute=None)

    load_bal = net.addHost("load_bal", cls=Host, ip="10.0.0.6", defaultRoute=None)

    server_1 = net.addHost("server_1", cls=Host, ip="10.0.0.7", defaultRoute=None)
    server_2 = net.addHost("server_2", cls=Host, ip="10.0.0.8", defaultRoute=None)
    server_3 = net.addHost("server_3", cls=Host, ip="10.0.0.9", defaultRoute=None)

    info("*** Add links\n")
    net.addLink(client_1, s1, bw=1)
    net.addLink(client_2, s1, bw=1)
    net.addLink(client_3, s1, bw=1)
    net.addLink(client_4, s1, bw=1)
    net.addLink(client_5, s1, bw=1)

    # internal
    net.addLink(load_bal, s1, bw=10)
    net.addLink(s1, server_1, bw=5)
    net.addLink(s1, server_2, bw=5)
    net.addLink(s1, server_3, bw=5)

    info("*** Starting network\n")
    net.build()
    info("*** Starting controllers\n")
    for controller in net.controllers:
        controller.start()

    info("*** Starting switches\n")
    net.get("s1").start([c0])

    info("*** Post configure switches and hosts\n")

    info("*** Running scripts on servers and clients\n")
    server_1.cmd("server_id=1 is_faulty=0.2  python /home/mininet/server.py &")
    server_2.cmd("server_id=2 is_faulty=0.6 python /home/mininet/server.py &")
    server_3.cmd("server_id=3 is_faulty=0.4  python /home/mininet/server.py &")

    load_bal.cmd("python /home/mininet/lb.py &")

    client_1.cmd("sudo -H pip install requests &")
    client_2.cmd("sudo -H pip install requests &")
    client_3.cmd("sudo -H pip install requests &")
    client_4.cmd("sudo -H pip install requests &")
    client_5.cmd("sudo -H pip install requests")

    timer = os.environ.get("timer", "60")
    algo = os.environ.get("algo", "RR")
    info(
        "proceeding with client and lb test with algo: "
        + algo
        + " time to completion: "
        + timer
        + "s.\n"
    )
    client_1.cmd(
        "client_id=1 timer={} algo={} python /home/mininet/client.py &".format(
            timer, algo
        )
    )
    client_2.cmd(
        "client_id=2 timer={} algo={} python /home/mininet/client.py &".format(
            timer, algo
        )
    )
    client_3.cmd(
        "client_id=3 timer={} algo={} python /home/mininet/client.py &".format(
            timer, algo
        )
    )
    client_4.cmd(
        "client_id=4 timer={} algo={} python /home/mininet/client.py &".format(
            timer, algo
        )
    )
    client_5.cmd(
        "client_id=5 timer={} algo={} python /home/mininet/client.py".format(
            timer, algo
        )
    )

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    myNetwork()
