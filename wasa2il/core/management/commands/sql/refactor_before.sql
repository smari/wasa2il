ALTER TABLE `core_polityruleset` MODIFY `issue_majority` numeric(5, 2) NOT NULL;
ALTER TABLE `core_issue` ADD `majority_percentage` numeric(5, 2) NOT NULL AFTER `deadline_votes`;
