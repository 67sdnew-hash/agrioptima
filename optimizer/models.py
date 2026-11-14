from django.db import models

class OptimizationRecord(models.Model):
    CROP_CHOICES = [
        ('Rice', 'Rice (Oryza sativa)'),
        ('Wheat', 'Wheat (Triticum aestivum)'),
        ('Maize', 'Maize (Zea mays)'),
        ('Cotton', 'Cotton (Gossypium hirsutum)'),
    ]

    # Baseline Soil & Environmental Inputs
    crop_type = models.CharField(max_length=50, choices=CROP_CHOICES)
    current_nitrogen = models.FloatField(
        verbose_name="Baseline Soil Nitrogen (N kg/ha)",
        help_text="Current available N in topsoil"
    )
    current_phosphorus = models.FloatField(
        verbose_name="Baseline Soil Phosphorus (P kg/ha)",
        help_text="Current available P in topsoil"
    )
    current_potassium = models.FloatField(
        verbose_name="Baseline Soil Potassium (K kg/ha)",
        help_text="Current available K in topsoil"
    )
    soil_ph = models.FloatField(
        verbose_name="Soil pH",
        help_text="Standard 1:2.5 soil-to-water suspension"
    )
    rainfall = models.FloatField(
        verbose_name="Seasonal Rainfall (mm)",
        help_text="Expected or historical seasonal precipitation"
    )
    target_yield = models.FloatField(
        verbose_name="Farmer Target Yield (tons/ha)",
        help_text="Desired harvest threshold"
    )

    # Optimization Outcomes
    baseline_yield = models.FloatField(verbose_name="Predicted Baseline Yield (tons/ha)")
    predicted_yield = models.FloatField(verbose_name="Predicted Post-Fertilizer Yield (tons/ha)")
    delta_nitrogen = models.FloatField(verbose_name="Prescribed Delta N (kg/ha)")
    delta_phosphorus = models.FloatField(verbose_name="Prescribed Delta P (kg/ha)")
    delta_potassium = models.FloatField(verbose_name="Prescribed Delta K (kg/ha)")
    total_fertilizer_kg = models.FloatField(verbose_name="Total Nutrient Supplement (kg/ha)")

    # Economics & Savings
    optimized_cost = models.FloatField(verbose_name="Optimized Input Cost ($/ha)")
    blanket_cost = models.FloatField(verbose_name="Standard Blanket Application Cost ($/ha)")
    cost_savings = models.FloatField(verbose_name="Cost Savings vs. Blanket ($/ha)")
    percent_savings = models.FloatField(verbose_name="Percent Input Cost Saved (%)")

    # Feasibility
    is_feasible = models.BooleanField(
        default=True,
        verbose_name="Target Yield Achievable"
    )
    infeasibility_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Agronomic Constraint Note"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Optimization Record"
        verbose_name_plural = "Optimization Records"

    def __str__(self):
        return f"{self.crop_type} - Target: {self.target_yield} t/ha ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
