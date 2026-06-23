from supabase import create_client

url = "https://qyounjfxmkdtowzbltcy.supabase.co"

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF5b3VuamZ4bWtkdG93emJsdGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDE0NTcsImV4cCI6MjA5NzcxNzQ1N30.p8YFIRABhE_boFanM6044pudQ_JntaWy7sLNFMY-kVU"

supabase = create_client(url, key)
