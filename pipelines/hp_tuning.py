import logging
import mlflow
from mlflow import MlflowClient
from typing import Dict, Any
import more_itertools
import yaml
from core import Trainer, Tuner, Digit_Data_Module
from utils import get_or_create_experiment

logger = logging.getLogger(__name__)


class HyperParamTuningPipeline:
    def __init__(
        self,
        model_configs: Dict[str, Dict[str, Any]],
        tuning_config: Dict[str, Any],
        data_module: Digit_Data_Module,
        tracking_uri: str = "127.0.0.1:5000",
        experiment_name: str = "experiment",
    ) -> None:
        mlflow_client = MlflowClient(tracking_uri=tracking_uri)
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(uri=tracking_uri)
        self.experiment_id = get_or_create_experiment(
            experiment_name=experiment_name, client=mlflow_client
        )
        self.data_module = data_module
        self.tuners = [
            Tuner(
                model_config=model_config,
                tuning_config=tuning_config,
                data_module=data_module,
                mlflow_client=mlflow_client,
                experiment_id=self.experiment_id,
            )
            for model_config in model_configs.values()
        ]

    def run_pipeline(self):
        # tuning
        more_itertools.consume((tuner.tune() for tuner in self.tuners))
        # find the best model
        tuning_runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            filter_string=f'tags."candidate" = "good"',
            output_format="list",
            order_by=["metrics.val_accuracy DESC"],
        )
        best_tuning_run = tuning_runs[0]
        best_model_config = yaml.safe_load(best_tuning_run.data.params["model_config"])
        best_tuning_accuracy = best_tuning_run.data.metrics["val_accuracy"]

        # re-train if needed
        best_run = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            filter_string=f'tags."candidate" = "best"',
            output_format="list",
            order_by=["metrics.accuracy DESC"],
        )
        # retrain = True
        if len(best_run) > 0:
            if best_run[0].data.metrics["val_accuracy"] >= best_tuning_accuracy:
                # retrain = False
                logger.info("can't find a better model")
                return
        trainer = Trainer(
            model_config=best_model_config,
            data_module=self.data_module,
            experiment_id=self.experiment_id,
            run_name="best_model",
        )
        logger.info("train and log the best model")
        trainer.train()
        # trainer.test()

        project_result = dict(
            experiment_id=self.experiment_id,
            tracking_uri=self.tracking_uri,
            model_uri=trainer.model_uri,
        )
        with open("./.project_result.yaml", "w") as f:
            yaml.dump(project_result, f)
