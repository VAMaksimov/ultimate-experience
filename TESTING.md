# Verification — 2026-11-01

## rc.2 hotfix results

- 27 tests run: 26 passed, one skipped (combined-campaign database unavailable in the current main-menu cache). The original pre-Oceans SQL replay and BBG comparison both passed in this run.
- Added checks that UI include targets are actually imported by dependencies and our UI filenames do not shadow their Lua files. ProductionPanel is now left to CQUI's own replacement; UI/TopPanel.lua was renamed to UI/UE_TopPanel.lua to stop recursive base includes.
- Repair refresh tests cover an open panel, a hidden panel, another selected city, repeated notifications, and reload without gameplay mutation.
- Executed installed BBM 1.37's actual resource-registration method using database resource definitions: all seven Oceans resources are recognized. Engine-provided resource indices/hashes are simulated for this targeted test.
- On October 30, the user's combined campaign log reported BBM 1.37 successful placement and Oceans generation of 167 Kelp tiles, Coral and Caviar. This is evidence for one generated map, not certification of every map script or coastal balance.
- That same campaign exposed rc.1's TopPanel include recursion and empty production wrapper. They are fixed in source; post-hotfix rendered UI verification is still pending. Desktop capture failed, so no visual success is claimed.
- rc.2 makes no gameplay SQL, map-generation, mod-ID or saved-property changes. Restart the game and reload the existing rc.1 save with the same mods enabled. No new campaign is needed for this hotfix.

Automated tests execute our Lua through Lupa and SQL in memory. Integration tests read the installed BBG and Better Report Screen source without modifying or distributing it.

## Covered

- Manifest dependencies/files, XML and every shipped Lua module's syntax.
- Oceans' actual four gameplay SQL files run between capture and restoration. Existing affected rows are preserved, removed gameplay attachments are restored, all seven new resources remain, and Fishing Boats integration remains.
- BBG's actual Fishery section and housing update are applied to both control and patched databases. Fishery values, adjacency, yields, modifiers and Shipyard attachments match.
- Existing localized descriptions survive Oceans' replacements.
- Reconstruction's 2-Iron start cost, human-only unlock and foreign keys.
- Repair order, exact/partial funds, unaffordable parent districts, no damage, repeat/reload notifications, AI and irrelevant events; reentrant completion callbacks do not double-charge.
- Survey on/off, promoted/unpromoted, recon/non-recon, barbarian/ordinary enemy, attack/defense, already-doubled awards, consecutive combat and duplicate/reload events.
- The installed report analyzer's actual requirements and district collection code selects completed eligible and unique districts and excludes unfinished/non-specialty districts. The added handler totals housing correctly.
- UI refresh once per revision, preservation of another selected city, and read-only refresh on loading a repair revision.

Lua game-object doubles do not prove engine event ordering. SQLite uses a deterministic stand-in for `Make_Hash`; hash values are not balance assertions. Starting Civ VI replaced the cached GS/BBG database with its main-menu base database. Tests subsequently load affected expansion rows and the GS project-resource table definition from installed official files when absent. This is targeted integration testing, not a complete engine database build.

## Game startup

Civ VI launched and Modding.log recorded discovery of Ultimate Experience with its ID and name. Window capture timed out on initial inspection and recovery. No campaign was configured or played through the UI. Existing unrelated mod-loading errors were present; discovery alone is not a clean gameplay smoke test.

## Before marking stable

1. Enable the required pack, Gathering Storm and Oceans. Check fresh Database.log/Lua.log for new errors.
2. Generate multiple seeded maps, including Better Balanced Maps. Verify sea luxuries, bonus resources and Kelp, and no new coastal Dyes. Save/reload must not regenerate resources.
3. Check Fisheries unlock at Celestial Navigation, work normally, retain BBG housing/Shipyard behavior and lack Oceans' removed bonuses.
4. Compare Medina Quarter estimates against actual housing when adopted/removed, with unique, unfinished and pillaged districts. Verify both report and CQUI government screens.
5. Test repairs with stockpiles 0, 1, 2, 11, 12, 17, 18, 23 and 24. Confirm the engine charges 2 once and gameplay charges only actual repairs. Check open city/production/resource UI, repeat selection, queued identical projects and save/reload.
6. Measure actual barbarian XP with Survey on/off and before/after promotion, attacking/defending; also test other XP bonuses, ordinary enemies and AI recon units.
7. Run an extended AI campaign; add optional mods incrementally. Confirm the AI never chooses Reconstruction and UI/turn performance remains healthy.

These manual checks remain unverified. Do not report them as passed without observing them in the game.
