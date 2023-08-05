from supabase.client import create_client, Client
from gotrue.types import UserAttributes
from custom.classes import User

# real
url: str = "https://rlotjjxjztdosrroisez.supabase.co"
#url: str = "https://gggkpkbgharvhmhjsgko.supabase.co"

#real
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsb3RqanhqenRkb3Nycm9pc2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTA4OTg5NjcsImV4cCI6MjAwNjQ3NDk2N30.NgdT8oneO5-eQV6Z2mKkxGvdkb7DWl5DSNxBOWqhbeI"
#key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZ2twa2JnaGFydmhtaGpzZ2tvIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTEwNDQ1NjEsImV4cCI6MjAwNjYyMDU2MX0.i9ZcX6Kf5vlRQLyw0LkSAPU6X5mDiBkJ-EmGmyIbeSY"
supabase: Client = create_client(url, key)


def select():
    res = supabase.table("Prova").select("*").execute()
    print(res)

def try_sign_up(user: User):
    try:
        supabase.auth.sign_up(email=user.email, password=user.password, data=user.dict())
        return True
    except:
        return False

def try_send_recovery_email(email: str):
    try:
        supabase.auth.api.reset_password_for_email(email=email)
        return True
    except:
        return False

def try_update_password(token:str, password: str):
    try:
        attrs = UserAttributes(password=password)
        supabase.auth.api.update_user(attributes=attrs, jwt=token)
        return True
    except:
        return False

def try_sign_in(email: str, password: str):
    try:
        supabase.auth.sign_in(email=email, password=password)
        return True
    except:
        return False
    
def try_sign_out():
    try:
        supabase.auth.sign_out()
        return True
    except:
        return False
    
def get_current_user():
    return supabase.auth.current_user