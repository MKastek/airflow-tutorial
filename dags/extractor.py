from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from pendulum import datetime
from airflow.datasets import Dataset

DATASET_COCKTAIL = Dataset('/tmp/cocktail.json')

def _get_cocktail(ti=None):
    import requests
    
    api = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    response = requests.get(api)
    with open(DATASET_COCKTAIL.uri, "wb") as f:
        f.write(response.content)
    ti.xcom_push(key='request_size', value=len(response.content))
        
def _check_size(ti=None):
    size = ti.xcom_pull(key='request_size', task_ids='get_cocktail')
    print(size)

@dag(
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    catchup=False
)
def extractor():
    
    get_cocktail = PythonOperator(
        task_id='get_cocktail',
        python_callable=_get_cocktail,
        outlets=[DATASET_COCKTAIL]
    )
    
    check_size = PythonOperator(
        task_id='check_size',
        python_callable=_check_size
    )
    
    get_cocktail >> check_size
    
extractor()