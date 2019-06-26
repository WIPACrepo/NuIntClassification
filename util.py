import json
from dataset import *
from model import *
from collections import Mapping



def dict_update(d, u):
    """ Recursively updates a dictionary with another. Used for parsing settings for training.
    
    Parameters:
    -----------
    d : dict
        The dict to update.
    u : dict
        The dict that contains keys that should be updated in d.
    """
    for key in u:
        if key in d:
            if isinstance(d[key], Mapping):
                dict_update(d[key], u[key])
            else:
                d[key] = u[key]
        else:
            raise RuntimeError(f'Unkown setting {key}')

def dataset_from_config(config):
    """ Creates a dataset from a configuration file. 
    
    Parameters:
    -----------
    config : dict
        The configuration dict.
    
    Returns:
    --------
    train : dataset.ShuffledTorchHD5Dataset
        Training dataset.
    val : dataset.ShuffledTorchHD5Dataset
        Validation dataset.
    test : dataset.ShuffledTorchHD5Dataset
        Testing dataset.
    
    """
    dataset_config = config['dataset']
    dataset_type = dataset_config['type'].lower()
    if dataset_type in ('hdf5', 'hd5'):
        train = ShuffledTorchHD5Dataset(
            dataset_config['paths']['train'],
            features = dataset_config['features'],
            coordinates = dataset_config['coordinates'],
            balance_dataset = dataset_config['balance_classes'],
            min_track_length = dataset_config['min_track_length'],
            max_cascade_energy = dataset_config['max_cascade_energy'],
            )
        val = ShuffledTorchHD5Dataset(
            dataset_config['paths']['validation'],
            features = dataset_config['features'],
            coordinates = dataset_config['coordinates'],
            balance_dataset = False,
            min_track_length = None,
            max_cascade_energy = None,
            )
        test = ShuffledTorchHD5Dataset(
            dataset_config['paths']['test'],
            features = dataset_config['features'],
            coordinates = dataset_config['coordinates'],
            balance_dataset = False,
            min_track_length = None,
            max_cascade_energy = None,
            )
        return train, val, test
    else:
        raise RuntimeError(f'Unknown dataset type {dataset_type}')

def model_from_config(config):
    """ Creates a model from a configuration.
    
    Parameters:
    -----------
    config : dict
        The configuration for the model.
    
    Returns:
    --------
    model : keras.models.Model
        A keras model.
    """
    number_input_features = len(config['dataset']['features'])
    model_config = config['model']
    model_type = model_config['type'].lower()
    if model_type == 'gcnn':
        model = GraphConvolutionalNetwork(
            number_input_features,
            units_graph_convolutions = model_config['hidden_units_graph_convolutions'],
            units_fully_connected = model_config['hidden_units_fully_connected'],
            use_batchnorm = model_config['use_batchnorm'],
            dropout_rate = model_config['dropout_rate'],
            use_residual = model_config['use_residual'],
        )
        num_classes = (model_config['hidden_units_graph_convolutions'] + model_config['hidden_units_fully_connected'])[-1]
    else:
        raise RuntimeError(f'Unkown model type {model_type}')
    return model