####
The Python script `create_resources.py` allows to creates "storage" resources for Kafka and Zookeeper. 
It create configuration files for 
1. storageclass
2. pv
3. pvc

It create a file for each replica based upon the list of workers defined in the configuration file. 

##Usage

```
./create_resources.py --help
usage: create_resources.py [-h] [--svc SVC] [--config CONFIG]

Creates Rucio Kafka Resources

options:
  -h, --help       show this help message and exit
  --svc SVC        The service (Kafka, Zookeeper, ...) for who storageclass,pv,pvc config must be generated
  --config CONFIG  Path to the server config
```
 
By default it create the configurations files for each service (Kafka and Zookeeper): the default value for `--svc` argument it's set to `all`, but you can specify only one service (or a new one if you need it). 

The default value for the configuration is `config.prod` available in this directory. 

The script create an output directory (`out`) containing all the generated yaml files.

To deploy them, you must run 

`kubectl apply -n rucio -f out/`
 
