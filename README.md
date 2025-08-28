dagshub_token=9f62af85e040b3b12010443ca5f9402ec6a764fd

MLFLOW_TRACKING_URI="https://dagshub.com/Aruba0397/NetworkSecurity.mlflow"
MLFLOW_TRACKING_USERNAME="Aruba0397"
MLFLOW_TRACKING_PASSWORD="9f62af85e040b3b12010443ca5f9402ec6a764fd"


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
            
            mlflow.end_run(status="FINISHED")   
