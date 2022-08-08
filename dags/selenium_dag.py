import os
from airflow.models import DAG
from airflow.operators.selenium_plugin import SeleniumOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
import airflow.hooks.S3_hook
from selenium_scripts.wake_up_to_money import download_podcast, get_test
from datetime import datetime, timedelta
import logging

class ExtendedPythonOperator(PythonOperator):
    '''
    extending the python operator so macros
    get processed for the op_kwargs field.
    '''
    template_fields = ('templates_dict', 'op_kwargs')


def upload_file_to_S3(file_name, key, bucket_name):
    '''
    Uploads a local file to s3.
    '''
    hook = airflow.hooks.S3_hook.S3Hook('S3_conn_id')
    hook.load_file(file_name, key, bucket_name)
    logging.info(
        'loaded {} to s3 bucket:{} as {}'.format(file_name, bucket_name, key))


def remove_file(file_name, local_path):
    '''
    Removes a local file.
    '''
    file_path = os.path.join(local_path, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        logging.info('removed {}'.format(file_path))


def weekday_branch():
    '''
    Returns task_id based on day of week.
    '''
    if datetime.today().weekday() in range(0, 5):
        return 'get_podcast'
    else:
        return 'end'

date = '{{ ds_nodash }}'
file_name = 'episode_{}.mp3'.format(date)
bucket_name = 'wake_up_to_money'
key = os.path.join(bucket_name, file_name)
cwd = os.getcwd()
local_downloads = os.path.join(cwd, 'downloads')

default_args = {
    'owner': 'mecbonjourno',
    'start_date': datetime(2022, 6, 8),
    'retries': 1,
    }

dag = DAG('selenium_example_dag',
          schedule_interval='*/5 * * * *',
          catchup=False,
          default_args=default_args)

start = DummyOperator(
    task_id='start',
    dag=dag)


get_podcast = SeleniumOperator(
    script=get_test,
    script_args=['https://www.ifood.com.br/delivery/porto-alegre-rs/nacional-gomes-freitas-jardim-sabara/379b1a2c-0d53-410f-b226-187a3f29c826'],
    task_id='get_podcast',
    dag=dag)


end = DummyOperator(
    task_id='end',
    dag=dag)

start >> get_podcast >> end

# start >> weekday_branch
# weekday_branch >> get_podcast
# get_podcast >> upload_podcast_to_s3
# upload_podcast_to_s3 >> remove_local_podcast
# remove_local_podcast >> end
# weekday_branch >> end
