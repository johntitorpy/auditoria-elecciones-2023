function show_elements(selector, callback) {
    var elems = $(selector);
    elems.show();
    if (callback != null) callback();
}

function hide_elements(selector, callback) {
    var elems = $(selector);
    elems.hide();
    if (callback != null) callback();
}
