import sys
import logging

import dask
from dask_yarn import YarnCluster
from dask.distributed import Client

import argparse


LOGGER_SETTINGS = {
    "stream": sys.stdout,
    "level": logging.INFO,
    "datefmt": '%Y-%m-%d %H:%M:%S',
    "format": '%(asctime)s %(levelname)s %(message)s'
}

logger = logging.getLogger("distributed.worker")
#logging.basicConfig(**LOGGER_SETTINGS)

# create a cluster where each worker has 2 cores and 1GiB of memory
with YarnCluster.from_current() as cluster:
    # connect to the cluster
    with Client(cluster) as client:
        import joblib
        from sklearn.datasets import load_digits
        from sklearn.model_selection import RandomizedSearchCV
        from sklearn.svm import SVC
        import numpy as np

        logger.warning('do joblib job')
        digits = load_digits()

        param_space = {
          'C': np.logspace(-6, 6, 13),
          'gamma': np.logspace(-8, 8, 17),
          'tol': np.logspace(-4, -1, 4),
          'class_weight': [None, 'balanced'],
        }

        model = SVC(kernel='rbf')
        search = RandomizedSearchCV(model, param_space, cv=3, n_iter=50, verbose=10)

        cluster.scale(20)

        with joblib.parallel_backend('dask', wait_for_workers_timeout=60):
            logger.warning('doing joblib job')
            search.fit(digits.data, digits.target)

logger.warning('done joblib job')

