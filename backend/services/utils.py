from models import TextResponse


def serialize_text(text):
    return TextResponse(
        _id=str(text['_id']),
        title=text['title'],
        content=text['content'],
        language=text['language'],
        user_id=str(text['user_id']),
        section_id=str(text['section_id']) if text['section_id'] else None,
        created_at=str(text['created_at'])
    )
    