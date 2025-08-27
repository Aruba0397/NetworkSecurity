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
        raise CustomException(e,sys)\

# save numpy array data to file
def save_numpy_array_data(file_path: str, array: np.array):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb")as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise CustomException(e,sys)
    
#sav e pickle file after KNN imputation
def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info("entered the save object in utils.py")
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb")as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("existed the save object utils.py")   
    except Exception as e:
        raise CustomException(e,sys)
    