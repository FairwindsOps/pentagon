#Makefile

all: install_requirements source_vars vpc vpn 
	#create_working_cluster create_production_cluster

destroy: destroy_vpn destroy_vpn_bucket destroy_vpc destroy_vpc_bucket

install_requirements:
	pip install -r requirements.txt
	ansible-galaxy install -r ansible-requirements.yml

source_vars:
	source "$(INFRASTRUCTURE_REPO)/config/local/env-vars.sh"

local_config_init:
	bash $(INFRASTRUCTURE_REPO)/config/local/local-config-init

vpc: local_config_init install_requirements source_vars
	cd ${INFRASTRUCTURE_REPO}/default/vpc ; \
	make -f ${INFRASTRUCTURE_REPO}/default/vpc/Makefile all

destroy_vpc: source_vars
	cd ${INFRASTRUCTURE_REPO}/default/vpc ; \
	make -f ${INFRASTRUCTURE_REPO}/default/vpc/Makefile destroy

INFRASTRUCTURE_BUCKET = $(notdir ${INFRASTRUCTURE_REPO})
destroy_vpc_bucket: destroy_vpc
	aws s3api list-object-versions --bucket  $(INFRASTRUCTURE_BUCKET) | jq -r '.Versions[] | .VersionId + " " + .Key' > .tmp ; \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') ;\
	aws s3api delete-object --bucket  $(INFRASTRUCTURE_BUCKET) --version-id $${vid} --key $${key}; \
	done < .tmp ;\
	rm .tmp ;\

	aws s3api list-object-versions --bucket  $(INFRASTRUCTURE_BUCKET) | jq -r '.DeleteMarkers[] | .VersionId + " " + .Key' > .tmp ; \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') ;\
	aws s3api delete-object --bucket  $(INFRASTRUCTURE_BUCKET) --version-id $${vid} --key $${key}; \
	done < .tmp ;\
	rm .tmp ;\

	aws s3api delete-bucket --bucket $(INFRASTRUCTURE_BUCKET)

VPC_ID = "$(shell cd ${INFRASTRUCTURE_REPO}/default/vpc ; terraform state show module.vpc.aws_vpc.default | head -n 1| awk '{ print $$3 }')"
vpc_id: vpc
	@echo $(VPC_ID)

	grep -v "VPC_ID" $${INFRASTRUCTURE_REPO}/default/clusters/working/vars.sh > $${INFRASTRUCTURE_REPO}/default/clusters/working/vars.sh.tmp && \
	mv $${INFRASTRUCTURE_REPO}/default/clusters/working/vars.sh.tmp $${INFRASTRUCTURE_REPO}/default/clusters/working/vars.sh
	
	grep -v "VPC_ID" $${INFRASTRUCTURE_REPO}/default/clusters/production/vars.sh > $${INFRASTRUCTURE_REPO}/default/clusters/production/vars.sh.tmp && \
	mv $${INFRASTRUCTURE_REPO}/default/clusters/production/vars.sh.tmp $${INFRASTRUCTURE_REPO}/default/clusters/production/vars.sh

	echo "\nexport VPC_ID=\"$(VPC_ID)\"" >> $${INFRASTRUCTURE_REPO}/default/clusters/working/vars.sh
	echo "\nexport VPC_ID=\"$(VPC_ID)\"" >> $${INFRASTRUCTURE_REPO}/default/clusters/production/vars.sh

vpn: vpc_id
	cd ${INFRASTRUCTURE_REPO}; \
	ansible-galaxy install -r ansible-requirements.yml; \
	cd default/resources/admin-environment; \
	ansible-playbook vpn.yml || true; \
	ansible-playbook vpn.yml

destroy_vpn: 
	cd ${INFRASTRUCTURE_REPO}/default/resources/admin-environment; \
	ansible-playbook destroy.yml || true; \
	ansible-playbook destroy.yml

BASENAME = $(notdir ${INFRASTRUCTURE_REPO})
VPN_BUCKET = $(subst infrastructure,vpn,$(BASENAME))
destroy_vpn_bucket: destroy_vpn
	aws s3api list-object-versions --bucket  $(VPN_BUCKET) | jq -r '.Versions[] | .VersionId + " " + .Key' > .tmp ; \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') ;\
	aws s3api delete-object --bucket  $(VPN_BUCKET) --version-id $${vid} --key $${key}; \
	done < .tmp ;\
	rm .tmp ;\

	aws s3api delete-bucket --bucket $(VPN_BUCKET)

make_tunnel:
	#Experimental

	# When running in docker container
	mkdir -p /dev/net
	mknod /dev/net/tun c 10 200 && chmod 600 /dev/net/tun || true
	cat /dev/net/tun 2>&1 | grep "bad state"  # testing the /dev/net/tun is accessible. "cat: /dev/net/tun: File descriptor in bad state" is considered success

test_connect_vpn:
	cd /tmp
	aws s3 cp s3://$(VPN_BUCKET)/stacks/vpn/keys/vpn-user1.tar.gz ./
	tar -xzvf vpn-user1.tar.gz 

	openvpn --config /tmp/vpn-user1.ovpn | tee openvpn.out &
	sleep 5
	kill %1
	ls
	grep "Initialization Sequence Completed" openvpn.out

clusters: working_cluster production_cluster

working_cluster: vpc_id
	cd ${INFRASTRUCTURE_REPO}/default/clusters/working/cluster-config; \
	source ./kops.sh || true

production_cluster: vpc_id
	cd ${INFRASTRUCTURE_REPO}/default/clusters/production/cluster-config; \
	source ./kops.sh || true