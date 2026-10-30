UPDATE Improvements SET
 Housing=(SELECT Housing FROM UE_OriginalFishery),
 TilesRequired=(SELECT TilesRequired FROM UE_OriginalFishery),
 AdjacentSeaResource=(SELECT AdjacentSeaResource FROM UE_OriginalFishery),
 Workable=(SELECT Workable FROM UE_OriginalFishery)
WHERE ImprovementType='IMPROVEMENT_FISHERY' AND EXISTS (SELECT 1 FROM UE_OriginalFishery);
DELETE FROM Improvement_Adjacencies WHERE ImprovementType='IMPROVEMENT_FISHERY';
INSERT INTO Improvement_Adjacencies SELECT * FROM UE_OriginalAdjacency;
DELETE FROM Improvement_YieldChanges WHERE ImprovementType='IMPROVEMENT_FISHERY';
INSERT INTO Improvement_YieldChanges SELECT * FROM UE_OriginalYields;
DELETE FROM ImprovementModifiers WHERE ImprovementType='IMPROVEMENT_FISHERY';
INSERT INTO ImprovementModifiers SELECT * FROM UE_OriginalImprovementModifiers;
DELETE FROM ImprovementModifiers WHERE ModifierId IN ('SUK_FISHERY_FOOD','SUK_FISHERY_PRODUCTION');
DELETE FROM DistrictModifiers WHERE ModifierId='SUK_OCEANS_WATER_PARK_AMENITIES';
DELETE FROM BuildingModifiers WHERE ModifierId IN ('SUK_OCEANS_AQUARIUM_SCIENCE','SUK_OCEANS_AQUARIUM_ADJACENT_SCIENCE','SUK_OCEANS_AQUATIC_CENTER_TOURISM');
INSERT OR IGNORE INTO BuildingModifiers SELECT * FROM UE_OriginalBuildings;
UPDATE Features SET MovementChange=(SELECT o.MovementChange FROM UE_OriginalFeatures o WHERE o.FeatureType=Features.FeatureType) WHERE FeatureType IN (SELECT FeatureType FROM UE_OriginalFeatures);
UPDATE Resources SET AdjacentToLand=(SELECT AdjacentToLand FROM UE_OriginalDyes), SeaFrequency=(SELECT SeaFrequency FROM UE_OriginalDyes) WHERE ResourceType='RESOURCE_DYES';
DELETE FROM Resource_ValidTerrains WHERE ResourceType='RESOURCE_DYES';
INSERT INTO Resource_ValidTerrains SELECT * FROM UE_OriginalDyesTerrain;
DELETE FROM Resource_ValidFeatures WHERE ResourceType='RESOURCE_DYES';
INSERT INTO Resource_ValidFeatures SELECT * FROM UE_OriginalDyesFeatures;
DELETE FROM Improvement_ValidResources WHERE ResourceType='RESOURCE_DYES';
INSERT INTO Improvement_ValidResources SELECT * FROM UE_OriginalDyesImprovements;
DROP TABLE UE_OriginalFishery;
DROP TABLE UE_OriginalAdjacency;
DROP TABLE UE_OriginalYields;
DROP TABLE UE_OriginalImprovementModifiers;
DROP TABLE UE_OriginalBuildings;
DROP TABLE UE_OriginalFeatures;
DROP TABLE UE_OriginalDyes;
DROP TABLE UE_OriginalDyesTerrain;
DROP TABLE UE_OriginalDyesFeatures;
DROP TABLE UE_OriginalDyesImprovements;
