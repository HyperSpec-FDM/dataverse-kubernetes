# Deploying, Running and Using Dataverse on Kubernetes

![Dataverse badge](https://img.shields.io/badge/Dataverse-v6.0-important.svg) ![Validation badge](https://jenkins.dataverse.org/job/dataverse-k8s/job/Kubeval%20Linting/job/release/badge/icon?subject=kubeval&status=valid&color=purple) ![DockerHub dataverse-k8s badge](https://img.shields.io/static/v1.svg?label=image&message=dataverse-k8s&logo=docker) ![DockerHub solr-k8s badge](https://img.shields.io/static/v1.svg?label=image&message=solr-k8s&logo=docker) ![License badge](https://img.shields.io/github/license/IQSS/dataverse-kubernetes) [![Docs badge](https://readthedocs.org/projects/dataverse-k8s/badge/?version=latest)](https://dataverse-k8s.rtfd.io/en/latest) [![IRC badge](https://img.shields.io/badge/IRC%20chat-%23dataverse-blue)](https://kiwiirc.com/client/irc.freenode.net/?nick=dataverse_k8s_?#dataverse)

This community-supported project aims at offering a new way to deploy, run and maintain a Dataverse installation for any purpose on any kind of Kubernetes-based cloud infrastructure.

You can use this on your laptop, in your on-prem datacentre or public cloud. With the power of [Kubernetes](http://kubernetes.io), many scenarios are possible.

- Documentation: [https://dataverse-k8s.rtfd.io](https://dataverse-k8s.rtfd.io)
- Support and new ideas: [https://github.com/IQSS/dataverse-kubernetes/issues](https://github.com/IQSS/dataverse-kubernetes/issues)

If you would like to contribute, you are most welcome.

This project follows the same branching strategy as the upstream Dataverse project, using a `release` branch for stable releases plus a `develop` branch. In this branch unexpected or breaking changes may happen.

## Prerequisites

1. **Running Kubernetes Cluster**
2. **Setup Networking for Kubernetes**
3. **Private Docker Registry**

## Usage

1. **Configure variables** for image building in [buildImages.py](Scripts/buildImages.py)
2. **Build images** for Dataverse, Solr and Shibboleth\
and push them to your private registry.

    Run [buildImages.py](Scripts/buildImages.py)
    ````
    python3 Scripts/buildImages.py
    ````
3. Deploy Dataverse to your Kubernetes Cluster

    Run [deploy.py](Scripts/deploy.py)
    ````
    python3 Scripts/deploy.py.py
    ````
