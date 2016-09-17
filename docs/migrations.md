migrations:

Possibility 1:
migrations always are run before updating an app Deployment
* This seems the most default-esque direction. Required pre-migrations are always run.
Post-migrations are configured as jobs. TBD: how to deploy a Job?

```
deploy:
  run migrate job with new image
  update Deployment
```

Possibility 2:
migrations always are run after updating an app Deployment. This would fail if there were migrations required for the
new version. This is really more appropos of running jobs post-deployment.

```
deploy:
  update Deployment
  run migrate job with new image
```

Possibility 3:
migrations always are not automated


---
if version + 1 requires migrations, then the migration should be included in its own deployment.
if migrations need to be
