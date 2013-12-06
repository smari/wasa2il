
function markdown_text_to_html(text) {
	return text.replace(/\n    /g, '<br />&nbsp;&nbsp;&nbsp;&nbsp;').replace(/\n/g, '<br />');
}
function markdown_html_to_text(text) {
	return text.replace(/&nbsp;/g, ' ').replace(/<br>|<div>|<\/div>/g, '\n');
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
var epiceditor = undefined;
var file = {'name': 'foobar.txt', defaultContent: 'Hello World'};

function refresh_epiceditor(epiceditor) {
	epiceditor.reflow();
	var hide_period = 1000;
	$('#content').css('visibility', 'hidden');
	if (epiceditor.is('edit')) {
		epiceditor.on('preview', function () {
				setTimeout(function () {
						epiceditor.edit();
						$('#content').css('visibility', 'visible');
					}, hide_period);
			});
		epiceditor.preview();
		epiceditor.removeListener('preview');
	} else {
		epiceditor.on('edit', function () {
				setTimeout(function () {
						epiceditor.preview();
						$('#content').css('visibility', 'visible');
					}, hide_period);
			});
		epiceditor.edit();
		epiceditor.removeListener('edit');
	}
}

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

	var	content = $('#content'),
		content_org = $('#content_org'),
		editor = undefined,
		previewer = undefined,
		line_height = undefined,
		opts = {
			container: content[0],
			basePath: '/static',
			file: file
		};
		epiceditor = new EpicEditor(opts);

	epiceditor.load(function () {
			var num_loaded = 0;
			editor = $(epiceditor.editor);
			previewer = $(epiceditor.previewer);
			editor.html(markdown_text_to_html(content_org.text()));

			var both_ready = function () {
					num_loaded++;
					if (num_loaded < 2) {
						return;
					} else if (num_loaded == 2) {
						setTimeout(both_ready, 300);
						return;
					}
					if (!PROPOSING) {
						epiceditor.on('preview', function () {
							line_height = parseInt(editor.css('line-height').replace('px', '')) + 2;
							var new_height = Math.max(editor.height(), previewer.height());
							content.css('height', new_height + line_height * 2);
							refresh_epiceditor(epiceditor);
						});
						epiceditor.preview();
						epiceditor.removeListener('preview');
					} else {
						refresh_epiceditor(epiceditor);
					}
				};

			editor.ready(both_ready);
			previewer.ready(both_ready);
		});

	editor.keyup(function () {
			var new_height = Math.max(editor.height(), previewer.height());
			content.css('height', new_height + line_height);
			epiceditor.reflow();
		});

	$('[data-tab="edit"]').bind('click', function (e) {
			$(this).parent().find('li').removeClass('active');
			$(this).addClass('active');
			$('#content_diff').fadeOut(function () {
					$('#content').fadeIn();
				});
			return false
		});
	$('[data-tab="diff"]').bind('click', function (e) {
			$(this).parent().find('li').removeClass('active');
			$(this).addClass('active');
			if (PROPOSING) {
				$('#content_diff').html('<pre>' + html_diff(content_org.text(), markdown_html_to_text(editor.html())) + '</pre>');
			}
			$('#content').fadeOut(function () {
					$('#content_diff').fadeIn();
				});
			e.preventDefault();
		});

	$('.document #propose_change').submit(function (e) {
		var inputs = $(this).find('input,textarea');
		inputs.attr('disabled', 'disabled');
		$.post(
			'/api/document/propose-change/',
			{
				document_id: DOCUMENT_ID,
				text: markdown_html_to_text(editor.html()),
				comments: $(this).find('#comments').val(),
				patch: get_patch(content_org.text(), markdown_html_to_text(editor.html())),
				diff: html_diff(content_org.text(), markdown_html_to_text(editor.html()))
			},
			function (data) {
				window.location.replace(window.location.pathname + '?v=' + data.order);
			},
			'json'
		)
		.fail(function () { inputs.removeAttr('disabled'); });
		e.preventDefault();
		return false;
	});

	$('#versions input[type="checkbox"]').bind('change', function () {
		var changes = $('#versions tr.change'),
			text = '',
			dmp = new diff_match_patch(),
			patches = [];
		for (var i=0; i < changes.length; i++) {
			var $change = $(changes[i]);
			if ($change.find('input[type="checkbox"]:checked').length == 1) {
				res = dmp.patch_apply(dmp.patch_fromText($change.data('patch')), text);
				if (res[1] == false)
					alert('Err... patching failed!');
				text = res[0];
			}
		}
		editor.html(markdown_text_to_html(text));
		editor.trigger('keyup');
		refresh_epiceditor(EpicEditor);
	});

});