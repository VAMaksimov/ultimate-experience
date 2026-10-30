-- Combat's reported EXPERIENCE_CHANGE is authoritative. Do not multiply normal
-- XP again: the compensation applies only to the one-point barbarian soft cap.
local seen = setmetatable({}, {__mode='k'});
local function Compensate(member, opponent)
    local id = member and member[CombatResultParameters.ID];
    local enemy = opponent and opponent[CombatResultParameters.ID];
    if not id or not enemy or id.type ~= 1 or enemy.type ~= 1 then return end
    local player, enemyPlayer = Players[id.player], Players[enemy.player];
    if not player or not enemyPlayer or not enemyPlayer:IsBarbarian() then return end
    local survey = GameInfo.Policies['POLICY_SURVEY'];
    if not survey or not player:GetCulture():IsPolicyActive(survey.Index) then return end
    local unit = UnitManager.GetUnit(id.player, id.id);
    if not unit then return end
    local info = GameInfo.Units[unit:GetType()];
    if not info or info.PromotionClass ~= 'PROMOTION_CLASS_RECON' then return end
    local xp = unit:GetExperience();
    if not xp or xp:GetLevel() < 1 then return end
    local earned = member[CombatResultParameters.EXPERIENCE_CHANGE];
    if earned ~= 1 then return end
    local current = xp:GetExperiencePoints();
    -- This marker is saved with the unit. A replayed event cannot award again.
    local previous = unit:GetProperty('UE_SURVEY_COMPENSATED_XP');
    if previous and current <= previous then return end
    unit:SetProperty('UE_SURVEY_COMPENSATED_XP', current + 1);
    xp:ChangeExperience(1);
    print('UE Survey: compensated player=' .. id.player .. ' unit=' .. id.id);
end
local function OnCombat(result)
    if seen[result] then return end
    seen[result] = true;
    local attacker = result[CombatResultParameters.ATTACKER];
    local defender = result[CombatResultParameters.DEFENDER];
    Compensate(attacker, defender);
    Compensate(defender, attacker);
end
Events.Combat.Add(OnCombat);
