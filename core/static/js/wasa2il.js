var issue_timer;
var issue_object;
var issue_id;
var election_timer;
var election_object;
var election_id;
var discussion_timer;
var discussion_object;
var discussion_id;
var show_closed_elections;


function user_logged_out() {
    var user_id = $('input[name=user_id]').val();
    if (user_id && user_id != 'None') location.reload(true);
}


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
                $("#topics_showstarred_toggle span").removeClass("icon-grey");
            } else {
                $("#topics_showstarred_toggle span").addClass("icon-grey");
            }
        }
    });
}


function elections_showclosed_toggle(polity_id) {
    show_closed_elections = (show_closed_elections ? 0 : 1);
    $.getJSON("/api/election/showclosed/", {"polity_id": polity_id, "showclosed": show_closed_elections}, function(data) {
        if (data.ok) {
            $("#elections_list tbody").html(data.html);
            if (data.showclosed) {
                $("#elections_showclosed_toggle span").removeClass("icon-grey");
            } else {
                $("#elections_showclosed_toggle span").addClass("icon-grey");
            }
        }
    });
}


function issue_comment_send(issue, comment) {
    comment_text = comment.val();

    if (comment_text == "") {
        comment.focus();
        return;
    }

    data = {
        'issue': issue,
        'comment': comment_text,
        'csrfmiddlewaretoken': $('.comment_form').find('input[name="csrfmiddlewaretoken"]').val(),
    }

    $.post("/api/issue/comment/send/", data, null, 'json').done(function(data) {
        if (data.ok) {
            comment.val("");
            issue_object = data.issue;
            issue_render();
            comment.focus();
        }
        else {
            alert('Error: Data was received but does not seem to be JSON');
        }
    }).fail(function(xhr, textStatus, errorThrown) {
        alert("Error: " + errorThrown);
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
    //remove selection and deactivate all active buttons
    $("#vote_yes").parent().children().removeClass('btn-success');
    $("#vote_yes").parent().children().removeClass('active');

    if (issue_object.vote == 1) {
        $("#vote_yes").addClass('btn-success');
        $("#vote_yes").addClass('active');
    } else if (issue_object.vote == -1) {
        $("#vote_no").addClass('btn-success');
        $("#vote_no").addClass('active');
    } else {
        $("#vote_abstain").addClass('btn-success');
        $("#vote_abstain").addClass('active');
    }
    $("#issue_votes_count").text(issue_object.votes.count);
    $("#issue_comments").empty();
    if (issue_object.comments.length > 0) {
        $("#issue-comments-header").show();
    }
    else {
        $("#issue-comments-header").hide();
    }
    for (i in issue_object.comments) {
        comment = issue_object.comments[i];
        div = "<div class=\"comment\" id=\"comment_" + comment.id + "\">";
        div +=    "<div class=\"comment_created_by\"><a href=\"/accounts/profile/" + comment.created_by + "/\">" + comment.created_by + "</a></div>";
        div +=    "<div class=\"comment_content\">" + comment.comment.replace(/\n/g, '<br />') + "</div>";
        div +=    "<div class=\"comment_created\">" + comment.created_since + "</div>";
        div += "</div>";
        $("#issue_comments").append(div);
    }
}


function discussion_poll(discussion) {
    $.getJSON("/api/discussion/poll/", {"discussion": discussion}, function(data) {
        if (data.ok) {
            discussion_object = data.discussion;
            discussion_render();
        } else {
            // Silent error reporting?
        }
    });
}


function discussion_render(discussion) {
    $("#discussion_comments").empty();
    for (i in discussion_object.comments) {
        comment = discussion_object.comments[i];
        div = "<div class=\"comment\" id=\"comment_" + comment.id + "\">";
        div +=    "<div class=\"comment_created_by\"><a href=\"/accounts/profile/" + comment.created_by + "/\">" + comment.created_by + "</a></div>";
        div +=    "<div class=\"comment_content\">" + comment.comment + "</div>";
        div +=    "<div class=\"comment_created\">" + comment.created_since + "</div>";
        div += "</div>";
        $("#discussion_comments").append(div);
    }
}



function discussion_comment_send(discussion, comment) {
    comment_text = comment.val();
    if (comment_text == "") { return; }
    $.getJSON("/api/discussion/comment/send/", {"discussion": discussion, "comment": comment_text}, function(data) {
        if (data.ok) {
            comment.val("");
            discussion_object = data.discussion;
            discussion_render();
        } else {
            // Silent error reporting?
        }
    });
}


function discussion_timer_start() {
    discussion_timer = window.setInterval(function() { discussion_poll(discussion_id); }, 5000);
}

function discussion_timer_stop() {
    window.clearInterval(discussion_timer);
}


function election_timer_start() {
    // This is basically just checking for new candidates or keeping
    // different tabs/windows in sync and as such, doesn't really need to
    // happen too frequently.  Doing this too fast just increases load.
    election_timer = window.setInterval(function() {
        election_poll(election_id);
    }, 20000);
}

function election_timer_stop() {
    window.clearInterval(election_timer);
}


function election_vote(val) {
    election_timer_stop();
    $.getJSON("/api/election/vote/", {"election": election_id, "vote": val}, function(data) {
        if (data.logged_out) user_logged_out();
        if (data.ok) {
            election_object = data.election;
        } else {
            $("#vote_error").show();
        }
        election_render();
        election_timer_start();
    });
}


function election_candidacy_announce() {
    $('#election_button_announce').hide();
    $('#election_announce_working').show();
    return election_candidacy(1);
}

function election_candidacy_withdraw() {
    var confirm_msg = $('#election_button_withdraw').data("confirm");
    if (!confirm_msg || confirm(confirm_msg)) {
        $('#election_button_withdraw').hide();
        $('#election_announce_working').show();
        return election_candidacy(0);
    }
}


function election_candidacy(val) {
    election_timer_stop();
    $.post("/api/election/candidacy/", {
        "csrfmiddlewaretoken": $('input[name=csrfmiddlewaretoken]').val(),
        "election": election_id,
        "val": val
    }, function(data) {
        if (data.ok) {
            election_object = data.election;
        } else {
            // FIXME: Error handling?
        }
        election_render();
        election_timer_start();
    }, "json").always(function() {
        $('#election_announce_working').hide();
    });
}


function election_poll(election) {
    $.getJSON("/api/election/poll/", {"election": election}, function(data) {
        if (data.logged_out) user_logged_out();
        if (data.ok) {
            election_object = data.election;
            $('#submit-working, #submit-is-magic, #submit-error').hide();
        } else {
            // FIXME: Error handling?
        }
        election_render();
    });
}


function election_render(election) {
    if (election_object.is_voting) {
        $(".voting").show();
    }

    // FIXME: The second term here makes much of the code below obsolete.
    //        This is deliberate; we would like to allow users to withdraw
    // their candidacy at any time, but we need a few more things before
    // that is safe and reasonable:
    //     1. E-mail notifications to people who have voted for the candidate
    //     2. A grace period so people can update their votes
    //     3. Double-checking the ballot counting logic to ensure this does
    //        not break anything at that end, as it will create a gap in
    //        the user's ballot sequence.
    if (election_object.is_closed || election_object.is_voting) {
        $("#election_button_withdraw").hide();
        $("#election_button_announce").hide();
    }
    else if (election_object.user_is_candidate) {
        $("#election_button_withdraw").show();
        $("#election_button_announce").hide();
    }
    else {
        $("#election_button_withdraw").hide();
        if (election_object.is_voting) {
            $("#election_button_announce").hide();
        } else if (election_object.is_waiting) {
            $("#election_button_announce").hide();
        } else {
            $("#election_button_announce").show();
        }
    }

    $("#election_votes_count").text(election_object.votes.count);
    $("#election_candidates_count").text(election_object.candidates.count);
    $("#candidates").html(election_object.candidates.html);
    $("#vote").html(election_object.vote.html);
}


$(document).ready(function() {
    // NOTE: The first text input field is the search field at the top of the page.
    // I was here. This gets the order incorrectly or something.
    var $inputs = $('input[type="text"],input[type="password"],textarea');
    if ($inputs.length > 1) {
        $inputs[1].focus();
    }
});


$(function() {

    $("i[rel='tooltip'],a[rel='tooltip']").tooltip({'placement': 'top'});

});

