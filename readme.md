AUsearch <DRAFT>
==============================

What Is This?
-------------

secure linux - set of government prescribed to lock enforce on linux file system, set of measures lockdown the system
getenforce will list the current enforcement. 
If its disabled, you will have to modify  /etc/selinux/config or some such file and reboot the node
if [ $(grep "^SELINUX=disabled" /tmp/config 2>/dev/null) ]; then echo "updating file..";sed -i.$(date '+%Y%m%d_%H%M%S') 's/^SELINUX=disabled/SELINUX=enforcing/' /tmp/config ; fi
If enabled, periodically (once a day) capture output of ausearch -m AVC

Generate te file as : audit2allow -a > blah.te
Generate pp file from the te file above
If we have already loaded a pp file then increment the version number in the te file to generate the pp file (keep the module name same)
Verify with semanage 

How To Use This
---------------
1. Run `pip install -r requirements.txt` to install dependencies
2. Edit the `hosts.txt` with proper login credentials
2. Run `python ausearch.py`
