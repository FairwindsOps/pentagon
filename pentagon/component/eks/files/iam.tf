#
# Kubernetes roles for aws-iam-authenticator
#

data "aws_caller_identity" "current" {}


data "aws_iam_policy_document" "kube-assume-role-policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    principals {
      type = "AWS"
      identifiers = ["arn:aws:iam:::root"]
    }
  }
}

/*
Roles for aws-iam-authenticator
*/
resource "aws_iam_role" "role_kube_engineer" {
  name                = "KubernetesEngineer"
  assume_role_policy  = "${data.aws_iam_policy_document.kube-assume-role-policy.json}"
}

resource "aws_iam_role" "role_kube_developer" {
  name                = "KubernetesDeveloper"
  assume_role_policy  = "${data.aws_iam_policy_document.kube-assume-role-policy.json}"
}


/*
This policy provides access to route53
*/
resource "aws_iam_policy" "external-dns" {
  name = "external-dns"
  description = "Provides access to route53 for external dns."

  policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Effect": "Allow",
     "Action": [
       "route53:ChangeResourceRecordSets"
     ],
     "Resource": [
       "arn:aws:route53:::hostedzone/*"
     ]
   },
   {
     "Effect": "Allow",
     "Action": [
       "route53:ListHostedZones",
       "route53:ListResourceRecordSets"
     ],
     "Resource": [
       "*"
     ]
   }
 ]
}
EOF

}
