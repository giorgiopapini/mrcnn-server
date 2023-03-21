from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Security
from fastapi.security import APIKeyQuery
from fastapi.responses import StreamingResponse
from typing import List
from custom.classes import Wound, Mask
from custom.responses import MultipleModelsWoundsResponse, MultipleModelsMasksResponse
import models
import uvicorn


# IMPORTANTE!! --> Capire come accettare anche immagini di tipo .jpg

# IMPORTANTE!! --> Per salvare i dati posso usare delle HASHING FUNCTION, rendono il contenuto illeggibile, però unico.
# in questo modo, quando un api_token viene inviato, il suo hash viene confrontato con gli hash presenti nel db, se esiste allora
# procede 

# IMPORTANTE!! --> Inviare l'API KEY in chiaro in questo modo nel link non è ottimale, probabilmente (JWT) potrebbe servire per 
# mascherare la key --> IN REALTA' SE NE OCCUPA (https) DI MASCHERARE E CIFRARE LA COMUNICAZIONE, JWT NON MI SERVE PER L'API

# IMPORTANTE!! --> Valutare se eliminare le immagini una volta inviata la response all'utente

# https://dev.to/rajshirolkar/fastapi-over-https-for-development-on-windows-2p7d

# Render dashboard https://dashboard.render.com/web/srv-cgcvglndvk4htnqm38rg/deploys/dep-cgd05je4dad6fr7vbhkg


app = FastAPI(
    title="WoundDetector"
)
models.load_mrcnn_model()


api_key_query = APIKeyQuery(name="api-key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_query)) -> str:
    if api_key == '000':
        return api_key

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


# API produce le maschere, il server della WEBAPP le salva nel local storage


# https://fastapi.tiangolo.com/tutorial/query-params/