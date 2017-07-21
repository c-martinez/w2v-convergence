# w2v-divergence
Need to add a high level wordy description here...
This is code implementing measure described in paper under review.

Time-shifting models produced by this script can be used to generate models for ShiCo (link to ShiCo repo & paper).

Time-shifting models generated using this method (based on Times news paper (link?)) can be found here (link).

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

## Measure divergence for a range
Use `runDivergenceRange.py` script.

Example:
```
./runDivergenceRange.py --y0 1785 --nYears 5 --outDir=outDir/
```

Perhaps more than one run is necessary.

## Visualize Measured divergence
Use `VisualizeDivergence.ipynb` (on jupyter notebook)

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
