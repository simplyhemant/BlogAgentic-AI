from src.states.blogstate import BlogState
from langchain_core.messages import SystemMessage, HumanMessage
from src.states.blogstate import Blog

class BlogNode:
    """
    A class to represent he blog node
    """

    def __init__(self,llm):
        self.llm=llm

    
    def title_creation(self,state:BlogState):
        """
        create the title for the blog
        """

        if "topic" in state and state["topic"]:
            prompt="""
                   You are an expert blog content writer. Use Markdown formatting. Generate
                   a blog title for the {topic}. This title should be creative and SEO friendly

                   """
            
            sytem_message=prompt.format(topic=state["topic"])
            print(sytem_message)
           
            response=self.llm.invoke(sytem_message)
            print(response)

            return {"blog":{"title":response.content}}
        
    def content_generation(self,state:BlogState):
        if "topic" in state and state["topic"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a detailed blog content with detailed breakdown for the {topic}"""
           
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            
            return {"blog": {"title": state['blog']['title'], "content": response.content}}


    def translation(self, state:BlogState):
        """
        Translate the content to the specified language.
        """

        translation_prompt="""
        You are an expert translator. Respond in valid JSON format with keys "title" and "content".
        Translate the following blog title and blog content into {current_language}.
        - Maintain the original tone, style, and formatting.
        - Adapt cultural references and idioms to be appropriate for {current_language}.

        ORIGINAL_TITLE:
        {blog_title}

        ORIGINAL_CONTENT:
        {blog_content}

        """

        blog_title = state["blog"]["title"]
        blog_content = state["blog"]["content"]
        messages = [
            HumanMessage(translation_prompt.format(current_language=state["current_language"], blog_title=blog_title, blog_content=blog_content))

        ]

        try:
            translation_content = self.llm.with_structured_output(Blog, method="json_mode").invoke(messages)
            return {"blog": {"title": translation_content.title, "content": translation_content.content}}
        except Exception:
            response = self.llm.invoke(messages)
            import json, re
            match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return {"blog": {"title": data.get("title", blog_title), "content": data.get("content", response.content)}}
                except Exception:
                    pass
            return {"blog": {"title": blog_title, "content": response.content}}

    def route(self, state: BlogState):
        return {"current_language": state['current_language']}

    def route_decision(self, state: BlogState):
        """
        Route the content to the respective translation function.
        """
        if state["current_language"] == "hindi":
            return "hindi"
        elif state["current_language"] == "french":
            return "french"
        else:
            return state["current_language"]