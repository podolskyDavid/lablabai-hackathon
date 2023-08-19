from supabase import create_client, Client
from task import Task
from pandas import DataFrame


url: str = "https://eiruqjgfkgoknuhihfha.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpcnVxamdma2dva251aGloZmhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI0MzQxNTcsImV4cCI6MjAwODAxMDE1N30.HKZHbuiB2r8NN367J0LkD2UgwhaqJS2f0Ux9ezCFETA"
supabase: Client = create_client(url, key)
table = supabase.table("db_steps")
bucket = supabase.storage.from_('bucket_steps')


def client():
    return supabase

def new_task(user_id: str, initial_df: DataFrame, initial_df_frontend: DataFrame | None = None):
    """ Create a new task for a new initial_df DataFrame or retrieve an existing task with task_id """
    return Task(user_id, None, initial_df, initial_df_frontend)


def get_task(user_id: str, task_id: int):
    """ Retrieve an existing task with task_id """
    return Task(user_id, task_id)
