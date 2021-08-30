### Conda environment:
#### Activate environment from file:
```console
host@name:~$ conda create --name <env-name> --file environment.txt
```
#### Export new installations:
``` console
host@name:~$ conda env export > environment.txt
```
### Build:
```console
host@name:~$ make all
```
