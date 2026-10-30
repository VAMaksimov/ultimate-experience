-- Runs at 4, before Oceans (5/6). Restore at 8, before BBG (11600+).
-- Capture live values instead of copying Firaxis or mod source data.
CREATE TABLE UE_OriginalFishery AS SELECT ImprovementType, Housing, TilesRequired, AdjacentSeaResource, Workable FROM Improvements WHERE ImprovementType='IMPROVEMENT_FISHERY';
CREATE TABLE UE_OriginalAdjacency AS SELECT * FROM Improvement_Adjacencies WHERE ImprovementType='IMPROVEMENT_FISHERY';
CREATE TABLE UE_OriginalYields AS SELECT * FROM Improvement_YieldChanges WHERE ImprovementType='IMPROVEMENT_FISHERY';
CREATE TABLE UE_OriginalImprovementModifiers AS SELECT * FROM ImprovementModifiers WHERE ImprovementType='IMPROVEMENT_FISHERY';
CREATE TABLE UE_OriginalBuildings AS SELECT * FROM BuildingModifiers WHERE ModifierId IN ('AQUARIUM_SEARESOURCE_SCIENCE','AQUARIUM_REEF_SCIENCE','AQUATICS_CENTER_WONDER_TOURISM');
CREATE TABLE UE_OriginalFeatures AS SELECT FeatureType, MovementChange FROM Features WHERE FeatureType IN ('FEATURE_REEF','FEATURE_BARRIER_REEF','FEATURE_HA_LONG_BAY');
CREATE TABLE UE_OriginalDyes AS SELECT ResourceType, AdjacentToLand, SeaFrequency FROM Resources WHERE ResourceType='RESOURCE_DYES';
CREATE TABLE UE_OriginalDyesTerrain AS SELECT * FROM Resource_ValidTerrains WHERE ResourceType='RESOURCE_DYES';
CREATE TABLE UE_OriginalDyesFeatures AS SELECT * FROM Resource_ValidFeatures WHERE ResourceType='RESOURCE_DYES';
CREATE TABLE UE_OriginalDyesImprovements AS SELECT * FROM Improvement_ValidResources WHERE ResourceType='RESOURCE_DYES';
