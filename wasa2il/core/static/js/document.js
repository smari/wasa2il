function make_reference(node) {
	var nodeid = node.data("id");
	var type = node.data("type");

	{% if document.is_proposed %}
	if (type == 0 || type == 1) {
		prop = '<a data-type="0" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_reference\').modal(\'show\');" class="btn btn-mini add">{% trans "Add reference" %}</a>'
			  + '<a data-type="1" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_assumption\').modal(\'show\');" class="btn btn-mini add">{% trans "Add assumption" %}</a>';
	} else {
		prop = '<a data-type="2" onclick="selected_item='+nodeid+'; statement_active=\'' + nodeid + '\';$(\'#modal_declaration\').modal(\'show\');" class="btn btn-mini add">{% trans "Add statement" %}</a>'
			  + '<a data-type="3" onclick="statement_active=\'' + nodeid + '\';$(\'#modal_subheading\').modal(\'show\');" class="btn btn-mini add">{% trans "Add subheading" %}</a>';

	}
	{% endif %}

	node.append('<div class="btn-group state_buttons">'
	          + '<a class="btn btn-mini delete">{% trans "Delete" %}</a>'
	{% if document.is_proposed %}
			  + prop
	{% endif %}
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
	$.getJSON("/api/document/statement/fork/", {"document": {{document.id}}, "original": item.data("id"), "text": ref}, function(data) {
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
	$.getJSON("/api/document/statement/import/", {"document": {{document.id}}, "text": ref}, function(data) {
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
	$.getJSON("/api/document/statement/new/{{document.id}}/0/", 
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
	$.getJSON("/api/document/statement/new/{{document.id}}/1/", 
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
	$.getJSON("/api/document/statement/new/{{document.id}}/2/", 
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
	$.getJSON("/api/document/statement/new/{{document.id}}/3/", 
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


(function ($) {

	$('body').delegate('.btn-group.state_buttons .delete', 'click', function () {
		var item = $(this).parent().parent();
		$.getJSON("/api/document/statement/delete/{{document.id}}/1/", 
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
		$.getJSON("/api/document/statement/delete/{{document.id}}/1/", 
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

})(jQuery);