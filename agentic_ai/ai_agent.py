import os
import json
import requests
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
class GraphState(TypedDict):
  messages: Annotated[List[BaseMessage], add_messages]
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
github_key = os.getenv("GITHUB_API_KEY")  
GITHUB_API_URL = "https://api.github.com"

try:
  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=gemini_key)
except Exception as e:
  raise ValueError(f"❌ Failed to initialize Gemini LLM: {e}")
  

def route(state: GraphState) -> str:
    last_user_msg = state["messages"][-1].content
    system_prompt = (
        "You are a routing assistant. Classify the user's message as either:\n"
        "- 'github_agent': if it is about repositories, pull requests, GitHub-related tasks\n"
        "- 'chat_agent': for anything else (general conversation, non-GitHub questions)\n"
        "- 'leave_agent': if it is about leave request\n"
        "Respond with only the label: 'github_agent', 'chat_agent', 'leave_agent'."
    )

    try:
        classification = llm.invoke([
            HumanMessage(content=system_prompt),
            HumanMessage(content=last_user_msg)
        ])
        route_decision = classification.content.strip().lower()
        if route_decision not in ["github_agent", "chat_agent", "leave_agent"]:
            route_decision = "chat_agent"
        return route_decision
    except Exception as e:
        print(f"⚠️ Routing failed: {e}. Defaulting to 'chat_agent'")
        return "chat_agent"

def chat_agent(state: GraphState) -> GraphState:
    try:
        response = llm.invoke(state["messages"])
    except Exception as e:
        response = AIMessage(content=f"⚠️ Failed to generate chat response: {e}")
    return {"messages": state["messages"] + [response]}

def github_agent(state: GraphState) -> GraphState:
    user_msg = state["messages"][-1].content
    headers = {"Authorization": f"Bearer {github_key}"}

    try:
        # Classify intent
        system_prompt = (
            "You are a classifier and helper for GitHub queries. "
            "Classify the user's request as one of the following:\n"
            "- 'list_repos'\n"
            "- 'count_commits'\n"
            "- 'count_prs'\n"
            "- 'general_question'\n"
            "Only output the label."
        )
        intent = llm.invoke([HumanMessage(content=system_prompt), HumanMessage(content=user_msg)]).content.strip()
    except Exception as e:
        return {"messages": state["messages"] + [AIMessage(content=f"Failed to classify GitHub intent: {e}")]}

    response_text = "Sorry, I couldn't process your GitHub request."

    try:
        if intent == "list_repos":
            user_resp = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
            user_resp.raise_for_status()
            username = user_resp.json()["login"]

            repos_resp = requests.get(f"{GITHUB_API_URL}/users/{username}/repos", headers=headers)
            repos_resp.raise_for_status()
            repos = [repo["name"] for repo in repos_resp.json()]
            response_text = f"User {username} has the following repositories: {', '.join(repos)}"

        elif intent == "count_commits":
            user_resp = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
            user_resp.raise_for_status()
            username = user_resp.json()["login"]

            repos_resp = requests.get(f"{GITHUB_API_URL}/users/{username}/repos", headers=headers)
            repos_resp.raise_for_status()
            total_commits = 0
            for repo in repos_resp.json():
                commits_resp = requests.get(f"{GITHUB_API_URL}/repos/{username}/{repo['name']}/commits", headers=headers)
                if commits_resp.status_code == 200:
                    commits = commits_resp.json()
                    user_commits = [commit for commit in commits if commit['author'] and commit['author']['login'] == username]
                    total_commits += len(user_commits)

            response_text = f"User {username} has made a total of {total_commits} commits across their repositories."

        elif intent == "count_prs":
            prs = requests.get(f"{GITHUB_API_URL}/search/issues?q=author:@me+type:pr", headers=headers)
            prs.raise_for_status()
            total_prs = prs.json().get("total_count", 0)
            response_text = f"You have opened {total_prs} pull requests."

        elif intent == "general_question":
            response_text = llm.invoke(user_msg).content

    except Exception as e:
        response_text = f"⚠️ Error processing GitHub request: {e}"

    return {"messages": state["messages"] + [AIMessage(content=response_text)]}

def summarize_conversation(messages: List[BaseMessage]) -> str:
    conversation_text = "\n".join([msg.content for msg in messages])
    summary_prompt = (
        "You are a helpful assistant. Summarize the following conversation in a concise manner:\n"
        f"{conversation_text}\n"
        "Summarize in 2-3 sentences."
    )
    try:
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        return f"⚠️ Failed to summarize conversation: {e}"
    
CHECKPOINT_DIR = "./checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def save_checkpoint(thread_id, state):
    try:
        if len(state["messages"]) > 8:
            summarized = summarize_conversation(state["messages"])
            state["messages"] = [HumanMessage(content=f"Summary of previous conversation: {summarized}")]
        with open(os.path.join(CHECKPOINT_DIR, f"{thread_id}.json"), "w") as f:
            json.dump([msg.dict() for msg in state["messages"]], f)
    except Exception as e:
        print(f"⚠️ Failed to save checkpoint: {e}")

def load_checkpoint(thread_id):
    path = os.path.join(CHECKPOINT_DIR, f"{thread_id}.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                msgs = json.load(f)
                messages = [HumanMessage(**m) if m["type"] == "human" else AIMessage(**m) for m in msgs]
                return {"messages": messages}
    except Exception as e:
        print(f"⚠️ Failed to load checkpoint: {e}")
    return {"messages": []}

builder = StateGraph(GraphState)
builder.add_node("chat_agent", chat_agent)
builder.add_node("github_agent", github_agent)
builder.add_node("leave_agent", github_agent)
builder.add_node("route", lambda x: x)

builder.add_conditional_edges("route", route, {
    "chat_agent": "chat_agent",
    "github_agent": "github_agent",
    "leave_agent": "leave_agent"
})

builder.set_entry_point("route")
builder.add_edge("chat_agent", END)
builder.add_edge("github_agent", END)
builder.add_edge("leave_agent", END)

try:
    graph = builder.compile()
except Exception as e:
    raise RuntimeError(f"❌ Failed to compile LangGraph: {e}")