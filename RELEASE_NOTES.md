# Ultimate Experience 0.1.0-rc.2

UI hotfix for rc.1: restore CQUI's production panel by removing the wrapper that included a non-imported dependency file. Rename our TopPanel wrapper to prevent it shadowing the game's base file and recursing indefinitely. Reconstruction refreshes an already-open production panel through CQUI's existing UI events; hidden panels stay hidden.

26 automated checks pass; one campaign-cache-only check is skipped. BBM 1.37 resource registration recognizes all seven Oceans resources. The user's prior campaign log confirms one successful BBM + BBG + Oceans map, including 167 Kelp tiles. Coastal start balance and multiple map seeds remain unverified.

**Existing rc.1 saves can be reloaded.** Fully exit the game and replace the old mod folder, rather than merging files, so the obsolete UI/TopPanel.lua is removed. Restart and load the same save with the same mods. No gameplay or map-generation changes are made by this hotfix. The workspace installation is already patched. Rendered UI confirmation after restart remains pending.

## Original rc.1 features

First release candidate for solo Gathering Storm campaigns using BBG 7.3.1.

- Keep Oceans' seven new resources, Kelp and map generation while restoring existing rules before BBG loads.
- Display district-based policy housing using Better Report Screen's eligibility logic and the CQUI government interface.
- Add human-only Reconstruction: 2 Iron activation, 10 per district, 6 per building, with city/production/resource UI refreshes.
- Compensate Survey's omitted bonus on one-point barbarian XP awards to promoted recon units.
- Declare dependencies and block Harmony in Diversity and the original Repair All mod.

Automated database, Lua and UI-event tests pass. Tests include actual BBG Fishery SQL and the installed report analyzer's district eligibility code. No third-party mod source or artwork is bundled.

**Prerelease limitations:** the game discovered the mod, but live window capture failed. Full map generation, actual engine event ordering/charging, rendered UI, and extended AI campaign acceptance are not yet verified. Optional mods are inventoried, not campaign-certified. See TESTING.md.

Download the **mod ZIP** for installation, or the **source ZIP** for development. Install dependencies from COLLECTION.md, disable the conflicting mods, enable Oceans mode, and start a new Gathering Storm campaign. Do not add/remove this mod mid-save. Multiplayer is not certified.
