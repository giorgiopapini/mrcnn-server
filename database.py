from typing import List, Optional, Dict, Tuple
import uuid
import secrets
from supabase.client import create_client, Client
from postgrest.types import CountMethod
from gotrue.types import UserAttributes
from custom.classes import APIKey, User


# real
URL: str = "https://rlotjjxjztdosrroisez.supabase.co"
#url: str = "https://gggkpkbgharvhmhjsgko.supabase.co"

#real
KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsb3RqanhqenRkb3Nycm9pc2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTA4OTg5NjcsImV4cCI6MjAwNjQ3NDk2N30.NgdT8oneO5-eQV6Z2mKkxGvdkb7DWl5DSNxBOWqhbeI"
#key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZ2twa2JnaGFydmhtaGpzZ2tvIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTEwNDQ1NjEsImV4cCI6MjAwNjYyMDU2MX0.i9ZcX6Kf5vlRQLyw0LkSAPU6X5mDiBkJ-EmGmyIbeSY"

SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsb3RqanhqenRkb3Nycm9pc2V6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MDg5ODk2NywiZXhwIjoyMDA2NDc0OTY3fQ.elW_-CbtKMch1YtsZkchR3hshMmLkY8mQ_yT2z2O_oM"
supabase: Client = create_client(URL, SERVICE_ROLE)

PROFILES_TABLE_NAME: str = "profiles"
API_KEYS_TABLE_NAME: str = "api_keys"
API_PLANS_TABLE_NAME: str = "api_plans"


def database_call(fn):
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
            return True
        except:
            return False
    return wrapper

@database_call
def try_sign_up(user: User):
    supabase.auth.sign_up(email=user.email, password=user.password, data=user.dict())

@database_call
def try_send_recovery_email(email: str):
    supabase.auth.api.reset_password_for_email(email=email)

@database_call
def try_update_password_with_token(token:str, password: str):
    attrs = UserAttributes(password=password)
    supabase.auth.api.update_user(attributes=attrs, jwt=token)

def try_update_password(password: str):
    return __try_update_user_auth_data(password=password)

def try_update_email(email: str):
    current_email: str = get_current_user().email
    if email != current_email:
        return __try_update_user_auth_data(email=email)
    return True

@database_call
def __try_update_user_auth_data(**kwargs):
    attrs = UserAttributes(**kwargs)
    supabase.auth.update(attributes=attrs)

@database_call
def try_update_profile_data(user: User):
    user_id = uuid.UUID(str(get_current_user_metadata().id))
    supabase.table(PROFILES_TABLE_NAME).update(json=user.dict()).eq("id", user_id).execute()

@database_call
def try_sign_in(email: str, password: str):
    supabase.auth.sign_in(email=email, password=password)
    
@database_call
def try_sign_out():
    supabase.auth.sign_out()
    
def get_current_user_metadata():
    return supabase.auth.current_user

@database_call
def try_get_current_user():
    return get_current_user()

def get_current_user() -> User:
    user_id: uuid.UUID = uuid.UUID(str(get_current_user_metadata().id))
    result = supabase.table(PROFILES_TABLE_NAME).select("*").eq("id", user_id).execute().data[0]
    return User(**result)

def try_delete_user():
    #user_id: str = str(get_current_user_metadata().id)
    #access_token: str = supabase.auth.current_session.access_token
    #supabase.auth.api.delete_user(uid=user_id, jwt=access_token)

    res = supabase.rpc("hello_world", {})
    print(res)

    # https://github.com/orgs/supabase/discussions/5208


def generate_api_key():
    key: str = secrets.token_urlsafe(42)

@database_call
def insert_new_api_key(project_name: str):
    user: User = get_current_user()
    api_key: str = secrets.token_urlsafe(34)
    supabase.table(API_KEYS_TABLE_NAME).insert({
        "key": api_key,
        "project_name": project_name,
        "user_id": str(user.id)
    }).execute()

def get_api_keys_count() -> int:
    _, count = get_api_keys()
    return count if count is not None else 0

def get_api_keys() -> Tuple[List[APIKey], Optional[int]]:
    user: User = get_current_user()
    res = supabase.table(API_KEYS_TABLE_NAME).select("*", count=CountMethod.exact).eq("user_id", str(user.id)).execute()
    api_keys: List[APIKey] = [APIKey(**element) for element in res.data]
    return api_keys, res.count

