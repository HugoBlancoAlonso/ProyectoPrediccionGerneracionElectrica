# Proyecto Final de Big Data

Repositorio del proyecto final con dos etapas principales:

- Capa Plata: extracción, limpieza y consolidación de datos.
- Capa Oro: unificación final y dashboard interactivo.

## Estructura del proyecto

- `plata/extraccion.ipynb`: descarga datos desde HDFS, procesa las fuentes y genera los ficheros intermedios.
- `oro/combinacion.ipynb`: consolida los datos finales y genera el dashboard interactivo.
- `oro/dashboard_df_consolidado.py`: script que construye la vista HTML del dashboard.
- `oro/data/dashboard_df_consolidado.html`: dashboard generado para abrir directamente en el navegador.
- `requirements.txt`: dependencias Python del proyecto.
- `docker-compose.yml` y `hadoop.env`: configuración del entorno HDFS.

## Requisitos previos

- Python 3.10 o superior.
- Docker y Docker Compose.
- Acceso a HDFS en local o al entorno configurado en `docker-compose.yml`.
- Credenciales y acceso a las fuentes de datos usadas en la capa Plata, si vas a regenerar los datos desde cero.

## Instalación

1. Crear un entorno virtual y activarlo.

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias.

```bash
pip install -r requirements.txt
```

## Despliegue del entorno de datos

1. Arrancar HDFS con Docker.

```bash
docker compose up -d
```
2. Conectar HDFS con jupyter
```
docker network connect proyectofinal_default jupyter_datascience
```

3. Verificar que el NameNode responde en `http://localhost:9870`.

4. Si es necesario, crear las rutas del datalake.

```bash
docker exec namenode hdfs dfs -mkdir -p /datalake/plata/consumo
docker exec namenode hdfs dfs -mkdir -p /datalake/plata/clima
docker exec namenode hdfs dfs -mkdir -p /datalake/plata/festivos
docker exec namenode hdfs dfs -mkdir -p /datalake/oro/datos
docker exec namenode hdfs dfs -chmod -R 777 /datalake
```

## Ejecución de la capa Plata

1. Abrir [plata/extracion.ipynb](plata/extracion.ipynb).
2. Ejecutar las celdas en orden.
3. Comprobar que se generan los archivos parquet intermedios y que se suben a HDFS.

## Ejecución de la capa Oro

1. Abrir [oro/combinacion.ipynb](oro/combinacion.ipynb).
2. Ejecutar las celdas en orden.
3. La última celda genera el dashboard interactivo y crea el archivo `oro/data/dashboard_df_consolidado.html`.

También puedes abrir directamente el dashboard en el navegador desde:

- [oro/data/dashboard_df_consolidado.html](oro/data/dashboard_df_consolidado.html)

## Cómo publicar o reutilizar el dashboard

El dashboard final no necesita servidor Python para visualizarse. Se puede:

- Abrir directamente el archivo HTML generado.
- Regenerarlo ejecutando la última celda de [oro/combinacion.ipynb](oro/combinacion.ipynb).
- Volver a crear el HTML ejecutando [oro/dashboard_df_consolidado.py](oro/dashboard_df_consolidado.py).

## Qué permite filtrar el dashboard

- Provincia.
- Estación.
- Rango de fechas.
- Tipo de día.
- Fuente de generación: ambas, solo eólica o solo hidráulica.

## Flujo de trabajo recomendado

1. Levantar HDFS con Docker.
2. Ejecutar la capa Plata para obtener los datos procesados.
3. Ejecutar la capa Oro para consolidar y generar el dashboard.
4. Abrir el HTML generado o el notebook de Oro para analizar los resultados.

## Notas importantes

- El archivo consolidado final se guarda como `oro/data/datos_consolidados.parquet`.
- Si cambias los datos de origen, vuelve a ejecutar la capa Plata y luego la capa Oro.
- Si el dashboard no refleja cambios recientes, regenera el HTML desde el notebook de Oro.

## Solución rápida de problemas

- Si Docker no arranca, revisa que los puertos no estén ocupados.
- Si HDFS no responde, comprueba los contenedores con `docker ps`.
- Si falta un paquete Python, reinstala dependencias con `pip install -r requirements.txt`.
- Si el dashboard no abre, verifica que exista `oro/data/dashboard_df_consolidado.html`.
