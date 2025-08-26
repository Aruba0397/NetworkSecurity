from dataclasses import dataclass

#output of data_ingestion.py
@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str
