FROM ubuntu:16.04

RUN apt-get update && apt-get install software-properties-common -y
RUN apt-add-repository ppa:ansible/ansible -y && apt-get update
RUN apt-get install -y ansible git python-dev python-pip python-dev libffi-dev libssl-dev wget vim zip openvpn awscli


RUN wget https://releases.hashicorp.com/terraform/0.10.0/terraform_0.10.0_linux_amd64.zip && unzip terraform_0.10.0_linux_amd64.zip && mv terraform /usr/local/bin/

RUN mkdir -p /pentagon 
COPY . /pentagon/

RUN pip install -U -e  ./pentagon