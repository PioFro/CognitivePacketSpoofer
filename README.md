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
