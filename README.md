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
XCOM is identified by key.  
![img.png](img.png)  

```python
from airflow.sdk import dag,task,Context  

@dag
def xcom_dag():
    @task
    def task_a(**context: Context):
        val = 42
        context['ti'].xcom_push(key='my_key', value=val)

    @task
    def task_b(**context: Context):
        val = context['ti'].xcom_pull(task_ids='task_a',key='my_key')
        print(val)

    task_a() >> task_b()
    
xcom_dag()
```
Equivalent methods of pushing and pulling xcom in taskflow approach.
```python
from airflow.sdk import dag,task,Context  

@dag
def xcom_dag():
    @task
    def task_a():
        val = 42
        return val #.xcom_push(key='return_value', value=val)

    @task
    def task_b(val: int):
        print(val)

    val = task_a()
    task_b(val)
    
xcom_dag()
```
Equivalent method without parsing the context.
```python
from airflow.sdk import dag,task,Context  

@dag
def xcom_dag():
    @task
    def task_a(ti):
        val = 42
        ti.xcom_push(key='my_key', value=val)

    @task
    def task_b(ti):
        val = ti.xcom_pull(task_ids='task_a',key='my_key')
        print(val)

    task_a() >> task_b()
    
xcom_dag()
```
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

### Sharing data between task with XComs  
`XCom` (short for `Cross-Communication`) is Airflow’s built-in mechanism for sharing data between tasks within a DAG run.     
Each task can **push** or **pull** small pieces of data to/from the Airflow **metadata database**.  
XComs are persisted in Airflow’s metadata database (xcom table).  
Each entry includes:
- DAG ID, task ID, execution date  
- `key`  
- `value` (serialized — by default `JSON` or `pickled`)  

### XCom Backend


### Callbacks: `on_success_callback` vs `on_failure_callback`  
Callback works both on dag and task  
```python
from airflow import dataset
from airflow.decorators import dag

def handle_failed_dag_run(context):
    print(f"Dag run failed with {context["task_instance"].task_id}")
    

@dag(
    on_failure_callback = handle_failed_dag_run
)
def my_dag():
  def task_b():
      print("consumer")
    
```
### Airflow CLI testing  

### How to test dag locally  

### Task group   
In Apache Airflow, a TaskGroup is a UI-only organizational feature that lets you visually group related tasks together in the Airflow graph view.  
It does not change scheduling, execution order, or task behavior—it simply makes large DAGs cleaner and easier to navigate.


```python
from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id="taskgroup_example",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
) as dag:

    @task
    def start():
        pass

    @task
    def end():
        pass

    with TaskGroup("processing_steps") as processing:
        @task
        def extract():
            pass

        @task
        def transform():
            pass

        @task
        def load():
            pass

        extract() >> transform() >> load()

    start() >> processing >> end()
```
### Task with branching    
Task branching in Apache Airflow allows you to choose which downstream tasks run based on a condition.  
Branching is similar to an if/else statement for your DAG.  
```python
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from datetime import datetime

@dag(start_date=datetime(2023,1,1), schedule="@daily")
def taskflow_branching():

    @task.branch
    def pick_branch():
        return "right_path"

    left_path = EmptyOperator(task_id="left_path")
    right_path = EmptyOperator(task_id="right_path")

    end = EmptyOperator(task_id="end", trigger_rule="none_failed_or_skipped")

    pick_branch() >> [left_path, right_path] >> end

dag = taskflow_branching()
```

### Trigger rules 
In Apache Airflow, Trigger Rules define when a task should run based on the state of its upstream tasks.  
By default, Airflow uses all_success, meaning a task runs only if every parent task succeeded.  
But trigger rules let you change that behavior—super useful for branching, error handling, retries, and cleanup tasks.    

| Trigger Rule   | Fires When…                         |
|----------------|-------------------------------------|
| all_success    | All upstream succeeded              |
| all_failed     | All upstream failed                 |
| one_success    | At least one succeeded              |
| one_failed     | At least one failed                 |
| all_done       | All upstream finished (any state)   |
| none_failed    | No upstream failed                  |
| none_skipped   | No upstream skipped                 |
| always         | Always runs                         |

```python
from airflow.utils.trigger_rule import TriggerRule

@task(trigger_rule=TriggerRule.ALL_FAILED)
def on_failure():
    print("Runs only if ALL upstream tasks fail")
```

### Templating tasks       
Templating allows you to pass dynamic information into task instances at runtime.  
The Airflow engine passed a few variables by default like start date.
```python
execute_query = SQLExecuteQueryOperator(
    task_id="execute_query",
    sql="SELECT * FROM my_table WHERE date = {{ ds }}",
    return_last=False,
)
```
```python
@task(trigger_rule=TriggerRule.ALL_FAILED, templates_dict={'the_current_date': '{{ ds }}'})
def on_failure():
    print(f"Runs only if ALL upstream tasks fail on {templates_dict['the_current_date']} ")
```

