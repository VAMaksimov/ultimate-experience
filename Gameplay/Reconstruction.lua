-- Original Ultimate Experience reconstruction implementation.
local busy = {}
local function Repair(playerID, cityID, orderType, objectID)
    if orderType ~= 3 then return end
    local project = GameInfo.Projects[objectID]
    if not project or project.ProjectType ~= 'PROJECT_UE_RECONSTRUCTION' then return end
    local player = Players[playerID]
    local city = CityManager.GetCity(playerID, cityID)
    if not player or not player:IsHuman() or not city then return end
    local queue = city:GetBuildQueue()
    -- Ignore canceled, stale, or repeated production notifications.
    if queue:GetCurrentProductionTypeHash() ~= project.Hash then return end
    local key = tostring(playerID) .. ':' .. tostring(cityID)
    if busy[key] then return end
    busy[key] = true
    local ok, err = pcall(function()
        local resources = player:GetResources()
        local iron = GameInfo.Resources['RESOURCE_IRON'].Index
        -- Activation is charged by Project_ResourceCosts, never again here.
        local repaired, remaining = 0, 0
        local function attempt(cost, action)
            if resources:GetResourceAmount(iron) < cost then
                remaining = remaining + 1
                return
            end
            action()
            resources:ChangeResourceAmount(iron, -cost)
            repaired = repaired + 1
        end
        local districts = city:GetDistricts()
        local byPlot = {}
        for index = 0, districts:GetNumDistricts() - 1 do
            local district = districts:GetDistrictByIndex(index)
            if district then byPlot[Map.GetPlot(district:GetX(), district:GetY()):GetIndex()] = district end
            if district and district:IsPillaged() then
                attempt(10, function() district:SetPillaged(false) end)
            end
        end
        local buildings = city:GetBuildings()
        local rows = {}
        for row in GameInfo.Buildings() do rows[#rows + 1] = row end
        table.sort(rows, function(a, b) return a.Index < b.Index end)
        for _, row in ipairs(rows) do
            if buildings:HasBuilding(row.Index) and buildings:IsPillaged(row.Index) then
                local district = byPlot[buildings:GetBuildingLocation(row.Index)]
                if district and district:IsPillaged() then
                    remaining = remaining + 1
                else
                    attempt(6, function() buildings:SetPillaged(row.Index, false) end)
                end
            end
        end
        queue:FinishProgress()
        city:SetProperty('UE_REPAIR_REVISION', (city:GetProperty('UE_REPAIR_REVISION') or 0) + 1)
        print('UE reconstruction: repaired=' .. repaired .. ', remaining=' .. remaining)
        if Game.GetLocalPlayer() == playerID then
            Game.AddWorldViewText(0, Locale.Lookup('LOC_UE_REPAIR_RESULT', repaired, remaining), city:GetX(), city:GetY())
        end
    end)
    busy[key] = nil
    if not ok then print('UE reconstruction error: ' .. tostring(err)) end
end
Events.CityProductionChanged.Add(Repair)
