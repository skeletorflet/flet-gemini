import flet as ft
import json
from flet_gemini import FletGemini, SafetyCategory, SafetyThreshold

# Replace with your actual Gemini API key
API_KEY = "YOUR_KEY"

# Default model
DEFAULT_MODEL = "gemini-1.5-pro"


def main(page: ft.Page):
    page.title = "FletGemini Example"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Create a single FletGemini control with all event handlers
    gemini_control = FletGemini(
        api_key=API_KEY,
        model=DEFAULT_MODEL,
        show_response=False,  # We'll handle display manually
        generation_config={
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
            "stopSequences": ["STOP"],
        },
        safety_settings=[
            {
                "category": SafetyCategory.HARASSMENT.value,
                "threshold": SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value,
            },
            {
                "category": SafetyCategory.HATE_SPEECH.value,
                "threshold": SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value,
            },
        ],
    )

    # =============== PROMPT TAB ===============
    # Response display for prompt
    prompt_response = ft.Text(
        "Response will appear here...", size=14, selectable=True, width=600
    )

    # Input field for custom prompts
    prompt_input = ft.TextField(
        label="Enter your prompt",
        multiline=True,
        min_lines=2,
        max_lines=5,
        width=600,
        value="Write a short story about a magical forest",
    )

    # Event handler for prompt response
    def on_prompt_response(e):
        prompt_response.value = f"✅ Response: {e.data}"
        page.update()

    # Register event handler
    gemini_control.on_response = on_prompt_response

    # Button to send prompt
    async def send_prompt(e):
        if prompt_input.value.strip():
            prompt_response.value = "🤖 Generating response..."
            page.update()
            img_path = r"C:\Users\Julian\Desktop\geminix\gemini\examples\flet_gemini_example\src\assets\00000.png"
            try:
                # await gemini_control.prompt_async(prompt_input.value)
                
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                await gemini_control.text_and_image_async(prompt_input.value, [img_bytes])
                # Response will be handled by the on_response event
            except Exception as ex:
                prompt_response.value = f"❌ Error: {str(ex)}"
                page.update()

    prompt_button = ft.ElevatedButton(
        "Send Prompt", on_click=send_prompt, icon=ft.Icons.SEND
    )

    prompt_tab = ft.Tab(
        text="Prompt",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Simple Prompt", size=18, weight=ft.FontWeight.W_500),
                    ft.Image(src="00000.png", width=300, height=150),
                    prompt_input,
                    prompt_button,
                    ft.Container(height=20),
                    prompt_response,
                ]
            ),
            padding=20,
        ),
    )

    # =============== CHAT TAB ===============
    # Chat history display
    chat_history = ft.ListView(
        spacing=10,
        auto_scroll=True,
        height=300,
        width=600,
    )

    # Input field for chat
    chat_input = ft.TextField(
        label="Type your message",
        multiline=True,
        min_lines=1,
        max_lines=3,
        width=600,
    )

    # Chat messages storage
    chat_messages = []

    # Event handler for chat response
    def on_chat_response(e):
        # Add assistant response to chat history
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"Assistant: {e.data}", selectable=True),
                # bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
                padding=10,
                width=600,
            )
        )
        # Add to chat messages for context
        chat_messages.append({"role": "model", "parts": [{"text": e.data}]})
        page.update()

    # Register event handler
    gemini_control.on_chat_response = on_chat_response

    # Button to send chat message
    async def send_chat(e):
        if chat_input.value.strip():
            # Add user message to chat history
            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(f"You: {chat_input.value}", selectable=True),
                    # bgcolor=ft.Colors.GREY_200,
                    border_radius=10,
                    padding=10,
                    width=600,
                )
            )

            # Add to chat messages for context
            chat_messages.append(
                {"role": "user", "parts": [{"text": chat_input.value}]}
            )

            # Clear input
            user_message = chat_input.value
            chat_input.value = ""
            page.update()

            try:
                await gemini_control.chat_async(chat_messages)
                # Response will be handled by the on_chat_response event
            except Exception as ex:
                chat_history.controls.append(
                    ft.Container(
                        content=ft.Text(f"Error: {str(ex)}", selectable=True),
                        # bgcolor=ft.Colors.RED_100,
                        border_radius=10,
                        padding=10,
                        width=600,
                    )
                )
                page.update()

    # Button to clear chat
    def clear_chat(e):
        chat_history.controls.clear()
        chat_messages.clear()
        page.update()

    chat_tab = ft.Tab(
        text="Chat",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Chat with Gemini", size=18, weight=ft.FontWeight.W_500),
                    chat_history,
                    ft.Row(
                        [
                            chat_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                tooltip="Send message",
                                on_click=send_chat,
                            ),
                        ]
                    ),
                    ft.ElevatedButton("Clear Chat", on_click=clear_chat),
                ]
            ),
            padding=20,
        ),
    )

    # =============== STREAMING CHAT TAB ===============
    # Streaming chat history display
    stream_history = ft.ListView(
        spacing=10,
        auto_scroll=True,
        height=300,
        width=600,
    )

    # Current streaming response container
    current_stream_response = ft.Text("", selectable=True)
    stream_response_container = ft.Container(
        content=current_stream_response,
        # bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=10,
        width=600,
        visible=False,
    )

    # Input field for streaming chat
    stream_input = ft.TextField(
        label="Type your message",
        multiline=True,
        min_lines=1,
        max_lines=3,
        width=600,
    )

    # Streaming chat messages storage
    stream_messages = []

    # Event handler for streaming chunks
    def on_stream_chunk(e):
        # Update the current streaming response
        if not stream_response_container.visible:
            stream_response_container.visible = True
            stream_history.controls.append(stream_response_container)

        current_stream_response.value += e.data
        page.update()

    # Register event handler
    gemini_control.on_chunk = on_stream_chunk

    # Button to send streaming chat message
    async def send_stream_chat(e):
        if stream_input.value.strip():
            # Add user message to chat history
            stream_history.controls.append(
                ft.Container(
                    content=ft.Text(f"You: {stream_input.value}", selectable=True),
                    # bgcolor=ft.Colors.GREY_200,
                    border_radius=10,
                    padding=10,
                    width=600,
                )
            )

            # Add to chat messages for context
            stream_messages.append(
                {"role": "user", "parts": [{"text": stream_input.value}]}
            )

            # Reset streaming response
            current_stream_response.value = "Assistant: "
            stream_response_container.visible = False

            # Clear input
            user_message = stream_input.value
            stream_input.value = ""
            page.update()

            try:
                await gemini_control.stream_chat_async(stream_messages)
                # Add completed response to messages for context
                stream_messages.append(
                    {
                        "role": "model",
                        "parts": [{"text": current_stream_response.value[11:]}],
                    }
                )
            except Exception as ex:
                stream_history.controls.append(
                    ft.Container(
                        content=ft.Text(f"Error: {str(ex)}", selectable=True),
                        # bgcolor=ft.Colors.RED_100,
                        border_radius=10,
                        padding=10,
                        width=600,
                    )
                )
                page.update()

    # Button to clear streaming chat
    def clear_stream_chat(e):
        stream_history.controls.clear()
        stream_messages.clear()
        current_stream_response.value = ""
        stream_response_container.visible = False
        page.update()

    stream_tab = ft.Tab(
        text="Streaming Chat",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Streaming Chat with Gemini",
                        size=18,
                        weight=ft.FontWeight.W_500,
                    ),
                    stream_history,
                    ft.Row(
                        [
                            stream_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                tooltip="Send message",
                                on_click=send_stream_chat,
                            ),
                        ]
                    ),
                    ft.ElevatedButton("Clear Chat", on_click=clear_stream_chat),
                ]
            ),
            padding=20,
        ),
    )

    # =============== UTILITIES TAB ===============
    # Token counting
    token_input = ft.TextField(
        label="Enter text to count tokens",
        multiline=True,
        min_lines=2,
        max_lines=5,
        width=600,
    )

    token_result = ft.Text("Token count will appear here")

    async def count_tokens(e):
        if token_input.value.strip():
            token_result.value = "Counting tokens..."
            page.update()

            try:
                result = await gemini_control.count_tokens_async(token_input.value)
                token_result.value = f"Token count: {result}"
            except Exception as ex:
                token_result.value = f"Error: {str(ex)}"

            page.update()

    # Model info
    model_dropdown = ft.Dropdown(
        width=300,
        label="Select model",
        value=DEFAULT_MODEL,
        options=[
            ft.dropdown.Option(DEFAULT_MODEL),
            ft.dropdown.Option("gemini-1.0-pro"),
            ft.dropdown.Option("gemini-pro-vision"),
        ],
    )

    model_info_result = ft.Text("Model info will appear here", selectable=True)

    async def get_model_info(e):
        if model_dropdown.value:
            model_info_result.value = "Getting model info..."
            page.update()

            try:
                result = await gemini_control.info_async(model_dropdown.value)
                # Format the JSON for better readability
                formatted_result = json.dumps(json.loads(result), indent=2)
                model_info_result.value = formatted_result
            except Exception as ex:
                model_info_result.value = f"Error: {str(ex)}"

            page.update()

    # List models
    models_result = ft.Text("Available models will appear here", selectable=True)

    async def list_models(e):
        models_result.value = "Listing models..."
        page.update()

        try:
            result = await gemini_control.list_models_async()
            # Format the JSON for better readability
            formatted_result = json.dumps(json.loads(result), indent=2)
            models_result.value = formatted_result
        except Exception as ex:
            models_result.value = f"Error: {str(ex)}"

        page.update()

    utilities_tab = ft.Tab(
        text="Utilities",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Token Counting", size=18, weight=ft.FontWeight.W_500),
                    token_input,
                    ft.ElevatedButton("Count Tokens", on_click=count_tokens),
                    token_result,
                    ft.Divider(),
                    ft.Text("Model Information", size=18, weight=ft.FontWeight.W_500),
                    ft.Row(
                        [
                            model_dropdown,
                            ft.ElevatedButton("Get Info", on_click=get_model_info),
                        ]
                    ),
                    model_info_result,
                    ft.Divider(),
                    ft.Text(
                        "List Available Models", size=18, weight=ft.FontWeight.W_500
                    ),
                    ft.ElevatedButton("List Models", on_click=list_models),
                    models_result,
                ]
            ),
            padding=20,
        ),
    )

    # =============== EMBEDDINGS TAB ===============
    # Embedding content
    embed_input = ft.TextField(
        label="Enter text to embed",
        multiline=True,
        min_lines=2,
        max_lines=5,
        width=600,
    )

    embed_result = ft.Text("Embedding will appear here (truncated)", selectable=True)
    async def embed_content(e):
        if embed_input.value.strip():
            embed_result.value = "Generating embedding..."
            page.update()

            try:
                # result YA es una lista, no un string JSON
                embedding = await gemini_control.embed_content_async(embed_input.value, "embedding-001")
                
                if embedding:
                    truncated = embedding[:5] + ["..."] + embedding[-5:]
                    embed_result.value = f"Embedding (truncated): {truncated}\n\nTotal dimensions: {len(embedding)}"
                else:
                    embed_result.value = "Error: No embedding returned"
            except Exception as ex:
                embed_result.value = f"Error: {str(ex)}"

            page.update()

    # Batch embedding
    batch_input = ft.TextField(
        label="Enter multiple texts to embed (one per line)",
        multiline=True,
        min_lines=3,
        max_lines=6,
        width=600,
        value="Hello world\nHow are you\nArtificial intelligence",
    )

    batch_result = ft.Text(
        "Batch embeddings will appear here (summary)", selectable=True
    )

    async def batch_embed(e):
        if batch_input.value.strip():
            texts = [line.strip() for line in batch_input.value.split("\n") if line.strip()]
            if not texts:
                batch_result.value = "No valid texts provided"
                page.update()
                return

            batch_result.value = f"Generating embeddings for {len(texts)} texts..."
            page.update()

            try:
                result = await gemini_control.batch_embed_contents_async(texts)
                embed_data = json.loads(result)
                
                # Nueva estructura de datos
                if "embeddings" in embed_data:
                    embeddings = embed_data["embeddings"]
                    summary = []
                    for i, embedding in enumerate(embeddings):
                        dim = len(embedding)
                        summary.append(f"Text {i + 1}: {dim} dimensions")
                    batch_result.value = "\n".join(summary)
                else:
                    batch_result.value = "Error: Unexpected embedding format"
            except Exception as ex:
                batch_result.value = f"Error: {str(ex)}"

            page.update()

    embeddings_tab = ft.Tab(
        text="Embeddings",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Generate Embeddings", size=18, weight=ft.FontWeight.W_500),
                    embed_input,
                    ft.ElevatedButton("Generate Embedding", on_click=embed_content),
                    embed_result,
                    ft.Divider(),
                    ft.Text("Batch Embeddings", size=18, weight=ft.FontWeight.W_500),
                    batch_input,
                    ft.ElevatedButton(
                        "Generate Batch Embeddings", on_click=batch_embed
                    ),
                    batch_result,
                ]
            ),
            padding=20,
        ),
    )

    # =============== ERROR HANDLING TAB ===============
    # Error display
    error_text = ft.Text("Errors will appear here", size=14, selectable=True, width=600)

    # Event handler for errors
    def on_error(e):
        error_text.value = f"❌ Error: {e.data}"
        page.update()

    # Register error handler
    gemini_control.on_error = on_error

    # Button to trigger an error (invalid API key)
    async def trigger_error(e):
        error_text.value = "Attempting to trigger an error..."
        page.update()

        # Temporarily save the real API key
        real_key = gemini_control.api_key

        try:
            # Set an invalid API key
            await gemini_control.init_async("invalid_api_key_to_trigger_error")
            # Try to use it
            await gemini_control.prompt_async("This should fail")
        except Exception as ex:
            error_text.value = f"❌ Error: {str(ex)}"
        finally:
            # Restore the real API key
            await gemini_control.init_async(real_key)

        page.update()

    # Button to cancel a request
    async def cancel_request(e):
        try:
            result = await gemini_control.cancel_request_async()
            error_text.value = f"Cancel result: {result}"
        except Exception as ex:
            error_text.value = f"❌ Error cancelling: {str(ex)}"

        page.update()

    error_tab = ft.Tab(
        text="Error Handling",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Error Handling", size=18, weight=ft.FontWeight.W_500),
                    ft.ElevatedButton("Trigger Error", on_click=trigger_error),
                    ft.ElevatedButton("Cancel Request", on_click=cancel_request),
                    error_text,
                ]
            ),
            padding=20,
        ),
    )

    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            prompt_tab,
            chat_tab,
            stream_tab,
            utilities_tab,
            embeddings_tab,
            error_tab,
        ],
        expand=True,
    )

    page.overlay.append(gemini_control)

    # Add the tabs to the page
    page.add(
        ft.Text("FletGemini Complete Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Explore all features of the FletGemini control", size=16),
        ft.Container(height=20),
        tabs,
    )


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
