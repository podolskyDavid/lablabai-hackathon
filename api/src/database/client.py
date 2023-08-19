from supabase import create_client, Client

url: str = "https://eiruqjgfkgoknuhihfha.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpcnVxamdma2dva251aGloZmhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI0MzQxNTcsImV4cCI6MjAwODAxMDE1N30.HKZHbuiB2r8NN367J0LkD2UgwhaqJS2f0Ux9ezCFETA"
supabase: Client = create_client(url, key)
table = supabase.table("db_steps")
bucket = supabase.storage.from_('bucket_steps')
