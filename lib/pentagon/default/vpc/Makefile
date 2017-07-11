.PHONY: all bucket plan apply destroy clean

all: bucket plan apply

bucket:
	aws s3 ls s3://$${INFRASTRUCTURE_BUCKET} \
	|| aws s3 mb s3://$${INFRASTRUCTURE_BUCKET} \
        &&  aws s3api put-bucket-versioning \
	 --bucket $${INFRASTRUCTURE_BUCKET} \
	 --versioning-configuration  \
	Status=Enabled

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
