import json
import os
from webbrowser import get
from src.readCSVFile import getAllTopicsList
from src.AIModel import generateBlogPost
from src.fileop import saveFile
from src.comfyui import generate_image_thumbnail, unload_models
from datetime import datetime
from src.blogschema import BlogPostSchema
from dotenv import load_dotenv

load_dotenv()

THUMBNAIL_IMAGE_BASE_URL = os.getenv("THUMBNAIL_IMAGE_BASE_URL")
BLOG_TEMPLATE_FILE = "./data/blog_template.txt"


def getDate():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %I:%M:%S %p")
    return formatted_time


def getBlogTemplate() -> str:
    with open(BLOG_TEMPLATE_FILE, "r") as file:
        template_content = file.read()
    finalPrompt = template_content
    return finalPrompt


def formatBlogMDX(
    blog_title: str,
    blog_keywords: str,
    blog_content: str,
    blog_description: str,
    slug: str,
) -> str:
    now = datetime.now()
    blog_formatted_time = now.strftime("%Y-%m-%d")

    mdx_template = getBlogTemplate().format(
        slug=slug,
        blog_title=blog_title,
        blog_formatted_time=blog_formatted_time,
        blog_keywords=blog_keywords,
        THUMBNAIL_IMAGE_URL=f"{THUMBNAIL_IMAGE_BASE_URL}{slug}_thumbnail_1.webp",
        blog_content=blog_content,
        blog_description=blog_description,
    )

    return mdx_template


## Main Script to generate blog posts from topics list

topics = getAllTopicsList()
print("Got Topics List from CSV")


for topic in topics:
    print("--------------------------------------------------")
    print(f"Starting Blog Post Generation at: {getDate()}")
    blog_topic = topic[1]
    blog_id = topic[0]
    print(f"{getDate()} Generating Blog Post for: {blog_topic}")
    blogGeneratedDate_temp = generateBlogPost(blog_topic)
    # print(blogGeneratedDate)
    blogGeneratedDate = BlogPostSchema(
        blog_title=blogGeneratedDate_temp.blog_title,
        seo_keywords=blogGeneratedDate_temp.seo_keywords,
        blog_post_markdown_content=blogGeneratedDate_temp.blog_post_markdown_content,
        prompts_for_thumbnail_image=blogGeneratedDate_temp.prompts_for_thumbnail_image,
        blog_short_description=blogGeneratedDate_temp.blog_short_description,
    )

    # Save raw blog post data as JSON
    saveFile(str(blogGeneratedDate.model_dump()), f"{blog_id}_raw.json")

    blogPost = blogGeneratedDate.blog_post_markdown_content
    blog_thumb_prompts = blogGeneratedDate.prompts_for_thumbnail_image
    blog_title = blogGeneratedDate.blog_title
    blog_keywords = blogGeneratedDate.seo_keywords
    blog_description = blogGeneratedDate.blog_short_description

    # Save Blog Post as MDX file
    blogMDX = formatBlogMDX(
        blog_title=blog_title,
        blog_keywords=blog_keywords,
        blog_content=blogPost,
        blog_description=blog_description,
        slug=blog_id,
    )

    saveFile(blogMDX, f"{blog_id}.mdx")
    print(f"{getDate()}Saved Blog Post to {blog_id}.mdx")

    # Generate Thumbnail Image using Z-Image
    for idx, prompt in enumerate(blog_thumb_prompts):
        print(f"{getDate()} Generating Thumbnail Image {idx + 1} with prompt: {prompt}")
        # Call ComfyUI to generate image
        generate_image_thumbnail(
            f"output/{blog_id.replace(' ', '_').lower()}_thumbnail_{idx + 1}", prompt
        )
    unload_models()
    print(f"Generated Blog Post: {blog_topic}")
    print(f"Completed Blog Post Generation at: {getDate()}")
    print("--------------------------------------------------")




