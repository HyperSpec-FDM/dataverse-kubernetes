=========
Upgrading
=========

For Kubernetes, we need to differ between upstream releases (*UR*) and (security) image
releases (*IR*) for their different release schemas.

Upstream releases (UR)
----------------------

When switching to a new Dataverse version, please always
`read upstream release notes carefully <https://github.com/IQSS/dataverse/releases>`_.

Obviously, upstream files and additions from this project are included in the images,
but sometimes, you will need to execute some actions manually.

These actions are left out of automation by intent. For example re-indexing
might be a heavy lifting task in your installation and put heavy load on your
deployment (you might want to schedule that for off-hours).

We will try to point out any of those in our release notes.



Image releases (IR)
-------------------

As described in the images documentation :doc:`/images/dataverse-k8s` and
:doc:`/images/solr-k8s`, the latest *UR* image is released with updated
base images every night.

As every container running on your cluster contains its own operating system
installation, it's a good idea to update regularly. It's not feasible to
run ``yum update`` or similar - instead, use rollouts to replace containers.

As of writing this in January 2020, there are two main approaches to ensure this.

Using pull policy and restart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First add ``imagePullPolicy: Always`` to the container or deployment spec if not
yet present (we don't set this by default to avoid unnecessary pulls).

Then run

.. code-block:: shell

  kubectl rollout restart deployment/dataverse
  kubectl rollout restart deployment/solr

which will trigger a complete redeployment of your pods, restarting the applications.

Using tools like "imago"
^^^^^^^^^^^^^^^^^^^^^^^^

Similar to `Watchtower <https://github.com/containrrr/watchtower>`_, you can use
a similar project named `Imago <https://github.com/philpep/imago>`_ to sync your
``Pod`` images with Docker Hub images.

This works independently from your ``imagePullPolicy`` by using the ``sha256``
image checksum in background.
