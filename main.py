# File: main.py
# import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from models.model_loader import load_all_models, predict_image, MODEL_REGISTRY
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


loaded_models_dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_models_dict
    loaded_models_dict = load_all_models()
    yield
    loaded_models_dict.clear()

app = FastAPI(title="Demo Luận Văn CBM", lifespan=lifespan)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class MetricsSchema(BaseModel): 
    size: str

class ResponseModel(BaseModel):
    model_key: str
    model_name: str
    prediction: str
    confidence: float
    inference_time_ms: float
    metrics: MetricsSchema
    concepts: dict | None = None
    top_3: list
    group_label: str | None = None
    ref_metrics: dict | None = None

# Trả về danh sách để Frontend vẽ Checkbox (gom nhóm theo giai đoạn + backbone)
@app.get("/models")
async def get_models():
    # Chỉ trả về những mô hình đã thực sự được nạp thành công vào RAM
    out = []
    for k in loaded_models_dict.keys():
        info = MODEL_REGISTRY[k]
        out.append({
            "key": k,
            "name": info["name"],
            "group": info["group"],
            "group_label": info["group_label"],
            "group_order": info["group_order"],
            "backbone": info["backbone"],
            "backbone_label": info["backbone_label"],
            "is_cbm": info["is_cbm"],
            "size": info["size"],
            "ref_metrics": info["ref_metrics"],
        })
    out.sort(key=lambda m: (m["group_order"], m["backbone_label"]))
    return out

@app.post("/predict", response_model=ResponseModel)
async def predict(model_key: str = Form(...), file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = predict_image(model_key, loaded_models_dict, image_bytes)
    info = MODEL_REGISTRY[model_key]

    return ResponseModel(
        model_key=model_key,
        model_name=info["name"],
        group_label=info["group_label"],
        ref_metrics=info["ref_metrics"] or None,
        **result
    )
@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")