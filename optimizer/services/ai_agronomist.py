"""
AgriOptima - AI Agronomist Copilot Service
Provides intelligent, scientific, and actionable agronomic advisory
grounded directly in the farmer's active soil chemistry, target yield, and prescription.
"""

import re
from typing import Dict, Any, List

def answer_agronomic_query(user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Answers an agronomic question using precision agriculture principles,
    crop physiology, and the active simulation context.
    """
    q = user_message.lower().strip()

    crop = context.get('crop_type', 'Wheat')
    n = float(context.get('current_nitrogen', 45.0))
    p = float(context.get('current_phosphorus', 20.0))
    k = float(context.get('current_potassium', 30.0))
    ph = float(context.get('soil_ph', 6.5))
    rain = float(context.get('rainfall', 750.0))
    target = float(context.get('target_yield', 6.0))

    dn = float(context.get('delta_nitrogen', 0.0))
    dp = float(context.get('delta_phosphorus', 0.0))
    dk = float(context.get('delta_potassium', 0.0))

    urea_bags = float(context.get('urea_bags', 0.0))
    dap_bags = float(context.get('dap_bags', 0.0))
    mop_bags = float(context.get('mop_bags', 0.0))
    leaching_risk = context.get('leaching_risk', 'OPTIMAL')

    # 1. Questions regarding Potassium (K)
    if any(w in q for w in ('potassium', 'mop', 'potash', 'k level', 'why k', 'why potassium')):
        response_text = (
            f"**Potassium (K) Analysis for your {crop}:**\n\n"
            f"Your current soil test shows **{k:.1f} kg/ha** of available K, while your target yield of **{target:.1f} t/ha** "
            f"requires additional osmotic pressure and vascular strength. We prescribed **+{dk:.1f} kg/ha of K** (~{mop_bags} bags of MOP 0-0-60).\n\n"
            f"• **Why it matters:** Potassium governs stomatal opening, drought endurance, and lodging resistance (preventing tall stems from bending). Without adequate K, crops cannot transport sugars to grain heads during reproductive filling.\n"
            f"• **Best Practice:** Apply MOP as a basal dose at planting. For sandy soils, consider splitting K across basal and tillering."
        )
        suggestions = [
            "What if I replace MOP with organic potassium sources like wood ash?",
            "Can potassium deficiency cause leaf tip burning?",
            "How does soil pH affect potassium uptake?"
        ]

    # 2. Questions regarding Nitrogen (N) / Urea
    elif any(w in q for w in ('nitrogen', 'urea', 'n level', 'why n', 'why nitrogen', 'yellowing')):
        response_text = (
            f"**Nitrogen (N) Strategy for your {crop}:**\n\n"
            f"Your baseline soil has **{n:.1f} kg/ha** of available N. To reach **{target:.1f} t/ha**, "
            f"the SLSQP optimizer prescribed **+{dn:.1f} kg/ha of N** (~{urea_bags} bags of Urea 46-0-0).\n\n"
            f"• **Diminishing Returns Note:** Notice that our non-linear model avoids excessive nitrogen over-dosing. Over-applying N above 200 kg/ha causes vegetative lodging, increases susceptibility to fungal rusts, and results in nitrate leaching.\n"
            f"• **4R Split Timing:** Never apply all urea at sowing. Split it: 30% basal, 40% at tillering (Day 25-30), and 30% at boot stage."
        )
        suggestions = [
            "What happens if heavy rain falls right after applying Urea?",
            "How can neem-coated urea reduce nitrogen losses?",
            "Can I apply urea as a foliar spray?"
        ]

    # 3. Questions regarding Phosphorus (P) / DAP
    elif any(w in q for w in ('phosphorus', 'dap', 'p level', 'phosphate', 'why p', 'root')):
        response_text = (
            f"**Phosphorus (P) Dynamics for your {crop}:**\n\n"
            f"Your soil test indicates **{p:.1f} kg/ha** of available P. We prescribed **+{dp:.1f} kg/ha of P** (~{dap_bags} bags of DAP 18-46-0).\n\n"
            f"• **Why Phosphorus is Crucial Early:** Phosphorus is relatively immobile in soil. Young seedlings require readily available phosphate within 5 cm of the seed to power ATP energy transfer and deep taproot establishment.\n"
            f"• **Application Method:** Band DAP 5 cm below and beside the seed furrow rather than broadcasting. Broadcasting leaves phosphate fixed in the dry top 1 cm of soil."
        )
        suggestions = [
            "Can DAP and Urea be mixed together in the fertilizer spreader?",
            "How does soil pH lock up available phosphorus?",
            "Are mycorrhizal fungi useful for phosphorus uptake?"
        ]

    # 4. Questions regarding Soil pH
    elif any(w in q for w in ('ph', 'acid', 'alkaline', 'lime', 'gypsum', 'lockout')):
        if ph < 6.0:
            ph_status = f"moderately acidic ({ph:.2f})"
            ph_advice = (
                "At this pH, phosphorus binds tightly with aluminum and iron ions, reducing availability. "
                "Consider applying agricultural lime (calcium carbonate, 1-2 tons/ha) before the next planting season to raise pH toward 6.5."
            )
        elif ph > 7.5:
            ph_status = f"moderately alkaline ({ph:.2f})"
            ph_advice = (
                "At high pH, phosphorus fixes with calcium, and micronutrients like Zinc and Iron become locked. "
                "Consider applying agricultural gypsum (calcium sulfate) or elemental sulfur, and use chelated Zinc (Zn-EDTA) foliar sprays."
            )
        else:
            ph_status = f"optimal ({ph:.2f})"
            ph_advice = "This provides the sweet spot for maximum cation exchange capacity (CEC) and unrestricted N-P-K bioavailability."

        response_text = (
            f"**Soil pH Evaluation ({ph:.2f}):**\n\n"
            f"Your soil pH is **{ph_status}** for {crop}.\n\n"
            f"{ph_advice}\n\n"
            f"• **Fertilizer Efficiency Impact:** At pH {ph:.2f}, fertilizer use efficiency is estimated at **{min(95, int(60 + 5 * (6.5 - abs(ph - 6.5))))}%**. Maintaining pH near 6.5 prevents nutrient waste."
        )
        suggestions = [
            "How do I apply agricultural lime properly?",
            "Will chemical fertilizers increase soil acidity over time?",
            "What cover crops thrive in my soil pH?"
        ]

    # 5. Questions regarding Weather / Leaching Risk
    elif any(w in q for w in ('rain', 'weather', 'leach', 'runoff', 'wash', 'flood', 'drought')):
        response_text = (
            f"**Climate & Moisture Advisory (14-Day Status: {leaching_risk}):**\n\n"
            f"Your seasonal rainfall parameter is **{rain:.1f} mm**.\n\n"
            f"• **Leaching Risk Context:** When heavy downpours occur within 48 hours of fertilizer broadcasting, up to 40% of mineral nitrate can wash past the root zone into groundwater.\n"
            f"• **Mitigation:** If rain exceeds 20mm/day in your forecast, delay top-dressing urea until after the moisture has soaked in and soil is walkable. Deep banding DAP and MOP at planting protects them from surface runoff."
        )
        suggestions = [
            "How do I synchronize my urea top-dressing with rainfall?",
            "What is the difference between leaching and surface volatilization?",
            "Should I irrigate immediately after applying fertilizer?"
        ]

    # 6. Questions regarding Organic Manure & Compost
    elif any(w in q for w in ('organic', 'manure', 'compost', 'fym', 'vermicompost', 'biofertilizer')):
        response_text = (
            f"**Integrating Organic Amendments with your Prescription:**\n\n"
            f"For your {crop} field, combining chemical fertilizers with well-decomposed **Farmyard Manure (FYM)** or **Vermicompost** enhances long-term soil structure and microbial diversity:\n\n"
            f"• **Nutrient Value:** 5 tons of quality FYM provides approx **25 kg N, 10 kg P, and 25 kg K**, along with humic acid and trace zinc/boron.\n"
            f"• **Prescription Adjustment:** If applying 5 t/ha of FYM, you can safely deduct ~1 bag of Urea and 0.5 bag of MOP from this chemical prescription.\n"
            f"• **Timing:** Incorporate manure 3-4 weeks before sowing to allow microbial mineralization."
        )
        suggestions = [
            "How much vermicompost should I apply per hectare?",
            "Can biofertilizers like Azotobacter replace chemical nitrogen?",
            "What are the best green manure crops to plant before wheat?"
        ]

    # 7. Default / General Agronomic Guidance
    else:
        response_text = (
            f"**Agronomic Assessment for {crop} (Target: {target:.1f} t/ha):**\n\n"
            f"Based on your soil profile (N: {n:.1f}, P: {p:.1f}, K: {k:.1f} kg/ha, pH: {ph:.2f}), "
            f"the prescriptive optimization computed: **+{dn:.1f} kg/ha N**, **+{dp:.1f} kg/ha P**, and **+{dk:.1f} kg/ha K**.\n\n"
            f"• **Commercial Packaging:** This translates to **{urea_bags} bags of Urea**, **{dap_bags} bags of DAP**, and **{mop_bags} bags of MOP** per hectare.\n"
            f"• **Key Agronomic Takeaway:** The priority is addressing the most limiting nutrient first (Liebig's Law of the Minimum) while avoiding luxury consumption of secondary nutrients.\n"
            f"• Feel free to ask me about split dosing, soil pH buffering, fertilizer mixing rules, or rainfall protection!"
        )
        suggestions = [
            f"Why did the solver recommend this specific ratio of N, P, and K for {crop}?",
            "How do I split this fertilizer application across the growing season?",
            "Can I apply micronutrients like Zinc with this recipe?"
        ]

    return {
        'response': response_text,
        'suggestions': suggestions,
        'crop_type': crop
    }
