import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
from deeppresenter.main import AgentLoop
from deeppresenter.utils.constants import WORKSPACE_BASE
from deeppresenter.utils.log import create_logger
from deeppresenter.utils.typings import ChatMessage, ConvertType, InputRequest, Role
from platformdirs import user_cache_dir

from pptagent import PPTAgentServer
from utils.i18n import get_text, get_available_languages

# UI Constants
UI_CHATBOT_HEIGHT = 300
MAX_THREADS = 16
SUPPORTED_LANGUAGES = ["en", "vi"]

timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
logger = create_logger(
    "DeepPresenterUI",
    log_file=user_cache_dir("deeppresenter") + f"/logs/{timestamp}.log",
)


ROLE_EMOJI = {
    Role.SYSTEM: "⚙️",
    Role.USER: "👤",
    Role.ASSISTANT: "🤖",
    Role.TOOL: "📝",
}

def get_convert_mapping(lang: str = "en") -> dict:
    """Get convert type mapping with translated labels."""
    return {
        get_text("output_freeform", lang): ConvertType.DEEPPRESENTER,
        get_text("output_template", lang): ConvertType.PPTAGENT,
    }


gradio_css = """
            .center-title {
                text-align: center;
                margin-bottom: 10px;
            }
            .center-subtitle {
                text-align: center;
                margin-bottom: 20px;
                opacity: 0.8;
            }
            .gradio-container {
                max-width: 100% !important;
                overflow-x: hidden !important;
            }
            .file-container .wrap {
                min-height: auto !important;
                height: auto !important;
            }

            .file-container .upload-container {
                display: none !important;  /* Hide large drag-drop area */
            }

            .file-container .file-list {
                min-height: 40px !important;
                padding: 8px !important;
            }

            footer {
                display: none !important;
            }

            .gradio-container .footer {
                display: none !important;
            }
            body {
                margin: 5px !important;
                padding: 0 !important;
            }
            .html-container {
                padding: 0 !important;
            }
"""


class UserSession:
    """Simplified user session class."""

    def __init__(self):
        self.loop = AgentLoop(
            session_id=f"{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4().hex[:8]}",
        )
        self.created_time = time.time()


