from django import forms
from .models import OptimizationRecord

class SoilOptimizationForm(forms.ModelForm):
    class Meta:
        model = OptimizationRecord
        fields = [
            'crop_type',
            'current_nitrogen',
            'current_phosphorus',
            'current_potassium',
            'soil_ph',
            'rainfall',
            'target_yield'
        ]
        widgets = {
            'crop_type': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'current_nitrogen': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 45.0',
                'step': '0.1',
                'min': '0'
            }),
            'current_phosphorus': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 20.0',
                'step': '0.1',
                'min': '0'
            }),
            'current_potassium': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 35.0',
                'step': '0.1',
                'min': '0'
            }),
            'soil_ph': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 6.5',
                'step': '0.01',
                'min': '3.5',
                'max': '10.0'
            }),
            'rainfall': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 850.0',
                'step': '1.0',
                'min': '100'
            }),
            'target_yield': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 7.5',
                'step': '0.1',
                'min': '0.5'
            }),
        }

    def clean_soil_ph(self):
        ph = self.cleaned_data.get('soil_ph')
        if ph < 3.5 or ph > 9.5:
            raise forms.ValidationError("Soil pH must realistically be between 3.5 and 9.5.")
        return ph

    def clean_target_yield(self):
        target = self.cleaned_data.get('target_yield')
        if target <= 0.0:
            raise forms.ValidationError("Target yield must be strictly greater than 0.")
        return target
