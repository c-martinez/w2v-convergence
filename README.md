# Word2Vec convergence
Need to add a high level wordy description here...
This is code implementing measure described in paper under review.

Time-shifting models produced by this script can be used to generate models for ShiCo (link to ShiCo repo & paper).

Time-shifting models generated using this method (based on Times newspaper (link?)) can be found here (link to data publication).

## Running these scripts
Install Python requirements:

```
pip install -r requirements.txt
```

Implement your own `helpers.py`:
```python
def getYears():
def getSentencesForYear(year):
def getSentencesInRange(startY, endY):
```

Implement your own `settings.py` (if required). Settings is used by `helpers.py` to determine location of data and cache directories. If you modify `getSentencesForYear` in such a way that caching is not required, then you don't need settings.

## Measure convergence for a range
Use `runConvergenceRange.py` script.

Example:
```
./runConvergenceRange.py --y0=1900 --nYears=10 --outDir=outDir/
```

Perhaps more than one run is necessary.

## Visualize Measured convergence
Use `VisualizeConvergence.ipynb` (on jupyter notebook)

<include graph here>
Use `outDir` from previous command as `outDir` on notebook cell.

<include explanation on how to interpret results>

Selected # models for example nYears = 2

## Generate time shifting models
Use `nYears` from previous step to set model.s

Example:
```
./runGenerateModels.py --y0=1900 --yN=1910 --nYears=5 --outDir=outDir/ --step=1
```

Will produce models:

Models        |
--------------|
1900_1905.w2v |
1901_1906.w2v |
1902_1907.w2v |
1903_1908.w2v |
1904_1909.w2v |
1905_1910.w2v |

Generated:

./runGenerateModels.py --y0=1900 --yN=2009 --nYears=2 --outDir=/data3/times/models1900_2years --step=1
