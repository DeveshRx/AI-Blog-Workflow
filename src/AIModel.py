import os
from src.blogschema import BlogPostSchema
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

AI_Model = os.getenv("AI_Model")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY")


system_prompt_template_blog_post = "./data/system_prompt.txt"
prompt_template_blog_post = "./data/prompt.txt"


def generateSystemPrompt() -> str:
    with open(system_prompt_template_blog_post, "r") as file:
        template_content = file.read()
    finalPrompt = template_content
    return finalPrompt


def getPrompt() -> str:
    with open(prompt_template_blog_post, "r") as file:
        template_content = file.read()
    finalPrompt = template_content
    return finalPrompt



def generateBlogPost(topic_name: str) -> str:
    sys_prompt = generateSystemPrompt()
    llm = ChatOpenAI(
        model=AI_Model,
        api_key=LM_STUDIO_API_KEY,
        base_url=LM_STUDIO_BASE_URL,
        #temperature=0.7,
    )
    agent = create_agent(
        model=llm,
        #tools=[get_weather],
        system_prompt=sys_prompt,
        response_format=ToolStrategy(BlogPostSchema),
    )
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": getPrompt().format(
                        topic_name=topic_name
                    ),
                }
            ]
        }
    )

    return response["structured_response"]
