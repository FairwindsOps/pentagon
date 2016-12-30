# Open Questions/Things to Consider

## Notes
* Drop the def cooldown on the master ASG
* How does master DNS work? It totally works, but I don't see how. user-data script?
* Run through, test and document HA master.

## To Do / To Decide
* How to represent this as infrastructure-as-code? The kops operations leave very little infrastructural code behind for the next operator to see. Initially, it can be a note in clusters/readme.md & vars in account/vars.sh



Cluster administrators vs. application owner
(Came from overview.md/glossary)

An application (read pods) are run in a namespace. That application, and any others in that namespace, together with any other additional resources comprise an environment.

Is there a diff between env and namespace? Is "environment" meaningless and basically synonymous with namespace? The nuance is an RDS instance that is cluster-wide. It's definitely not correlated to an application's "environment" settings eg. Rails' `config/environments/`.
