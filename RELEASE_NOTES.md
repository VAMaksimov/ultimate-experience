# Ultimate Experience 0.1.0-rc.1

First release candidate for solo Gathering Storm campaigns using BBG 7.3.1.

- Keep Oceans' seven new resources, Kelp and map generation while restoring existing rules before BBG loads.
- Display district-based policy housing using Better Report Screen's eligibility logic and the CQUI government interface.
- Add human-only Reconstruction: 2 Iron activation, 10 per district, 6 per building, with city/production/resource UI refreshes.
- Compensate Survey's omitted bonus on one-point barbarian XP awards to promoted recon units.
- Declare dependencies and block Harmony in Diversity and the original Repair All mod.

Automated database, Lua and UI-event tests pass. Tests include actual BBG Fishery SQL and the installed report analyzer's district eligibility code. No third-party mod source or artwork is bundled.

**Prerelease limitations:** the game discovered the mod, but live window capture failed. Full map generation, actual engine event ordering/charging, rendered UI, and extended AI campaign acceptance are not yet verified. Optional mods are inventoried, not campaign-certified. See TESTING.md.

Download the **mod ZIP** for installation, or the **source ZIP** for development. Install dependencies from COLLECTION.md, disable the conflicting mods, enable Oceans mode, and start a new Gathering Storm campaign. Do not add/remove this mod mid-save. Multiplayer is not certified.
