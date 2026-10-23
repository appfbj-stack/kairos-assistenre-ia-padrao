from fastapi import APIRouter

router = APIRouter(prefix=" /api/vault\, tags=[\vault\])

@router.get(\/notes\)
async def list_notes():
 return {\notes\: [], \total\: 0}
