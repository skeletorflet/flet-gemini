from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json

from flet.core.constrained_control import Control
from flet.core.control import OptionalNumber, Ref
from flet.core.types import OptionalControlEventCallable


class SafetyCategory(Enum):
    """Safety categories for content filtering."""
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    SEXUALLY_EXPLICIT = "sexually_explicit"
    DANGEROUS_CONTENT = "dangerous_content"


class SafetyThreshold(Enum):
    """Safety thresholds for content filtering."""
    BLOCK_NONE = "block_none"
    BLOCK_ONLY_HIGH = "block_only_high"
    BLOCK_MEDIUM_AND_ABOVE = "block_medium_and_above"
    BLOCK_LOW_AND_ABOVE = "block_low_and_above"


class FletGemini(Control):
    """
    FletGemini Control - A Flet control for Google Gemini AI integration.

    Provides easy access to Google's Gemini AI model for text generation,
    chat, embeddings, and more with support for async operations and event handling.
    """

    def __init__(
        self,
        #
        # Control
        #
        data: Optional[Any] = None,
        ref: Optional[Ref] = None,
        #
        # FletGemini specific
        #
        api_key: Optional[str] = None,
        prompt: Optional[str] = None,
        value: Optional[str] = None,
        model: Optional[str] = None,
        show_response: Optional[bool] = True,
        generation_config: Optional[Dict[str, Any]] = None,
        safety_settings: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        on_response: OptionalControlEventCallable = None,
        on_chat_response: OptionalControlEventCallable = None,
        on_chunk: OptionalControlEventCallable = None,
        on_error: OptionalControlEventCallable = None,
    ):
        Control.__init__(
            self,
            data=data,
            ref=ref,
        )

        self.api_key = api_key
        self.prompt = prompt
        self.value = value
        self.model = model
        self.show_response = show_response
        self.generation_config = generation_config
        self.safety_settings = safety_settings
        self.system_prompt = system_prompt
        self.on_response = on_response
        self.on_chat_response = on_chat_response
        self.on_chunk = on_chunk
        self.on_error = on_error

    def _get_control_name(self):
        return "flet_gemini"

    # api_key
    @property
    def api_key(self):
        """
        Google Gemini API key for authentication.
        """
        return self._get_attr("api_key")

    @api_key.setter
    def api_key(self, value):
        self._set_attr("api_key", value)

    # prompt
    @property
    def prompt(self):
        """
        Text prompt to send to Gemini AI. Setting this will automatically trigger a request.
        """
        return self._get_attr("prompt")

    @prompt.setter
    def prompt(self, value):
        self._set_attr("prompt", value)

    # value
    @property
    def value(self):
        """
        Display text when no response is available.
        """
        return self._get_attr("value")

    @value.setter
    def value(self, value):
        self._set_attr("value", value)
        
    # model
    @property
    def model(self):
        """
        The Gemini model to use for requests.
        """
        return self._get_attr("model")

    @model.setter
    def model(self, value):
        self._set_attr("model", value)

    # show_response
    @property
    def show_response(self):
        """
        Whether to display the AI response in the control.
        """
        return self._get_attr("show_response")

    @show_response.setter
    def show_response(self, value):
        self._set_attr("show_response", value)
        
    # generation_config
    @property
    def generation_config(self):
        """
        Configuration for text generation (temperature, topK, topP, etc.).
        """
        return self._get_attr("generation_config")

    @generation_config.setter
    def generation_config(self, value):
        if value is not None and not isinstance(value, str):
            value = json.dumps(value)
        self._set_attr("generation_config", value)
        
    # safety_settings
    @property
    def safety_settings(self):
        """
        Safety settings for content filtering.
        """
        return self._get_attr("safety_settings")

    @safety_settings.setter
    def safety_settings(self, value):
        if value is not None and not isinstance(value, str):
            value = json.dumps(value)
        self._set_attr("safety_settings", value)
        
    # system_prompt
    @property
    def system_prompt(self):
        """
        System prompt to use for chat conversations.
        """
        return self._get_attr("system_prompt")

    @system_prompt.setter
    def system_prompt(self, value):
        self._set_attr("system_prompt", value)

    # response (read-only)
    @property
    def response(self):
        """
        The latest response from Gemini AI (read-only).
        """
        return self._get_attr("response")

    # on_response
    @property
    def on_response(self):
        """
        Event handler called when a response is received from Gemini AI.
        """
        return self._get_event_handler("on_response")

    @on_response.setter
    def on_response(self, handler):
        self._add_event_handler("on_response", handler)
        
    # on_chat_response
    @property
    def on_chat_response(self):
        """
        Event handler called when a chat response is received from Gemini AI.
        """
        return self._get_event_handler("on_chat_response")

    @on_chat_response.setter
    def on_chat_response(self, handler):
        self._add_event_handler("on_chat_response", handler)
        
    # on_chunk
    @property
    def on_chunk(self):
        """
        Event handler called when a chunk is received from streaming responses.
        """
        return self._get_event_handler("on_chunk")

    @on_chunk.setter
    def on_chunk(self, handler):
        self._add_event_handler("on_chunk", handler)

    # on_error
    @property
    def on_error(self):
        """
        Event handler called when an error occurs.
        """
        return self._get_event_handler("on_error")

    @on_error.setter
    def on_error(self, handler):
        self._add_event_handler("on_error", handler)

    # Methods
    async def prompt_async(self, text: str, model: Optional[str] = None):
        """
        Send a prompt to Gemini AI asynchronously.

        Args:
            text: The prompt text to send to Gemini
            model: Optional model name to use for this request

        Returns:
            The response from Gemini AI
        """
        params = {"text": text}
        if model:
            params["model"] = model
        return await self.invoke_method_async("prompt", params, wait_for_result=True)

    async def init_async(self, api_key: str):
        """
        Initialize Gemini with an API key asynchronously.

        Args:
            api_key: Google Gemini API key

        Returns:
            Success message or error
        """
        return await self.invoke_method_async("init", {"api_key": api_key}, wait_for_result=True)
        
    async def chat_async(self, chats: List[Dict[str, Any]], model: Optional[str] = None):
        """
        Send a chat request to Gemini AI asynchronously.

        Args:
            chats: List of chat messages with role and parts
            model: Optional model name to use for this request

        Returns:
            The chat response from Gemini AI
        """
        params = {"chats": json.dumps(chats)}
        if model:
            params["model"] = model
        return await self.invoke_method_async("chat", params, wait_for_result=True)
        
    async def stream_chat_async(self, chats: List[Dict[str, Any]], model: Optional[str] = None):
        """
        Start a streaming chat with Gemini AI asynchronously.

        Args:
            chats: List of chat messages with role and parts
            model: Optional model name to use for this request

        Returns:
            Status message indicating stream started
        """
        params = {"chats": json.dumps(chats)}
        if model:
            params["model"] = model
        return await self.invoke_method_async("stream_chat", params, wait_for_result=True)
        
    async def count_tokens_async(self, text: str, model: Optional[str] = None):
        """
        Count tokens in a text string asynchronously.

        Args:
            text: The text to count tokens for
            model: Optional model name to use for this request

        Returns:
            The token count as a string
        """
        params = {"text": text}
        if model:
            params["model"] = model
        return await self.invoke_method_async("count_tokens", params, wait_for_result=True)
        
    async def info_async(self, model: str):
        """
        Get information about a Gemini model asynchronously.

        Args:
            model: The model name to get information for

        Returns:
            JSON string with model information
        """
        return await self.invoke_method_async("info", {"model": model}, wait_for_result=True)
        
    async def list_models_async(self):
        """
        List available Gemini models asynchronously.

        Returns:
            JSON string with list of available models
        """
        return await self.invoke_method_async("list_models", {}, wait_for_result=True)
        
    async def embed_content_async(self, text: str, model: Optional[str] = None):
        params = {"text": text}
        if model:
            params["model"] = model
            
        result = await self.invoke_method_async("embed_content", params, wait_for_result=True)
        print(f"Raw result: {result}")  # DEBUG
        
        data = json.loads(result)
        print(f"Parsed data: {data}")  # DEBUG
        
        embedding = data.get("embedding", [])
        print(f"Embedding: {embedding}")  # DEBUG
        
        return embedding
        
    async def batch_embed_contents_async(self, texts: List[str], model: Optional[str] = None):
        """
        Generate embeddings for multiple text contents asynchronously.

        Args:
            texts: List of text strings to generate embeddings for
            model: Optional model name to use for this request

        Returns:
            JSON string with embedding vectors for each text
        """
        params = {"texts": json.dumps(texts)}
        if model:
            params["model"] = model
        return await self.invoke_method_async("batch_embed_contents", params, wait_for_result=True)
        
    async def cancel_request_async(self):
        """
        Cancel any ongoing Gemini requests asynchronously.

        Returns:
            Status message indicating request cancelled
        """
        return await self.invoke_method_async("cancel_request", {}, wait_for_result=True)
        
    async def text_and_image_async(self, text: str, images: List[bytes], model: Optional[str] = None):
        """
        Send text and images to Gemini for multimodal processing asynchronously.

        Args:
            text: The text prompt
            images: List of image data as bytes
            model: Optional model name to use for this request

        Returns:
            The response from Gemini AI
        """
        params = {
            "text": text,
            "images": json.dumps([[b for b in img] for img in images])
        }
        if model:
            params["model"] = model
        return await self.invoke_method_async("text_and_image", params, wait_for_result=True)
