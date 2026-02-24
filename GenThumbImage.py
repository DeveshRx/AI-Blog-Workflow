import json
import os
from pathlib import Path
from webbrowser import get
from src.readCSVFile import getAllTopicsList
from src.AIModel import generateBlogPost
from src.fileop import saveFile
from src.comfyui import generate_image_thumbnail, unload_models
from datetime import datetime
from src.blogschema import BlogPostSchema
from dotenv import load_dotenv
import ast

load_dotenv()


def getDate():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %I:%M:%S %p")
    return formatted_time


def getRAWFile(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as file:
        template_content = file.read()
    finalPrompt = template_content
    return finalPrompt


def isImageAlreadyExists(filename: str) -> bool:
    image_file = Path(filename)
    return image_file.exists()


topics = getAllTopicsList()
print("Got Topics List from CSV")


for topic in topics:
    print("--------------------------------------------------")
    print(f"Starting Blog Post Generation at: {getDate()}")
    blog_topic = topic[1]
    blog_id = topic[0]

    blog_raw_file = Path(f"output/{blog_id}_raw.json")

    if blog_raw_file.exists():
        raw_content = getRAWFile(blog_raw_file)
        blogJSON = ast.literal_eval(raw_content)
        blog_thumb_list = blogJSON["prompts_for_thumbnail_image"]
        print(f"{getDate()} Blog Post for: {blog_id}_raw.json already exists.")

        for idx, thumb_prompt in enumerate(blog_thumb_list):
            if isImageAlreadyExists(
                f"output/{blog_id.replace(' ', '_').lower()}_thumbnail_{idx + 1}.webp"
            ):
                print(
                    f"{getDate()} Thumbnail Image {idx + 1} for: {blog_id} already exists. Skipping generation."
                )
            else:
                print(
                    f"{getDate()} Generating Thumbnail Image {idx + 1} for: {blog_id}"
                )
                generate_image_thumbnail(
                    f"output/{blog_id.replace(' ', '_').lower()}_thumbnail_{idx + 1}",
                    thumb_prompt,
                )

    else:
        print(f"{getDate()} not found: {blog_id}_raw.json")
