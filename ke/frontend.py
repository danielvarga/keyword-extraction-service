import sys

from thenounproject.api import Api
from thenounproject.models import Icon


NOUN_PROJECT_API_KEY = "7cb34b5950bf40d2812daaec467dcf31"
NOUN_PROJECT_SECRET_KEY = "41564da71677472ba023ffb85c24b806"
NOUN_PROJECT_REQUEST_COUNT_LIMIT = 1000

g_noun_project_request_count = 0


# unicode to xml
def encode(unicode_data):
    return unicode_data.encode('ascii', 'xmlcharrefreplace')


# output is html-format ascii-encoded bytestream
# if positions_to_bold is an ordered iterable and show_icon is True,
# we use the first element of positions_to_bold that has some noun project icon returned.
def render(sent, positions_to_bold=[], show_icon=False):
    # output is ascii bytestream
    def rendertoken(token):
        if token.is_space:
            return str(token)
        if token.i in positions_to_bold:
            return "<b>%s</b>%s" % (encode(unicode(token)), token.whitespace_)
        else:
            return encode(unicode(token)) + token.whitespace_
    rendered_text = "".join([rendertoken(t) for t in sent])

    if show_icon:
        urls = []
        for position in positions_to_bold:
            token_str = str(sent[position].lemma_)
            url = noun_first_icon(token_str)
            if url is not None:
                urls.append(url)
        if len(urls) > 0:
            icon_html = "<img src=\"%s\" height=\"50\"/>" % urls[0]
        else:
            icon_html = "[missing icon]"
        rendered_line = icon_html
        rendered_line += rendered_text

    return rendered_line


# just a test
def put_spans_around_tokens(doc):
    output = []
    html_unbolded = '<span class="{classes}">{word}</span>{space}'
    html_bolded = '<b><span class="{classes}">{word}</span></b>{space}'
    i = 0
    for token in doc:
        if token.is_space:
            output.append(token.text)
        else:
            i += 1
            classes = 'pos-{}'.format(token.tag_)
            if i % 2 == 0:
                html = html_unbolded
            else:
                html = html_bolded
            output.append(html.format(classes=classes, word=token.text, space=token.whitespace_))
    string = ''.join(output)
    string = string.replace('\n', '')
    string = string.replace('\t', '    ')
    return '<pre>{}</pre>'.format(string)


def noun_first_icon(query):
    global g_noun_project_request_count
    g_noun_project_request_count += 1
    if g_noun_project_request_count > NOUN_PROJECT_REQUEST_COUNT_LIMIT:
        if g_noun_project_request_count == NOUN_PROJECT_REQUEST_COUNT_LIMIT + 1:
            sys.stderr.write("Noun Project request count limit reached.\n")
        return None

    api = Api(NOUN_PROJECT_API_KEY, NOUN_PROJECT_SECRET_KEY)
    try:
        icons = api.icon.list(query)
        icon = icons[0]
    except:
        return None
    return icon.preview_url


def test_noun_project():
    print noun_first_icon("fish")


def main():
    test_noun_project()
    return

    import spacy
    nlp = spacy.load('en')
    doc = nlp(u"This is a test.\n\nHello   world.")
    html = put_spans_around_tokens(doc)
    print html


if __name__ == "__main__":
    main()
