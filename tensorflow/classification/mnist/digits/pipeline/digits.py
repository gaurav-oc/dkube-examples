import kfp.dsl as dsl
from kfp import components
from kubernetes import client as k8s_client
import json

from random import randint

dkube_training_op           = components.load_component_from_file("../components/training/component.yaml")
dkube_serving_op            = components.load_component_from_file("../components/serving/component.yaml")
dkube_viewer_op             = components.load_component_from_file('../components/viewer/component.yaml')

@dsl.pipeline(
    name='dkube-mnist-pl',
    description='sample mnist digits pipeline with dkube components'
)
def d3pipeline(
    #Dkube authentication token
    auth_token,
    #By default 'default' is used as the job group for runs
    job_group = 'default',
    #Framework. One of tensorflow, pytorch, sklearn
    framework = "tensorflow",
    #Framework version
    version = "1.14",
    #By default tf v1.14 image is used here, v1.13 or v1.14 can be used.
    #Or any other custom image name can be supplied.
    #For custom private images, please input username/password
    training_container=json.dumps({'image':'docker.io/ocdr/d3-datascience-tf-cpu:v1.14', 'username':'', 'password': ''}),
    #Name of the workspace in dkube. Update accordingly if different name is used while creating a workspace in dkube.
    training_program="mnist",
    #Script to run inside the training container
    training_script="python model.py",
    tuning = '{ "studyName": "mnist-dkube-tuning", "owner": "crd", "optimizationtype": "maximize", "objectivevaluename": "train_accuracy_1", "optimizationgoal": 0.99, "requestcount": 1, "metricsnames": [ "train_accuracy_1" ], "parameterconfigs": [ { "name": "--learning_rate", "parametertype": "double", "feasible": { "min": "0.01", "max": "0.05" } }, { "name": "--batch_size", "parametertype": "int", "feasible": { "min": "100", "max": "200" } }, { "name": "--num_epochs", "parametertype": "int", "feasible": { "min": "1", "max": "10" } } ] }',
    #Input datasets for training. Update accordingly if different name is used while creating dataset in dkube.
    training_datasets=json.dumps(["mnist"]),
    #Input dataset mount paths
    training_input_dataset_mounts=json.dumps(["/opt/dkube/input"]),
    #Output models for training.
    training_outputs=json.dumps(["mnist"]),
    #Output dataset mount paths
    training_output_mounts=json.dumps(["/opt/dkube/output"]),
    #Request gpus as needed. Val 0 means no gpu, then training_container=docker.io/ocdr/dkube-datascience-tf-cpu:v1.12
    training_gpus=0,
    #Any envs to be passed to the training program
    training_envs=json.dumps([{"steps": 100}]),
    #Device to be used for serving - dkube mnist example trained on gpu needs gpu for serving else set this param to 'cpu'
    serving_device='cpu',
    #Serving image
    serving_image=json.dumps({'image':'docker.io/ocdr/tensorflowserver:1.14', 'username':'', 'password': ''}),
    #Transformer image
    transformer_image=json.dumps({'image':'docker.io/ocdr/mnist-example-preprocess:2.0.7', 'username':'', 'password': ''}),
    #Name of the transformer project in dkube. Update accordingly if different name is used while creating a workspace in dkube.
    transformer_project="mnist-transformer",
    #Script to execute the transformer
    transformer_code="tensorflow/classification/mnist/digits/transformer/transformer.py"):

    train       = dkube_training_op(auth_token, training_container,
                                    program=training_program, run_script=training_script,
                                    datasets=training_datasets, outputs=training_outputs,
                                    input_dataset_mounts=training_input_dataset_mounts,
                                    output_mounts=training_output_mounts,
                                    ngpus=training_gpus, envs=training_envs,
                                    tuning=tuning, job_group=job_group,
                                    framework=framework, version=version)
    serving     = dkube_serving_op(auth_token, train.outputs['artifact'],
                                device=serving_device, serving_image=serving_image,
                                transformer_image=transformer_image,
                                transformer_project=transformer_project,
                                transformer_code=transformer_code).after(train)
    #inference   = dkube_viewer_op(auth_token, serving.outputs['servingurl'],
    #                             'digits', viewtype='inference').after(serving)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(d3pipeline, __file__ + '.tar.gz')

