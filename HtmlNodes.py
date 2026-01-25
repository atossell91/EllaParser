class HtmlNode:
    def __init__(self, tag_name, attributes=None, text=""):
        self.type = "element"
        self.tag_name: str = tag_name
        if attributes is None:
           self.attributes = []
        else: 
            self.attributes: list[tuple[str, str]] = attributes
        self.children: list["HtmlNode"] = []
    
    def __str__(self):
        return f'{self.tag_name}'
    
class HtmlTextNode:
    def __init__(self, text=""):
        self.type = "text"
        self.text = text
