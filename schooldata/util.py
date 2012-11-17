def paged(page_size, iterable):
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    yield page

