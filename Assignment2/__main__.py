"""
---
title: Denoising Diffusion Probabilistic Models (DDPM) training
summary: >
  Training code for
  Denoising Diffusion Probabilistic Model.
---

# [Denoising Diffusion Probabilistic Models (DDPM)](index.html) training

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]
(https://colab.research.google.com/github/labmlai/annotated_deep_learning_paper_implementations/blob/master/labml_nn/diffusion/ddpm/experiment.ipynb)

This trains a DDPM based model on CelebA HQ dataset. You can find the download instruction in this
[discussion on fast.ai](https://forums.fast.ai/t/download-celeba-hq-dataset/45873/3).
Save the images inside [`data/celebA` folder](#dataset_path).

The paper had used an exponential moving average of the model with a decay of $0.9999$. We have skipped this for
simplicity.

(obtained from: From: https://github.com/labmlai/annotated_deep_learning_paper_implementations/blob/master/labml_nn/diffusion/ddpm/experiment.py)
"""

from typing import List

import torch
import torch.utils.data
import torchvision

from labml import lab, tracker, experiment, monit
from labml.configs import BaseConfigs, option
from labml_helpers.device import DeviceConfigs
from noise import DenoiseDiffusion
from unet import UNet
import os


def main():
    # Settings for restoring/creating experiment

    LOAD_CHECKPOINT = False # True, False
    MY_UUID = 'AbeSaveTesting2' 
    EXP = 'recurrent' # 'recurrent', 'residual'

    # Create experiment
    experiment.create(
        name='diffuse',
        writers={'screen', 'labml'},
        uuid=MY_UUID,
    )

    # Create configurations
    configs = Configs()
    print(f'Status: Device is using GPU: {torch.cuda.is_available()}')

    # Set the model
    configs.convolutional_block = EXP

    # Set configurations. You can override the defaults by passing the values in the dictionary.
    experiment.configs(configs, {
        'dataset': 'MNIST',  # 'CIFAR10', 'CelebA' 'MNIST'
        'image_channels': 1,  # 3, 3, 1
        'epochs': 5,  # 100, 100, 5
    })

    # Initialize
    configs.init()

    # Set models for saving and loading
    experiment.add_pytorch_models({'eps_model': configs.eps_model})

    if not LOAD_CHECKPOINT:
        # Start the experiment
        with experiment.start():
            configs.run()   

    elif LOAD_CHECKPOINT:
        checkpoint_uuid = MY_UUID # Note: set this to the checkpoint you want to load

        # Load the experiment from 
        experiment.load(run_uuid=checkpoint_uuid) # Note: there's also an optional checkpoint number param (checkpoint=[int])

        # Start the experiment (note: not using with experiment.start() when loading)
        with experiment.start():
            configs.run()   


