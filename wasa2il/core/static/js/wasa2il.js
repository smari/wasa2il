
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


function elections_showclosed_toggle(polity_id) {
    show_closed_elections = (show_closed_elections ? 0 : 1);
    $.getJSON("/api/election/showclosed/", {"polity_id": polity_id, "showclosed": show_closed_elections}, function(data) {
        if (data.ok) {
            $("#elections_list tbody").html(data.html);
            if (data.showclosed) {
                $("#elections_showclosed_toggle i").removeClass("icon-grey");
            } else {
                $("#elections_showclosed_toggle i").addClass("icon-grey");
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
    if (issue_object.vote == 1) {
        $("#vote_yes").button('toggle');
    } else if (issue_object.vote == -1) {
        $("#vote_no").button('toggle');
    } else {
        $("#vote_abstain").button('toggle');
    }
    $("#issue_votes_count").text(issue_object.votes.count);
    $("#issue_comments").empty();
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
    election_timer = window.setInterval(function() { election_poll(election_id); }, 5000);
}

function election_timer_stop() {
    window.clearInterval(election_timer);
}


function election_vote(val) {
    election_timer_stop();
    $.getJSON("/api/election/vote/", {"election": election_id, "vote": val}, function(data) {
        if (data.ok) {
            election_object = data.election;
            election_render();            
        } else {
            $("#vote_error").show();
        }
        election_timer_start();
    });
}


function election_candidacy_announce() {
    return election_candidacy(1);
}

function election_candidacy_withdraw() {
    return election_candidacy(0);
}


function election_candidacy(val) {
    election_timer_stop();
    $.getJSON("/api/election/candidacy/", {"election": election_id, "val": val}, function(data) {
        if (data.ok) {
            election_object = data.election;
            election_render();            
        } else {
        }
        election_timer_start();
    });
}


function election_poll(election) {
    $.getJSON("/api/election/poll/", {"election": election}, function(data) {
        if (data.ok) {
            election_object = data.election;
            election_render();
        } else {
            // Silent error reporting?
        }
    });
}


function election_render(election) {
    if (election_object.is_voting) {
        $("#election_button_announce").hide();
        $("#election_button_withdraw").hide();
        $(".voting").show();
    } else {
        $(".voting").hide();
        if (election_object.user_is_candidate) {
            $("#election_button_announce").hide();
            $("#election_button_withdraw").show();
        } else {
            $("#election_button_withdraw").hide();
            $("#election_button_announce").show();
        }
    }
    $("#election_votes_count").text(election_object.votes.count);
    $("#election_candidates_count").text(election_object.candidates.count);
    if($("#candidates").attr('data-loaded')){
        //data has been loaded, do not update
    }
    else{
        $("#candidates").html(election_object.candidates.html);
        $("#candidates").attr('data-loaded', "true");
    }
    $("#vote").html(election_object.vote.html);
}





$(function() {

    $("i[rel='tooltip'],a[rel='tooltip']").tooltip({'placement': 'top'});

});

