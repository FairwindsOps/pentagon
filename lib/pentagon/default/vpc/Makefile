.PHONY: all plan apply destroy provision ssh

all: plan apply provision

plan:
	terraform remote pull || ./terraform-remote.sh && terraform remote pull
	terraform get -update
	terraform plan -module-depth=-1 -var-file terraform.tfvars -out terraform.tfplan

apply:
	terraform apply terraform.tfplan
	terraform remote push

destroy:
	terraform plan -destroy -var-file terraform.tfvars -out terraform.tfplan
	terraform apply terraform.tfplan

clean:
	rm -f terraform.tfplan
	rm -f terraform.tfstate
	rm -fR .terraform/
