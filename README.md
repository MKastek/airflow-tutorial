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
