from pathlib import Path
from typing import Optional, Literal, Callable
from dataclasses import dataclass

import torch
import ignite.distributed as idist


@dataclass
class TrainingConfig:
    """NFFLr configuration for the optimization process.

    Parameters
    ----------
    experiment_dir : Path
        directory to load model configuration and artifacts
    output_dir : Path, optional
        directory to save model artifacts (checkpoints, metrics)
    progress : bool
        enable console progress bar and metric logging
    diskcache : Path, optional
        directory to cache transformed `Atoms` data during training

    """

    # logging and data
    experiment_dir: Path = Path(".")
    output_dir: Optional[Path] = None
    progress: bool = True
    random_seed: int = 42
    dataloader_workers: int = 0
    pin_memory: bool = False
    progress: bool = True
    diskcache: Optional[Path] = None
    checkpoint: bool = True

    # optimization
    optimizer: Literal["sgd", "adamw"] = "adamw"
    criterion: torch.nn.Module | Callable = torch.nn.MSELoss()
    scheduler: Literal["onecycle"] | None = "onecycle"
    warmup_steps: float | int = 0.3
    per_device_batch_size: int = 256
    batch_size: Optional[int] = None
    gradient_accumulation_steps: int = 1
    learning_rate: float = 1e-2
    weight_decay: float = 1e-5
    epochs: int = 30
    swag_epochs: Optional[int] = None
    swag_anneal_epochs: int = 1
    swag_learning_rate: Optional[float] = None

    # model initialization
    initialize_bias: bool = False
    initialize_estimated_reference_energies: bool = False
    resume_checkpoint: Optional[Path] = None

    # evaluation
    train_eval_fraction: float = 0.1

    def __post_init__(self):
        # get_world_size is evaluating to 1 if this is evaluated outside of idist.Parallel
        # self.batch_size = self.per_device_batch_size * idist.get_world_size()

        if self.output_dir is None:
            self.output_dir = self.experiment_dir

        if self.swag_learning_rate is None and self.swag_epochs is not None:
            self.swag_lr = self.learning_rate / 10
