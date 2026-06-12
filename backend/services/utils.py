from models import TextResponse, SectionResponse


def serialize_text(text):
    return TextResponse(
        _id=str(text['_id']),
        title=text['title'],
        content=text['content'],
        language=text['language'],
        section_id=str(text['section_id']) if text['section_id'] else None,
        created_at=str(text['created_at'])
    )

def serialize_section(section):
    return SectionResponse(
        _id=str(section['_id']),
        title=section['title'],
        parent_id=str(section['parent_id']) if section['parent_id'] else None,
        created_at=str(section['created_at'])
    )