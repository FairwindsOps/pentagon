#!/bin/bash

FILTER=$1

aws ec2 --region=us-east-1 describe-instances --filters "Name=tag:Env,Values=$FILTER" --query 'Reservations[*].Instances[*].{Name:Tags[?Key==`Name`].Value[],PrivateIpAddress:PrivateIpAddress}' 
