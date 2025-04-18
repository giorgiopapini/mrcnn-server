from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Security, Request, Body
from fastapi.security import APIKeyQuery
from fastapi.responses import RedirectResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from custom.classes import User, Wound, Mask
from custom.responses import MultipleModelsWoundsResponse, MultipleModelsMasksResponse
from starlette.templating import Jinja2Templates
import models
import database
from custom import functions
import functools


MAXIMUM_API_KEYS = 3

# IMPORTANTE!! --> Capire come accettare anche immagini di tipo .jpg

# IMPORTANTE!! --> Per salvare i dati posso usare delle HASHING FUNCTION, rendono il contenuto illeggibile, però unico.
# in questo modo, quando un api_token viene inviato, il suo hash viene confrontato con gli hash presenti nel db, se esiste allora
# procede????? (fare davvero in questo modo??)


# IMPORTANTE!! --> Eliminare le immagini una volta inviata la response all'utente

# https://dev.to/rajshirolkar/fastapi-over-https-for-development-on-windows-2p7d


# IMPORTANTE!!! --> Creare endpoint che ritorni il rapporto pixel cm data un'immagine contenente un aruco marker, e le dimensioni
#                   dell'aruco marker e il tipo di aruco marker --> Da valutare il fatto che le immagini possono essere 
#                   "resized" in fase di visualizzazione, e quindi il rapporto cm/pixel cambierebbe


# uvicorn api:app --host 0.0.0.0 --port 8000 --reload

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="WoundDetector"
)
models.load_mrcnn_model()


