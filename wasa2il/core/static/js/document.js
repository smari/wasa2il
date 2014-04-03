
function markdown_text_to_html(text) {
    return text.replace(/\n    /g, '<br />&nbsp;&nbsp;&nbsp;&nbsp;').replace(/\n/g, '<br />');
}

function html_diff(original, amendment) {
    var dmp = new diff_match_patch();
    var d = dmp.diff_main(original, amendment);
    dmp.diff_cleanupSemantic(d);
    return dmp.diff_prettyHtml(d).replace(/&para;/g, '');
}

function get_patch(original, amendment) {

    var dmp = new diff_match_patch();
    var d = dmp.diff_main(original, amendment);

    if (d.length > 2) {
        dmp.diff_cleanupSemantic(d);
    }

    var patch_list = dmp.patch_make(original, amendment, d);
    return dmp.patch_toText(patch_list);
}
var file = {'name': 'foobar.txt', defaultContent: 'Hello World'};

$(function () {

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });

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

    $('[tabname="view"]').bind('click', function (e) {
        $(this).parent().find('li').removeClass('active');
        $(this).addClass('active');
        $('#legal-text-diff').fadeOut(0, function () {
            $('#legal-text').fadeIn(0);
        });
        return false
    });
    $('[tabname="diff"]').bind('click', function (e) {
        $(this).parent().find('li').removeClass('active');
        $(this).addClass('active');
        $('#legal-text').fadeOut(0, function () {
            $('#legal-text-diff').fadeIn(0);
        });
        return false
        // e.preventDefault();
    });

    $('.document #propose_change').submit(function (e) {
        var inputs = $(this).find('input,textarea');
        inputs.attr('disabled', 'disabled');
        $.post(
            '/api/document/propose-change/',
            {
                document_id: DOCUMENT_ID,
                text: $('#legal-text-editor').val(),
                comments: $(this).find('#comments').val(),
                patch: '',
                diff: ''
            },
            function (data) {
                window.location.replace(window.location.pathname + '?v=' + data.order);
            },
            'json'
        ).fail(function () { inputs.removeAttr('disabled'); });
        e.preventDefault();
        return false;
    });

    $('.document #propose_change #btn_preview').click(function(e) {
        input_text = $('#legal-text-editor').val();
        $.get(
            '/api/document/render-markdown/',
            {
                text: $('#legal-text-editor').val()
            },
            function(data) {
                $preview = $('#legal-text');
                $preview.html(data.content);
                $preview.show();
            },
            'json'
        ).fail(function(data) {
            alert('Fail:' + data);
        });
    });

});
