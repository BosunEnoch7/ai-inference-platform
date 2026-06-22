from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_inference_service
from app.api.rate_limit import enforce_rate_limit
from app.api.security import verify_api_key
from app.models.inference import InferenceRequest, InferenceResponse
from app.services.inference import InferenceService

router = APIRouter()


@router.post(
    "/inference",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Run text inference",
)
async def infer(
    request: InferenceRequest,
    _: Annotated[None, Depends(verify_api_key)],
    __: Annotated[None, Depends(enforce_rate_limit)],
    service: Annotated[InferenceService, Depends(get_inference_service)],
) -> InferenceResponse:
    return await service.infer(request)
