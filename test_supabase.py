from supabase_client import supabase

def test_connection():
    user=supabase.table("user_profile").select("*").limit(1).execute()
    print("connection established", user)

if __name__=="__main__":
    test_connection()