### XCom Backend  
An XCom backend in Airflow is a pluggable system that stores and retrieves task-to-task communication data (XComs) using a custom storage provider instead of the default metadata database.  
For instance it could be S3 bucket from AWS.    
In Airflow, the **storage threshold** setting defines the **maximum size of an XCom value that Airflow will store in the metadata database before switching to the XCom backend’s external storage (such as S3, GCS, or another custom backend)**.  

### Variables  
Variable is key-word object to store values. By default variables are encrypted.
```python
@task(trigger_rule=TriggerRule.ALL_FAILED, templates_dict={'the_current_date': '{{ ds }}, my_api_key: {{ var.value.api }}'})
def on_failure():
    print(f"Runs only if ALL upstream tasks fail on {templates_dict['the_current_date']} ")
    print(f"API {templates_dict['my_api_key']} ")
```
## Scaling Airflow 
### Sequential Executor  
In Apache Airflow, the SequentialExecutor is the simplest executor used to run tasks. It is primarily meant for development, testing, and debugging, not for production.      

`SequentialExecutor` is used with SQLite because SQLite cannot handle concurrent writes, and running tasks sequentially prevents database locking issues.
  
`SequentialExecutor` is an Airflow executor that runs:
- Only one task at a time  
- In a single process  
- In the same machine as the scheduler
It is the default executor when you first install Airflow in standalone mode.    

The Executor decides where and how the task should run (Kubernetes, your local machine).  

### Local Executor  
LocalExecutor is an Airflow executor that runs multiple tasks in parallel on the same machine using Python multiprocessing.  

It’s the first production-capable executor—fast, simple, and does not require Celery or Kubernetes. PostgreSQL can handle many simultaneous connections and writes safely.  

### Concurrency settings in Airflow
- **parallelism**: The maximum number of tasks that can run concurrently on each scheduler within a single Airflow environment.  
- **max_active_tasks_per_dag**: The maximum number of tasks that can be scheduled at the same time across all runs of a DAG. At the DAG level: `max_active_tasks`.
- **max_active_runs_per_dag**: Determines the maximum number of active DAG runs (per DAG) that the Airflow scheduler can create at a time. At the DAG level: `max_acitve_runs`.

### Celery Executor  
In Apache Airflow, the Celery Executor is a distributed task execution backend that uses Celery, a popular asynchronous task queue, to run Airflow tasks across multiple worker machines.  
he CeleryExecutor allows Airflow to scale out by distributing task execution to multiple workers.  

Instead of running all tasks on the same machine (like `SequentialExecutor` or `LocalExecutor`), tasks are pushed into a message queue, and multiple Celery workers pull tasks and execute them independently.

### Airflow on Kubernetes  
- The Kubernetes executor runs each task in an individual Kubernetes Pod.  
- The Kubernetes executor sends a message to the KubeAPI that creates a POD and runs the task in it.  
- When a task completes, its Pod is terminated and the resources are returned to your cluster.  
- Task are isolated from each other.  
- Task isolation allow granular resource allocation and easier dependency management.  


### The @task.short_circuit decorator  
- simple check if run / not run next task  
```python
@task.short_circuit  
def should_continue():
    if condition_met: 
        return True
    return False 
```
#### Use case:  
- simple go/no-go decisions    
- validation checkpoints    
- external dependency checks  

### DAG versioning   
DAG versioning is available in Airflow 3.0.   

### DAG Bundle  
DAG Bundle is a collection of files containing DAG code and supporting files. DAG bundles are named after the backend they use to store the DAG code.  
- they are versioned and unversioned DAG bundles  
- the default DAG bundle is the LocalDagBundle and is not versioned  
- GitDagBundles is versioned

### Asset  
An Asset is an object that is defined by a unique name. Optionally, a URI can be arrached to the asset, when it represents a concrete data entity, like a file in an object storage or a tble in db.   

```python
from airflow.sdk import Asset  

my_asset = Asset(name="my_asset", uri="file://path/my_file", group="my_group")
```
When you define an asset using the @asset taskflow decorator, Airflow actually creates a DAG with the same id in the background.  
```python
@asset(schedule="@daily", uri="file://path/my_file", group="my_group")
def my_asset():
   ... 
```  

Outlet are a task parameter that contains the list of Assets a specific tasks produces updates to, as soon as it completes successfully.  
```python
from airflow.sdk import Asset, task 

@task(outlets=[Asset("my_asset")])
def my_task():
    ...
```

Inlets are a task parameter that contains the list of Assets a specific task has access to, typically to access extra information from related dataset events. Inlets for a task do not affect the schedule of the DAG.

```python
@task(inlets=[my_asset])
def get_extra_inlet(inlet_events):
   ... 
```

#### Asset schedules  
- schedule=[Asset("a"),Asset("b")]
- schedule=(Asset("a")|Asset("b")), schedule=(Asset("a") & Asset("b"))
- schedule=AssetOrTimeSchedule()  

### Airflow environments   
```bash
airflow version
```

```bash
airflow info 
```

```bash
airflow config list
```

```bash
airflow cheat-sheet
```

```bash  
airflow variables export variables.json
```