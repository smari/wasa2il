BEGIN;
CREATE TABLE `core_baseissue` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(128) NOT NULL,
    `slug` varchar(128) NOT NULL,
    `description` longtext
)
;
CREATE TABLE `core_userprofile` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL UNIQUE,
    `displayname` varchar(255),
    `email_visible` bool NOT NULL,
    `bio` longtext,
    `picture` varchar(100),
    `language` varchar(6) NOT NULL,
    `topics_showall` bool NOT NULL,
    `high_seat` bool NOT NULL
)
;
ALTER TABLE `core_userprofile` ADD CONSTRAINT `user_id_refs_id_55007184` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `core_polityruleset` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `polity_id` integer NOT NULL,
    `name` varchar(255) NOT NULL,
    `issue_quora_percent` bool NOT NULL,
    `issue_quora` integer NOT NULL,
    `issue_majority` integer NOT NULL,
    `issue_discussion_time` integer NOT NULL,
    `issue_proposal_time` integer NOT NULL,
    `issue_vote_time` integer NOT NULL,
    `confirm_with_id` integer,
    `adopted_if_accepted` bool NOT NULL
)
;
ALTER TABLE `core_polityruleset` ADD CONSTRAINT `confirm_with_id_refs_id_279baccd` FOREIGN KEY (`confirm_with_id`) REFERENCES `core_polityruleset` (`id`);
CREATE TABLE `core_polity_officers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `polity_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`polity_id`, `user_id`)
)
;
ALTER TABLE `core_polity_officers` ADD CONSTRAINT `user_id_refs_id_eb2ba083` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `core_polity_members` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `polity_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`polity_id`, `user_id`)
)
;
ALTER TABLE `core_polity_members` ADD CONSTRAINT `user_id_refs_id_69271430` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `core_polity` (
    `baseissue_ptr_id` integer NOT NULL PRIMARY KEY,
    `created_by_id` integer,
    `modified_by_id` integer,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `parent_id` integer,
    `invite_threshold` integer NOT NULL,
    `is_administrated` bool NOT NULL,
    `is_listed` bool NOT NULL,
    `is_nonmembers_readable` bool NOT NULL,
    `is_newissue_only_officers` bool NOT NULL,
    `image` varchar(100),
    `document_frontmatter` longtext,
    `document_midmatter` longtext,
    `document_footer` longtext
)
;
ALTER TABLE `core_polity` ADD CONSTRAINT `baseissue_ptr_id_refs_id_30e033ab` FOREIGN KEY (`baseissue_ptr_id`) REFERENCES `core_baseissue` (`id`);
ALTER TABLE `core_polity` ADD CONSTRAINT `created_by_id_refs_id_f6e26a14` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_polity` ADD CONSTRAINT `modified_by_id_refs_id_f6e26a14` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_polityruleset` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_6fd3d9ce` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_polity_officers` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_2a0f7844` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_polity_members` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_d46bc709` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_polity` ADD CONSTRAINT `parent_id_refs_baseissue_ptr_id_9fb27875` FOREIGN KEY (`parent_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
CREATE TABLE `core_topic` (
    `baseissue_ptr_id` integer NOT NULL PRIMARY KEY,
    `created_by_id` integer,
    `modified_by_id` integer,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `polity_id` integer NOT NULL,
    `image` varchar(100)
)
;
ALTER TABLE `core_topic` ADD CONSTRAINT `baseissue_ptr_id_refs_id_455584b6` FOREIGN KEY (`baseissue_ptr_id`) REFERENCES `core_baseissue` (`id`);
ALTER TABLE `core_topic` ADD CONSTRAINT `created_by_id_refs_id_8e2b12d9` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_topic` ADD CONSTRAINT `modified_by_id_refs_id_8e2b12d9` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_topic` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_8a018460` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
CREATE TABLE `core_usertopic` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `topic_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`topic_id`, `user_id`)
)
;
ALTER TABLE `core_usertopic` ADD CONSTRAINT `user_id_refs_id_75de8f8c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_usertopic` ADD CONSTRAINT `topic_id_refs_baseissue_ptr_id_aad1d0aa` FOREIGN KEY (`topic_id`) REFERENCES `core_topic` (`baseissue_ptr_id`);
CREATE TABLE `core_issue_topics` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `issue_id` integer NOT NULL,
    `topic_id` integer NOT NULL,
    UNIQUE (`issue_id`, `topic_id`)
)
;
ALTER TABLE `core_issue_topics` ADD CONSTRAINT `topic_id_refs_baseissue_ptr_id_4d8d42bf` FOREIGN KEY (`topic_id`) REFERENCES `core_topic` (`baseissue_ptr_id`);
CREATE TABLE `core_issue` (
    `baseissue_ptr_id` integer NOT NULL PRIMARY KEY,
    `created_by_id` integer,
    `modified_by_id` integer,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `polity_id` integer NOT NULL,
    `deadline_proposals` datetime,
    `deadline_votes` datetime,
    `ruleset_id` integer
)
;
ALTER TABLE `core_issue` ADD CONSTRAINT `baseissue_ptr_id_refs_id_ddae36ee` FOREIGN KEY (`baseissue_ptr_id`) REFERENCES `core_baseissue` (`id`);
ALTER TABLE `core_issue` ADD CONSTRAINT `created_by_id_refs_id_6b8dbde3` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_issue` ADD CONSTRAINT `modified_by_id_refs_id_6b8dbde3` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_issue` ADD CONSTRAINT `ruleset_id_refs_id_285b1bbd` FOREIGN KEY (`ruleset_id`) REFERENCES `core_polityruleset` (`id`);
ALTER TABLE `core_issue` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_e759fce4` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_issue_topics` ADD CONSTRAINT `issue_id_refs_baseissue_ptr_id_b7161533` FOREIGN KEY (`issue_id`) REFERENCES `core_issue` (`baseissue_ptr_id`);
CREATE TABLE `core_comment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_by_id` integer,
    `modified_by_id` integer,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `issue_id` integer NOT NULL
)
;
ALTER TABLE `core_comment` ADD CONSTRAINT `created_by_id_refs_id_40c4b8f5` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_comment` ADD CONSTRAINT `modified_by_id_refs_id_40c4b8f5` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_comment` ADD CONSTRAINT `issue_id_refs_baseissue_ptr_id_9c2a8afd` FOREIGN KEY (`issue_id`) REFERENCES `core_issue` (`baseissue_ptr_id`);
CREATE TABLE `core_delegate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `delegate_id` integer NOT NULL,
    `base_issue_id` integer NOT NULL,
    UNIQUE (`user_id`, `base_issue_id`)
)
;
ALTER TABLE `core_delegate` ADD CONSTRAINT `user_id_refs_id_8827bef8` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_delegate` ADD CONSTRAINT `delegate_id_refs_id_8827bef8` FOREIGN KEY (`delegate_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_delegate` ADD CONSTRAINT `base_issue_id_refs_id_c2b1db27` FOREIGN KEY (`base_issue_id`) REFERENCES `core_baseissue` (`id`);
CREATE TABLE `core_vote` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `issue_id` integer NOT NULL,
    `value` integer NOT NULL,
    `cast` datetime NOT NULL,
    `power_when_cast` integer NOT NULL,
    UNIQUE (`user_id`, `issue_id`)
)
;
ALTER TABLE `core_vote` ADD CONSTRAINT `user_id_refs_id_6eebf50f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_vote` ADD CONSTRAINT `issue_id_refs_baseissue_ptr_id_b08c2101` FOREIGN KEY (`issue_id`) REFERENCES `core_issue` (`baseissue_ptr_id`);
CREATE TABLE `core_membershipvote` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `voter_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `polity_id` integer NOT NULL,
    UNIQUE (`voter_id`, `user_id`, `polity_id`)
)
;
ALTER TABLE `core_membershipvote` ADD CONSTRAINT `voter_id_refs_id_ef248c71` FOREIGN KEY (`voter_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_membershipvote` ADD CONSTRAINT `user_id_refs_id_ef248c71` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_membershipvote` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_8ad38e98` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
CREATE TABLE `core_membershiprequest` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `requestor_id` integer NOT NULL,
    `polity_id` integer NOT NULL,
    `fulfilled` bool NOT NULL,
    `fulfilled_timestamp` datetime,
    `left` bool NOT NULL,
    UNIQUE (`requestor_id`, `polity_id`)
)
;
ALTER TABLE `core_membershiprequest` ADD CONSTRAINT `requestor_id_refs_id_f4e8b5bf` FOREIGN KEY (`requestor_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_membershiprequest` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_6963ae86` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
CREATE TABLE `core_document_issues` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` integer NOT NULL,
    `issue_id` integer NOT NULL,
    UNIQUE (`document_id`, `issue_id`)
)
;
ALTER TABLE `core_document_issues` ADD CONSTRAINT `issue_id_refs_baseissue_ptr_id_f02b7fd0` FOREIGN KEY (`issue_id`) REFERENCES `core_issue` (`baseissue_ptr_id`);
CREATE TABLE `core_document` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(128) NOT NULL,
    `slug` varchar(128) NOT NULL,
    `polity_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `is_adopted` bool NOT NULL,
    `is_proposed` bool NOT NULL
)
;
ALTER TABLE `core_document` ADD CONSTRAINT `user_id_refs_id_35f3a44a` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_document` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_2547b171` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_document_issues` ADD CONSTRAINT `document_id_refs_id_7441133f` FOREIGN KEY (`document_id`) REFERENCES `core_document` (`id`);
CREATE TABLE `core_documentcontent` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `document_id` integer NOT NULL,
    `created` datetime NOT NULL,
    `text` longtext NOT NULL,
    `diff` longtext NOT NULL,
    `patch` longtext NOT NULL,
    `order` integer NOT NULL,
    `comments` longtext NOT NULL,
    `status` varchar(32) NOT NULL
)
;
ALTER TABLE `core_documentcontent` ADD CONSTRAINT `user_id_refs_id_f748fd9a` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_documentcontent` ADD CONSTRAINT `document_id_refs_id_4d3f5fe7` FOREIGN KEY (`document_id`) REFERENCES `core_document` (`id`);
CREATE TABLE `core_statement` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `document_id` integer NOT NULL,
    `type` integer NOT NULL,
    `number` integer NOT NULL,
    `text` longtext NOT NULL
)
;
ALTER TABLE `core_statement` ADD CONSTRAINT `user_id_refs_id_e56ee4db` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_statement` ADD CONSTRAINT `document_id_refs_id_492dd5f4` FOREIGN KEY (`document_id`) REFERENCES `core_document` (`id`);
CREATE TABLE `core_statementoption` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statement_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `text` longtext NOT NULL
)
;
ALTER TABLE `core_statementoption` ADD CONSTRAINT `user_id_refs_id_465ce7d8` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_statementoption` ADD CONSTRAINT `statement_id_refs_id_c61aa3d0` FOREIGN KEY (`statement_id`) REFERENCES `core_statement` (`id`);
CREATE TABLE `core_changeproposal` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_by_id` integer,
    `modified_by_id` integer,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `document_id` integer NOT NULL,
    `issue_id` integer NOT NULL,
    `action` varchar(20) NOT NULL,
    `content` longtext
)
;
ALTER TABLE `core_changeproposal` ADD CONSTRAINT `created_by_id_refs_id_80718ced` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_changeproposal` ADD CONSTRAINT `modified_by_id_refs_id_80718ced` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_changeproposal` ADD CONSTRAINT `issue_id_refs_baseissue_ptr_id_bd7c5c9b` FOREIGN KEY (`issue_id`) REFERENCES `core_issue` (`baseissue_ptr_id`);
ALTER TABLE `core_changeproposal` ADD CONSTRAINT `document_id_refs_id_a8179a14` FOREIGN KEY (`document_id`) REFERENCES `core_document` (`id`);
CREATE TABLE `core_meeting_managers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meeting_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`meeting_id`, `user_id`)
)
;
ALTER TABLE `core_meeting_managers` ADD CONSTRAINT `user_id_refs_id_ad90aa51` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `core_meeting_attendees` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meeting_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`meeting_id`, `user_id`)
)
;
ALTER TABLE `core_meeting_attendees` ADD CONSTRAINT `user_id_refs_id_23e1ff0b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `core_meeting` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `polity_id` integer NOT NULL,
    `location` varchar(200),
    `time_starts` datetime,
    `time_started` datetime,
    `time_ends` datetime,
    `time_ended` datetime,
    `is_agenda_open` bool NOT NULL
)
;
ALTER TABLE `core_meeting` ADD CONSTRAINT `user_id_refs_id_82cc6491` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_meeting` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_b371d588` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_meeting_managers` ADD CONSTRAINT `meeting_id_refs_id_f0181e33` FOREIGN KEY (`meeting_id`) REFERENCES `core_meeting` (`id`);
ALTER TABLE `core_meeting_attendees` ADD CONSTRAINT `meeting_id_refs_id_8439df87` FOREIGN KEY (`meeting_id`) REFERENCES `core_meeting` (`id`);
CREATE TABLE `core_meetingrules` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `length_intervention` integer NOT NULL,
    `length_directresponse` integer NOT NULL,
    `length_clarify` integer NOT NULL,
    `length_pointoforder` integer NOT NULL,
    `max_interventions` integer NOT NULL,
    `max_directresponses` integer NOT NULL,
    `max_clarify` integer NOT NULL,
    `max_pointoforder` integer NOT NULL
)
;
CREATE TABLE `core_meetingagenda` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meeting_id` integer NOT NULL,
    `item` varchar(200) NOT NULL,
    `order` integer NOT NULL,
    `done` integer NOT NULL
)
;
ALTER TABLE `core_meetingagenda` ADD CONSTRAINT `meeting_id_refs_id_eb4dbbf` FOREIGN KEY (`meeting_id`) REFERENCES `core_meeting` (`id`);
CREATE TABLE `core_meetingintervention` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meeting_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `agendaitem_id` integer NOT NULL,
    `motion` integer NOT NULL,
    `order` integer NOT NULL,
    `done` integer NOT NULL
)
;
ALTER TABLE `core_meetingintervention` ADD CONSTRAINT `user_id_refs_id_a57006e0` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_meetingintervention` ADD CONSTRAINT `meeting_id_refs_id_2bf47916` FOREIGN KEY (`meeting_id`) REFERENCES `core_meeting` (`id`);
ALTER TABLE `core_meetingintervention` ADD CONSTRAINT `agendaitem_id_refs_id_fc975a50` FOREIGN KEY (`agendaitem_id`) REFERENCES `core_meetingagenda` (`id`);
CREATE TABLE `core_votingsystem` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `systemname` varchar(50) NOT NULL
)
;
CREATE TABLE `core_election` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(128) NOT NULL,
    `slug` varchar(128) NOT NULL,
    `polity_id` integer NOT NULL,
    `votingsystem_id` integer NOT NULL,
    `deadline_candidacy` datetime NOT NULL,
    `deadline_votes` datetime NOT NULL
)
;
ALTER TABLE `core_election` ADD CONSTRAINT `polity_id_refs_baseissue_ptr_id_16939e4f` FOREIGN KEY (`polity_id`) REFERENCES `core_polity` (`baseissue_ptr_id`);
ALTER TABLE `core_election` ADD CONSTRAINT `votingsystem_id_refs_id_e582b056` FOREIGN KEY (`votingsystem_id`) REFERENCES `core_votingsystem` (`id`);
CREATE TABLE `core_candidate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `election_id` integer NOT NULL
)
;
ALTER TABLE `core_candidate` ADD CONSTRAINT `user_id_refs_id_2ee6a6eb` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_candidate` ADD CONSTRAINT `election_id_refs_id_905fc136` FOREIGN KEY (`election_id`) REFERENCES `core_election` (`id`);
CREATE TABLE `core_electionvote` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `election_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `candidate_id` integer NOT NULL,
    `value` integer NOT NULL,
    UNIQUE (`election_id`, `user_id`, `candidate_id`),
    UNIQUE (`election_id`, `user_id`, `value`)
)
;
ALTER TABLE `core_electionvote` ADD CONSTRAINT `user_id_refs_id_57eb9f24` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `core_electionvote` ADD CONSTRAINT `candidate_id_refs_id_19ca4d04` FOREIGN KEY (`candidate_id`) REFERENCES `core_candidate` (`id`);
ALTER TABLE `core_electionvote` ADD CONSTRAINT `election_id_refs_id_2bbebdd1` FOREIGN KEY (`election_id`) REFERENCES `core_election` (`id`);
COMMIT;
