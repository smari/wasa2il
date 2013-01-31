
var meeting_object;
var meeting_timer;
var meeting_id;
var issue_timer;
var issue_object;
var issue_id;
var statement_active;

function document_propose(doc, val) {
	data = {};
	if (issue_id != undefined) {
		data["issue"] = issue_id;
	}
	$.getJSON("/api/document/propose/" + doc + "/" + val + "/", data, function(data) {
		if (data.ok) {
			$('#document_import').modal('hide');
			if (data.html_user_documents != undefined) {
				$("#document_user_proposals_table").html(data.html_user_documents);
			}
			if (data.html_all_documents != undefined) {
				$("#document_all_proposals_table").html(data.html_all_documents);
			}
		}
	});
}


function document_import(doc) {
	data = {};
	if (issue_id != undefined) {
		data["issue"] = issue_id;
	}
	data["document"] = doc;

	$.getJSON("/api/issue/import/", data, function(data) {
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


function issue_vote(val) {
	issue_timer_stop();
	$.getJSON("/api/issue/vote/", {"issue": issue_id, "vote": val}, function(data) {
		if (data.ok) {
			issue_object = data.issue;
			issue_render();			
		} else {
			$("#vote_error").show();
		}
		issue_timer_start();
	});
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
	console.log(issue_object.vote);
	if (issue_object.vote == 1) {
		$("#vote_yes").button('toggle');
	} else if (issue_object.vote == -1) {
		$("#vote_no").button('toggle');
	} else {
		$("#vote_abstain").button('toggle');
	}
	$("#issue_votes_count").text(issue_object.votes.count);
	$("#issue_votes_yes").text(issue_object.votes.yes);
	$("#issue_votes_no").text(issue_object.votes.no);
	// $("#issue_votes_abstain").text(issue_object.votes.abstain);
	$("#issue_comments").empty();
	for (i in issue_object.comments) {
		comment = issue_object.comments[i];
		div = "<div class=\"comment\" id=\"comment_" + comment.id + "\">";
		div +=	"<div class=\"comment_created_by\"><a href=\"/accounts/profile/" + comment.created_by + "/\">" + comment.created_by + "</a></div>";
		div +=	"<div class=\"comment_content\">" + comment.comment + "</div>";
		div +=	"<div class=\"comment_created\">" + comment.created_since + "</div>";
		div += "</div>";
		$("#issue_comments").append(div);
	}
}


$(function() {

	$("i[rel='tooltip'],a[rel='tooltip']").tooltip({'placement': 'top'});

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

});

