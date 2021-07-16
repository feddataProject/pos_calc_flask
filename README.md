## dependencies: 
```
sudo apt-get install libproj-dev proj-data proj-bin
sudo apt-get install libgeos-dev
sudo pip install cython 
sudo pip install cartopy
pip install nvector
```
## nvector library references
https://nvector.readthedocs.io/en/latest/

## calculation refereces: (#ex 8)
https://cran.r-project.org/web/packages/nvctr/vignettes/position-calculations.html#example-8-a-and-azimuthdistance-to-b
https://pypi.org/project/nvector/

## test nvector package
first: 
```
pip install pytest
```
and then from python shell:
```
>>> import nvector as nv
>>> nv.test('--doctest.modules--')
```