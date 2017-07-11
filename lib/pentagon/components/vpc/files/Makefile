.PHONY: all plan apply destroy provision ssh

all: plan apply provision

plan:
	terraform init -backend=true
	terraform plan -module-depth=-1 -var-file terraform.tfvars

apply:
	terraform apply

destroy:
	terraform plan -destroy -var-file terraform.tfvars -out terraform.tfplan
	terraform apply terraform.tfplan

clean:
	rm -f terraform.tfplan
	rm -f terraform.tfstate
	rm -fR .terraform/
