## dependencies: 
```
sudo apt-get install libproj-dev proj-data proj-bin
sudo apt-get install libgeos-dev
sudo pip install cython 
sudo pip install cartopy
pip install nvector
```

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