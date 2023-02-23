#!/bin/bash

# MPI operator installation

if [[ ${1} = "install" ]]; then
    if [ ! -d "mpi-operator" ]; then
        git clone git@github.com:kubeflow/mpi-operator.git mpi-operator
    fi

    cd mpi-operator
    kubectl apply -f deploy/v2beta1/mpi-operator.yaml

elif [[ ${1} = "uninstall" ]]; then
    if [ ! -d "mpi-operator" ]; then
        git clone git@github.com:kubeflow/mpi-operator.git mpi-operator
    fi

    cd mpi-operator
    kubectl delete -f deploy/v2beta1/mpi-operator.yaml

else
    echo "Nothing to do"

fi
