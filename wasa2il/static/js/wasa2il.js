

function document_propose(doc, val) {
	$.getJSON("/api/propose/", {"document": doc, "status": val}, function(data) {
		if (data) {
			
		}
	});
}


function meeting_attend(meeting, val) {
	$.getJSON("/api/meeting/attend/" + meeting + "/", {"meeting": meeting, "status": val}, function(data) {
		if (data) {
			
		}
	});
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
