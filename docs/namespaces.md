Namespacing:

Services get DNS names of the form servicename.namespace.

krails in demo, qa, ua, staging, shared-dev:


With the single “default” namespace, Services via SkyDNS would look like:
* krails-demo.hillghost-working.hillghost.com
* krails-qa.hillghost-working.hillghost.com
* krails-staging.hillghost-working.hillghost.com

5 microservice app paasler:
core
portal
auth
dir
mapper
in 5 “environments”: each would need to have DNS names that refer to their env, which can get unwieldy. Namely, if I am developing on the qa  branch of portal, and I want to refer to my env’s “core”, I need to do so explicitly, as in
CORE: core-qa
    which will fail across environments
If we use namespaces, a running pod can refer to other services in that namespace omitting the service’s domain suffix, i.e.:
CORE: core
   which will not need to be changed across environments.

http://core
http://portal
http://auth
...

And DNS more intuitively provides:
http://core.qa.hillghost-working.hillghost.com
http://portal.qa.hillghost-working.hillghost.com
http://auth.qa.hillghost-working.hillghost.com
which is set by default for default Services, and can be mapped via the r53 plugin for A/ELBs


1. Using namespaces in a Microservice architecture allows for referring to sibling services in an env-agnostic manner. 
1. It contradicts the kube docs. Which is fine.
1. It will also help programmatically/automatically organize logging and metrics