from xml.dom import minidom

def getText(nodelist):
    rc = []
    for node in nodelist:
        name, type = node.localName, node.nodeType
        if type == node.TEXT_NODE:
            rc.append(node.data)
        else:
            rc.append(getText(node.childNodes))
    return ''.join(rc).strip(' \n\t')

book = minidom.parse('b.fb2')
anno = book.getElementsByTagName('annotation')[0]
data = getText(anno.childNodes)
print(data)