# UI enpoints
def protected_route(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = database.get_current_user_metadata()
        if user:
            return func(*args, **kwargs)
        else:
            return RedirectResponse(url="/sign-in")
    return wrapper



@app.get("/home", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

@app.get("/sign-in", include_in_schema=False)
def sign_in_get(request: Request):
    return templates.TemplateResponse("sign-in.html", {"request": request})

@app.post("/sign-in", include_in_schema=False)
def sign_in(request: Request, email: str = Form(...), password: str = Form(...)):
    if not database.try_sign_in(email, password):
        raise HTTPException(status_code=302, detail='Wrong credentials')

@app.get("/sign-up", include_in_schema=False)
def sign_up_get(request: Request):
    return templates.TemplateResponse("sign-up.html", {"request": request})

@app.post("/sign-up", include_in_schema=False)
def sign_up(request: Request, user: User):
    if not database.try_sign_up(user):
        raise HTTPException(status_code=302, detail='Could not sign up')

@app.post("/sign-out", include_in_schema=False)
def sign_out(request: Request):
    if not database.try_sign_out():
        raise HTTPException(status_code=302, detail='Could not sign out')
    
@app.get("/recover", include_in_schema=False)
def recover(request: Request):
    return templates.TemplateResponse("recover.html", {"request": request})

@app.get("/update-password", include_in_schema=False)
def update_password_get(request: Request):
    return templates.TemplateResponse("update-password.html", {"request": request})

@app.post("/update-password", include_in_schema=False)
def update_password_post(request: Request, body: dict = Body(...)):
    access_token: Optional[str] = body.get("access_token", None)
    password: str = body["password"]
    if not access_token:
        if not database.try_update_password(password=password):
            raise HTTPException(status_code=404, detail="Could not update password")
    else:
        if not database.try_update_password_with_token(access_token, password):
            raise HTTPException(status_code=404, detail="Could not update password")

@app.post("/update-user-data", include_in_schema=False)
def update_user_data(request: Request, user: User):
    if functions.check_email_regex(user.email):
        if not database.try_update_email(user.email):
            raise HTTPException(status_code=409, detail="There is already an account using this email")
        if not database.try_update_profile_data(user):
            raise HTTPException(status_code=406, detail="Could not update profile data")
    else:
        raise HTTPException(status_code=422, detail="Invalid email address") 
    
@app.post("/delete-user", include_in_schema=False)
def delete_user(request: Request):
    database.try_delete_user()

@app.post("/send-recovery-email", include_in_schema=False)
def send_recovery_email(request: Request, email: str = Form(...)):
    if not database.try_send_recovery_email(email):
        raise HTTPException(status_code=404, detail="Email does not exist")

@app.get("/check-email", include_in_schema=False)
def check_email(request: Request):
    return templates.TemplateResponse("check-email.html", {"request": request})

@app.get("/success", include_in_schema=False)
def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/account-overview", include_in_schema=False)
#@protected_route
def account_overview(request: Request):
    user = database.get_current_user()
    if not user:
        return RedirectResponse(url="/sign-in")
    else:
        return templates.TemplateResponse("account-overview.html", {"request": request, **user.dict()})

@app.get("/account-settings", include_in_schema=False)
#@protected_route
def account_settings(request: Request):
    user = database.get_current_user()
    # print(database.try_sign_in(user.email, "pppp"))  # Use this in order to check if user inserted correct old password
    if not user:
        return RedirectResponse(url="/sign-in")
    else:
        return templates.TemplateResponse("account-settings.html", {"request": request, **user.dict()})

@app.get("/account-keys", include_in_schema=False)
#@protected_route
def account_keys(request: Request):
    api_keys, count = database.get_api_keys()
    api_keys_dict = [key.dict() for key in api_keys]
    print(api_keys_dict)
    return templates.TemplateResponse("account-keys.html", {"request": request, "api_keys": api_keys_dict, "api_count": count})
    
@app.post("/account-keys/generate-key", include_in_schema=False)
def insert_key(request: Request, body: dict = Body(...)):
    project_name: str = body["project_name"]
    if database.get_api_keys_count() < MAXIMUM_API_KEYS:
        if not database.insert_new_api_key(project_name=project_name):
            raise HTTPException(status_code=400, detail="Could not create a new API token")
    else:
        raise HTTPException(status_code=400, detail="You have reached the maximum amount of API keys (3 API keys)")



# API endpoints
api_key_query = APIKeyQuery(name="api-key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_query)) -> str:
    if database.api_exists(api_key):
        if not database.token_exceeds_calls_limit(api_key):
            database.increment_calls_count(api_key)
            return api_key
        else:
            raise HTTPException(
            status_code=401,
            detail='API calls limit exceeded'   
        )
    else:
        raise HTTPException(
            status_code=401,
            detail='Invalid or missing API key'
        )


@app.post("/mrcnn/mask-image/")
async def calculate_mrcnn_mask_image(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
) -> StreamingResponse:
    mrcnn_img = models.get_mrcnn_mask_img(file, api_key)
    return StreamingResponse(mrcnn_img.to_bytes(), media_type="image/png")

@app.post("/mrcnn/mask/")
async def calculate_mrcnn_masks(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
) -> List[Mask]:
    mrcnn_img = models.get_mrcnn_mask_img(file, api_key)
    return mrcnn_img.masks

@app.post("/mrcnn/wounds/")
async def calculate_mrcnn_wounds_from_image(
    api_key: str = Security(verify_api_key),
    ratio: float = Form(...),
    file: UploadFile = File(...)
) -> List[Wound]:
    mask_img = models.get_mrcnn_mask_img(file, api_key)
    return models.get_wounds_from_mask_img(mask_img, ratio)


@app.post("/grabcut/mask-image/")
async def calculate_grabcut_mask_image(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
) -> StreamingResponse:
    grabcut_img = models.get_grabcut_mask_img(file, api_key)
    return StreamingResponse(grabcut_img.to_bytes(), media_type="image/png")

@app.post("/grabcut/mask/")
async def calculate_grabcut_masks(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
) -> List[Mask]:
    grabcut_mask = models.get_grabcut_mask_img(file, api_key)
    return grabcut_mask.masks

@app.post("/grabcut/wounds/")
async def calculate_grabcut_wounds_from_image(
    api_key: str = Security(verify_api_key),
    ratio: float = Form(...),
    file: UploadFile = File(...)
) -> List[Wound]:
    mask_img = models.get_grabcut_mask_img(file, api_key)
    return models.get_wounds_from_mask_img(mask_img, ratio)



@app.post("/all-models/mask-image/")
async def calculate_all_model_masks_images(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
):
    mrcnn_img, grabcut_img = models.get_mrcnn_and_grabcut_masks_img(file, api_key)
    ...

@app.post("/all-models/mask/")
async def calculate_all_model_masks(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...)
) -> MultipleModelsMasksResponse:
    mrcnn, grabcut = models.get_mrcnn_and_grabcut_masks_img(file, api_key)
    return MultipleModelsMasksResponse(
        mrcnn_masks=mrcnn.masks,
        grabcut_masks=grabcut.masks
    )

@app.post("/all-models/wounds/")
async def calculate_all_model_wounds(
    api_key: str = Security(verify_api_key),
    ratio: float = Form(...),
    file: UploadFile = File(...)
) -> MultipleModelsWoundsResponse:
    mrcnn, grabcut = models.get_mrcnn_and_grabcut_masks_img(file, api_key)
    mrcnn_wounds = models.get_wounds_from_mask_img(mrcnn, ratio)
    grabcut_wounds = models.get_wounds_from_mask_img(grabcut, ratio)
    return MultipleModelsWoundsResponse(
        mrcnn_wounds=mrcnn_wounds,
        grabcut_wounds=grabcut_wounds
    )


@app.post("/custom-mask/wounds/")
async def calculate_wounds_from_inserted_mask_image(
    api_key: str = Security(verify_api_key),
    ratio: float = Form(...),
    file: UploadFile = File(...)
) -> List[Wound]:
    return models.get_wounds_from_mask_file(file, ratio)

@app.post("/custom-mask/grabcut-mask")
async def calculate_grabcut_mask_from_custom_mask(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...),
    mask: UploadFile = File(...)
) -> StreamingResponse:  
    grabcut_mask = models.get_grabcut_from_mask(file, mask)
    return StreamingResponse(grabcut_mask.to_bytes(), media_type="image/png")

# API produce le maschere, il server della WEBAPP le salva nel local storage


# https://fastapi.tiangolo.com/tutorial/query-params/