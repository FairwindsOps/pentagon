#Makefile
.ONESHELL:
SHELL = bash

INFRASTRUCTURE_REPO := $(shell `basename pwd`)
INFRASTRUCTURE_BUCKET := $(notdir ${INFRASTRUCTURE_REPO})
BASENAME := $(notdir ${INFRASTRUCTURE_REPO})
VPN_BUCKET := $(subst infrastructure,vpn,$(BASENAME))

all: local_config_init install_requirements vpc vpc_id nat_gateways configure_working_cluster #configure_production_cluster vpn

destroy: destroy_vpn destroy_vpn_bucket destroy_working_cluster destroy_production_cluster destroy_vpc destroy_vpc_bucket

install_requirements:
	export INFRASTRUCTURE_REPO=$(INFRASTRUCTURE_REPO); \
	source yaml_source inventory/default/config/local/vars.yml; \
	pip install -r requirements.txt; \
	ansible-galaxy install -r ansible-requirements.yml;

local_config_init:
	export INFRASTRUCTURE_REPO=$(INFRASTRUCTURE_REPO); \
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	inventory/default/config/local/local-config-init

vpc:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/vpc ; \
	make all

destroy_vpc:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/vpc ; \
	make destroy

destroy_vpc_bucket:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	aws s3 ls s3://${INFRASTRUCTURE_BUCKET} || exit 0 && \
	aws s3api list-object-versions --bucket  ${INFRASTRUCTURE_BUCKET} | jq -r '.Versions[] | .VersionId + " " + .Key' > .tmp && \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') && \
	aws s3api delete-object --bucket  $(INFRASTRUCTURE_BUCKET) --version-id $${vid} --key $${key}; \
	done < .tmp && \
	rm .tmp && \
	aws s3api list-object-versions --bucket  $(INFRASTRUCTURE_BUCKET) | jq -r '.DeleteMarkers[] | .VersionId + " " + .Key' > .tmp && \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') ;\
	aws s3api delete-object --bucket  $(INFRASTRUCTURE_BUCKET) --version-id $${vid} --key $${key}; \
	echo $? ; \
	done < .tmp &&\
	rm .tmp &&\
	aws s3api delete-bucket --bucket $(INFRASTRUCTURE_BUCKET)

VPC_ID = "$(shell  source yaml_source inventory/default/config/local/vars.yml; source yaml_source inventory/default/config/private/secrets.yml;  cd inventory/default/vpc ; terraform output aws_vpc_id)"
vpc_id:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	grep -v "vpc_id" inventory/default/clusters/working/vars.yml > inventory/default/clusters/working/vars.yml.tmp && \
	mv inventory/default/clusters/working/vars.yml.tmp inventory/default/clusters/working/vars.yml; \
	grep -v "vpc_id" inventory/default/clusters/production/vars.yml > inventory/default/clusters/production/vars.yml.tmp && \
	mv inventory/default/clusters/production/vars.yml.tmp inventory/default/clusters/production/vars.yml; \
	echo "vpc_id: $(VPC_ID)" >> inventory/default/clusters/working/vars.yml; \
	echo "vpc_id: $(VPC_ID)" >> inventory/default/clusters/production/vars.yml;

nat_gateways:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	echo "nat_gateways:" > inventory/default/clusters/nat_gateways.yml; \
	cd inventory/default/vpc; \
	for ng in `terraform output -json aws_nat_gateway_ids |jq -r '.value[]' `; \
	  do echo "  - $$ng" >> ../clusters/nat_gateways.yml; \
	done; \
	cd ../clusters; \
	cat nat_gateways.yml >> working/vars.yml; \
	cat nat_gateways.yml >> production/vars.yml

vpn:
	export INFRASTRUCTURE_REPO=$(INFRASTRUCTURE_REPO); \
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	ansible-galaxy install -r ansible-requirements.yml; \
	cd inventory/default/resources/admin-environment; \
	ansible-playbook vpn.yml || true; \
	ansible-playbook vpn.yml

destroy_vpn: 
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/resources/admin-environment; \
	ansible-playbook destroy.yml || true; \
	ansible-playbook destroy.yml || true; \
	ansible-playbook destroy.yml

destroy_vpn_bucket:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	aws s3 ls s3://$(VPN_BUCKET) || exit 0 && \
	aws s3api list-object-versions --bucket  $(VPN_BUCKET) | jq -r '.Versions[] | .VersionId + " " + .Key' > .tmp && \
	while read version ; do echo $$version ; vid=$$(echo $$version | awk '{ print $$1 }') ; key=$$(echo $$version | awk '{ print $$2 }') ;\
	aws s3api delete-object --bucket  $(VPN_BUCKET) --version-id $${vid} --key $${key}; \
	done < .tmp &&\
	rm .tmp &&\
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

configure_working_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	export INFRASTRUCTURE_REPO=$(INFRASTRUCTURE_REPO); \
	cd inventory/default/clusters/working; \
	pentagon add kops.cluster -f vars.yml -D"name=cluster-config"; \
	cd cluster-config; \
	source ./kops.sh || true

configure_production_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	export INFRASTRUCTURE_REPO=$(INFRASTRUCTURE_REPO); \
	cd inventory/default/clusters/production; \
	pentagon add kops.cluster -f vars.yml -D"name=cluster-config"; \
	cd cluster-config; \
	source ./kops.sh || true

update_working_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/clusters/working/cluster-config; \
	kops update cluster `cat ../vars.yml | shyaml get-value cluster_name` --yes

update_production_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/clusters/production/cluster-config; \
	kops update cluster `cat ../vars.yml | shyaml get-value cluster_name` --yes

destroy_working_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/clusters/working; \
	kops delete cluster `cat vars.yml | shyaml get-value cluster_name` --yes

destroy_production_cluster:
	source yaml_source inventory/default/config/local/vars.yml; \
	source yaml_source inventory/default/config/private/secrets.yml; \
	cd inventory/default/clusters/production; \
	kops delete cluster `cat vars.yml | shyaml get-value cluster_name` --yes
