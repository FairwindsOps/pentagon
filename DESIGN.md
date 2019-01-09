# Pentagon Design Document:

## Intent

Pentagon is a framework for generating an Infrastructure As Code Repository (IACR). It is intended to provide a flexible and meaningful hierarchical structure to manage cloud infrastructure using a common set of tools. At ReactiveOps we use Pentagon generated IACRs to manage and maintain our client's cloud infrastructure. Our practice and experience has driven us to devise a highly flexible, highly repeatable framework that ensures uniformity of process. Pentagon has grown from a series of sensible decisions about how an IACR is “shaped”. It has a strict organization that is intended to enable automation and remain flexible to a wide variety of clouds, network, clusters and to provide a thoughtful structure for external resources.

## Key Design Elements

### Pentagon is a framework for components that are generators.

It is loosely modeled after Rails or Django and aims to provide an extensible framework for component modules. These component modules may be native or external but when external modules are installed, the interface is transparent to the user. Pentagon generators produce configuration files that should have sensible defaults provided for most values, but can be overridden by configuration.

### Pentagon provides a way to keep you IACRs up to date.

As new decisions are made, new features are added, and standards or requirements change, it is important to keep you IACR up to date. As Pentagon versions changes, so should your IACRs. Pentagon provides a migration framework so that updating the configuration and content of you IACR is defined in code. Any structure or code change should involve a new versioned migration. Exceptions may be where an update would be a breaking change or where large scale recreation of assets is required.

## Scope

### In Scope:

- Any process or component module that templates or creates files and directories for use within the context of the IACR
- Migrations to update standards and defaults in an older IACR to a newer version
- Read only interaction with infrastructure resources

### Out of Scope:

- Deep documentation how to use the supporting tools (terraform, ansible, kops etc)
- Automations and scripts to support workflows for infrastructure management practices
- Tooling to support interaction with the infrastructure repository
- Creating, or modifying any infrastructure resources
Architecture

TBD
