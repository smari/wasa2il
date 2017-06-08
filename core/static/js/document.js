
var file = {'name': 'foobar.txt', defaultContent: 'Hello World'};

$(function () {

    var content = $('#content'),
        content_org = $('#content_org'),
        editor = undefined,
        previewer = undefined,
        line_height = undefined,
        opts = {
            container: content[0],
            basePath: '/static',
            file: file
        };

});
