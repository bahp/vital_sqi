#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'vital_sqi',
    version = '0.1.0',
    packages = find_packages(include = ["vital_sqi", "vital_sqi.*"]),
    description = "Signal quality control pipeline for electrocardiogram and "
                 "photoplethysmogram",
    long_description = long_description,
    author='Hai Ho, Khoa Le',
    author_email = 'haihb@oucru.org, khoaldv@oucru.org',
    py_modules = ['common', 'data', 'preprocess', 'sqi'],
    install_requires = ['dtw-python==1.1.6',
                        'heartpy==1.2.6',
                        'hrv-analysis==1.0.3',
                        'matplotlib==3.3.3',
                        'numpy==1.19.5',
                        'pandas==1.2.1',
                        'plotly==4.14.3',
                        'scikit-learn==0.24.1',
                        'scipy==1.6.0',
                        'statsmodels==0.12.1',
                        'tqdm==4.56.0',
                        'lightgbm==3.2.0',
                        'xgboost==1.3.3',
                      'py-ecg-detectors==1.0.2'],
    python_requires = '>3.6',
    zip_safe = False,
    url = 'https://github.com/meta00/vital_sqi',
    license = 'MIT',
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
        'Programming Language :: Python :: 3.7'
        'Programming Language :: Python :: 3.8'

    ],
)