"""
Kairós Multimodal API Routes
Handles voice, image, and document upload + processing.
"""
import base64
import json
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant
from app.multimodal.engine import MultimodalEngine, MultimodalInput

logger = logging.getLogger("kairos.multimodal")

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


async def resolve_tenant(
    request: Request,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    api_key = authorization[7:]
    result = await db.execute(
        select(Tenant).where(Tenant.api_key == api_key, Tenant.is_active == True)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")
    request.state.tenant = tenant
    return tenant


class MultimodalRequest(BaseModel):
    message: str = ""
    audio_base64: str = ""
    images: list = []
    documents: list = []
    conversation_id: str = ""
    app_slug: str = ""
    language: str = "pt-BR"
    tts_response: bool = False


class MultimodalResponse(BaseModel):
    content: str
    audio_base64: str = ""
    conversation_id: str = ""


@router.post("/chat")
async def multimodal_chat(
    req: MultimodalRequest,
    request: Request,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    engine: MultimodalEngine = container.multimodal_engine

    inp = MultimodalInput()
    inp.text = req.message
    inp.audio_base64 = req.audio_base64
    inp.images = req.images
    inp.documents = req.documents
    inp.conversation_id = req.conversation_id
    inp.app_slug = req.app_slug
    inp.language = req.language

    processed = engine.process_input(inp)
    text = processed.text

    context_key = f"api:{tenant.id}"
    ctx = container.context_manager.get(context_key)
    if not ctx:
        ctx = container.context_manager.build(
            tenant_id=str(tenant.id),
            tenant_name=tenant.name,
            tenant_slug=tenant.slug,
            user_id="api-user",
            user_name="API User",
            user_email="api@kairos.local",
            app_slug=req.app_slug or "default",
        )
        container.context_manager.set(context_key, ctx)

    result = await container.orchestrator.process_message(
        message=text,
        context_key=context_key,
        conversation_id=req.conversation_id,
    )

    out = engine.process_output(
        text=result["content"],
        conversation_id=result["conversation_id"],
        tts=req.tts_response,
    )

    return MultimodalResponse(
        content=out.text,
        audio_base64=out.audio_base64,
        conversation_id=out.conversation_id,
    )


@router.post("/voice")
async def voice_chat(
    audio: UploadFile = File(...),
    conversation_id: str = Form(""),
    app_slug: str = Form(""),
    language: str = Form("pt-BR"),
    request: Request = None,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    engine: MultimodalEngine = container.multimodal_engine

    audio_bytes = await audio.read()
    b64 = base64.b64encode(audio_bytes).decode()

    inp = MultimodalInput()
    inp.audio_base64 = b64
    inp.conversation_id = conversation_id
    inp.app_slug = app_slug
    inp.language = language

    processed = engine.process_input(inp)

    context_key = f"api:{tenant.id}"
    ctx = container.context_manager.get(context_key)
    if not ctx:
        ctx = container.context_manager.build(
            tenant_id=str(tenant.id),
            tenant_name=tenant.name,
            tenant_slug=tenant.slug,
            user_id="api-user",
            user_name="API User",
            user_email="api@kairos.local",
            app_slug=app_slug or "default",
        )
        container.context_manager.set(context_key, ctx)

    result = await container.orchestrator.process_message(
        message=processed.text,
        context_key=context_key,
        conversation_id=conversation_id,
    )

    out = engine.process_output(result["content"], result["conversation_id"], tts=True)
    return JSONResponse({
        "transcription": processed.text,
        "content": out.text,
        "audio_base64": out.audio_base64,
        "conversation_id": out.conversation_id,
    })


@router.post("/vision")
async def vision_analyze(
    file: UploadFile = File(...),
    prompt: str = Form("Descreva esta imagem em detalhes."),
    request: Request = None,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    engine: MultimodalEngine = container.multimodal_engine

    file_bytes = await file.read()
    b64 = base64.b64encode(file_bytes).decode()

    result = engine.vision._analyze(b64, prompt)
    return result


@router.post("/document")
async def document_process(
    file: UploadFile = File(...),
    action: str = Form("read"),
    request: Request = None,
    tenant=Depends(resolve_tenant),
):
    from kairos_vision.document_reader import DocumentReader
    container = request.app.state.container
    engine: MultimodalEngine = container.multimodal_engine

    file_bytes = await file.read()
    saved = engine.save_upload(file_bytes, file.filename)

    reader = DocumentReader()
    doc = reader.read(saved["path"])
    if "error" in doc:
        return doc

    if action == "summarize" and doc.get("text"):
        summary = reader.summarize(saved["path"], engine.or_key)
        return {"filename": file.filename, **summary}

    return {"filename": file.filename, **doc}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    request: Request = None,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    engine: MultimodalEngine = container.multimodal_engine
    file_bytes = await file.read()
    saved = engine.save_upload(file_bytes, file.filename)
    return saved


@router.get("/voice/devices")
async def list_audio_devices():
    try:
        from kairos_voice.microphone import list_microphones
        return {"devices": list_microphones()}
    except Exception as e:
        return {"error": str(e), "devices": []}
