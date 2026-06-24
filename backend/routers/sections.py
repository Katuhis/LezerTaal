from fastapi import APIRouter, HTTPException, Body, Depends

from exceptions import SectionNotEmptyError
from models import SectionCreate
from services.sections import db_get_sections_by_parent, db_get_section, db_create_section, db_update_section, db_delete_section
from services.auth import get_current_user

router = APIRouter(prefix="/sections", tags=["sections"])

@router.get("")
async def get_sections(user_id: str = Depends(get_current_user)):
    sections = await db_get_sections_by_parent(user_id)
    return {"result": sections}

@router.get("/{section_id}")
async def get_section(section_id: str):
    try:
        section = await db_get_section(section_id)
        return {"result": section}
    except ValueError:
        raise HTTPException(status_code=404, detail="Section not found")

@router.get("/{section_id}/children")
async def get_section_children(section_id: str, user_id: str = Depends(get_current_user)):
    sections = await db_get_sections_by_parent(user_id, section_id)
    return {"result": sections}

@router.post("", status_code=201)
async def post_section(section: SectionCreate = Body(...), user_id: str = Depends(get_current_user)):
    result = await db_create_section(
        section.title,
        user_id,
        section.parent_id)

    return {"result": str(result)}

@router.put("/{section_id}", status_code=200)
async def put_section(section_id: str, section: SectionCreate = Body(...)):
    try:
        result = await db_update_section(
            section_id,
            section.title,
            section.parent_id
        )
        return {"result": result}
    except ValueError:
        raise HTTPException(status_code=404, detail="Section not found")

@router.delete("/{section_id}", status_code=204)
async def delete_section(section_id: str):
    try:
        await db_delete_section(section_id)
    except SectionNotEmptyError:
        raise HTTPException(status_code=400, detail="Section is not empty")
    except ValueError:
        raise HTTPException(status_code=404, detail="Section not found")