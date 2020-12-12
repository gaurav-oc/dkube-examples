import zipfile
import os
import numpy as np
import pandas as pd
import argparse

# import sys
import yaml

# sys.path.insert(0, os.path.abspath("/usr/local/lib/python3.6/dist-packages"))
from dkube.sdk import *

inp_path = "/opt/dkube/input/"
train_out_path = "/opt/dkube/output/"
# test_out_path = "./"

if __name__ == "__main__":

    ########--- Parse for parameters ---########

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", dest="url", default=None, type=str, help="setup URL")
    parser.add_argument("--fs", dest="fs", required=True, type=str, help="featureset")

    global FLAGS
    FLAGS, unparsed = parser.parse_known_args()

    ########--- Get DKube client handle ---########

    dkubeURL = FLAGS.url
    # Dkube user access token for API authentication
    authToken = os.getenv("DKUBE_USER_ACCESS_TOKEN")
    # Get client handle
    api = DkubeApi(URL=dkubeURL, token=authToken)

    ########--- Extract and load data  ---########

    if not os.path.exists("titanic"):
        os.makedirs("titanic")
    with zipfile.ZipFile(os.path.join(inp_path, "titanic.zip"), "r") as zip_ref:
        zip_ref.extractall("titanic")

    train_data = pd.read_csv("titanic/train.csv")
    print(train_data.describe())

    ########--- Process raw data  ---########

    # Fill in null values with median
    train_data["Age"].fillna(value=train_data["Age"].median(), inplace=True)

    # Drop rows where fare is less than 100
    train_data = train_data[train_data["Fare"] < 100]

    # Fill in null values
    train_data["Embarked"].fillna(method="ffill", inplace=True)

    # test_data = pd.read_csv("titanic/test.csv")
    # test_data['Age'].fillna(value=test_data['Age'].median(), inplace=True)
    # test_data['Fare'].fillna(test_data['Fare'].median() , inplace = True)

    # Select features for training
    features = ["Pclass", "Sex", "SibSp", "Parch"]
    train_df = pd.get_dummies(train_data[features])
    train_df = pd.concat([train_data[["Age", "Fare", "Survived"]], train_df], axis=1)
    print(train_df.head())

    ########--- Upload Featureset metadata ---########

    # featureset to use
    fs = FLAGS.fs

    # Prepare featurespec - Name, Description, Schema for each feature
    keys = dataset.keys()
    schema = dataset.dtypes.to_list()
    featureset_metadata = []
    for i in range(len(keys)):
        metadata = {}
        metadata["name"] = str(keys[i])
        metadata["description"] = None
        metadata["schema"] = str(schema[i])
        featureset_metadata.append(metadata)

    # Convert featureset metadata (featurespec) to yaml
    featureset_metadata = yaml.dump(featureset_metadata, default_flow_style=False)
    with open("fspec.yaml", "w") as f:
        f.write(featureset_metadata)

    # Upload featureset metadata (featurespec)
    resp = api.upload_featurespec(featureset=fs, filepath="fspec.yaml")
    print("featurespec upload response:", resp)

    ########--- Commit features ---########

    # Features
    df = train_df
    # Featureset
    featureset = DkubeFeatureSet()
    # Specify features path - mounted as output
    featureset.update_features_path(path=train_out_path)
    # Write features - Dataframe
    featureset.write(dataset)
    # Commit featuresset
    resp = api.commit_features()
    print("featureset commit response:", resp)
