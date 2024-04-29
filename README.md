# PAC-MD ![Badge en Desarollo](https://img.shields.io/badge/VERSION-1.0%20-yellow) ![Badge en Desarollo](https://img.shields.io/badge/ESTADO-beta_estable%20-green) ![Badge en Desarollo](https://img.shields.io/badge/LICENCIA-mpl2.0%20-red) 


_PAC-PHOS4D es una herramienta de post-procesamiento de archivos de salida de simulaciones por zona de luz natural para edificios reconstruidos de [phos4dtool](https://igit.architektur.tu-darmstadt.de/phos-4d/phos4dtools) . Las métricas dinámicas incorporadas a esta herramienta son: Iluminancia promedio, CDI y sCDI._

### Requisitos

```
Windows or Mac OS or Linux operating system:
Python 3.9-3.11
Numpy 1.26.4
Pandas 2.2.2
Matplotlib 3.8.4
Plotly 5.21.0
Configparser 7.0.0
Visual Studio Code
```
Las versiones indicadas son las mínimas requeridas, pero se pueden utilizar las versiones más recientes tanto de Python como de las librerías.

### Instalación

Crear la carpeta donde se instalará la herramienta 'pac_phos4d'

Ingresar a la carpeta

```
cd pac_phos4d
```
 
Crear entorno virtual

```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install matplotlib numpy pandas plotly configparser
```

Clonar carpeta de 'pac_phos4d' desde Github

```
git clone https://github.com/INAHE-CONICET/PAC-PHOS4D.git
```

o descomprimir el archivo ZIP descargado en la carpeta donde se instaló 'pac_phos4d' y salir.

---

Para instalar Visual Studio Code, dirijase al siguiente link (https://code.visualstudio.com/Download)

---

### Flujo de trabajo

Ingresar a la capeta donde se instaló 'pac_phos4d'

```
cd pac_phos4d
```

Activar el entorno virtual

```
source env/bin/activate
```

Ingresar a la capeta descargada 'PAC-PHOS4D'

```
cd ./PAC-PHOS4D/
```

En el caso de usuario Windows defina las siguientes carpetas y comente (;) 'OS Mac o Linux' (linea 13-14) en el archivo 'setup.cfg'

```
4  [PATH]
5  ;For Windows Systems, use the following definitions, uncomment if required: 
6  ;data_file_path is path to data files .tsv type 
7  ;csv_save_path is path where results data will be stored
8  data_file_path = .\example\export_pts4-median_month-median_100cmV.tsv
9  csv_save_path = .\
10 
11
12 ;For Mac System, use the following definitions, uncomment if required:
13 ;data_file_path = ./example/export_pts4-median_month-median_100cmV.tsv
14 ;csv_save_path = ./example/
```

En el caso de usuarios OS Mac o Linux, comente 'OS Windows' (8-9)

Ejecutar el post-procesamiento

```
python3 pac_phos4d.py
```

A los resultados se puede acceder desde:

```
./example/results_pho4dt.csv
```
