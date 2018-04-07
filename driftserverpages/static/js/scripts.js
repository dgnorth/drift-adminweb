function addParameterToURL(param){
    _url = location.href;
    _url += (_url.split('?')[1] ? '&':'?') + param;
    return _url;
}
function add_page(field, p, t, curr_page, num_pages) {
        cls = '';
        if (p == curr_page && p == t)
            cls = 'page-current'
        else if (p == 0 || p == num_pages+1 || p == curr_page)
            cls = 'page-disabled'
        var url = location.href.replace("page="+curr_page, "page="+p);
        if (url == location.href) {
            url = addParameterToURL("page="+p)
        }
        field.append('<li class="page-item"><a href="'+url+'" class="page-link '+cls+'">'+t+'</a></li>')

}
function pagination(curr_page, num_pages) {
    if (num_pages <= 1) {
        return;
    }
    var lst = $('.pagination');
    add_page(lst, 1, 'First', curr_page, num_pages)
    add_page(lst, curr_page-1, '<<', curr_page, num_pages)
    for (i = 1; i < num_pages+1; i++) {
        if (num_pages <= 5 || i == 1 || i == num_pages || (i >= curr_page-2 && i <= curr_page+2))
            add_page(lst, i, i, curr_page, num_pages)
        else if (num_pages > 5 && (i == curr_page-3 || i == curr_page+3))
            add_page(lst, i, '...', curr_page, num_pages)
    }
    add_page(lst, curr_page+1, '>>', curr_page, num_pages)
    add_page(lst, num_pages, 'Last', curr_page, num_pages)
}
