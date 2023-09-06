#!/usr/bin/env python3
import yaml
import re
import os
from argparse import ArgumentParser

config='config.prod'
cluster='rucio-frdf'

def read_config(config='config.prod'):
    try:
        with open(config, 'r') as file:
        # Read a single line
            wkn=re.findall(r'\[(.*?)\]', file.readline())
            return([worker.strip() for worker in wkn[0].split(',')])
    except FileNotFoundError:
        print(f"The file {config} was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def set_pv(kind):
    workers=read_config()
    pv_yaml=read_template('pv')
    pv_yaml['spec']['local']['path']=f"/data/kafka/{kind}"
    pv_yaml['spec']['storageClassName']=f"{kind}-local-storage"
    i=0
    nm=f'{cluster}-{kind}-'
    for worker in workers:
        name=f'{nm}{i}'
        pvc_name=f'data-{nm}{i}'
        pv_yaml['metadata']['name']=name
        pv_yaml['metadata']['labels']['pvc_name']=pvc_name
        set_pvc(kind, pvc_name)
        i=i+1
        if 'nodeAffinity' in pv_yaml.get('spec', {}):
            for term in pv_yaml['spec']['nodeAffinity'].get('required', {}).get('nodeSelectorTerms', []):
                for expr in term.get('matchExpressions', []):
                    if expr.get('key') == 'kubernetes.io/hostname':
                        expr['values'] = [worker]
        write_yaml(pv_yaml, f'pv-{name}.yaml')

        
def set_pvc(kind, name):
    pvc_yaml=read_template('pvc')
    pvc_yaml['spec']['storageClassName']=f"{kind}-local-storage"
    pvc_yaml['metadata']['name']=name
    pvc_yaml['spec']['selector']['matchLabels']['pvc_name']=name
    write_yaml(pvc_yaml, f'pvc-{name}.yaml')


def set_sc(kind):
    sc_yaml=read_template('storageclass')
    sc_yaml['metadata']['name']=f'{kind}-local-storage'
    write_yaml(sc_yaml, f"storageclass-{kind}.yaml")

def read_template(rsr):
    match rsr:
        case "storageclass":
            file='storageclass_template.yaml'
        case "pv":
            file='pv_template.yaml'
        case "pvc":
            file='pvc_template.yaml'
    
    stream = open(f"./template/{file}", "r")
    return(yaml.load(stream, Loader=yaml.FullLoader))

def write_yaml(data, fname):
    if not os.path.exists('out'):
        os.makedirs('out')
    outname=f'out/{fname}'
    with open(outname, 'w') as file:
        yaml.dump(data, file)

def main():
    services=['kafka', 'zookeeper']
    parser = ArgumentParser(description='Creates Rucio Kafka Resources')
    parser.add_argument('--svc',
                        action='store',
                        help='The service (Kafka, Zookeeper, ...) for who storageclass,pv,pvc config must be generated', default='all')
    parser.add_argument('--config',
                        action='store',
                        help='Path to the server config', default='config.prod')
    parser.add_argument('--clustername',
                        action='store',
                        help='Strimzi cluster name', default='rucio-frdf')
    args = parser.parse_args()
    
    global config
    config=args.config
    global cluster
    cluster=args.clustername
    
    if args.svc=='all':
        for service in services:
            set_sc(service)
            set_pv(service)

    else:
        set_sc(args.svc)
        set_pv(args.svc)


if __name__ == '__main__':
    main()
