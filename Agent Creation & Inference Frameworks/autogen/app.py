import os
import autogen
from typing import Dict, Optional, Union, List
import json
from dotenv import load_dotenv
load_dotenv()

# Configuration for the two different Groq API keys and models
class GroqConfig:
    def __init__(self):
        # Default configurations - will be overridden by set_api_keys method
        self.config_list = []
        
    def set_api_keys(self, api_key1: str, model1: str, api_key2: str, model2: str):
        """Set up two different Groq API keys with their respective models"""
        self.config_list = [
            {
                "model": model1,
                "api_key": api_key1,
                "base_url": "https://api.groq.com/openai/v1",
            },
            {
                "model": model2,
                "api_key": api_key2,
                "base_url": "https://api.groq.com/openai/v1",
            }
        ]
        return self.config_list

# Custom agent class for selecting specific models
class GroqAgent:
    def __init__(self, groq_config: GroqConfig):
        self.groq_config = groq_config
        self.agents = {}
        
    def create_agents(self, user_persona: str = "User", coder_persona: str = "Coder"):
        """Create the AutoGen agents for user and coder roles"""
        # Configuration for the user proxy agent
        user_proxy = autogen.UserProxyAgent(
            name=user_persona,
            system_message="I am the user who needs help with coding tasks.",
            human_input_mode="TERMINATE",
            code_execution_config={"work_dir": "workspace", "use_docker": False},
        )
        
        # Configurations for the two coder assistants with different models
        coder_config_list = [
            {
                "name": f"{coder_persona}_1",
                "model": self.groq_config.config_list[0]["model"],
                "config_list": [self.groq_config.config_list[0]],
                "system_message": f"I am a senior Python programmer that writes robust, well-documented code. I'll use {self.groq_config.config_list[0]['model']} for generating solutions."
            },
            {
                "name": f"{coder_persona}_2",
                "model": self.groq_config.config_list[1]["model"],
                "config_list": [self.groq_config.config_list[1]],
                "system_message": f"I am a senior Python programmer that writes robust, well-documented code. I'll use {self.groq_config.config_list[1]['model']} for generating solutions."
            }
        ]
        
        # Create the coding assistant agents
        coder_agents = []
        for config in coder_config_list:
            coder = autogen.AssistantAgent(
                name=config["name"],
                llm_config={
                    "config_list": config["config_list"],
                    "temperature": 0.2,
                    "timeout": 120,
                },
                system_message=config["system_message"],
            )
            coder_agents.append(coder)
            
        # Store the agents for later use
        self.agents = {
            "user_proxy": user_proxy,
            "coders": coder_agents
        }
        
        return self.agents
    
    def get_agent(self, agent_name: str):
        """Retrieve a specific agent by name"""
        if agent_name == "user_proxy":
            return self.agents["user_proxy"]
        
        for coder in self.agents["coders"]:
            if coder.name == agent_name:
                return coder
                
        return None
        
    def start_chat(self, model_index: int = 0, task: str = None):
        """Start a chat with a specific coder model"""
        if model_index >= len(self.agents["coders"]):
            raise ValueError(f"Model index {model_index} is out of range. Available models: 0-{len(self.agents['coders'])-1}")
            
        user_proxy = self.agents["user_proxy"]
        selected_coder = self.agents["coders"][model_index]
        
        if task:
            user_proxy.initiate_chat(selected_coder, message=task)
        else:
            print(f"Chat initiated with {selected_coder.name}. Type 'exit' to end the conversation.")
            user_proxy.initiate_chat(selected_coder)
            
    def group_chat(self, task: str):
        """Create a group chat with all agents"""
        if not self.agents:
            raise ValueError("Agents not created yet. Call create_agents() first.")
            
        # Create a group chat environment
        groupchat = autogen.GroupChat(
            agents=[self.agents["user_proxy"]] + self.agents["coders"],
            messages=[],
            max_round=12
        )
        
        # Create the group chat manager
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={
                "config_list": self.groq_config.config_list,
                "temperature": 0.2,
            }
        )
        
        # Start the group chat
        self.agents["user_proxy"].initiate_chat(
            manager,
            message=task
        )

# Example usage function
def run_groq_agent():
    # Initialize the Groq configuration
    groq_config = GroqConfig()
    
    # Get API keys from environment variables or input
    api_key1 = os.environ.get("GROQ_API_KEY_1") or input("Enter Groq API Key 1: ")
    model1 = os.environ.get("GROQ_MODEL_1") or input("Enter Groq Model 1 (e.g., llama3-8b-8192): ")
    
    api_key2 = os.environ.get("GROQ_API_KEY_2") or input("Enter Groq API Key 2: ")
    model2 = os.environ.get("GROQ_MODEL_2") or input("Enter Groq Model 2 (e.g., mixtral-8x7b-32768): ")
    
    # Set up the configuration
    groq_config.set_api_keys(api_key1, model1, api_key2, model2)
    
    # Initialize the agent manager
    agent_manager = GroqAgent(groq_config)
    
    # Create the agents
    agents = agent_manager.create_agents()
    
    # Example menu for interacting with the agents
    while True:
        print("\n=== Groq Agent Menu ===")
        print("1. Chat with Model 1")
        print("2. Chat with Model 2")
        print("3. Start a group chat with both models")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        if choice == "1":
            task = input("Enter your coding task for Model 1: ")
            agent_manager.start_chat(model_index=0, task=task)
        elif choice == "2":
            task = input("Enter your coding task for Model 2: ")
            agent_manager.start_chat(model_index=1, task=task)
        elif choice == "3":
            task = input("Enter your coding task for the group chat: ")
            agent_manager.group_chat(task=task)
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run_groq_agent()