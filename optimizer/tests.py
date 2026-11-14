import json
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
from optimizer.services.pdf_generator import generate_agronomist_pdf, calculate_commercial_bags
from optimizer.services.weather import fetch_weather_forecast


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

    def test_commercial_bags_converter(self):
        bags = calculate_commercial_bags(dn_kg=46.0, dp_kg=20.0, dk_kg=30.0)
        self.assertIn('urea_bags', bags)
        self.assertIn('dap_bags', bags)
        self.assertIn('mop_bags', bags)
        self.assertGreater(bags['total_bags'], 0.0)

    def test_agronomist_pdf_generation_and_view(self):
        record = OptimizationRecord.objects.create(
            crop_type='Wheat',
            current_nitrogen=40.0,
            current_phosphorus=20.0,
            current_potassium=30.0,
            soil_ph=6.5,
            rainfall=750.0,
            target_yield=6.0,
            baseline_yield=3.8,
            predicted_yield=6.1,
            delta_nitrogen=25.0,
            delta_phosphorus=15.0,
            delta_potassium=20.0,
            total_fertilizer_kg=60.0,
            optimized_cost=70.5,
            blanket_cost=270.0,
            cost_savings=199.5,
            percent_savings=73.9,
            is_feasible=True
        )

        pdf_bytes = generate_agronomist_pdf(record).getvalue()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

        response = self.client.get(reverse('export_pdf_report', args=[record.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f"AGRI-{record.id:05d}", response['Content-Disposition'])

    def test_weather_proxy_service(self):
        # 1. Lat/Lon query
        response = self.client.get(reverse('weather_proxy'), {'lat': 31.1471, 'lon': 75.3412})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_14d_precip_mm', data)
        self.assertIn('leaching_risk', data)
        self.assertIn('recommended_rainfall_mm', data)

        # 2. Auto IP geolocation query
        res_auto = self.client.get(reverse('weather_proxy'), {'auto': 'true'})
        self.assertEqual(res_auto.status_code, 200)
        data_auto = res_auto.json()
        self.assertIn('location_name', data_auto)
        self.assertIn('recommended_rainfall_mm', data_auto)

        # 3. City query
        res_city = self.client.get(reverse('weather_proxy'), {'city': 'Kolkata'})
        self.assertEqual(res_city.status_code, 200)
        data_city = res_city.json()
        self.assertTrue('location_name' in data_city or 'error' in data_city)

    def test_multi_zone_api_optimization(self):
        payload = {
            'zones': [
                {
                    'name': 'North Zone',
                    'area_ha': 10.0,
                    'crop_type': 'Wheat',
                    'current_nitrogen': 40.0,
                    'current_phosphorus': 18.0,
                    'current_potassium': 30.0,
                    'soil_ph': 6.2,
                    'rainfall': 750.0,
                    'target_yield': 6.5,
                    'lat': 31.1471,
                    'lon': 75.3412
                },
                {
                    'name': 'South Zone',
                    'area_ha': 20.0,
                    'crop_type': 'Wheat',
                    'current_nitrogen': 60.0,
                    'current_phosphorus': 30.0,
                    'current_potassium': 45.0,
                    'soil_ph': 6.8,
                    'rainfall': 750.0,
                    'target_yield': 7.0,
                    'lat': 31.1511,
                    'lon': 75.3452
                }
            ]
        }

        response = self.client.post(
            reverse('optimize_zone_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['zones']), 2)
        self.assertEqual(data['summary']['total_farm_area_ha'], 30.0)
        self.assertGreater(data['summary']['total_savings_usd'], 0.0)
        self.assertEqual(data['geojson']['type'], 'FeatureCollection')
        self.assertEqual(len(data['geojson']['features']), 2)

    def test_split_schedule_and_ics_export(self):
        record = OptimizationRecord.objects.create(
            crop_type='Wheat',
            current_nitrogen=40.0,
            current_phosphorus=20.0,
            current_potassium=30.0,
            soil_ph=6.5,
            rainfall=750.0,
            target_yield=6.0,
            baseline_yield=3.8,
            predicted_yield=6.1,
            delta_nitrogen=25.0,
            delta_phosphorus=15.0,
            delta_potassium=20.0,
            total_fertilizer_kg=60.0,
            optimized_cost=70.5,
            blanket_cost=270.0,
            cost_savings=199.5,
            percent_savings=73.9,
            is_feasible=True
        )

        from optimizer.services.split_schedule import calculate_split_schedule, generate_ics_calendar
        from datetime import datetime

        schedule = calculate_split_schedule(
            crop_type='Wheat',
            sowing_date=datetime.now(),
            urea_bags=3.0,
            dap_bags=2.0,
            mop_bags=1.5,
            delta_n_kg=25.0,
            delta_p_kg=15.0,
            delta_k_kg=20.0
        )
        self.assertEqual(len(schedule), 3)
        self.assertEqual(schedule[0]['stage_number'], 1)
        self.assertEqual(schedule[1]['stage_number'], 2)
        self.assertEqual(schedule[2]['stage_number'], 3)

        ics_text = generate_ics_calendar(
            crop_type='Wheat',
            sowing_date=datetime.now(),
            urea_bags=3.0,
            dap_bags=2.0,
            mop_bags=1.5,
            delta_n_kg=25.0,
            delta_p_kg=15.0,
            delta_k_kg=20.0
        )
        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("BEGIN:VEVENT", ics_text)
        self.assertIn("END:VCALENDAR", ics_text)

        # Test ICS View
        res_ics = self.client.get(reverse('export_ics_calendar', args=[record.id]))
        self.assertEqual(res_ics.status_code, 200)
        self.assertIn('text/calendar', res_ics['Content-Type'])
        self.assertIn('.ics', res_ics['Content-Disposition'])

    def test_ai_agronomist_chat_api(self):
        payload = {
            'message': 'Why did you recommend this amount of Potassium for wheat?',
            'context': {
                'crop_type': 'Wheat',
                'current_nitrogen': 40.0,
                'current_phosphorus': 20.0,
                'current_potassium': 30.0,
                'soil_ph': 6.5,
                'rainfall': 750.0,
                'target_yield': 6.0,
                'delta_nitrogen': 20.0,
                'delta_phosphorus': 12.0,
                'delta_potassium': 25.0,
                'urea_bags': 2.5,
                'dap_bags': 1.8,
                'mop_bags': 1.5,
                'savings': 180.0
            }
        }

        response = self.client.post(
            reverse('agronomist_chat_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('response', data['data'])
        self.assertIn('Potassium', data['data']['response'])
        self.assertGreaterEqual(len(data['data']['suggestions']), 1)
