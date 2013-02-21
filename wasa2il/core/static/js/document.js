function make_reference(node) {
	var nodeid = node.data("id");
	var type = node.data("type");

	if (PROPOSED) {
		if (type == 0 || type == 1) {
			prop = '<a data-type="0" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_reference\').modal(\'show\');" class="btn btn-mini add">' + _("Add reference") + '</a>'
				  + '<a data-type="1" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_assumption\').modal(\'show\');" class="btn btn-mini add">' + _("Add assumption") + '</a>';
		} else {
			prop = '<a data-type="2" onclick="selected_item='+nodeid+'; statement_active=\'' + nodeid + '\';$(\'#modal_declaration\').modal(\'show\');" class="btn btn-mini add">' + _("Add statement") + '</a>'
				  + '<a data-type="3" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_subheading\').modal(\'show\');" class="btn btn-mini add">' + _("Add subheading") + '</a>';
		}
	}

	node.append('<div class="btn-group state_buttons">'
	          + '<a class="btn btn-mini delete">' + _("Delete") + '</a>'
			  + (PROPOSED ? prop : '')
	          + '</div>');
}

$(function() {
	$('#modal_reference').modal({show: false, keyboard: true, backdrop: false});
	$('#modal_assumption').modal({show: false, keyboard: true, backdrop: false});
	$('#modal_declaration').modal({show: false, keyboard: true, backdrop: false});
	$('#modal_subheading').modal({show: false, keyboard: true, backdrop: false});

	$("#statements_references li").each(function(id, node) {
		make_reference($(node));
	});

	$("#statements_assumptions li").each(function(id, node) {
		make_reference($(node));
	});
                
	$("#statements_declarations li").each(function(id, node) {
		make_reference($(node));
	});

});

function statement_fork(item) {
	var ref = $("#newversion").val();
	$.getJSON("/api/document/statement/fork/", {"document": DOCUMENT_ID, "original": item.data("id"), "text": ref}, function(data) {
		if (data.ok) {
			var k = $('#statements_references').append('<li data-id="' + data.seq + '" data-seq="' + data.seq + '">' + data.html + '</li>');
			make_reference(k);
			$('#modal_reference').modal('hide');
		} else {
			// Error message
		}
	});
}

function structure_import() {
	var ref = $("#import_structure").val();
	$.getJSON("/api/document/statement/import/", {"document": DOCUMENT_ID, "text": ref}, function(data) {
		if (data.ok) {
			for (i = 0; i < data.new.length; i++) {
				d = data[i];
				var k = $('#statements_references').append('<li data-id="' + d.seq + '" data-seq="' + d.seq + '">' + d.html + '</li>');
				make_reference(k);
			}
			$('#modal_reference').modal('hide');
		} else {
			// Error message
		}
	});
	
}

function new_reference() {
	var ref = $("#reference").val();
	$.getJSON("/api/document/statement/new/" + DOCUMENT_ID + "/0/", 
		{text: ref}, function(data) {
		if (data.ok) {
			var k = $('#statements_references').append('<li data-id="' + data.seq + '" data-seq="' + data.seq + '">' + data.html + '</li>');
			make_reference(k);
			$('#modal_reference').modal('hide');
		} else {
			// Error message
		}
	});
}

function new_assumption() {
	var ref = $("#assumption").val();
	$.getJSON("/api/document/statement/new/" + DOCUMENT_ID + "/1/", 
		{text: ref}, function(data) {
		if (data.ok) {
			var k = $('#statements_assumptions').append('<li data-id="' + data.seq + '" data-seq="' + data.seq + '">' + data.html + '</li>');
			make_reference(k);
			$('#modal_assumption').modal('hide');
			$('#modal_assumption #assumption').val('');
		} else {
			// Error message
		}
	});
}


function new_declaration() {
	var ref = $("#declaration").val();
	$.getJSON("/api/document/statement/new/" + DOCUMENT_ID + "/2/", 
		{text: ref, after: selected_item}, function(data) {
		if (data.ok) {
			var k = $('#statements_declarations ol:last').append('<li data-id="' + data.seq + '" data-seq="' + data.seq + '">' + data.html + '</li>');
			make_reference(k);
			$('#modal_declaration').modal('hide');
			$('#modal_declaration #declaration').val('');
		} else {
			// Error message
		}
	});
}

function new_subheading() {
	var ref = $("#subheading").val();
	$.getJSON("/api/document/statement/new/DOCUMENT_ID/3/", 
		{text: ref}, function(data) {
		if (data.ok) {
			var k = $('#statements_declarations').append('<li class="statement_subheading" data-id="' + data.seq + '" data-seq="' + data.seq + '">' + data.html + '</li>');
			make_reference(k);
			$('#modal_subheading').modal('hide');
			$('#modal_subheading #subheading').val('');
		} else {
			// Error message
		}
	});
}

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
			editor = $(epiceditor.editor);
			previewer = $(epiceditor.previewer);
			editor.html(markdown_text_to_html(content_org.text()));
			line_height = parseInt(editor.css('line-height').replace('px', '')) + 2;

			var new_height = Math.max(editor.height(), previewer.height());
			content.css('height', new_height + line_height);
			epiceditor.reflow();
			setTimeout(function () {
			if (!PROPOSING) {
				epiceditor.edit();
				epiceditor.preview();
			} else {
				epiceditor.preview();
				epiceditor.edit();
			}
		}, 300);
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
		epiceditor.edit();
		setTimeout(function () {
			epiceditor.preview();
		}, 300);
	});

	return;


	$('body').delegate('.btn-group.state_buttons .delete', 'click', function () {
		var item = $(this).parent().parent();
		$.getJSON("/api/document/statement/delete/" + DOCUMENT_ID + "/1/", 
			{
				id: $(this).data('id')
			},
			function(data) {
				if (data.ok) {
					item.css('color', 'red');
					item.css('text-decoration', 'line-through');
				} else {
					// Error message
				}
			}
		);
	});

	$('bodyxxx').delegate('.modal .btn-primary', 'click', function () {
		var item = $(this).parent().parent(),
			type = $(this).data('type'),
			text = "";
		if      (type == 0) text = $('reference').val();
		else if (type == 1) text = $('assumption').val();
		else if (type == 2) text = $('statement').val();
		else if (type == 3) text = $('subheading').val();
		console.log(text);
		$.getJSON("/api/document/statement/delete/" + DOCUMENT_ID + "/1/", 
			{
				id: $(this).data('id')
			},
			function(data) {
				if (data.ok) {
					$('<li>Whoo</li>').insertAfter(item);
				} else {
					// Error message
				}
			}
		);
	});

});