class ChatDemo:
    def create_interface(self):
        """Create Gradio interface with i18n support."""
        default_lang = "en"

        with gr.Blocks(
            title="DeepPresenter",
            theme=gr.themes.Soft(),
            css=gradio_css,
        ) as demo:
            # Language state
            lang_state = gr.State(default_lang)

            gr.Markdown(
                "# DeepPresenter",
                elem_classes=["center-title"],
            )

            with gr.Row():
                with gr.Column():
                    # Language dropdown at top
                    with gr.Row():
                        lang_dropdown = gr.Dropdown(
                            choices=get_available_languages(),
                            value=default_lang,
                            label=get_text("language_label", default_lang),
                            scale=1,
                        )

                    chatbot = gr.Chatbot(
                        value=[],
                        height=UI_CHATBOT_HEIGHT,
                        show_label=False,
                        type="messages",
                        render_markdown=True,
                        elem_classes=["chat-container"],
                    )

                    with gr.Row():
                        pages_dd = gr.Dropdown(
                            label=get_text("pages_label", default_lang),
                            choices=[get_text("pages_auto", default_lang)] + [str(i) for i in range(1, 31)],
                            value=get_text("pages_auto", default_lang),
                            scale=1,
                        )
                        convert_type_dd = gr.Dropdown(
                            label=get_text("output_type_label", default_lang),
                            choices=list(get_convert_mapping(default_lang).keys()),
                            value=list(get_convert_mapping(default_lang).keys())[0],
                            scale=1,
                        )
                        template_choices = PPTAgentServer.list_templates()
                        template_dd = gr.Dropdown(
                            label=get_text("template_label", default_lang),
                            choices=template_choices + [get_text("pages_auto", default_lang)],
                            value=get_text("pages_auto", default_lang),
                            scale=2,
                            visible=False,
                        )

                    def _toggle_template_visibility(v: str, lang: str):
                        # Check for Template keyword in any language
                        template_keywords = [get_text("output_template", lang) for lang in SUPPORTED_LANGUAGES]
                        is_template = any(kw in v for kw in template_keywords)
                        return gr.update(visible=is_template)

                    convert_type_dd.change(
                        _toggle_template_visibility,
                        inputs=[convert_type_dd, lang_state],
                        outputs=[template_dd],
                    )

                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder=get_text("input_placeholder", default_lang),
                            scale=4,
                            container=False,
                        )

                        send_btn = gr.Button(get_text("send_button", default_lang), scale=1, variant="primary")
                        download_btn = gr.DownloadButton(
                            f"📥 {get_text('download_button', default_lang)}",
                            scale=1,
                            variant="secondary",
                        )

                    attachments_input = gr.File(
                        file_count="multiple",
                        type="filepath",
                        elem_classes=["file-container"],
                    )

            # Language change handler
            def update_ui_language(lang):
                return (
                    gr.update(label=get_text("language_label", lang)),
                    gr.update(
                        label=get_text("pages_label", lang),
                        choices=[get_text("pages_auto", lang)] + [str(i) for i in range(1, 31)],
                        value=get_text("pages_auto", lang),
                    ),
                    gr.update(
                        label=get_text("output_type_label", lang),
                        choices=list(get_convert_mapping(lang).keys()),
                        value=list(get_convert_mapping(lang).keys())[0],
                    ),
                    gr.update(
                        label=get_text("template_label", lang),
                        choices=PPTAgentServer.list_templates() + [get_text("pages_auto", lang)],
                        value=get_text("pages_auto", lang),
                    ),
                    gr.update(placeholder=get_text("input_placeholder", lang)),
                    gr.update(value=get_text("send_button", lang)),
                    gr.update(value=f"📥 {get_text('download_button', lang)}"),
                    lang,
                )

            lang_dropdown.change(
                update_ui_language,
                inputs=[lang_dropdown],
                outputs=[
                    lang_dropdown, pages_dd, convert_type_dd, template_dd,
                    msg_input, send_btn, download_btn, lang_state
                ],
            )

            async def send_message(
                message,
                history,
                attachments,
                convert_type_value,
                template_value,
                num_pages_value,
                lang,
                request: gr.Request,
            ):
                user_session = UserSession()

                has_message = bool(message and message.strip())
                has_attachments = bool(attachments)
                if not has_message and not has_attachments:
                    yield (
                        history,
                        message,
                        gr.update(value=None),
                        gr.update(),
                    )
                    return

                default_instruction = get_text("default_instruction", lang)
                history.append(
                    {"role": "user", "content": message or default_instruction}
                )

                aggregated_parts: list[str] = []
                history.append({"role": "assistant", "content": ""})

                loop = user_session.loop

                # Find convert type from any language mapping
                selected_convert_type = None
                for check_lang in SUPPORTED_LANGUAGES:
                    mapping = get_convert_mapping(check_lang)
                    if convert_type_value in mapping:
                        selected_convert_type = mapping[convert_type_value]
                        break
                if selected_convert_type is None:
                    selected_convert_type = ConvertType.DEEPPRESENTER

                # Handle auto value in any language
                auto_values = [get_text("pages_auto", lang) for lang in SUPPORTED_LANGUAGES]
                selected_num_pages = (
                    None if num_pages_value in auto_values else int(num_pages_value)
                )
                if template_value in auto_values:
                    template_value = None

                async for yield_msg in loop.run(
                    InputRequest(
                        instruction=message or default_instruction,
                        template=template_value,
                        attachments=attachments or [],
                        num_pages=str(selected_num_pages),
                        convert_type=selected_convert_type,
                    )
                ):
                    if isinstance(yield_msg, (str, Path)):
                        file_content = f"📄 {get_text('slide_complete', lang)}"
                        aggregated_parts.append(file_content)
                        aggregated_text = "\n\n".join(aggregated_parts).strip()
                        history[-1]["content"] = aggregated_text
                        yield (
                            history,
                            "",
                            gr.update(value=None),
                            gr.update(value=str(yield_msg)),
                        )

                    elif isinstance(yield_msg, ChatMessage):
                        role_msg = f"{ROLE_EMOJI[yield_msg.role]} **{str(yield_msg.role).title()} Message**"
                        if yield_msg.text:
                            aggregated_parts.append(role_msg)

                        if yield_msg.text is not None and yield_msg.text.strip():
                            if yield_msg.role == Role.TOOL:
                                aggregated_parts.append(
                                    "```json\n"
                                    + yield_msg.text.replace("\\n", "\n")
                                    + "\n```"
                                )
                            else:
                                aggregated_parts.append(yield_msg.text)

                        if yield_msg.tool_calls:
                            for tool_call in yield_msg.tool_calls:
                                tool_msg = f"{ROLE_EMOJI.get(yield_msg.role, '💬')} **Tool Call: {tool_call.function.name}**"
                                aggregated_parts.append(tool_msg)

                                if hasattr(tool_call.function, "arguments"):
                                    args_str = tool_call.function.arguments
                                    args_msg = f"```json\n{args_str}\n```"
                                    aggregated_parts.append(args_msg)

                        aggregated_text = "\n\n".join(aggregated_parts).strip()
                        history[-1]["content"] = aggregated_text

                        yield (
                            history,
                            message,
                            gr.update(value=None),
                            gr.update(),
                        )

                    else:
                        raise ValueError(
                            f"Unsupported response message type: {type(yield_msg)}"
                        )

            msg_input.submit(
                send_message,
                inputs=[
                    msg_input,
                    chatbot,
                    attachments_input,
                    convert_type_dd,
                    template_dd,
                    pages_dd,
                    lang_state,
                ],
                outputs=[
                    chatbot,
                    msg_input,
                    attachments_input,
                    download_btn,
                ],
                concurrency_limit=None,
            )

            send_btn.click(
                send_message,
                inputs=[
                    msg_input,
                    chatbot,
                    attachments_input,
                    convert_type_dd,
                    template_dd,
                    pages_dd,
                    lang_state,
                ],
                outputs=[
                    chatbot,
                    msg_input,
                    attachments_input,
                    download_btn,
                ],
                concurrency_limit=None,
            )

        return demo


if __name__ == "__main__":
    import warnings

    chat_demo = ChatDemo()
    demo = chat_demo.create_interface()

    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="websockets.legacy"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets"
    )

    serve_url = "localhost" if len(sys.argv) == 1 else sys.argv[1]
    demo.launch(
        debug=True,
        server_name=serve_url,
        server_port=7861,
        share=False,
        max_threads=MAX_THREADS,
        allowed_paths=[WORKSPACE_BASE],
    )
