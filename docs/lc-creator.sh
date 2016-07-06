AWS_CMD="aws ec2"
AWS_ASG_CMD="aws autoscaling"

ASG_NAME="working-minion-group-us-east-1b-medium"
KUBE_NODE_IMAGE="ami-6c9ea606"
IAM_PROFILE_NODE="kubernetes-minion"
NODE_SIZE="t2.medium"
AWS_SSH_KEY_NAME="kubernetes-SHA256kgs3RUR7oNM+k65XoVOyjXIX8y0USh3naeywC7C2gUA"
NODE_SG_ID="sg-0f087974"
public_ip_option="--no-associate-public-ip-address"
spot_price_option=""

NODE_ROOT_DISK_SIZE=${NODE_ROOT_DISK_SIZE:-32}
NODE_ROOT_DISK_TYPE="${NODE_ROOT_DISK_TYPE:-gp2}"
EPHEMERAL_BLOCK_DEVICE_MAPPINGS=",{\"DeviceName\": \"/dev/sdc\",\"VirtualName\":\"ephemeral0\"},{\"DeviceName\": \"/dev/sdd\",\"VirtualName\":\"ephemeral1\"},{\"DeviceName\": \"/dev/sde\",\"VirtualName\":\"ephemeral2\"},{\"DeviceName\": \"/dev/sdf\",\"VirtualName\":\"ephemeral3\"}"

ROOT_DEVICE_NODE=$($AWS_CMD describe-images --image-ids $KUBE_NODE_IMAGE --query 'Images[].RootDeviceName')
ROOT_DEVICE_NODE=/dev/xvda

NODE_BLOCK_DEVICE_MAPPINGS="[{\"DeviceName\":\"${ROOT_DEVICE_NODE}\",\"Ebs\":{\"DeleteOnTermination\":true,\"VolumeSize\":${NODE_ROOT_DISK_SIZE},\"VolumeType\":\"${NODE_ROOT_DISK_TYPE}\"}} ${EPHEMERAL_BLOCK_DEVICE_MAPPINGS}]"


aws autoscaling create-launch-configuration \
--launch-configuration-name ${ASG_NAME}2 \
--image-id $KUBE_NODE_IMAGE \
--iam-instance-profile ${IAM_PROFILE_NODE} \
--instance-type $NODE_SIZE \
--key-name ${AWS_SSH_KEY_NAME} \
--security-groups ${NODE_SG_ID} \
${public_ip_option} \
${spot_price_option} \
--block-device-mappings "${NODE_BLOCK_DEVICE_MAPPINGS}" \
--user-data "fileb://node-user-data.gz"
