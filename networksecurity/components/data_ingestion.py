from networksecurity.logging.logger import logging
from networksecurity.exception.exception import CustomException


#configuration of the data Ingestion config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import sys
import os
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split


from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise CustomException(e,sys)
    
    #read data from mongodb
    def export_collection_as_dataframe(self):
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection =self.mongo_client[database_name][collection_name]
            
            df=pd.DataFrame(list(collection.find()))
            # remove bydefault additional _id column
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
            
            df.replace({"na": np.nan}, inplace =True)
            return df
        except Exception as e:
            raise CustomException(e,sys)
     
    # store data to create raw data csv
    def  export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            #creating a folder
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise CustomException(e,sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
       try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("performed tarin test split on the dataframe")
            
            #create dir to store tarin test split
            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info("saving train and test file path as csv")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info("exported train and test file path")
            
       except Exception as e:
           raise CustomException(e,sys) 
           
            
    
    def initiate_data_ingestion(self):
        try:
            #1 reading data from db
            dataframe= self.export_collection_as_dataframe()
            #2 storing data
            dataframe=self.export_data_into_feature_store(dataframe)
            #3  train test split
            self.split_data_as_train_test(dataframe)
            #4 storing output 
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                       test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact
        
        except Exception as e:
            raise CustomException(e,sys)
            

