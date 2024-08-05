# Tevico

Tevico is an extensible open-source, Python-based auditing framework that empowers users to comprehensively scan their infrastructure and apps for compliance adherence, security vulnerabilities, and custom operational checks.

## Table of Contents

- [Getting Started](#getting-started)
- [CLI Examples](#cli-examples)
    - [init](#init-getting-started-with-the-project)
    - [install](#install-install-framework-entities-from-remote-repos)
    - [add](#add-add-an-entity-to-the-project)
    - [run](#run-run-the-project-with-given-configuration)
- [Community Code of Conduct](#community-code-of-conduct)
- [License](#license)

## Getting Started

TODO: Add stuff here.

## CLI Examples

Following CLI params will help you to get an idea about the project and its capabilitites. 


### `init`: Getting started with the project.

The `init` command will setup the default configurations and install basic scans to get you started. The `init` command in turn calls `install` command once the configuration setup is completed.

```bash
tevico init
```

### `install`: Install framework entities from remote repos

The `install` command helps you to install all dependent platforms, scans, profiles and channels.

```bash
tevico install <ENTITY>
```

Eg.:-

```bash
## To install all entities
tevico install

## To install all channels
tevico install channels

## To install all platforms
tevico install platforms

## To install all scans
tevico install scans
```

### `add`: Add an entity to the project

The `add` command helps you add an entity to the project.

```bash
tevico add <ENTITY> <NAME>
```

Eg.:-

```bash
## To add a new platform
tevico add platform aws

## To add a new scan
tevico add scan aws_iam_role

## To add a new channel channel
tevico add channel slack
```

### `run`: Run the project with given configuration

```bash
tevico run
```

## Community Code of Conduct

Tevico current follows the CNCF Code of Conduct. You can get the details of the code of conduct [here](https://github.com/cncf/foundation/blob/master/code-of-conduct.md). For any violations of this code of conduct you can connect with us over an [email](mailto:).

## License

Copyright 2024 Tevico

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.