class Configs(BaseConfigs):
    """
    Class for holding configuration parameters for training a DDPM model.

    Attributes:
        device (torch.device):           Device on which to run the model.
        eps_model (UNet):                U-Net model for the function `epsilon_theta`.
        diffusion (DenoiseDiffusion):    DDPM algorithm.
        image_channels (int):            Number of channels in the image (e.g. 3 for RGB).
        image_size (int):                Size of the image.
        n_channels (int):                Number of channels in the initial feature map.
        channel_multipliers (List[int]): Number of channels at each resolution.
        is_attention (List[bool]):       Indicates whether to use attention at each resolution.
        convolutional_block (str):       Type of the convolutional block used
        schedule_name (str):             Function of the noise schedule
        n_steps (int):                   Number of time steps.
        batch_size (int):                Batch size.
        n_samples (int):                 Number of samples to generate.
        learning_rate (float):           Learning rate.
        epochs (int):                    Number of training epochs.
        dataset (torch.utils.data.Dataset):         Dataset to be used for training.
        data_loader (torch.utils.data.DataLoader):  DataLoader for loading the data for training.
        optimizer (torch.optim.Adam):               Optimizer for the model.
    """

    # Device to train the model on.
    # [`DeviceConfigs`](https://docs.labml.ai/api/helpers.html#labml_helpers.device.DeviceConfigs)
    #  picks up an available CUDA device or defaults to CPU.
    device: torch.device = DeviceConfigs()
    # Retrieve model information
    show = True

    # U-Net model for $\textcolor{lightgreen}{\epsilon_\theta}(x_t, t)$
    eps_model: UNet
    # [DDPM algorithm](index.html)
    diffusion: DenoiseDiffusion

    # Number of channels in the image. $3$ for RGB.
    image_channels: int = 3
    # Image size
    image_size: int = 32
    # Number of channels in the initial feature map
    n_channels: int = 64  # 64 (Default: Ho et al.; Limit is VRAM)
    # The list of channel numbers at each resolution.
    # The number of channels is `channel_multipliers[i] * n_channels`
    channel_multipliers: List[int] = [1, 2, 2, 4]
    # The list of booleans that indicate whether to use attention at each resolution
    is_attention: List[int] = [False, False, False, True]
    # Convolutional block type used in the UNet blocks. Possible options are 'residual' and 'recurrent'.
    # convolutional_block = 'residual'
    convolutional_block = 'recurrent'

    # Defines the noise schedule. Possible options are 'linear' and 'cosine'.
    schedule_name: str = 'linear'
    # Number of time steps $T$ (with $T$ = 1_000 from Ho et al).
    n_steps: int = 1000  # 1000 (Default: Ho et al.)

    # Batch size
    batch_size: int = 64  # 64 (Default: Ho et al.; Limit is VRAM)
    # Number of samples to generate
    n_samples: int = 16
    # Learning rate
    learning_rate: float = 2e-5
    # Number of training epochs
    epochs: int = 1000

    # Dataset
    dataset: torch.utils.data.Dataset
    # Dataloader
    data_loader: torch.utils.data.DataLoader

    # Adam optimizer
    optimizer: torch.optim.Adam

    def init(self):
        """
        Initialize the model, dataset, and optimizer objects.
        """

        # Create $\textcolor{lightgreen}{\epsilon_\theta}(x_t, t)$ model
        self.eps_model = UNet(
            image_channels=self.image_channels,
            n_channels=self.n_channels,
            ch_mults=self.channel_multipliers,
            is_attn=self.is_attention,
            conv_block=self.convolutional_block
        ).to(self.device)

        # Create [DDPM class](index.html)
        self.diffusion = DenoiseDiffusion(
            eps_model=self.eps_model,
            n_steps=self.n_steps,
            schedule_name=self.schedule_name,
            device=self.device,
        )

        # Show the number of params used by the model
        if self.show:
            pytorch_total_params = sum(p.numel() for p in self.eps_model.parameters())
            print(f'The total number of parameters are: {pytorch_total_params}')

        # Create dataloader
        self.data_loader = torch.utils.data.DataLoader(self.dataset, self.batch_size, shuffle=True, pin_memory=True)
        # Create optimizer
        self.optimizer = torch.optim.Adam(self.eps_model.parameters(), lr=self.learning_rate)

        # Image logging
        tracker.set_image("sample", True)

    def sample(self) -> None:
        """
        Generate samples from a trained Denoising Diffusion Probabilistic Model (DDPM).
        """

        with torch.no_grad():
            # Sample from the noise distribution at the final time step: x_T ~ p(x_T) = N(x_T; 0, I)
            x = torch.randn([self.n_samples, self.image_channels, self.image_size, self.image_size],
                            device=self.device)

            # Remove noise at each time step in reverse order (so remove noise for T steps)
            for t_ in monit.iterate('Sample', self.n_steps):
                # Get current time step
                t = self.n_steps - t_ - 1
                # Sample from the noise distribution at the current time step: x_{t-1} ~ p_theta(x_{t-1}|x_t)
                x = self.diffusion.p_sample(x, x.new_full((self.n_samples,), t, dtype=torch.long))

            # Log the final denoised samples
            tracker.save('sample', x)


    def train(self) -> None:
        """
        Train a Denoising Diffusion Probabilistic Model (DDPM) with the set dataloader.
        """

        # Iterate through the dataset
        for data in monit.iterate('Train', self.data_loader):
            # Increment global step
            tracker.add_global_step()
            # Move data to device
            data = data.to(self.device)

            # Make the gradients zero
            self.optimizer.zero_grad()
            # Calculate loss
            loss = self.diffusion.loss(data)
            # Compute gradients
            loss.backward()
            # Take an optimization step
            self.optimizer.step()
            # Track the loss
            tracker.save('loss', loss)

    def run(self):
        """
        ### Training loop
        """
        for _ in monit.loop(self.epochs):
            # Train the model
            self.train()
            # Sample some images
            # self.sample()
            # New line in the console
            tracker.new_line()
            # Save the model
            experiment.save_checkpoint()


class MNISTDataset(torchvision.datasets.MNIST):
    """
    ### MNIST dataset
    """

    def __init__(self, image_size):
        transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize(image_size),
            torchvision.transforms.ToTensor(),
        ])

        super().__init__(str(lab.get_data_path()), train=True, download=True, transform=transform)

    def __getitem__(self, item):
        return super().__getitem__(item)[0]


@option(Configs.dataset, 'MNIST')
def mnist_dataset(c: Configs):
    """
    Create MNIST dataset
    """
    return MNISTDataset(c.image_size)


class CIFAR10Dataset(torchvision.datasets.CIFAR10):
    """
    ### MNIST dataset
    """

    def __init__(self, image_size):
        transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize(image_size),
            torchvision.transforms.ToTensor(),
        ])

        super().__init__(str(lab.get_data_path()), train=True, download=True, transform=transform)

    def __getitem__(self, item):
        return super().__getitem__(item)[0]


@option(Configs.dataset, 'CIFAR10')
def mnist_dataset(c: Configs):
    """
    Create CIFAR10 dataset
    """
    return CIFAR10Dataset(c.image_size)


if __name__ == '__main__':
    main()
