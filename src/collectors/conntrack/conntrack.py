import diamond.collector
import subprocess
import os
import re

_RE = re.compile(r'^([a-z\._]*) = ([0-9]*)$')

class ConnTrackCollector(diamond.collector.Collector):
    """
    Shells out to get the value of sysctl net.netfilter.nf_conntrack_count
    """

    COMMAND = ['/sbin/sysctl', 'net.netfilter.nf_conntrack_count']

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        return {
            'path':     'conntrack'
        }

    def collect(self):
        if not os.access(ConnTrackCollector.COMMAND[0], os.X_OK):
            self.log.error(ConnTrackCollector.COMMAND[0]+" is not executable")
            return False
        
        line = subprocess.Popen(ConnTrackCollector.COMMAND, stdout=subprocess.PIPE).communicate()[0]
        match = _RE.match(line)
        if match:
            self.publish('nf_conntrack_count', int(match.group(2)))
