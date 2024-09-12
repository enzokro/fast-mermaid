import re
import base64
import httpx
from fasthtml.common import *
from fasthtml.svg import *


# creates the app with Tailwind for styling
app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
    )
)

class FastMermaid:
    """A Mermaid file uploader and editor with live SVG rendering."""
    def __init__(self, content=""):
        self.content = content

    def __ft__(self):
        """Trying out custom FastHTML classes."""
        return Div(
            Div(
                H2("Live Editor", cls="text-3xl font-bold mb-4"),
                Form(
                    Input(type="file", name="mermaid_file", accept=".mmd,.txt,.mermaid", cls="mb-2 p-2 w-full border rounded text-2xl"),
                    Button("Upload File", cls="btn bg-blue-500 hover:bg-blue-700 text-white text-xl font-bold py-2 px-4 rounded"),
                    enctype="multipart/form-data",
                    hx_post="/upload",
                    hx_target="#mermaid-input",
                    hx_swap="innerHTML",
                    cls="mb-4"
                ),
                Textarea(
                    self.content,
                    id="mermaid-input",
                    name="mermaid_input",
                    hx_post="/render",
                    hx_trigger="keyup changed delay:500ms, htmx:afterSettle",
                    hx_target="#mermaid-output",
                    hx_swap="innerHTML",
                    cls="flex-grow w-full p-2 border rounded resize-none text-2xl"
                ),
                cls="w-full md:w-1/2 p-4 flex flex-col"
            ),
            Div(
                H2("Rendered Mermaid Output", cls="text-3xl font-bold mb-4"),
                Div(id="mermaid-output", cls="border p-2 bg-white w-full h-full flex items-center justify-center"),
                cls="w-full md:w-1/2 p-4 flex flex-col h-full"
            ),
            cls="flex flex-col md:flex-row h-screen bg-gray-100"
        )

def create_mermaid_ui():
    "Builds the main editor UI."
    return Titled("FastHTML Mermaid Editor",
        FastMermaid(),
        cls="text-4xl font-bold mb-4 p-4 bg-blue-100"
    )


async def process_mermaid_content(content):
    """Calls the Mermaid Ink API on `content` and returns a FastHTML `Svg`."""
    encoded_content = base64.urlsafe_b64encode(content.encode()).decode()
    svg_url = f"https://mermaid.ink/svg/{encoded_content}"
    async with httpx.AsyncClient() as client:
        response = await client.get(svg_url)
        if response.status_code == 200:
            svg_content = response.text
            return Svg(
                NotStr(svg_content),
                preserveAspectRatio="xMidYMid meet",
                cls="w-full h-full"
            )
        else:
            return P(f"Failed to render diagram: HTTP {response.status_code}", cls="text-red-500")

@rt('/')
def get():
    return create_mermaid_ui()

@rt('/upload')
async def post(request):
    "Reads the uploaded file and returns its content."
    try:
        form = await request.form()
        file = form['mermaid_file']
        if not file.filename:
            return P("No file selected", cls="text-red-500")

        content = (await file.read()).decode('utf-8')
        return content
    except Exception as e:
        return P(f"An error occurred during upload: {str(e)}", cls="text-red-500")

@rt('/render')
async def post(request):
    "Processes the Mermaid content in the form and returns an SVG."
    try:
        form_data = await request.form()
        content = form_data.get('mermaid_input', '').strip()
        return await process_mermaid_content(content)
    except Exception as e:
        return P(f"An error occurred during rendering: {str(e)}", cls="text-red-500")


# run the mermaid editor
serve()