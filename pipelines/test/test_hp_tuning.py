import sys
if "." not in sys.path: sys.path.append(".")
import unittest
import logging
import mlflow
from mlflow import MlflowClient

from utils import load_config, get_or_create_experiment
from core import Digit_Data_Module, Toy_Data_Module
from pipelines import HyperParamTuningPipeline

logging.basicConfig(
        format="{asctime}::{levelname}::{name}::{message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO
    )
logger = logging.getLogger(__name__)
project_config = load_config("config/project_config.yaml")

#logger.info("prepare digit data module")
#data_module = Digit_Data_Module()
logger.info("prepare toy data module")
data_module = Toy_Data_Module()

logger.info("create mlflow client")
mlflow_client = MlflowClient(
    #tracking_uri=project_config["mlflow"]["tracking_uri"]
)

logger.info("create mlflow experiment")
experiment_name = "handwriten-digit-recognition"
experiment_id = get_or_create_experiment(
    experiment_name=experiment_name, #project_config["mlflow"]["experiment_name"],
    client=mlflow_client
)

class Test_hp_tuning(unittest.TestCase):
    def test_hp_tuning(self):
        hp_tuning_ppl = HyperParamTuningPipeline(
            model_configs=project_config["models"],
            tuning_config=project_config["optuna"],
            data_module=data_module,
            mlflow_client=mlflow_client,
            experiment_id=experiment_id
        )
        hp_tuning_ppl.run_pipeline()
if __name__=="__main__":
    unittest.main()