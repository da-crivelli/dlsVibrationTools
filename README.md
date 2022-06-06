# dlsVibrationTools

Vibration analysis and visualisation tools for an EPICS-based vibration IOC.

Originally developed at Diamond Light Source Ltd.


## Installing
On the command line, run:

```bash
git clone https://github.com/da-crivelli/dlsVibrationTools.git
cd dlsVibrationTools

#cleanup old virtualenv
pipenv --rm

pipenv install -e .
```
## Usage

After installing, on the command line, run:
```bash
pipenv run vibration-report
```