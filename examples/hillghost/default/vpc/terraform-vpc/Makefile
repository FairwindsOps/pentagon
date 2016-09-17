.DEFAULT_GOAL := help
.PHONY: help requirements test

TEMPDIR := $(shell mktemp -d)
TF_VERSION = 0.6.16
TF_PLATFORM = darwin
SHELL := /bin/bash

bin/terraform:
	wget https://releases.hashicorp.com/terraform/$(TF_VERSION)/terraform_$(TF_VERSION)_$(TF_PLATFORM)_amd64.zip
	unzip terraform_$(TF_VERSION)_$(TF_PLATFORM)_amd64.zip -d bin/

requirements: bin/terraform ## Install required software

test: requirements ## Execute all tests
	@for i in `find . -name terraform.\*.tfvars.example`; do \
		bin/terraform plan -var-file $$i 1> $(TEMPDIR)/$$i.output && \
		diff tests/fixtures/$$i.output $(TEMPDIR)/$$i.output; \
		if [[ $$? -ne 0 ]] ; then exit 1; fi; \
	done
	@echo "Temp directory: $(TEMPDIR)"

help: ## Halp!
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
