# Install Kafka with Strimzi

In this project  there is the config used to deploy Kafka+MM2 on CC-IN2P3 K8S cluster. 
It share resources with the RSP (same nodes). 

The USDF cluster to monitoring is not ready, so MM2 is set to mirror a CC-IN2P3 kafka cluster (used to monitoring dCache activity) and in particular the `billingLSST` topic. 

The following steps are needed to deploy it: 
1. install strimzi operator
2. create resources (storageclass, pv,pvc) and deploy it
3. deploy Kafka
4. deploy MM2

All these steps are quickly described in the next sections. 


## Install Strimzi Operator via Helm

Install strimzi operator as following:

```
helm install strimzi-cluster-operator --namespace rucio --set replicas=2 oci://quay.io/strimzi-helm/strimzi-kafka-operator

helm ls
```

This install the strinzi operator (with a replica level=2 and  in `rucio` namespace).

Doc:
1. [github](https://github.com/strimzi/strimzi-kafka-operator/tree/main/helm-charts/helm3/strimzi-kafka-operator)
2. [Strimzi web site](https://strimzi.io/docs/operators/latest/deploying.html#deploying-cluster-operator-helm-chart-str)


## Create the storageclass, pv and pvc

Using the statefulset used by Strimzi to configure Kafka pods, it is possible assign permanent storage at each pod. 
The `create_resources.py` script allows to generate all the resources for a specific cluster configuration. 

```
❯ ./create_resources.py -h
usage: create_resources.py [-h] [--svc SVC] [--config CONFIG] [--clustername CLUSTERNAME]

Creates Rucio Kafka Resources

options:
  -h, --help            show this help message and exit
  --svc SVC             The service (Kafka, Zookeeper, ...) for who storageclass,pv,pvc config must be
                        generated
  --config CONFIG       Path to the server config
  --clustername CLUSTERNAME
                        Strimzi cluster name
```

Config is expected to contains a line as 

```
nodes=[worker1,worker2,...,workerN]
```
 
 For CC-IN2P3 case we use the following command to generate an deply resources: 

```
cd create_pvpvc && ./create_resources.py && kubectl apply -n rucio -f out/
```

## Deploy Kafka

To deploy Kafka (and Zookeeper), we deploy the customization available in `kafka` directory: 

```
kubectl apply -k kafka/
```


## Deploy MM2

Once Kafka deployed, we deploy MM2 via: 

```
k apply -f mirrormaker2/mm2.yaml
```



 
