DeepDrummer WEB user experiment
===============================

This is the code base for a WEB interface to conduct user experiments for the Mila DeepDrummer project.

Free software: BSD license


Installation
------------

To install this package and all requisites, you should use a Python virtual environment.

For example:

```
# Install the web server in a virtual environment
git clone https://github.com/fosterrath-mila/deepgroove_user_exp.git
cd deepgroove_web_user_exp
virtualenv -p python3.6 env36
source env36/bin/activate
pip3 install -e .
cd ..

# Install the DeepDrummer package
git clone https://github.com/mila-iqia/DeepDrummer.git
cd DeepDrummer
pip3 install -e .
cd ..

```

With these commands, you will have a shell with all required dependencies. 

QuickStart
----------

```
cd deepgroove_web_user_exp
source env36/bin/activate
export FLASK_APP=deepgroove_web_user_experiment.deepgroove_web_user_experiment
export FLASK_DEBUG=1
flask run
```
