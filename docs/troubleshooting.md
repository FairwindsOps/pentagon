# Troubleshooting

## KubeConfig
If you lose your `kubeconfig` file or it gets corrupted or something like that and you have access to the s3 bucket `$KOPS_STATE_STORE`, you can regenerate your `kubeconfig`file with `kops export kubecfg mycluster.example.com`. This is also a way not to use 1password for `kubeconfig` files.

## More Topics to come
