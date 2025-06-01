import flet as ft
import json
from flet_gemini import FletGemini, SafetyCategory, SafetyThreshold

# Replace with your actual Gemini API key
API_KEY = "AIzaSyCTpmY_rKZLlWc-AnnyjUqbj5SHrfG3NWo"

# Default model
DEFAULT_MODEL = "gemini-2.0-flash"


def main(page: ft.Page):
    page.title = "FletGemini Example"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.scroll = ft.ScrollMode.AUTO
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

    chat_column = ft.Column([], expand=True, scroll="auto")

    # Input field for custom prompts
    prompt_input = ft.TextField(
        label="Enter your prompt",
        multiline=True,
        min_lines=2,
        max_lines=5,
        value="Qué hay en la imagen?",
    )

    # Event handler for prompt response
    def on_prompt_response(e):
        chat_column.controls.append(ft.Text(f"✅ Response: {e.data}"))
        page.update()

    # Register event handler
    gemini_control.on_response = on_prompt_response

    imagen = None

    def fp_result(e: ft.FilePickerResultEvent):
        nonlocal imagen
        if e.files[0].path:
            imagen = e.files[0].path

    fp = ft.FilePicker(on_result=fp_result)
    page.overlay.append(fp)

    # Button to send prompt
    async def send_prompt(e):
        nonlocal imagen
        if prompt_input.value.strip():
            if imagen is not None:
                chat_column.controls.append(ft.Image(imagen, width=300))
            chat_column.controls.append(ft.Text(f"User: {prompt_input.value.strip()}"))
            page.update()
            try:
                # await gemini_control.prompt_async(prompt_input.value)

                with open(imagen, "rb") as f:
                    img_bytes = f.read()
                await gemini_control.text_and_image_async(prompt_input.value, [img_bytes])
                # Response will be handled by the on_response event
            except Exception as ex:
                prompt_response.value = f"❌ Error: {str(ex)}"
                page.update()

    prompt_button = ft.ElevatedButton(
        "Send Prompt", on_click=send_prompt, icon=ft.Icons.SEND
    )
    fp_button = ft.ElevatedButton(
        "Open Image",
        on_click=lambda _: fp.pick_files(
            "Pick Image", file_type=ft.FilePickerFileType.IMAGE
        ),
    )
    prompt_tab = ft.Tab(
        text="Prompt",
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Simple Prompt", size=18, weight=ft.FontWeight.W_500),
                    prompt_input,
                    ft.Row([prompt_button, fp_button]),
                    ft.Container(height=20),
                    chat_column,
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
