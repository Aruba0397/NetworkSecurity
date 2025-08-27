from networksecurity.logging.logger import logging
from networksecurity.exception.exception import CustomException

from networksecurity.entity.artifact_entity import(
    DataTransformationArtifact,
    ModelTrainerArtifact
)
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data
from networksecurity.utils.main_utils.utils import evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

import sys
import os
import mlflow
from urllib.parse import urlparse

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)


import dagshub
dagshub.init(repo_owner='Aruba0397', repo_name='NetworkSecurity', mlflow=True)

os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/Aruba0397/NetworkSecurity.mlflow"
os.environ["MLFLOW_TRACKING_USERNAME"]="Aruba0397"
os.environ["MLFLOW_TRACKING_PASSWORD"]="9f62af85e040b3b12010443ca5f9402ec6a764fd"

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig, data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise CustomException(e,sys)
      
      # track mlflow
    def  track_mlflow(self, best_model, classificationmetric):
        
        mlflow.set_tracking_uri("https://dagshub.com/Aruba0397/NetworkSecurity.mlflow")
            
        with mlflow.start_run():
            # log metrics
            f1_score = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score
                
            mlflow.log_metric("f1_score", f1_score)
            mlflow.log_metric("precision", precision_score)
            mlflow.log_metric("recall", recall_score)
                
            # log model (without model registry)
            mlflow.sklearn.log_model(best_model, "model")
                

                
        #model evaluation
    def train_model(self,X_train,y_train,X_test,y_test):  
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        model_report:dict=evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, params=params)
        
        #to get best model score fro model report
        best_model_score=max(sorted(model_report.values()))
        
        #to get best model name from model report
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        
        #best model for prediction
        best_model= models[best_model_name]
        
        y_train_pred=best_model.predict(X_train)
        classification_train_metric=get_classification_score(y_true=y_train, y_pred=y_train_pred)
        
        #tracking experiments with the mlflow
        self.track_mlflow(best_model, classification_train_metric )
        
        y_test_pred=best_model.predict(X_test)
        classification_test_metric=get_classification_score(y_true=y_test, y_pred=y_test_pred)
        
        
        #tracking experiments with the mlflow
        self.track_mlflow(best_model, classification_test_metric )
        
        #loading pickle file
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)
        
        #for prediction of new test data
        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        
        #saving pickle file
        save_object(self.model_trainer_config.trained_model_file_path,obj=Network_Model)
        
        #model pusher to final models folder for deployment
        save_object("final_model/model.pkl", best_model)
        
        #creating model trainer artifact output of trainng and evaluation
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            # read data from data transformation artifact
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path
            
            #loading training and testing array
            train_arr=load_numpy_array_data(train_file_path)
            test_arr=load_numpy_array_data(test_file_path)
            
            X_train, y_train, X_test, y_test =(
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )
            
            model_trainer_artifact=self.train_model(X_train,y_train,X_test,y_test)
            return model_trainer_artifact
            
  
        except Exception as e:
            raise CustomException(e,sys)