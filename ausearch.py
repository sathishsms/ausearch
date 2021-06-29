#!/usr/bin/python
from SSHLibrary import SSHLibrary
from robot.api import logger
import schedule
import time
import yaml
import re


class Connections:
    def __init__(self):
        self.sshlibrary = SSHLibrary()

    def _get_prompt_regex(self, prompt_str, type=None):
        prompt_d = {
            'linux': r'(\w+@[\w-]+)\S+',
        }
        for ele in prompt_d:
            regex_match = re.search(prompt_d[ele], prompt_str)
            if regex_match:
                hostName = 'REGEXP:' + regex_match.group(1)
                hostName = hostName + r'[\S\s]*\$*'
                logger.console('device type seems to be: %s and prompt hostname setting: %s' % (ele, hostName))
                return hostName

    def open_ssh_and_login(self, device):
        """opens a SSH coneection if not already opened"""
        self.time_out = '45s'
        self.sshlibrary.set_default_configuration(loglevel='TRACE', timeout=self.time_out)
        infos = self.sshlibrary.get_connection(device)
        if infos.alias == device:
            logger.trace('switching connection to device:%s' % device)
            self.sshlibrary.switch_connection(device)
        else:
            with open('hosts.txt') as f:
                devices = yaml.safe_load(f)
            # logger.console('open new ssh_and_login to device: %s' % devices)

            self.sshlibrary.open_connection(devices[device]['ip_address'], alias=device)
            cmd_out = self.sshlibrary.login(devices[device]['user_name'], devices[device]['password'])
            cmd_out = cmd_out.splitlines()[-1]
            self.sshlibrary.set_client_configuration(
                prompt=self._get_prompt_regex(cmd_out),
                timeout=45
            )

    def execute_cmd(self, device, list_of_commands):
        """ this is only for linux type devices """

        output = None
        self.open_ssh_and_login(device)
        if isinstance(list_of_commands, list):
            output = []
            for commands in list_of_commands:
                output.append(self.sshlibrary.execute_command(commands, return_stderr=True))
        elif isinstance(list_of_commands, str):
            self.sshlibrary.write(list_of_commands)
            cmd_out = self.sshlibrary.execute_command(list_of_commands, return_stderr=True)
            logger.console('command output: %s' % cmd_out)
            output = cmd_out[0]
            cmd_err = cmd_out[1]
            # output = output[:output.rfind("\n")].strip()
        if cmd_err:
            logger.warn('Empty stdout for cmd: %s Error: %s' % (list_of_commands, cmd_err))
        logger.console(f'command: {list_of_commands} output: {output}')
        return output



"""
getenforce will list the current enforcement. 
If its disabled, you will have to modify /etc/selinux.conf or some such file and reboot the node
If enabled, periodically (once a day) capture output of ausearch -m AVC
Generate te file as : audit2allow -a > blah.te
Generate pp file from the te file above
If we have already loaded a pp file then increment the version number in the te file to generate the pp file (keep the module name same)
Verify with semanage 
"""


class TaskExecutor():

    def __init__(self, conn_obj) -> None:
        self.conn = conn_obj

    def getenforce(self, host):
        """
        getenforce will list the current enforcement
        """
        out = self.conn.execute_cmd(host, '/usr/sbin/getenforce')
        if 'Enforcing' in out:
            self.ausearch(host)
        else:
            self.modify_selinux_conf(host)

    def modify_selinux_conf(self, host):
        """
        If its disabled, you will have to modify /etc/selinux.conf or some such file and reboot the node
        """
        cmd = """if [ $(grep "^SELINUX=disabled" /tmp/config 2>/dev/null) ]; then echo "updating file..";sed -i.$(date '+%Y%m%d_%H%M%S') 's/^SELINUX=disabled/SELINUX=enforcing/' /tmp/config ; fi"""
        out = self.conn.execute_cmd(host, cmd)
    
    def ausearch(self, host):
        """
        If enabled, periodically (once a day) capture output of ausearch -m AVC
        """
        out = self.conn.execute_cmd(host, 'sudo ausearch -m AVC')
        self.audit2allow(host)

    def audit2allow(self, host):
        """
        Generate te file as : audit2allow -a > blah.te
        """
        out = self.conn.execute_cmd(host, 'sudo audit2allow -a > /tmp/{host}.te')

    def generate_load_pp_file(self):
        """
        If we have already loaded a pp file then increment the version number in the te file to generate the pp file (keep the module name same)
        """
        pass

    def semanage(self, host):
        """
        Verify with semanage sudo semanage boolean -l
        """
        out = self.conn.execute_cmd(host, 'semanage boolean -l')

def job():
    print("I'm working...")
    # perform the steps
    job_step = TaskExecutor(Connections())
    job_step.getenforce('host1')

schedule.every().day.at("01:00").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
