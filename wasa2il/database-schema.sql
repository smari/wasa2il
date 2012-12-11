BEGIN;
CREATE TABLE "core_baseissue" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "slug" varchar(128) NOT NULL,
    "description" text
)
;
CREATE TABLE "core_userprofile" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "bio" text,
    "picture" varchar(100),
    "topics_showall" bool NOT NULL
)
;
CREATE TABLE "core_polity_members" (
    "id" integer NOT NULL PRIMARY KEY,
    "polity_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("polity_id", "user_id")
)
;
CREATE TABLE "core_polity" (
    "baseissue_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "core_baseissue" ("id"),
    "created_by_id" integer REFERENCES "auth_user" ("id"),
    "modified_by_id" integer REFERENCES "auth_user" ("id"),
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL,
    "parent_id" integer,
    "invite_threshold" integer NOT NULL,
    "is_listed" bool NOT NULL,
    "is_nonmembers_readable" bool NOT NULL,
    "image" varchar(100)
)
;
CREATE TABLE "core_topic" (
    "baseissue_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "core_baseissue" ("id"),
    "created_by_id" integer REFERENCES "auth_user" ("id"),
    "modified_by_id" integer REFERENCES "auth_user" ("id"),
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL,
    "polity_id" integer NOT NULL REFERENCES "core_polity" ("baseissue_ptr_id"),
    "image" varchar(100)
)
;
CREATE TABLE "core_usertopic" (
    "id" integer NOT NULL PRIMARY KEY,
    "topic_id" integer NOT NULL REFERENCES "core_topic" ("baseissue_ptr_id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("topic_id", "user_id")
)
;
CREATE TABLE "core_issue_topics" (
    "id" integer NOT NULL PRIMARY KEY,
    "issue_id" integer NOT NULL,
    "topic_id" integer NOT NULL REFERENCES "core_topic" ("baseissue_ptr_id"),
    UNIQUE ("issue_id", "topic_id")
)
;
CREATE TABLE "core_issue_options" (
    "id" integer NOT NULL PRIMARY KEY,
    "issue_id" integer NOT NULL,
    "voteoption_id" integer NOT NULL,
    UNIQUE ("issue_id", "voteoption_id")
)
;
CREATE TABLE "core_issue" (
    "baseissue_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "core_baseissue" ("id"),
    "created_by_id" integer REFERENCES "auth_user" ("id"),
    "modified_by_id" integer REFERENCES "auth_user" ("id"),
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL
)
;
CREATE TABLE "core_comment" (
    "id" integer NOT NULL PRIMARY KEY,
    "created_by_id" integer REFERENCES "auth_user" ("id"),
    "modified_by_id" integer REFERENCES "auth_user" ("id"),
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL,
    "comment" text NOT NULL,
    "issue_id" integer NOT NULL REFERENCES "core_issue" ("baseissue_ptr_id")
)
;
CREATE TABLE "core_delegate" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "delegate_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "base_issue_id" integer NOT NULL REFERENCES "core_baseissue" ("id"),
    UNIQUE ("user_id", "base_issue_id")
)
;
CREATE TABLE "core_voteoption" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "slug" varchar(128) NOT NULL
)
;
CREATE TABLE "core_vote" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "issue_id" integer NOT NULL REFERENCES "core_issue" ("baseissue_ptr_id"),
    "option_id" integer NOT NULL REFERENCES "core_voteoption" ("id"),
    "cast" datetime NOT NULL,
    UNIQUE ("user_id", "issue_id")
)
;
CREATE TABLE "core_membershipvote" (
    "id" integer NOT NULL PRIMARY KEY,
    "voter_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "polity_id" integer NOT NULL REFERENCES "core_polity" ("baseissue_ptr_id"),
    UNIQUE ("voter_id", "user_id", "polity_id")
)
;
CREATE TABLE "core_membershiprequest" (
    "id" integer NOT NULL PRIMARY KEY,
    "requestor_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "polity_id" integer NOT NULL REFERENCES "core_polity" ("baseissue_ptr_id"),
    "fulfilled" bool NOT NULL,
    "fulfilled_timestamp" datetime,
    UNIQUE ("requestor_id", "polity_id")
)
;
CREATE TABLE "core_document_issues" (
    "id" integer NOT NULL PRIMARY KEY,
    "document_id" integer NOT NULL,
    "issue_id" integer NOT NULL REFERENCES "core_issue" ("baseissue_ptr_id"),
    UNIQUE ("document_id", "issue_id")
)
;
CREATE TABLE "core_document" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "slug" varchar(128) NOT NULL,
    "polity_id" integer NOT NULL REFERENCES "core_polity" ("baseissue_ptr_id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "is_adopted" bool NOT NULL,
    "is_proposed" bool NOT NULL
)
;
CREATE TABLE "core_statement_text" (
    "id" integer NOT NULL PRIMARY KEY,
    "statement_id" integer NOT NULL,
    "statementoption_id" integer NOT NULL,
    UNIQUE ("statement_id", "statementoption_id")
)
;
CREATE TABLE "core_statement" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "document_id" integer NOT NULL REFERENCES "core_document" ("id"),
    "type" integer NOT NULL,
    "number" integer NOT NULL
)
;
CREATE TABLE "core_statementoption" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "text" text NOT NULL
)
;
CREATE TABLE "core_meeting_managers" (
    "id" integer NOT NULL PRIMARY KEY,
    "meeting_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("meeting_id", "user_id")
)
;
CREATE TABLE "core_meeting_attendees" (
    "id" integer NOT NULL PRIMARY KEY,
    "meeting_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("meeting_id", "user_id")
)
;
CREATE TABLE "core_meeting" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "polity_id" integer NOT NULL REFERENCES "core_polity" ("baseissue_ptr_id"),
    "location" varchar(200),
    "time_starts" datetime,
    "time_started" datetime,
    "time_ends" datetime,
    "time_ended" datetime,
    "is_agenda_open" bool NOT NULL
)
;
CREATE TABLE "core_meetingrules" (
    "id" integer NOT NULL PRIMARY KEY,
    "length_intervention" integer NOT NULL,
    "length_directresponse" integer NOT NULL,
    "length_clarify" integer NOT NULL,
    "length_pointoforder" integer NOT NULL,
    "max_interventions" integer NOT NULL,
    "max_directresponses" integer NOT NULL,
    "max_clarify" integer NOT NULL,
    "max_pointoforder" integer NOT NULL
)
;
CREATE TABLE "core_meetingagenda" (
    "id" integer NOT NULL PRIMARY KEY,
    "meeting_id" integer NOT NULL REFERENCES "core_meeting" ("id"),
    "item" varchar(200) NOT NULL,
    "order" integer NOT NULL,
    "done" integer NOT NULL
)
;
CREATE TABLE "core_meetingintervention" (
    "id" integer NOT NULL PRIMARY KEY,
    "meeting_id" integer NOT NULL REFERENCES "core_meeting" ("id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "agendaitem_id" integer NOT NULL REFERENCES "core_meetingagenda" ("id"),
    "motion" integer NOT NULL,
    "order" integer NOT NULL,
    "done" integer NOT NULL
)
;
CREATE INDEX "core_userprofile_fbfc09f1" ON "core_userprofile" ("user_id");
CREATE INDEX "core_polity_b5de30be" ON "core_polity" ("created_by_id");
CREATE INDEX "core_polity_6162aa58" ON "core_polity" ("modified_by_id");
CREATE INDEX "core_polity_63f17a16" ON "core_polity" ("parent_id");
CREATE INDEX "core_topic_b5de30be" ON "core_topic" ("created_by_id");
CREATE INDEX "core_topic_6162aa58" ON "core_topic" ("modified_by_id");
CREATE INDEX "core_topic_45004adb" ON "core_topic" ("polity_id");
CREATE INDEX "core_usertopic_57732028" ON "core_usertopic" ("topic_id");
CREATE INDEX "core_usertopic_fbfc09f1" ON "core_usertopic" ("user_id");
CREATE INDEX "core_issue_b5de30be" ON "core_issue" ("created_by_id");
CREATE INDEX "core_issue_6162aa58" ON "core_issue" ("modified_by_id");
CREATE INDEX "core_comment_b5de30be" ON "core_comment" ("created_by_id");
CREATE INDEX "core_comment_6162aa58" ON "core_comment" ("modified_by_id");
CREATE INDEX "core_comment_18752524" ON "core_comment" ("issue_id");
CREATE INDEX "core_delegate_fbfc09f1" ON "core_delegate" ("user_id");
CREATE INDEX "core_delegate_45d71fe7" ON "core_delegate" ("delegate_id");
CREATE INDEX "core_delegate_6ba13549" ON "core_delegate" ("base_issue_id");
CREATE INDEX "core_vote_fbfc09f1" ON "core_vote" ("user_id");
CREATE INDEX "core_vote_18752524" ON "core_vote" ("issue_id");
CREATE INDEX "core_vote_2f3b0dc9" ON "core_vote" ("option_id");
CREATE INDEX "core_membershipvote_fb621b2b" ON "core_membershipvote" ("voter_id");
CREATE INDEX "core_membershipvote_fbfc09f1" ON "core_membershipvote" ("user_id");
CREATE INDEX "core_membershipvote_45004adb" ON "core_membershipvote" ("polity_id");
CREATE INDEX "core_membershiprequest_8aa01657" ON "core_membershiprequest" ("requestor_id");
CREATE INDEX "core_membershiprequest_45004adb" ON "core_membershiprequest" ("polity_id");
CREATE INDEX "core_document_45004adb" ON "core_document" ("polity_id");
CREATE INDEX "core_document_fbfc09f1" ON "core_document" ("user_id");
CREATE INDEX "core_statement_fbfc09f1" ON "core_statement" ("user_id");
CREATE INDEX "core_statement_f4226d13" ON "core_statement" ("document_id");
CREATE INDEX "core_statementoption_fbfc09f1" ON "core_statementoption" ("user_id");
CREATE INDEX "core_meeting_fbfc09f1" ON "core_meeting" ("user_id");
CREATE INDEX "core_meeting_45004adb" ON "core_meeting" ("polity_id");
CREATE INDEX "core_meetingagenda_784bb48" ON "core_meetingagenda" ("meeting_id");
CREATE INDEX "core_meetingintervention_784bb48" ON "core_meetingintervention" ("meeting_id");
CREATE INDEX "core_meetingintervention_fbfc09f1" ON "core_meetingintervention" ("user_id");
CREATE INDEX "core_meetingintervention_dff5cc89" ON "core_meetingintervention" ("agendaitem_id");
COMMIT;
