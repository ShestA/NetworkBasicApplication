### Conda environment:
#### Activate environment from file:
```console
host@name:~$ conda env create --file environment.yml
host@name:~$ conda activate NetworkBasicApplication
```
#### Export new installations:
``` console
host@name:~$ conda env export | cut -f 1 -d '=' > environment.yml
host@name:~$ sed -i 's/name: base/name: NetworkBasicApplication/g' environment.yml > environment.yml
```
### Build:
```console
host@name:~$ make all
```
