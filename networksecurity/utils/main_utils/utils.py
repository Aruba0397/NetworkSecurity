from networksecurity.logging.logger import logging
from networksecurity.exception.exception import CustomException
import sys
import os
import numpy as np
import yaml
import dill
import pickle

def read_yml_file(file_path: str)-> dict:
    try:
        with open(file_path, 'rb') as yml_file:
            return yaml.safe_load(yml_file)
    except Exception as e:
        raise CustomException(e,sys) 

#writing report for drift
def write_yml_file(file_path: str, content: object, replace:bool=False)-> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w")as file:
            yaml.dump(content, file)
    except Exception as e:
        raise CustomException(e,sys)