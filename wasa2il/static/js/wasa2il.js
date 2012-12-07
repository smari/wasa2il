

function document_propose(doc, val) {
	$.getJSON("/api/propose/", {"document": doc, "status": val}, function(data) {
		if (data.ok) {
			
		}
	});
}


function polity_membership_vote(polity, user) {
	$.getJSON("/api/polity/membershipvote/", {"polity": polity, "user": user}, function(data) {
		if (data.ok) {
			if (data.accepted) {
				$("#membershiprequest_" + user).hide();
				$("#modal_members_list").append("<a href=\"/accounts/profile/" + data.username + "/\" class=\"thumbnail\">" + data.username + "</a>");
			} else {
				$("#membershiprequest_percent_" + user).css("width", data.percent);
				$("#membershiprequest_percent_" + user).text(data.votes + "/" + data.votesneeded);
			}
		} else {

		}
	});
}


function meeting_poll(meeting) {
	$.getJSON("/api/meeting/poll/", {"meeting": meeting}, function(data) {
		if (data.ok) {
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
		if (data) {
			
		}
	});
}


function meeting_start(meeting) {

}


function meeting_stop(meeting) {

}


function meeting_agenda_close(meeting) {

}


function meeting_agenda_open(meeting) {

}


function meeting_agenda_add(meeting) {

}


function meeting_intervention_add(meeting, type) {

}


function meeting_intervention_next(meeting) {

}


function meeting_intervention_previous(meeting) {

}
