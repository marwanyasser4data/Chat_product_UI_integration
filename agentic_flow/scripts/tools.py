import requests
import json
import http.client
import json
from typing import Optional, Dict, Any

from urllib3 import response



class VectaraAPIs:
    """
    A wrapper class for interacting with the Vectara Tools & MCP Server APIs.
    """

    def __init__(self, api_key: str):
        """
        Initialize the Vectara API wrapper.

        Args:
            api_key (str): Your Vectara API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.vectara.io/v2"

    # -------------------------
    # Tools
    # -------------------------
    def list_tools(self):
        """
        List all available tools (filtering can be added later).

        Returns:
            Response object from the Vectara API.
        """
        url = f"{self.base_url}/tools"
        headers = {
            "Accept": "application/json",
            "x-api-key": self.api_key
        }
        return requests.get(url, headers=headers)

    def create_tool(
        self,
        name: str,
        title: str,
        description: str,
        code: str,
        language: str = "python",
        max_execution_time_seconds: int = 30,
        max_memory_mb: int = 100
    ):
        """
        Create a new tool in Vectara.

        Args:
            name (str): Tool internal name.
            title (str): Display title.
            description (str): Short description of what the tool does.
            code (str): The executable code for the tool.
            language (str): Language of the tool. Default: python.
            max_execution_time_seconds (int): Max runtime.
            max_memory_mb (int): Memory limit in MB.

        Returns:
            Response object from the Vectara API.
        """
        url = f"{self.base_url}/tools"

        payload = {
            "type": "lambda",
            "name": name,
            "title": title,
            "description": description,
            "language": language,
            "code": code,
            "execution_configuration": {
                "max_execution_time_seconds": max_execution_time_seconds,
                "max_memory_mb": max_memory_mb
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

        return requests.post(url, headers=headers, data=json.dumps(payload))

    # -------------------------
    # MCP Tool Servers
    # -------------------------
    def create_tool_server(
        self,
        name: str,
        description: str,
        mcp_url: str,
        auth_token: str,
        transport: str = "streamable-http",
        headers_override: dict = None,
        enabled: bool = True,
        metadata: dict = None
    ):
        """
        Register an external MCP server in Vectara.

        Args:
            name (str): MCP server name.
            description (str): Description of the server.
            mcp_url (str): URL of the MCP server endpoint.
            auth_token (str): Bearer token for authentication.
            transport (str): Transport protocol (default "streamable-http").
            headers_override (dict): Optional additional headers.
            enabled (bool): Whether the server is active.
            metadata (dict): Optional metadata.

        Returns:
            Response object from the Vectara API.
        """

        url = f"{self.base_url}/tool_servers"

        payload = {
            "name": name,
            "type": "mcp",
            "description": description,
            "uri": mcp_url,
            "headers": headers_override or {},
            "transport": transport,
            "auth": {
                "type": "bearer",
                "token": auth_token
            },
            "enabled": enabled,
            "metadata": metadata or {}
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

        return requests.post(url, headers=headers, data=json.dumps(payload))
    

    def list_servers(self):
        url = "https://api.vectara.io/v2/tool_servers"

        payload = {}
        headers = {
        'Accept': 'application/json',
        'x-api-key': self.api_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response

    def update_tool_server(
        self,
        tool_server_id: str,
        name: str,
        description: str,
        uri: str,
        transport: str = "streamable-http",
        auth_type: str = "bearer",
        auth_token: str = "abcd",
        headers_override: dict = None,
        enabled: bool = True,
        metadata: dict = None
    ):
        """
        Update an existing Vectara MCP or HTTP Tool Server.

        Parameters:
        ----------
        tool_server_id : str
            The unique ID of the tool server to update.
        name : str
            Updated name of the tool server.
        description : str
            Description of the tool server and its purpose.
        uri : str
            The server URI (SSE or streamable HTTP endpoint).
        transport : str
            Transport protocol. Must be one of:
                - "sse"  (legacy)
                - "streamable-http" (new format)
        auth_type : str
            Authentication type (typically "bearer").
        auth_token : str
            Token used for the bearer authentication.
        headers_override : dict
            Custom headers to be passed to the server.
        enabled : bool
            Whether the tool server should remain active.
        metadata : dict
            Optional metadata dictionary.

        Returns:
        --------
        dict
            JSON API response from Vectara.
        """

        VALID_TRANSPORTS = ["sse", "streamable-http"]

        # Validate transport protocol
        if transport not in VALID_TRANSPORTS:
            raise ValueError(
                f"Invalid transport '{transport}'. Must be one of: {VALID_TRANSPORTS}"
            )

        if headers_override is None:
            headers_override = {}

        if metadata is None:
            metadata = {}

        url = f"{self.base_url}/tool_servers/{tool_server_id}"

        payload = {
            "name": name,
            "description": description,
            "uri": uri,
            "headers": headers_override,
            "transport": transport,
            "auth": {
                "type": auth_type,
                "token": auth_token
            },
            "enabled": enabled,
            "metadata": metadata
        }
        headers = { 
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.api_key }

        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        return response


    
    ## !!! incomplete
    # First step will be modified later (added to function params)
    def create_agent(
        self,
        key: str,
        name: str,
        department: str,
        description: str,
        tools_config: dict,
        system_prompt: str,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        enable_agent: bool = True
    ):
        """
            Create a new Vectara Agent.

            Parameters:
            ----------
            key : str
                Unique identifier for the agent.
            name : str
                Human-readable name of the agent.
            description : str
                A general description of the agent's purpose.
            type : str
                The type the agent. Must be one of:
                [mcp, corpora_search, web_search, lambda,
                structured_indexing, sub_agent, artifact_read,
                artifact_grep, image_read, document_conversion]
            query : str
                Override query for the tool (if applicable).
            model_name : str
                Name of the LLM model to use (e.g. "gpt-4", "gpt-4o-mini").
            temperature : float
                Sampling temperature for the model.
            max_tokens : int
                Maximum number of tokens allowed in response.
            top_p : float
                Nucleus sampling parameter.
            enabled : bool
                Whether the agent should be active after creation.

            Returns:
            --------
            dict
                JSON response from the Vectara API.
        """
        url = f"{self.base_url}/agents"

        payload = {
            "key": key,
            "name": name,
            "description": description,
            "tool_configurations": tools_config,
            "model": {
                "name": model_name,
                "parameters": {
                    "max_tokens": max_tokens
                },
                "retry_configuration": {
                    "enabled": True,
                    "max_retries": 3,
                    "initial_backoff_ms": 2000,
                    "max_backoff_ms": 30000,
                    "backoff_factor": 2
                }
            },
            "first_step": {
                "type": "conversational",
                "instructions": [
                    {
                        "type": "inline",
                        "name": "Initial Instruction",
                        "description": "Provides initial context and guidelines for support interactions",
                        "template_type": "velocity",
                        "template": system_prompt,
                        "metadata": {
                            "version": "1.0.0",
                            "author": "support-team"
                        },
                        "enabled": True
                    }
                ],
                "output_parser": {
                    "type": "default"
                }
            },
            "metadata": {
                "department": department,
                "version": "1.0.0",
                "owner": "support-team"
            },
            "enabled": enable_agent
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response
    


    def create_agent_session(
        self,
        agent_key: str,
        session_key: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        tti_minutes: int = 60,
        host: str = "api.vectara.io"
    ) -> Dict[str, Any]:
        """
        Create a new Vectara agent session.
        
        Args:
            agent_key: The agent identifier
            api_key: Your Vectara API key
            session_key: Unique key for the session
            name: Human-readable name for the session
            description: Optional description of the session
            metadata: Optional metadata dictionary
            enabled: Whether the session is enabled (default: True)
            tti_minutes: Time-to-idle in minutes (default: 60)
            host: Vectara API host (default: api.vectara.io)
        
        Returns:
            Dictionary containing the API response
            
        Raises:
            Exception: If the API request fails
        """
        # Prepare the payload
        payload = {
            "key": session_key,
            "name": name,
            "enabled": enabled,
            "tti_minutes": tti_minutes
        }
        
        # Add optional fields if provided
        if description:
            payload["description"] = description
        
        if metadata:
            payload["metadata"] = metadata
        
        # Set up the connection and headers
        conn = http.client.HTTPSConnection(host)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        
        try:
            # Make the request
            endpoint = f"/v2/agents/{agent_key}/sessions"
            conn.request("POST", endpoint, json.dumps(payload), headers)
            
            # Get the response
            res = conn.getresponse()
            data = res.read()
            response_text = data.decode("utf-8")
            
            # Parse JSON response
            response_data = json.loads(response_text)
            
            # Check if request was successful
            if res.status >= 200 and res.status < 300:
                return {
                    "success": True,
                    "status_code": res.status,
                    "data": response_data
                }
            else:
                return {
                    "success": False,
                    "status_code": res.status,
                    "error": response_data
                }
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": response_text
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        finally:
            conn.close()
    
    def get_session(self, agent_key: str, session_key: str):
        """
        Retrieve details of an existing session for a specific Vectara agent.

        Parameters:
        - agent_key (str): The unique key of the agent.
        - session_key (str): The unique session identifier whose details are requested.

        Returns:
        - Response: The HTTP response from the Vectara API containing session details.
        """

        url = f"https://api.vectara.io/v2/agents/{agent_key}/sessions/{session_key}"

        headers = {
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

        return requests.get(url, headers=headers)


    def interact_with_agent(self, agent_key: str, session_key: str, message: str, stream_response: bool = False):
        """
        Send a message to a Vectara agent inside an existing session.

        Parameters:
        - agent_key (str): The unique key identifying the agent.
        - session_key (str): The session identifier for the current conversation session.
        - message (str): The text message to send to the agent.
        - stream_response (bool): Whether to stream the response (True) or wait for full output (False).

        Returns:
        - Response: The HTTP response from the Vectara API.
        """

        session_response = self.get_session(agent_key= agent_key, session_key= session_key)
        if session_response.status_code > 201:
            create_session = self.create_agent_session(agent_key= agent_key, session_key= session_key, name=session_key)
            print(f'Create session status: {create_session}')
 
            
        url = f"https://api.vectara.io/v2/agents/{agent_key}/sessions/{session_key}/events"

        payload = {
            "type": "input_message",
            "messages": [
                {
                    "type": "text",
                    "content": message
                }
            ],
            "stream_response": False
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "x-api-key": self.api_key   
        }
        
        if not stream_response:
            response = requests.post(url, headers=headers, data=json.dumps(payload,ensure_ascii=False))
            return response.json()
        else:
            headers["Accept"] = "text/event-stream"
            payload['stream_response'] = True
            response = requests.post(url, headers=headers, data=json.dumps(payload,ensure_ascii=False), stream=True)
        print(f'Here is the payload: {payload}')
        print("response:       ",response)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        # Streaming mode
        try:
            line_count = 0
            has_error = False
            for line in response.iter_lines(decode_unicode=False):
                line = line.decode('utf-8')
                line_count += 1
                print(f"Line {line_count}: {line[:100]}")  # Print first 100 chars
                
                # Check for error events
                if line.startswith("event:error"):
                    has_error = True
                    continue
                if line.startswith("data:"):
                    json_str = line[5:].strip()  # Remove "data:" prefix
                    if json_str:  # Skip empty data lines
                        try:
                            data = json.loads(json_str)
                            # If this is an error message, yield it as content
                            if has_error and data.get('type') == 'error':
                                error_msgs = data.get('messages', [])
                                error_text = ' - '.join(error_msgs) if error_msgs else 'Unknown error'
                                yield {'content': f'خطأ: {error_text}'}
                                has_error = False
                                continue
                            yield data
                        except json.JSONDecodeError as e:
                            print(f"Parse error: {e}, Line: {json_str}")
                            continue
        except Exception as e:
            print("Stream error:", e)