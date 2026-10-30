include('productionpanel_CQUI');
LuaEvents.UE_RefreshProduction.Add(function()
    if not ContextPtr:IsHidden() then Refresh() end
end);
