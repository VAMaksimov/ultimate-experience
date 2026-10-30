-- The expansion includes EPC's imported GovernmentScreen; CQUI extends it.
include('governmentscreen_CQUI_expansion2');
local originalRealize = RealizePolicyCard;
function RealizePolicyCard(card, policyType)
    originalRealize(card, policyType);
    local analysis = ExposedMembers.RMA;
    if not analysis or not analysis.CalculateModifierEffect then return end
    local text, _, tooltip = analysis.CalculateModifierEffect('Policy', policyType, Game.GetLocalPlayer());
    if card.Effect and card.EffectContainer then
        card.EffectContainer:SetHide(text == '');
        card.Effect:SetText(text);
        card.Effect:SetToolTipString(tooltip or text);
    end
end
