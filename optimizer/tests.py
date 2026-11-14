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


class CommunityFeatureTests(TestCase):
    def test_community_hub_view_and_seed(self):
        response = self.client.get(reverse('community_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Farmer Community")
        self.assertContains(response, "Live Farmer Radio")
        # Check that seed data was populated
        from optimizer.models import CommunityPost, CommunityChatMessage
        self.assertGreater(CommunityPost.objects.count(), 0)
        self.assertGreater(CommunityChatMessage.objects.count(), 0)

    def test_community_create_post_api(self):
        payload = {
            'author_name': 'Amandeep Singh',
            'author_location': 'Bathinda, Punjab',
            'crop_type': 'Cotton',
            'category': 'fertilizer',
            'title': 'Pink bollworm defense and potash split timing',
            'content': 'Has anyone experienced better boll retention with split potash applications?',
            'soil_metrics': 'N: 50, P: 18, K: 32 kg/ha',
            'latitude': 30.2110,
            'longitude': 74.9455
        }
        response = self.client.post(
            reverse('community_create_post_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['post']['author'], 'Amandeep Singh')
        self.assertEqual(data['post']['crop'], 'Cotton')

    def test_community_reply_and_upvote_api(self):
        from optimizer.models import CommunityPost
        post = CommunityPost.objects.create(
            author_name='Test Farmer',
            author_location='Test Valley',
            crop_type='Wheat',
            title='Test Question',
            content='Test body content'
        )

        # Test Reply
        reply_payload = {
            'author_name': 'Reply Farmer',
            'author_location': 'Neighbor Field',
            'content': 'I suggest applying 30 kg/ha K2O at squaring.'
        }
        rep_resp = self.client.post(
            reverse('community_reply_api', kwargs={'post_id': post.id}),
            data=json.dumps(reply_payload),
            content_type='application/json'
        )
        self.assertEqual(rep_resp.status_code, 200)
        self.assertTrue(rep_resp.json()['success'])
        self.assertEqual(post.replies.count(), 1)

        # Test Upvote
        up_resp = self.client.post(reverse('community_upvote_api', kwargs={'post_id': post.id}))
        self.assertEqual(up_resp.status_code, 200)
        self.assertEqual(up_resp.json()['upvotes'], 1)

    def test_community_chat_api(self):
        # Test POST
        msg_payload = {
            'author_name': 'Chatty Grower',
            'author_location': 'Central Belt',
            'channel': 'nearby',
            'message': 'Canal water release scheduled for tomorrow 6 AM.'
        }
        post_resp = self.client.post(
            reverse('community_chat_api'),
            data=json.dumps(msg_payload),
            content_type='application/json'
        )
        self.assertEqual(post_resp.status_code, 200)
        self.assertTrue(post_resp.json()['success'])

        # Test GET
        get_resp = self.client.get(reverse('community_chat_api') + '?channel=nearby')
        self.assertEqual(get_resp.status_code, 200)
        data = get_resp.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['messages']), 1)


class FarmerAuthTests(TestCase):
    def test_phone_registration_with_otp_and_login(self):
        # 1. Send OTP for phone registration
        send_payload = {
            'method': 'phone',
            'full_name': 'Kuldeep Sandhu',
            'phone_number': '+919876543210',
            'email': '',
            'farm_location': 'Moga, Punjab',
            'primary_crop': 'Wheat',
            'password': 'safe_farm_password_123'
        }
        res_send = self.client.post(
            reverse('send_registration_otp_api'),
            data=json.dumps(send_payload),
            content_type='application/json'
        )
        self.assertEqual(res_send.status_code, 200)
        send_data = res_send.json()
        self.assertTrue(send_data['success'])
        self.assertEqual(len(send_data['otp']), 6)

        # 2. Verify with incorrect OTP
        res_bad = self.client.post(
            reverse('verify_registration_otp_api'),
            data=json.dumps({'otp': '000000'}),
            content_type='application/json'
        )
        self.assertEqual(res_bad.status_code, 400)
        self.assertFalse(res_bad.json()['success'])

        # 3. Verify with correct OTP
        res_verify = self.client.post(
            reverse('verify_registration_otp_api'),
            data=json.dumps({'otp': send_data['otp']}),
            content_type='application/json'
        )
        self.assertEqual(res_verify.status_code, 200)
        self.assertTrue(res_verify.json()['success'])

        # 4. Check user created in database
        from django.contrib.auth.models import User
        from optimizer.models import FarmerProfile
        user = User.objects.filter(first_name='Kuldeep Sandhu').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.farmer_profile.phone_number, '+919876543210')
        self.assertEqual(user.farmer_profile.primary_crop, 'Wheat')

        # 5. Log out
        self.client.logout()

        # 6. Log back in with Phone Number + password
        res_login_phone = self.client.post(reverse('login'), {
            'identifier': '+919876543210',
            'password': 'safe_farm_password_123'
        }, follow=True)
        self.assertEqual(res_login_phone.status_code, 200)
        self.assertTrue(res_login_phone.context['user'].is_authenticated)

    def test_email_registration_and_login(self):
        # 1. Send OTP for email registration
        send_payload = {
            'method': 'email',
            'full_name': 'Claire Lefebvre',
            'phone_number': '',
            'email': 'claire@ferme-beauce.fr',
            'farm_location': 'Chartres, France',
            'primary_crop': 'Wheat',
            'password': 'france_agri_secure_pass'
        }
        res_send = self.client.post(
            reverse('send_registration_otp_api'),
            data=json.dumps(send_payload),
            content_type='application/json'
        )
        self.assertEqual(res_send.status_code, 200)
        send_data = res_send.json()
        self.assertTrue(send_data['success'])

        # 2. Verify OTP
        res_verify = self.client.post(
            reverse('verify_registration_otp_api'),
            data=json.dumps({'otp': send_data['otp']}),
            content_type='application/json'
        )
        self.assertEqual(res_verify.status_code, 200)
        self.assertTrue(res_verify.json()['success'])

        # 3. Log out
        self.client.logout()

        # 4. Log in with Email + Password
        res_login_email = self.client.post(reverse('login'), {
            'identifier': 'claire@ferme-beauce.fr',
            'password': 'france_agri_secure_pass'
        }, follow=True)
        self.assertEqual(res_login_email.status_code, 200)
        self.assertTrue(res_login_email.context['user'].is_authenticated)


class LeafDoctorAndNDVITests(TestCase):
    def test_leaf_doctor_service_pathogen(self):
        from optimizer.services.leaf_doctor import diagnose_leaf_image
        diag = diagnose_leaf_image(crop_type='Wheat', symptom_hints='yellow stripe rust pustules')
        self.assertTrue(diag['success'])
        self.assertEqual(diag['type'], 'pathogen')
        self.assertIn('Rust', diag['primary_diagnosis'])
        self.assertGreater(diag['confidence_score'], 80.0)
        self.assertIn('delta_n', diag['nutrient_adjustments'])

    def test_leaf_doctor_service_deficiency(self):
        from optimizer.services.leaf_doctor import diagnose_leaf_image
        diag = diagnose_leaf_image(crop_type='Wheat', symptom_hints='pale yellow chlorosis V-shape on lower leaves')
        self.assertTrue(diag['success'])
        self.assertEqual(diag['type'], 'nutrient_deficiency')
        self.assertIn('Nitrogen', diag['primary_diagnosis'])
        self.assertGreater(diag['nutrient_adjustments']['delta_n'], 0)

    def test_leaf_doctor_api_endpoint(self):
        payload = {
            'crop_type': 'Maize',
            'symptom_hints': 'purple reddish margins on seedling foliage'
        }
        res = self.client.post(
            reverse('leaf_doctor_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('Phosphorus', data['primary_diagnosis'])

    def test_ndvi_satellite_service(self):
        from optimizer.services.ndvi_satellite import generate_field_ndvi_analysis
        analysis = generate_field_ndvi_analysis(lat=31.1471, lon=75.3412)
        self.assertTrue(analysis['success'])
        self.assertIn('geojson', analysis)
        self.assertEqual(analysis['geojson']['type'], 'FeatureCollection')
        self.assertGreaterEqual(len(analysis['geojson']['features']), 16)
        self.assertGreater(analysis['mean_ndvi'], 0.1)
        self.assertLessEqual(analysis['mean_ndvi'], 1.0)
        self.assertIn('health_score', analysis)

    def test_ndvi_satellite_api_endpoint(self):
        res = self.client.get(reverse('ndvi_satellite_api') + '?lat=31.1471&lon=75.3412')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('geojson', data)
        self.assertIn('mean_ndvi', data)
        self.assertIn('palette', data)



