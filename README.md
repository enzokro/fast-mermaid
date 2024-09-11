# fast-mermaid
Live Mermaid editor and renderer built with FastHTML

## Creating Mermaid Graphs

You can either upload a valid Mermaid file, or type directly into the text area.
Both interactions will create a Mermaid graph via their Ink API, and render it in the display area.

> Notes
There are a few helper functions to deal with the SVG returned by Mermaid, and making sure we fill in the available space. This is mainly done by parsing the `viewBox` returned by the Mermaid API, and growing the content as needed.

I am still new to HTMX, so there is likely a much cleaner way of handling the text area rendering. Happy to merge in PRs and changes!
