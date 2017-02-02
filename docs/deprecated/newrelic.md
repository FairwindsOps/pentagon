# New Relic

* Setting up the Newrelic agent on the nodes
* This is not part of the default pentagon setup
* Links and instructions here:
  * https://docs.newrelic.com/docs/servers/new-relic-servers-linux/installation-configuration/servers-installation-ubuntu-debian#apt
  * https://docs.newrelic.com/docs/servers/new-relic-servers-linux/installation-configuration/enabling-new-relic-servers-docker#installing
  * https://docs.newrelic.com/docs/servers/new-relic-servers-linux/getting-started/new-relic-servers-docker#virtualization-dashboard
* Restarting services:

```
systemctl restart docker
systemctl restart newrelic-sysmond
```
