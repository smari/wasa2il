
var meeting_object;
var meeting_timer;
var meeting_id;

function document_propose(doc, val) {
	$.getJSON("/api/propose/", {"document": doc, "status": val}, function(data) {
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
	} else {
		$('.meeting-agendaclosed').show();
		$('.meeting-agendaopen').hide();
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
		$("#managerlist").append("<li><i class=\"" + st + "\"></i> <a href=\"/accounts/profile/" + entry + "/\">" + entry + "</a></li>");
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

		$("#agenda-items").append("<li data-seqid=\"" + item.id + "\"" + done + ">" + item.item + actions + interventions + "</li>");
	}
	if (meeting_object.is_agenda_open) {
		$("#agenda-items").sortable({ update: function(event, ui) {
			ord = [];
			$("#agenda-items li").each(function(item) {
				ord.push($($("#agenda-items li")[item]).data("seqid"));
			});
			$.getJSON("/api/meeting/agenda/reorder/", {"meeting": meeting_id, "order": ord}, function() {
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
}


function meeting_agenda_open(meeting) {
	$.getJSON("/api/meeting/agenda/open/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;
			meeting_render();
		}
	});
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


function topic_star(topic) {
	$.getJSON("/api/topic/star/", {"topic": topic}, function(data) {
		if (data.ok) {
			if (data.starred) {
				$("#topicstar_" + topic).removeclass("icon-star-blank");
				$("#topicstar_" + topic).addclass("icon-star");
			} else {
				$("#topicstar_" + topic).removeclass("icon-star");
				$("#topicstar_" + topic).addclass("icon-star-blank");
			}
			topics_render();
		}
	});
}

$(function() {

	$('.membership_request').click(function (e) {
		var id = $(this).attr('data-id');

		$.ajax({
			url: '/api/polity/membershipvote/',
			type: 'POST',
			data: { id: id, csrfmiddlewaretoken: $(this).attr('data-csrftoken') },
			success: function (e2) {
				if (data.accepted) {
					$("#membershiprequest_" + user).hide();
					$("#modal_members_list").append("<a href=\"/accounts/profile/" + data.username + "/\" class=\"thumbnail\">" + data.username + "</a>");
				} else {
					$("#membershiprequest_percent_" + user).css("width", data.percent);
					$("#membershiprequest_percent_" + user).text(data.votes + "/" + data.votesneeded);
				}
			},
			error: function (e2) {
				alert('Some error happened with voting...');
			}
		})
		return false;
	});

});

