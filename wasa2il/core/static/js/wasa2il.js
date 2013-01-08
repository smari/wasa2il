
var meeting_object;
var meeting_timer;
var meeting_id;
var issue_timer;
var issue_object;
var issue_id;

function document_propose(doc, val) {
	data = {};
	if (issue_id != undefined) {
		data["issue"] = issue_id;
	}
	$.getJSON("/api/document/propose/" + doc + "/" + val + "/", data, function(data) {
		if (data.ok) {
			if (data.html_user_documents != undefined) {
				$("#document_user_proposals_table").html(data.html_user_documents);
			}
			if (data.html_all_documents != undefined) {
				$("#document_all_proposals_table").html(data.html_all_documents);
			}
		}
	});
}

function topic_star(topic) {
	$.getJSON("/api/topic/star/", {"topic": topic}, function(data) {
		if (data.ok) {
			$("#topics_list tbody").html(data.html);
		}
	});
}


function topics_showstarred_toggle(polity) {
	$.getJSON("/api/topic/showstarred/", {"polity": polity}, function(data) {
		if (data.ok) {
			$("#topics_list tbody").html(data.html);
			if (data.showstarred) {
				$("#topics_showstarred_toggle i").removeClass("icon-grey");
			} else {
				$("#topics_showstarred_toggle i").addClass("icon-grey");
			}
		}
	});
}


function issue_comment_send(issue, comment) {
	comment_text = comment.val();
	if (comment_text == "") { return; }
	$.getJSON("/api/issue/comment/send/", {"issue": issue, "comment": comment_text}, function(data) {
		if (data.ok) {
			comment.val("");
			issue_object = data.issue;
			issue_render();
		} else {
			// Silent error reporting?
		}
	});
}


function issue_timer_start() {
	issue_timer = window.setInterval(function() { issue_poll(issue_id); }, 5000);
}

function issue_timer_stop() {
	window.clearInterval(issue_timer);
}


function issue_poll(issue) {
	$.getJSON("/api/issue/poll/", {"issue": issue}, function(data) {
		if (data.ok) {
			issue_object = data.issue;
			issue_render();
		} else {
			// Silent error reporting?
		}
	});
}


function issue_render(issue) {
	$("#issue_comments").empty();
	for (i in issue_object.comments) {
		comment = issue_object.comments[i];
		div = "<div class=\"comment\" id=\"comment_" + comment.id + "\">";
		div +=	"<div class=\"comment_created_by\"><a href=\"/accounts/profile/" + comment.created_by + "/\">" + comment.created_by + "</a></div>";
		div +=	"<div class=\"comment_content\">" + comment.comment + "</div>";
		div +=	"<div class=\"comment_created\">" + comment.created + "</div>";
		div += "</div>";
		$("#issue_comments").append(div);
	}
}


$(function() {

	/* --- MEMBERSHIP RELATED --- */

	$('.membership_request').click(function (e) {
		var self = $(this),
			id = $(this).attr('data-id');

		$.ajax({
			url: '/api/polity/membershipvote/',
			type: 'POST',
			data: { id: id, csrfmiddlewaretoken: $(this).attr('data-csrftoken') },
			success: function (data) {
				var user = data;
				if (data.accepted) {
					$(this).find(".membership_request").hide();
					$("#modal_members_list").append("<a href=\"/accounts/profile/" + data.username + "/\" class=\"thumbnail\">" + data.username + "</a>");
				} else {
					$(this).find(".membershiprequest_percent").css("width", data.percent);
					$(this).find(".membershiprequest_percent").text(data.votes + "/" + data.votesneeded);
				}
				self.css('opacity', '0.5');
				self.unbind('click');
				self.click(function(e3) {
					e.preventDefault();
					return false;
				});
			},
			error: function (e2) {
				alert('Some error happened with voting...');
			}
		});
		return false;
	});

	/* --- MEETINGS --- */

	/*
		TODO: Why on earth didn't I delegate the filtering to the server...
		Probably because I wanted to try doing it on the client side.
		Also, this means we can use the api call directly..
		Well. This will have to do for now :p Optimize later.
	*/
	var meeting_manager = $('.meeting-manager form')
		add_manager_input = meeting_manager.find('#meeting_manager_add');
	meeting_manager.bind('submit', function (e) {
		meeting_manager_add($('#meeting_manager_add').val());
		$(this)[0].reset();
		e.preventDefault();
		return false;
	});
	if (add_manager_input.length > 0) {
		add_manager_input.autocomplete({
			source: function (request, response) {
				$.ajax({
					url: '/api/polity/' + add_manager_input.attr('data-polity-id') + '/members/',
					type: 'GET',
					dataType: 'json',
					success: function (data) {
						var members = $.map(data.members, function (m) {
								m.label = m.str;
								m.value = m.username;
								return m;
							}),
							current_admins = $('.managerlist li').map(function () { return $(this).attr('data-user-id')*1; } );
						//var re = new RegExp('^' + request.term.toLowerCase() + '.*'),
						var re = new RegExp(request.term.toLowerCase()),
							max_ret = 3;
						count = 0;
						filtered = $.grep(members, function (m) {
								if (count > max_ret)
									return false;
								if ($.inArray(m.id, current_admins) != -1)
									return false;
								return re.exec(m.str.toLowerCase()) !== null && ++count;
							});
						if (filtered.length >= max_ret) {
							filtered[filtered.length - 1] = '...';
						}
						response(filtered);
					},
					error: function (data) { console.log('Autocomplete error'); /* handle errors! */ },
					async: false
				});
			},
			minLength: 0
		}).data('autocomplete')._renderItem = function (ul, item) {
			/* TODO: And this most certainly is a bit of an overkill.. Refacor later :p */
			var dots = item == '...';
			return $('<li' + (dots? ' style="padding: 2px 0.4em"' : '') + '>')
				.data('item.autocomplete', item)
				.append(dots ? item : '<a>' + item.str + '</a>')
				.appendTo( ul );
		};
		/*
			TODO: The focus attribute is apparently not working on current jquery-ui
			Should update soon, and remove this comment.
		*/
		add_manager_input.bind('focus', function (event, ui) {
				$(this).autocomplete("search", '');
		});
	}

});

