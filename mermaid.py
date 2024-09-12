import base64
import re
import httpx
from fasthtml.common import *
from fasthtml.svg import *


# create the app with Tailwind for styling 
app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
    )
)

class MermaidEditor:
    """A Mermaid editor with live preview."""
    def __init__(self, content: str = ""):
        self.content = content

    def __ft__(self):
        """Trying out custom FastHTML classes."""
        return Div(
            Div(
                H2("Live Editor", cls="text-2xl font-bold mb-4"),
                Form(
                    Input(type="file", name="mermaid_file", accept=".mmd,.txt,.mermaid", cls="mb-2 p-2 w-full border rounded"),
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
                    hx_trigger="keyup changed delay:250ms, htmx:afterSettle",
                    hx_target="#mermaid-output",
                    hx_swap="innerHTML",
                    cls="flex-grow w-full p-2 border rounded resize-none text-2xl"
                ),
                cls="w-full md:w-1/2 p-4 flex flex-col"
            ),
            Div(
                H2("Rendered Mermaid Content", cls="text-2xl font-bold mb-4"),
                Div(id="mermaid-output", cls="border p-2 bg-white w-full h-full flex items-center justify-center"),
                cls="w-full md:w-1/2 p-4 flex flex-col h-full"
            ),
            cls="flex flex-col md:flex-row h-screen bg-gray-100"
        )

def create_mermaid_ui():
    return Titled(
        "FastHTML Mermaid Editor",
        MermaidEditor(),
        cls="text-3xl font-bold mb-4 p-4 bg-blue-100"
    )

def extract_and_adjust_viewbox(svg_content: str) -> Tuple[str, str]:
    match = re.search(r'viewBox="([^"]*)"', svg_content)
    if match:
        x, y, width, height = map(float, match.group(1).split())
        if x < 0 or y < 0:
            adj_width = width + abs(x)
            adj_height = height + abs(y)
            new_viewbox = f"0 0 {adj_width} {adj_height}"
            svg_content = svg_content.replace(
                '<svg',
                f'<svg transform="translate({-x} {-y})"',
                1
            )
            return new_viewbox, svg_content
        else:
            return match.group(1), svg_content
    return None, svg_content


async def process_mermaid_content(content: str) -> Svg:
    encoded_content = base64.urlsafe_b64encode(content.encode()).decode()
    svg_url = f"https://mermaid.ink/svg/{encoded_content}"
    async with httpx.AsyncClient() as client:
        response = await client.get(svg_url)
        if response.status_code == 200:
            svg_content = response.text
            viewBox, adjusted_svg_content = extract_and_adjust_viewbox(svg_content)
            return Svg(
                NotStr(adjusted_svg_content),
                viewBox=viewBox,
                preserveAspectRatio="xMidYMid meet",
                cls="w-full h-full"
            )
        else:
            print(f"Failed to render diagram: HTTP {response.status_code}")
            return P(f"Failed to render diagram: HTTP {response.status_code}", cls="text-red-500")

@rt('/')
def get():
    return create_mermaid_ui()

@rt('/upload')
async def post(request):
    form = await request.form()
    file = form['mermaid_file']
    if not file.filename:
        print("No file selected")
        return P("No file selected", cls="text-red-500")

    content = (await file.read()).decode('utf-8')
    return content

@rt('/render')
async def post(request):
    form_data = await request.form()
    content = form_data.get('mermaid_input', '').strip()
    return await process_mermaid_content(content)

serve()