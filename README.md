# Airflow  

## Data orchestration
Data orchestration is the process of coordinating and automating the movement, transformation, and integration of data across various systems and processes to ensure efficient and reliable data workflows.  

## Airflow installation 
`apache-airflow-core` is the core distribution package of Apache Airflow. It contains the essential components needed for a minimal Airflow installation: 
- the scheduler, 
- the webserver (API server / UI), 
- the DAG file processor, 
- the triggerer.

## General DAG template  
```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    description='my dag does that',
    tags=['team'],
    catchup=False
)
def my_dag():

    @task
    def extract():
        return 42

    @task
    def transform(val):
        return val + 42

    @task
    def load(val):
        print(val)

    load(transform(extract()))


my_dag()
```

### Core components 
- Web server (serves the user interface)
- User Interface 
- Meta data, Meta data database (contains meta data)
- Tasks
- Scheduler (schedules tasks while checking dependencies are met)
- Executor (defines how and on which system execute tasks Kubernetes, local machine)
- Worker (executes your tasks)
- Triggerer (used for a special type of tasks)

#### Task
Task is the basic unit of execution. 

#### Operator   
Operator is predefined task template.

#### DAG (Directed Acyclic Graph)

#### How does Airflow work?  
##### Creating and scheduling a DAG:

- Create a new DAG (e.g., middag.py)

- Add the DAG file to the DAGs directory

#### Scheduler process:

- Scans DAGs directory every 5 minutes (default)
- Detects new DAG file
- Serializes the DAG into the Metadatabase (stores DAG code for faster/easier access)

#### DAG execution flow:

- Scheduler checks if DAG is ready to run → creates a DAG run (instance of DAG at a specific time)
- DAG run has different states (e.g., running, success, failed)

#### Task execution flow:

- Scheduler identifies tasks → creates task instances
- Task instances also have different states
- Scheduler sends task instances to the executor
- Executor pushes task instances into a queue (invisible but essential)
- State changes to queued (updated in Metadatabase)
- Worker process picks task instance from queue and executes it
- State changes to running
- When execution finishes, worker updates task instance state in Metadatabase (e.g., success)

#### Final steps:

- Scheduler checks if more tasks need to run
- DAG run is marked success or failed based on task instance states
- User can monitor everything via the Airflow UI  
 

 
#### Airflow limitations:  

#### Airflow commands:  
Check if the metadata database can be reached  
`airflow db check`  

Purge old records in database tables in archive tables  
`airflow db clean`  

Export archived data from the archive tables (default csv)  
`airflow db export-archived`

Initialize the database  
`airflow db init`  

Run subsections of a DAG for specified data range  
`airflow dags backfill my_dag --reset-dagrun --rerun-failed-tasks --run-backwards -s 2024-01-01 -e 2024-01-10`  

Re-sync DAGs  
`airflow dags reserialize`  

List all the DAGs  
`airflow dags list`

Test a task instance  
`airflow tasks test my_dag my_task 2024-01-01`


### Astro commands  
Start  
`astro dev start`  

Stop  
`astro dev stop`    

Test  
`astro dev run tasks test dag_id`

### Airflow hooks   
In Apache Airflow, a hook is an interface that allows Airflow to connect and interact with external systems or services, such as databases, APIs, cloud providers (AWS, GCP, Azure), file systems, or any other data source.
A hook is an abstraction layer over an external service.  

It encapsulates connection logic, authentication, and methods for performing operations, so developers don’t have to reimplement those details every time.    

BaseHook is the abstract base class from which all other hooks in Airflow inherit. 
#### The main responsibilities of BaseHook:
**Connection Management**  
It provides the method `get_connection(conn_id)` that retrieves a connection from Airflow’s metadata database:  
```python
conn = BaseHook.get_connection('my_postgres')
print(conn.host, conn.login, conn.password)
```
Example of custom Hook to connect to api:
```python
from airflow.hooks.base import BaseHook
import requests

class MyApiHook(BaseHook):
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id
        self.conn = self.get_connection(conn_id)
        self.base_url = self.conn.host

    def get_data(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, auth=(self.conn.login, self.conn.password))
        response.raise_for_status()
        return response.json()
```
### Migrating to Airflow task flow 

### XCOM

### Airflow providers

### Notifier  


### Creating DAGs  
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(...)  

ta = PythonOperator(task_id='ta',dag=dag)
tb = PythonOperator(task_id='tb',dag=dag)
```  
#### Context manager  
```python 
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(...):
    ta = PythonOperator(task_id='ta')
    tb = PythonOperator(task_id='tb')
```
#### dag decorator  
DAG id will be the name of the function.
```python 
from airflow.decorators import dag
from airflow.operators.python import PythonOperator

@dag
def my_dag():
    ta = PythonOperator(task_id='ta')
    tb = PythonOperator(task_id='tb')

my_dag()
```
### Backfill and catchup  
In Apache Airflow, `catchup` is a setting that controls whether Airflow should run all past DAG runs that were missed (based on the DAG’s `start_date` and `schedule`) when you first start or unpause a DAG.    

In Apache Airflow, backfill means running a DAG for past (historical) dates or schedules that were missed — usually to “fill in” data gaps or reprocess older time periods.  
```bash
airflow dags backfill -s 2025-11-01 -e 2025-11-05 example_dag
```

### Airflow variable `data_interval_end`
`data_interval_end` can be used to replace `NOW()` in SQL queries, `data_interval_end` is the date of the current DAG Run. Airflow variable `data_interval_end` makes your DAG idempotent.  


### Timezones in Airflow  
By default, everything in Airflow is displayed in UTC.   

### Datasets   
Dataset in Airflow is a pointer to some resources.  

Producer of dataset:
```python
from airflow import dataset

file = Dataset("/tmp/data.txt")

@dag(...)
def my_dag():
  def task_a(outlets=[file]):
    with open(file.uri,'a') as f:
        f.write("producer update")
```
Consumer of dataset:
```python
from airflow import dataset

file = Dataset("/tmp/data.txt")

@dag(...)
def my_dag(schedule=[file]):
  def task_b():
      print("consumer")
    
```

### Conditional Dataset Scheduling    
Wait for both dataset a and b.
```python
from airflow import dataset

a = Dataset("data_a")
b = Dataset("data_b")

@dag(...)
def my_dag(schedule=[a,b]):
    ...
```
Wait for dataset a aor b.
```python
from airflow import dataset

a = Dataset("data_a")
b = Dataset("data_b")

@dag(...)
def my_dag(schedule=(a | b)):
    ...
```