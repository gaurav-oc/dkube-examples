import sys, time
from dkube.sdk import *
from dkube.sdk.lib.api import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--url', dest = 'url', type=str)
parser.add_argument('--auth_token',dest = 'authtoken', type=str)
parser.add_argument('--user',dest = 'user', type=str)
args = parser.parse_args()

dkubeURL = args.url
authToken = args.authtoken
user = args.user


gittoken = '5610fdfc35d7158d9c44771c35b0e49d3ee70fd3'

api = DkubeApi(dkubeURL=dkubeURL, authToken=authToken)

project = DkubeProject(user, name='regression')
project.update_project_source(source='github')
project.update_github_details('https://github.com/oneconvergence/dkube-apps/tree/reg-demo', branch='reg-demo', authmode = 'apikey', authkey = gittoken)
try:
    api.create_project(project)
except:
    print("Datum already exists")
    
dataset = DkubeDataset(user, name='clinical')
dataset.update_dataset_source(source='github')
dataset.update_github_details('https://github.com/oneconvergence/dkube-apps/tree/reg-demo-data/clinical', branch='reg-demo-data', authmode = 'apikey', authkey = gittoken)
try:
    api.create_dataset(dataset)
except:
    print("Datum already exists")
    
dataset = DkubeDataset(user, name='images')
dataset.update_dataset_source(source='github')
dataset.update_github_details('https://github.com/oneconvergence/dkube-apps/tree/reg-demo-data/image_data', branch='reg-demo-data', authmode = 'apikey', authkey = gittoken)
try:
    api.create_dataset(dataset)
except:
    print("Datum already exists")
    
dataset = DkubeDataset(user, name='rna')
dataset.update_dataset_source(source='github')
dataset.update_github_details('https://github.com/oneconvergence/dkube-apps/tree/reg-demo-data/rna', branch='reg-demo-data', authmode = 'apikey', authkey = gittoken)
try:
    api.create_dataset(dataset)
except:
    print("Datum already exists")
    
dvs_datasets = ['clinical-preprocessed', 'clinical-train', 'clinical-test', 'clinical-val',
                'images-preprocessed', 'images-train', 'images-test', 'images-val',
                'rna-train', 'rna-test', 'rna-val']

for each_dataset in dvs_datasets:
    dataset = DkubeDataset(user, name=each_dataset)
    dataset.update_dataset_source(source='dvs')
    try:
        api.create_dataset(dataset)
    except:
        print("Datum already exists")
        
model = DkubeModel(user, name='regression-model')
model.update_model_source(source='dvs')
try:
    api.create_model(model)
except:
    print("Datum already exists")

print("Finishing Dataset creation")
time.sleep(60)
