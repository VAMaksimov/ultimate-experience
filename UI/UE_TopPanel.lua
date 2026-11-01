-- Unique basename: TopPanel.lua would shadow the base file in the VFS.
include('toppanel_CQUI_expansion2');
LuaEvents.UE_RefreshTopPanel.Add(function()
    RefreshResources();
    OnRefreshYields();
end);
