# fast-mermaid
Live Mermaid editor and renderer using FastHTML

## Creating Mermaid Graphs

You can either upload a valid Mermaid file, or type directly into the text area!
Both interactions will create a Mermaid graph using the official Ink API, and render it in the display area.

## Notes 

There are some helper functions to to make the SVG returned by the Mermaid API fills up the available space. This is done by parsing the `viewBox` returned by the API, and changing its dimensions as needed.

I also included a sample file "editor_workflow.mermaid" that shows how this app itself works. You can upload it to see its graph.