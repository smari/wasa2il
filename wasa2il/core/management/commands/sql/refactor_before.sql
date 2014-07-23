-- Re-order columns in the wrong place
-- ALTER TABLE `core_userprofile` MODIFY `verified_token` varchar(100) AFTER `verified_name`;
-- ALTER TABLE `core_polity` MODIFY `is_administrated` bool NOT NULL AFTER `invite_threshold`;
-- ALTER TABLE `core_polity` MODIFY `is_newissue_only_officers` bool NOT NULL AFTER `is_nonmembers_readable`;

-- Update `core_issue` table
ALTER TABLE `core_issue` ADD `documentcontent_id` integer AFTER `polity_id`;
ALTER TABLE `core_issue` ADD `is_processed` bool NOT NULL AFTER `ruleset_id`;
ALTER TABLE `core_issue` ADD CONSTRAINT `documentcontent_id_refs_id_2daee4a1` FOREIGN KEY (`documentcontent_id`) REFERENCES `core_documentcontent` (`id`);

-- Update `core_documentcontent` table
ALTER TABLE `core_documentcontent` DROP COLUMN `diff`;
ALTER TABLE `core_documentcontent` DROP COLUMN `patch`;
ALTER TABLE `core_documentcontent` ADD COLUMN `predecessor_id` integer AFTER `status`;

