-- Extend the original analysis in its own context, without distributing its code.
include('RealModifierAnalysis');
local originalImpact = ApplyEffectAndCalculateImpact;
function ApplyEffectAndCalculateImpact(modifier, subject, subjectType)
    if modifier.EffectType == 'EFFECT_ADJUST_DISTRICT_HOUSING' then
        if subject.SubjectType ~= 'District' then return nil end
        local amount = tonumber(modifier.Arguments.Amount);
        if amount == nil then return nil end
        local impact = YieldTableNew();
        impact.HOUSING = amount;
        return impact;
    end
    return originalImpact(modifier, subject, subjectType);
end
-- EPC's installed version passes player 0. Its policy estimates must use the
-- player whose government screen is open, including a nonzero local player ID.
local originalCalculate = CalculateModifierEffect;
function CalculateModifierEffect(kind, objectType, playerID, cityID, influence)
    if kind == 'Policy' then playerID = Game.GetLocalPlayer() end
    return originalCalculate(kind, objectType, playerID, cityID, influence);
end
ExposedMembers.RMA.CalculateModifierEffect = CalculateModifierEffect;
print('UE: district housing analysis installed');
