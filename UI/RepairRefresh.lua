-- UI only: observe completed gameplay revisions after the engine publishes them.
local revisions = {};
local function Flush()
    local playerID = Game.GetLocalPlayer();
    local player = Players[playerID];
    if not player then return end
    for _, city in player:GetCities():Members() do
        local id = city:GetID();
        local revision = city:GetProperty('UE_REPAIR_REVISION') or 0;
        if revisions[id] == nil then revisions[id] = 0 end
        if revision ~= revisions[id] then
            revisions[id] = revision;
            local selected = UI.GetHeadSelectedCity();
            if selected and selected:GetID() == id and selected:GetOwner() == playerID then
                LuaEvents.RefreshCityPanel();
                LuaEvents.CityPanelTabRefresh();
                -- Keep CQUI's own ReplaceUIScript: its production Lua is not
                -- imported into the VFS and cannot be included by our wrapper.
                -- Reopen only an already-visible panel, through CQUI's own
                -- handlers. Open detects the reversing slide and refreshes it.
                local production = ContextPtr:LookUpControl('/InGame/ProductionPanel');
                if production and not production:IsHidden() then
                    LuaEvents.CQUI_ProductionPanel_CityviewDisable();
                    LuaEvents.CQUI_ProductionPanel_CityviewEnable();
                end
            end
            local report = ExposedMembers.RMA;
            if report and report.RefreshBaseData then report.RefreshBaseData(playerID) end
            LuaEvents.UE_RefreshTopPanel();
        end
    end
end
Events.GameCoreEventPublishComplete.Add(Flush);
Events.LoadGameViewStateDone.Add(Flush);
