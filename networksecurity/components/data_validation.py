from networksecurity.logging.logger import logging
from networksecurity.exception.exception import CustomException

from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yml_file,write_yml_file

from scipy.stats import ks_2samp
import pandas as pd
import sys
import os


class DataValidation:
    def __init__(self, data_ingestion_artifact:DataIngestionArtifact,
               data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config=read_yml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise CustomException(e,sys)
    
    @staticmethod
    def read_df(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e,sys)
        
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:  
        try:
            number_of_columns=len(self._schema_config)
            logging.info(f"required number of columns {number_of_columns}")
            logging.info(f"Dataframe has columns: {len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns:
                return True
            return False
        except Exception as e:
            raise CustomException(e,sys)
    
    def validate_numerical_columns(self,dataframe:pd.DataFrame)->bool:  
        try:
            numerical_columns=[col for col in dataframe.columns if dataframe[col].dtype !='O']
            logging.info(f"numerical columns are: {numerical_columns}")
            if len(numerical_columns)==0:
                return False
            return True
        except Exception as e:
            raise CustomException(e,sys) 
    
    def detect_dataset_drift(self,base_df, current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_dist=ks_2samp(d1,d2) #appling stats test
                if threshold<is_same_dist.pvalue:
                    is_found=False #no drift
                else:
                    is_found=True #drift
                    status=False
                #creating report for drift
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})
            drift_report_file_path=self.data_validation_config.drift_report_file_path
            #creating dir
            dir_path=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yml_file(file_path=drift_report_file_path, content=report)
        except Exception as e:
            raise CustomException(e,sys)   
        
        
        
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            #get the train and test file path
            train_file_path= self.data_ingestion_artifact.trained_file_path
            test_file_path= self.data_ingestion_artifact.test_file_path
            
            #read data from train and test
            train_dataframe=DataValidation.read_df(train_file_path)
            test_dataframe=DataValidation.read_df(test_file_path)
            
            #validate number of columns
            status=self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"train dataframe does not contain all columns \n"
            status=self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"test dataframe does not contain all columns \n"
            
            #validate numerical  columns
            status=self.validate_numerical_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"train dataframe does not contain numerical columns \n"
            status=self.validate_numerical_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"test dataframe does not contain numerical columns \n"
            
            # checking data drift
            status=self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            
            #output
            data_validation_artifact=DataValidationArtifact(
                validation_status= status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path= self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path= None,
                invalid_test_file_path =None,
                drift_report_file_path= self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
            
        except Exception as e:
            raise CustomException(e,sys)


