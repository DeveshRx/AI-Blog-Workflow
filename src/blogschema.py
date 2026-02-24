from pydantic import BaseModel
from enum import Enum


class BlogPostSchema(BaseModel):
    blog_post_markdown_content: str
    blog_title: str
    blog_short_description: str
    seo_keywords: str
    prompts_for_thumbnail_image: list[str]


class RunMode(Enum):
    GENERATE_BLOG_POST_WITH_THUMBNAIL = 1
    GENERATE_BLOG_POST_TEXT = 2
    GENERATE_THUMBNAIL_IMAGE = 3
    
    