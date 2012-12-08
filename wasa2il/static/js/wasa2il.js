
var meeting_object;

function document_propose(doc, val) {
	$.getJSON("/api/propose/", {"document": doc, "status": val}, function(data) {
		if (data.ok) {
			
		}
	});
}



function meeting_poll(meeting) {
	$.getJSON("/api/meeting/poll/", {"meeting": meeting}, function(data) {
		if (data.ok) {
			meeting_object = data.meeting;

			if (data.meeting.is_agenda_open) {
				$('.meeting-agendaclosed').hide();
				$('.meeting-agendaopen').show();
			} else {
				$('.meeting-agendaclosed').show();
				$('.meeting-agendaopen').hide();
			}

			if (data.meeting.is_ongoing) {
				$('.meeting-notongoing').hide();
				$('.meeting-ongoing').show();
			} else {
				$('.meeting-ongoing').hide();
				$('.meeting-notongoing').show();
			}

			if (data.meeting.is_not_started) {
				$('.meeting-notstarted').show();
			} else {
				$('.meeting-notstarted').hide();
			}

			if (data.meeting.is_ended) {
				$('.meeting-ended').show();
			} else {
				$('.meeting-ended').hide();
			}

			if (data.meeting.user_is_manager) {
				$('.meeting-manager').show();
			} else {
				$('.meeting-manager').hide();
			}

			if (data.meeting.user_is_attendee) {
				$('.meeting-attendee').show();
			} else {
				$('.meeting-attendee').hide();
			}

			$("#attendancelist").empty();
			for (i in data.meeting.attendees) {
				entry = data.meeting.attendees[i];
				if ($.inArray(entry, data.meeting.managers) > -1) {
					st = "icon-bullhorn";
				} else {
					st = "icon-user";
				}
				$("#attendancelist").append("<li><i class=\"" + st + "\"></i> <a href=\"/accounts/profile/" + entry + "/\">" + entry + "</a></li>")
			}
//.meeting-notongoing, .meeting-ongoing, .meeting-notstarted, .meeting-ended,
//.meeting-agendaopen, .meeting-agendaclosed, .meeting-manager, .meeting-attendee
			
		} else {
			// Silent error reporting?
		}
	});
}


function meeting_render(meeting, structure) {
	
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

}


function meeting_agenda_open(meeting) {

}


function meeting_agenda_add(meeting) {
	$("#agenda-item-add").show();
}


function meeting_intervention_add(meeting, type) {

}


function meeting_intervention_next(meeting) {

}


function meeting_intervention_previous(meeting) {

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
