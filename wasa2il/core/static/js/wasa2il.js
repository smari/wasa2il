
var meeting_object;
var meeting_timer;
var meeting_id;
var issue_timer;
var issue_object;
var issue_id;

function document_propose(doc, val) {
	$.getJSON("/api/document/propose/" + doc + "/" + val + "/", function(data) {
		if (data.ok) {
			
		}
	});
}


function meeting_timer_start() {
	meeting_timer = window.setInterval(function() { meeting_poll(meeting_id); }, 1000);
}

function meeting_timer_stop() {
	window.clearInterval(meeting_timer);
}


function meeting_poll(meeting) {
	$.getJSON("/api/meeting/poll/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		} else {
			// Silent error reporting?
		}
	});
}


function meeting_render() {
	if (meeting_object.is_agenda_open) {
		$('.meeting-agendaclosed').hide();
		$('.meeting-agendaopen').show();
		$('#agenda-item-add').show();
	} else {
		$('.meeting-agendaclosed').show();
		$('.meeting-agendaopen').hide();
		$('#agenda-item-add').hide();
	}

	if (meeting_object.is_ongoing) {
		$('.meeting-notongoing').hide();
		$('.meeting-ongoing').show();
	} else {
		$('.meeting-ongoing').hide();
		$('.meeting-notongoing').show();
	}

	if (meeting_object.is_not_started) {
		$('.meeting-notstarted').show();
	} else {
		$('.meeting-notstarted').hide();
	}

	if (meeting_object.is_ended) {
		$('.meeting-ended').show();
	} else {
		$('.meeting-ended').hide();
	}

	if (meeting_object.user_is_manager) {
		$('.meeting-manager').show();
	} else {
		$('.meeting-manager').hide();
	}

	if (meeting_object.user_is_attendee) {
		$('.meeting-attendee').show();
	} else {
		$('.meeting-attendee').hide();
	}

	$("#attendancelist").empty();
	for (i in meeting_object.attendees) {
		entry = meeting_object.attendees[i];
		if ($.inArray(entry, meeting_object.managers) > -1) {
			st = "icon-bullhorn";
		} else {
			st = "icon-user";
		}
		$("#attendancelist").append("<li><i class=\"" + st + "\"></i> <a href=\"/accounts/profile/" + entry + "/\">" + entry + "</a></li>");
	}

	$("#managerlist").empty();
	for (i in meeting_object.managers) {
		entry = meeting_object.managers[i];
		st = "icon-bullhorn";
		$("#managerlist").append("<li data-user-id=\"" + entry.id + "\"><i class=\"" + st + "\"></i> <a href=\"/accounts/profile/" + entry.username + "/\">" + entry.str + "</a></li>");
	}

	$("#agenda-items").empty();
	for (i in meeting_object.agenda) {
		item = meeting_object.agenda[i];
		if (item.done == 2) {
			done = " class=\"done\"";
		} else if (item.done == 1) {
			done = " class=\"ongoing\"";
		} else {
			done = "";
		}
		if (meeting_object.is_agenda_open) {
			actions = "<div class=\"agenda-actions\"><a class=\"btn btn-mini btn-warning\" onclick=\"meeting_agenda_remove(" + item.id + ");\">×</a></div>";
		} else {
			actions = "";
		}
		interventions = "<ol class=\"interventions\">"
		for (j in item.interventions) {
			intervention = item.interventions[j];
			if (intervention.motion == 1) { type = "icon-hand-up"; } else
			if (intervention.motion == 2) { type = "icon-hand-left"; } else
			if (intervention.motion == 3) { type = "icon-question-sign"; } else
			if (intervention.motion == 4) { type = "icon-info-sign"; }
			interventions += "<li><i class=\"" + type + "\"></i> <a href=\"/accounts/profile/" + intervention.user + "\">" + intervention.user + "</li>";
		}
		interventions += "</ol>";

		$("#agenda-items").append("<li data-seqid=\"" + item.id + "\"" + done + "><span class=\"title\">" + item.item + '</span>' + actions + interventions + "</li>");
	}
	if (meeting_object.is_agenda_open) {
		$("#agenda-items").sortable({ update: function(event, ui) {
			ord = [];
			$("#agenda-items li").each(function(item) {
				ord.push($($("#agenda-items li")[item]).data("seqid"));
			});
			$.getJSON("/api/meeting/agenda/reorder/", {"meeting": meeting_id, "order": ord}, function(data) {
				if (data.ok) {
					meeting_object = data.meeting;
					meeting_render();
				}
			});
		}});
	} else {
		var isDisabled = $( "#agenda-items" ).sortable( "option", "disabled" );
		if (!isDisabled) {
			$("#agenda-items").sortable("disable");
		}
	}
	$("#agenda-items li").mousedown(function(){ meeting_timer_stop(); });
	$("#agenda-items li").mouseup(function(){ meeting_timer_start(); });
//.meeting-notongoing, .meeting-ongoing, .meeting-notstarted, .meeting-ended,
//.meeting-agendaopen, .meeting-agendaclosed, .meeting-manager, .meeting-attendee
}


function meeting_attend(meeting, val) {
	$.getJSON("/api/meeting/attend/" + meeting + "/", {"meeting": meeting, "status": val}, function(data) {
		if (data.ok) {
			
		}
	});
}


function meeting_start(meeting, force) {
	now = new Date();
	if (!force && Date.parse(meeting_object.time_starts_iso) > now.getTime()) {
		$("#meeting_start_early").modal();
		return;
	}
	$.getJSON("/api/meeting/start/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			
		}
	});
}


function meeting_end(meeting) {
	$.getJSON("/api/meeting/end/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			
		}
	});
}


function meeting_agenda_close(meeting) {
	$.getJSON("/api/meeting/agenda/close/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
	$('#agenda-item-add').hide();
}


function meeting_agenda_open(meeting) {
	$.getJSON("/api/meeting/agenda/open/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
	$('#agenda-item-add').show();
}


function meeting_agenda_add(meeting, item) {
	$.getJSON("/api/meeting/agenda/add/", {"meeting": meeting, "item": item}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_agenda_remove(item) {
	$.getJSON("/api/meeting/agenda/remove/", {"item": item, "meeting": meeting_id}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_agenda_next(meeting) {
	$.getJSON("/api/meeting/agenda/next/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_agenda_prev(meeting) {
	$.getJSON("/api/meeting/agenda/prev/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_intervention_add(meeting, type) {
	$.getJSON("/api/meeting/intervention/add/", {"meeting": meeting, "type": type}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_intervention_next(meeting) {
	$.getJSON("/api/meeting/intervention/next/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_intervention_previous(meeting) {
	$.getJSON("/api/meeting/intervention/prev/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
}


function meeting_manager_add(username) {
	$.getJSON("/api/meeting/manager/add/", {"meeting": meeting_id, "user": username}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	})
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


});

