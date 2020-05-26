DeepDrummer WEB user experiment
===============================

This is the code base for a WEB interface to conduct user experiments for the Mila DeepDrummer project.

Free software: BSD license


Installation
------------

To install this package and all requisites, you should use a Python virtual environment.

For example:

```
virtualenv -p python3.6 env36
source env36/bin/activate

# Install the DeepDrummer package
git clone https://github.com/mila-iqia/DeepDrummer.git
cd DeepDrummer
pip3 install -e .
cd ..

git clone https://github.com/fosterrath-mila/deepgroove_user_exp.git
cd deepgroove_web_user_exp/
pip3 install -e .
```

With these commands, you will have a shell with all required dependencies. 

QuickStart
----------

```
source env36/bin/activate
export FLASK_APP=deepgroove_web_user_experiment.deepgroove_web_user_experiment
export FLASK_DEBUG=1
flask run
```
