from django.test import TestCase
from django.urls import reverse
from optimizer.models import OptimizationRecord
from optimizer.services.optimization import (
    optimize_fertilizer,
    generate_response_curves,
    MAX_DELTA_N,
    MAX_DELTA_P,
    MAX_DELTA_K
)

class FertilizerOptimizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.crop = 'Wheat'
        cls.baseline_n = 35.0
        cls.baseline_p = 15.0
        cls.baseline_k = 25.0
        cls.ph = 6.5
        cls.rainfall = 700.0

    def test_standard_feasible_optimization(self):
        target_yield = 5.5
        result = optimize_fertilizer(
            crop_type=self.crop,
            current_n=self.baseline_n,
            current_p=self.baseline_p,
            current_k=self.baseline_k,
            ph=self.ph,
            rainfall=self.rainfall,
            target_yield=target_yield
        )

        self.assertTrue(result['is_feasible'])
        self.assertIsNone(result['infeasibility_note'])
        self.assertGreaterEqual(result['predicted_yield'], target_yield - 0.25)
        self.assertGreaterEqual(result['delta_n'], 0.0)
        self.assertGreaterEqual(result['delta_p'], 0.0)
        self.assertGreaterEqual(result['delta_k'], 0.0)
        self.assertLessEqual(result['delta_n'], MAX_DELTA_N)
        self.assertLessEqual(result['delta_p'], MAX_DELTA_P)
        self.assertLessEqual(result['delta_k'], MAX_DELTA_K)

    def test_zero_fertilizer_when_baseline_exceeds_target(self):
        target_yield = 1.0
        result = optimize_fertilizer(
            crop_type=self.crop,
            current_n=self.baseline_n,
            current_p=self.baseline_p,
            current_k=self.baseline_k,
            ph=self.ph,
            rainfall=self.rainfall,
            target_yield=target_yield
        )

        self.assertTrue(result['is_feasible'])
        self.assertEqual(result['delta_n'], 0.0)
        self.assertEqual(result['delta_p'], 0.0)
        self.assertEqual(result['delta_k'], 0.0)
        self.assertEqual(result['total_fertilizer_kg'], 0.0)
        self.assertEqual(result['optimized_cost'], 0.0)
        self.assertEqual(result['percent_savings'], 100.0)

    def test_infeasible_target_yield_handling(self):
        unrealistic_target = 50.0
        result = optimize_fertilizer(
            crop_type=self.crop,
            current_n=self.baseline_n,
            current_p=self.baseline_p,
            current_k=self.baseline_k,
            ph=self.ph,
            rainfall=self.rainfall,
            target_yield=unrealistic_target
        )

        self.assertFalse(result['is_feasible'])
        self.assertIsNotNone(result['infeasibility_note'])
        self.assertIn("exceeds the maximum biologically attainable yield", result['infeasibility_note'])
        self.assertAlmostEqual(result['predicted_yield'], result['max_attainable_yield'], delta=0.6)

    def test_response_curves_generation(self):
        curves = generate_response_curves(
            crop_type=self.crop,
            current_n=self.baseline_n,
            current_p=self.baseline_p,
            current_k=self.baseline_k,
            ph=self.ph,
            rainfall=self.rainfall,
            opt_dn=30.0,
            opt_dp=15.0,
            opt_dk=10.0,
            n_points=15
        )

        self.assertIn('nitrogen_curve', curves)
        self.assertEqual(len(curves['nitrogen_curve']['labels']), 15)
        self.assertEqual(len(curves['nitrogen_curve']['yields']), 15)
        self.assertEqual(curves['nitrogen_curve']['current_x'], round(self.baseline_n, 1))

    def test_dashboard_post_flow_and_database_persistence(self):
        response = self.client.post(reverse('dashboard'), {
            'crop_type': 'Maize',
            'current_nitrogen': 50.0,
            'current_phosphorus': 20.0,
            'current_potassium': 30.0,
            'soil_ph': 6.5,
            'rainfall': 800.0,
            'target_yield': 9.0
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prescribed Fertilizer Application")
        self.assertEqual(OptimizationRecord.objects.count(), 1)

        record = OptimizationRecord.objects.first()
        self.assertEqual(record.crop_type, 'Maize')
        self.assertGreater(record.predicted_yield, 0.0)
