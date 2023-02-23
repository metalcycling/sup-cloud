#!/bin/bash

# MCAD controller installation

if [[ ${1} = "install" ]]; then
    if [ ! -d "mcad-operator" ]; then
        git clone git@github.com:project-codeflare/multi-cluster-app-dispatcher.git mcad-operator
    fi

    helm upgrade --install --wait mcad-controller ./mcad-operator/deployment/mcad-controller --namespace kube-system \
        --set loglevel=10 \
        --set image.repository=supcloud.azurecr.io/sup-cloud/mcad-controller \
        --set image.tag=latest \
        --set image.pullPolicy=Always \
        --set configMap.name=mcad-controller-configmap \
        --set configMap.quotaEnabled='"false"' \
        --set configMap.preemptionEnabled='"true"' \
        --set configMap.backoffTime=20 \
        --set coscheduler.rbac.apiGroup="scheduling.sigs.k8s.io" \
        --set coscheduler.rbac.resource="podgroups"

    kubectl apply -f mcad-roles.yaml

elif [[ ${1} = "uninstall" ]]; then
    helm uninstall -n kube-system mcad-controller

else
    echo "Nothing to do"

fi
