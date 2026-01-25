from HtmlNodes import HtmlNode, HtmlTextNode

self_closers = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
    'input', 'link', 'meta', 'source', 'track', 'wbr'
}

def write(text, indent=0):
    print(text)

def attributes_to_string(attributes):
    out_str = ""
    for key, value in attributes:
        out_str += f'{key}="{value}" '
    return out_str.strip()

def TreeToHtml(tree):
    if isinstance(tree, HtmlTextNode):
        write(tree.text)
    else:
        tag = tree.tag_name.lower()
        attr_str = attributes_to_string(tree.attributes)

        if tag in self_closers:
            write(f'<{tag} {attr_str}>')  # HTML5 style; add "/" for XHTML if needed
            return

        write(f'<{tag} {attr_str}>')
        for child in tree.children:
            TreeToHtml(child)
        write(f'</{tag}>')
