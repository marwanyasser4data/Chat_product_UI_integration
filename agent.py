"""
LangGraph Agent Implementation with Real LLM Support
"""
print('agent module is imported !!!')
from langchain_openai import ChatOpenAI
from langchain_core.language_models.fake import FakeStreamingListLLM
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from typing import Generator, Optional
import os
from agentic_flow.scripts.vectara_app import generate_response as agent_generate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
class CustomAgent:
    def update_config(self, any):
        pass
    def generate_response(
        self, 
        message: str, 
        session_key: str
        ) -> Generator[str, None, None]:
        for i in agent_generate(message, session_key):
            yield i


class ChatAgent:
    """Chat agent with memory using LangGraph and real LLM"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize chat agent with configuration
        
        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config or {}
        self.checkpointer = InMemorySaver()
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration"""
        provider = self.config.get('provider', 'fake')
        model_name = self.config.get('model', 'gpt-4')
        temperature = self.config.get('temperature', 0.7)
        max_tokens = self.config.get('max_tokens', 2000)
        
        if provider == 'openai':
            api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found, using Fake LLM")
                return self._get_fake_llm()
            
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                streaming=True
            )
        
        elif provider == 'openrouter':
            api_key = self.config.get('api_key') or os.getenv('OPENROUTER_OPENAI_API_KEY')
            base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            
            if not api_key:
                print("Warning: No OpenRouter API key found, using Fake LLM")
                return self._get_fake_llm()
            
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url=base_url,
                streaming=True
            )
        
        else:
            # Default to Fake LLM
            return self._get_fake_llm()
    
    def _get_fake_llm(self):
        """Get Fake LLM for testing"""
        return FakeStreamingListLLM(
            responses=[
                'مرحباً! أنا مساعد ذكي جاهز لمساعدتك. كيف يمكنني أن أساعدك اليوم؟',
                'سأكون سعيداً بالإجابة على أسئلتك. ما الذي تريد معرفته؟',
                'هذا سؤال رائع! دعني أساعدك في ذلك.',
                'بالتأكيد! يمكنني مساعدتك في هذا الموضوع.',
                'شكراً لسؤالك. إليك ما أعرفه عن هذا الموضوع...',
                'هل لديك أي استفسارات أخرى؟ أنا هنا للمساعدة!'
            ]
        )
    
    def _create_agent(self):
        """Create LangGraph agent"""
        tools = self.config.get('tools', [])
        
        return create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=self.checkpointer
        )
    
    def update_config(self, new_config: dict):
        """Update agent configuration and reinitialize"""
        self.config.update(new_config)
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
    
    def generate_response(
        self, 
        message: str, 
        session_key: str
    ) -> Generator[str, None, None]:
        """
        Generate streaming response from the agent
        
        Args:
            message: User message
            session_key: Unique session identifier
            
        Yields:
            Streaming response chunks
        """
        config = {
            'configurable': {
                'thread_id': session_key
            }
        }
        
        try:
            # Stream events from the agent
            for events in self.agent.stream(
                {'messages': [('user', message)]},
                config=config,
                stream_mode='values'
            ):
                msgs = events.get('messages', [])
                if msgs:
                    # Get the last message
                    last_msg = msgs[-1]
                    # Handle both string and object responses
                    if isinstance(last_msg, str):
                        yield last_msg
                    elif hasattr(last_msg, 'content'):
                        yield last_msg.content
                    else:
                        # Fallback to string representation
                        yield str(last_msg)
        except Exception as e:
            # Fallback response if agent fails
            yield f"عذراً، حدث خطأ: {str(e)}"


# Global agent instance
# chat_agent = ChatAgent()

chat_agent = CustomAgent()