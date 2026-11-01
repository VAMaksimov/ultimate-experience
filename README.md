# Ultimate Experience

**0.1.0-rc.2 · Civilization VI · Gathering Storm · solo against AI**

A separate compatibility mod for BBG 7.3.1, Sukritact's Oceans, CQUI, Better Report Screen and Extended Policy Cards. This repository contains original patch code, not their code or artwork. Upstream mods remain installed and can receive updates.

## Install

**Upgrading from rc.1:** this UI-only hotfix can be used with an existing rc.1 campaign. Fully exit Civ VI, replace the entire Ultimate_Experience folder (do not merge folders: the old UI/TopPanel.lua must be removed), then restart and load your save. Keep the same enabled mods. The locally installed workspace has already been updated. A new campaign is required for initial installation or changing map-generation mods, not for this hotfix.

1. Install the five required mods in [COLLECTION.md](COLLECTION.md), plus Rise and Fall and Gathering Storm.
2. Put the `Ultimate_Experience` folder in the game's `Mods` directory. This workspace is already installed there.
3. Disable Harmony in Diversity and Repair All Districts and Buildings / Total Reconstruction Project. Both are declared as conflicting mods.
4. Enable Ultimate Experience and its dependencies. Start a **new Gathering Storm campaign**.
5. Enable the **Sukritact's Oceans** game mode for its resources and Kelp. The Oceans patch is inactive when that mode is off.

This is a release candidate with automated checks passing. Live map generation, engine event timing, rendered UI and an extended AI campaign still require in-game acceptance testing. The game discovered the mod, but the window-capture tool failed during verification. See [TESTING.md](TESTING.md).

## Features

**Oceans under BBG rules.** New ocean resources, Kelp, artwork, map generation, intrinsic yields and Monopolies integration remain. The patch restores existing Fishery, water-park building, Liang, resource and reef-movement rules before BBG loads. BBG's Celestial Navigation Fishery unlock and Shipyard interaction remain authoritative. New-resource Fishing Boats and compatible Kelp placement remain. Oceans' conversion of Dyes to a coastal resource is undone.

The patch captures live values at load order 4, restores selected changes at 8, then BBG applies its rules at 11600+. An upstream change to those orders or affected tables requires a compatibility recheck. No upstream SQL is copied.

**Policy housing.** Better Report Screen's requirement evaluator now handles district housing amounts, fixing BBG's Medina Quarter estimates. Completed eligible districts, including unique replacements, are counted with the modifier's actual amount. Other effects retain their upstream calculations. Policy estimates use the actual local player rather than assuming player 0. CQUI's government layout and filters remain.

**Reconstruction.** After Iron Working, human players can select Reconstruction. The engine charges **2 Iron to activate**; gameplay charges **10 per district** and **6 per building repaired**. Districts precede buildings; buildings use database-index order. Affordable repairs proceed while unaffordable items stay damaged. Buildings under an unrepaired district stay damaged. A message reports the result. A human-only unlock keeps the AI using ordinary repairs.

UI code observes a saved repair revision and refreshes the selected city panel, city tabs, production list, resources and yields after gameplay publishes its changes. UI callbacks never perform repairs or spend iron. Stale and reentrant project notifications are guarded.

**Survey XP.** Promoted recon units with Survey receive one extra XP when barbarian combat reports a one-point award. An award already doubled to two receives no extra XP. Other units, ordinary opponents, unpromoted units and Survey-off combat are unaffected. Attacking and defending human/AI recon units qualify. A saved unit marker and event guard prevent repeated compensation.

## Compatibility and maintenance

**Better Balanced Maps 1.37:** keep it enabled if you used it to create the campaign. One combined BBM + BBG + Oceans map was confirmed in the user's game log: BBM placement succeeded and Oceans generated 167 Kelp tiles plus new resources. An integration test executes BBM's resource-registration method against Oceans resource definitions. No replacement map generator is needed. Oceans subsequently redistributes sea resources, so BBM's coastal start balancing is not guaranteed unchanged; multiple-seed balance testing remains pending. Enabling BBM after map creation cannot rebalance an existing map.

- Initial balance reference: BBG **7.3.1**. Dependency authors, source links, versions, license findings and code fingerprints are recorded in [installed-mods.json](installed-mods.json).
- Optional installed mods are inventoried in the collection document; campaign compatibility is not yet certified.
- New campaigns only; no multiplayer guarantee. Do not remove the mod mid-campaign.
- New science, breeding and nomadic mechanics are deferred; see [ROADMAP.md](ROADMAP.md).
- UI extensions load original scripts using `include`; upstream files must remain available. No third-party source or assets are redistributed.

## Development

Run `python tools/build.py` to regenerate the manifest and inventory from sibling mod folders. Install `lupa` into Python or `.test-deps`, then run `python tests/test_mod.py`. Tests read installed dependencies and the game's cached database; all test database writes occur in memory.

Run `python tools/package.py` for a mod ZIP and source ZIP. Archives exclude dependencies and test runtimes. Original source is MIT licensed; dependencies retain their own licenses. Intended publication destination: `VAMaksimov/ultimate-experience`.
