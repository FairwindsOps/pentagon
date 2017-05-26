# Secrets in Pentagon
Please submit PRs with format proposals for types of secrets that are not currently laid out here.

## config/private
`config/private` holds the sensitive files for client/account-wide access. Store AWS keys, kube_config files, etc in here. Use the template in `config/local`. This directory will never be checked into version control system and should have a very restrictive `.gitignore` that ignores all files except .gitignore:

```
# .gitignore

!.gitignore
*
```

## Secrets in 1password
Secrets need to be shared with authorized users, but because we cannot store these secrets in version control, we use 1password and we name and organize the files like this:

[TYPE] | [FILENAME] (OPTIONAL ASSOCIATED USERNAME or IDENTIFIER)
---|---
[github]  |  ${CLIENT}_aws_rsa.tgz
[kubeconfig]  | hillghost_config
[hydra] | working-1.demo.hillghost.com-hydra-secrets.tgz
[hydra] | production-1.demo.hillghost.com-hydra-secrets.tgz

## kube_config
kops writes the `kube_config` file when you create a new cluster to the environment variable $KUBE_CONFIG. kops does not clobber any prior cluster config, it adds to it.

Each client should have 1 `kube_config` file that holds credentials to connect to all of their clusters (ie: if the client has 3 clusters, they will have 1 `kube_config` file).  After creating the required clusters for the client (working/production), it is appropriate to upload your configuration to 1password. The file that is shared in 1password should be as plain as possible- don't upload custom contexts.

If you lose your `kubeconfig` file or it gets corrupted or something like that and you have access to the s3 bucket `$KOPS_STATE_STORE`, you can regenerate your `kubeconfig`file with `kops export kubecfg mycluster.example.com`. This is also a way not to use 1password for `kubeconfig` files.

## hydra

Create a tarball with the relevant files on a 1 tgz per-cluster basis, and create a secure note in 1password. Then link these files to that note.
```
$ tar czf working-1.demo.hillghost.com-hydra-secrets.tgz default/clusters/working/kubernetes/hydra/pki/ default/clusters/working/kubernetes/hydra/hydra.secret.yml
$ tar czf production-1.demo.hillghost.com-hydra-secrets.tgz default/clusters/production/kubernetes/hydra/pki/ default/clusters/production/kubernetes/hydra/hydra.secret.yml
```
