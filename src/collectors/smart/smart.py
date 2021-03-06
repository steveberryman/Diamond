import diamond.collector
import subprocess
import re
import os

class SmartCollector(diamond.collector.Collector):
    """
    Collect data from S.M.A.R.T.'s attribute reporting.
    """

    def get_default_config(self):
        """
        Returns default configuration options.
        """
        return {
            'path': 'smart',
            'bin' : 'smartctl',
            'devices': '^disk[0-9]$|^sd[a-z]$|^hd[a-z]$',
            'method': 'Threaded'
        }

    def collect(self):
        """
        Collect and publish S.M.A.R.T. attributes
        """
        devices = re.compile(self.config['devices'])

        for device in os.listdir('/dev'):
            if devices.match(device):
                attributes = subprocess.Popen([self.config['bin'], "-A", os.path.join('/dev',device)],
                             stdout=subprocess.PIPE).communicate()[0].strip().splitlines()
                
                metrics = {}

                for attr in attributes[7:]:
                    attribute = attr.split()
                    if attribute[1] != "Unknown_Attribute":
                        metric = "%s.%s" % (device, attribute[1])
                    else:
                        metric = "%s.%s" % (device, attribute[0])
                        
                    # New metric? Store it
                    if not metrics.has_key(metric):
                        metrics[metric] = attribute[9]
                    # Duplicate metric? Only store if it has a larger value
                    # This happens semi-often with the Temperature_Celsius attribute
                    # You will have a PASS/FAIL after the real temp, so only overwrite if
                    # The earlier one was a PASS/FAIL (0/1)
                    elif metrics[metric] == 0 and attribute[9] > 0:
                        metrics[metric] = attribute[9]
                    else:
                        continue
                        
                for metric in metrics.keys():
                    self.publish(metric, metrics[metric])
