INSERT OR REPLACE INTO LocalizedText SELECT * FROM UE_OriginalOceanText;
DROP TABLE UE_OriginalOceanText;
INSERT OR REPLACE INTO LocalizedText (Tag, Language, Text) VALUES
('LOC_GAMEMODE_SUK_OCEANS_DESCRIPTION','en_US','Adds Sukritact’s ocean resources and Kelp Forests. Ultimate Experience preserves BBG rules for existing Fisheries, governors, buildings, resources and reef movement. New resources retain their yields and compatible Fishing Boats.');
