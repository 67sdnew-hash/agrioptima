"""
AgriOptima - 4R Nutrient Stewardship Split-Application Scheduler & .ICS Exporter
Computes physiologically synchronized multi-stage fertilizer dosages:
1. Basal Sowing (Day 0): 100% DAP + 100% MOP + 30% Urea
2. Vegetative / Tillering (Day 25-35): 40% Urea
3. Heading / Reproductive (Day 50-65): 30% Urea
Generates RFC 5545 compliant .ics calendar files and Google Calendar quick-links.
"""

from datetime import datetime, timedelta
import urllib.parse
from typing import Dict, Any, List

CROP_GROWTH_STAGES = {
    'Wheat': {
        'stage2_days': 28,
        'stage2_name': 'Crown Root Initiation & Active Tillering',
        'stage3_days': 55,
        'stage3_name': 'Booting & Spikelet Initiation',
    },
    'Rice': {
        'stage2_days': 21,
        'stage2_name': 'Active Tillering & Panicle Primordia',
        'stage3_days': 48,
        'stage3_name': 'Panicle Initiation & Booting',
    },
    'Maize': {
        'stage2_days': 30,
        'stage2_name': 'V6 Stage (Knee-High Rapid Growth)',
        'stage3_days': 60,
        'stage3_name': 'Tasseling & Silking Phase',
    },
    'Cotton': {
        'stage2_days': 35,
        'stage2_name': 'Squaring (First Flower Bud)',
        'stage3_days': 70,
        'stage3_name': 'Peak Flowering & Boll Development',
    }
}


def calculate_split_schedule(
    crop_type: str,
    sowing_date: datetime,
    urea_bags: float,
    dap_bags: float,
    mop_bags: float,
    delta_n_kg: float,
    delta_p_kg: float,
    delta_k_kg: float
) -> List[Dict[str, Any]]:
    """
    Computes a 3-stage physiological split-application schedule for fertilizers.
    """
    stage_spec = CROP_GROWTH_STAGES.get(crop_type, CROP_GROWTH_STAGES['Wheat'])

    date_stage1 = sowing_date
    date_stage2 = sowing_date + timedelta(days=stage_spec['stage2_days'])
    date_stage3 = sowing_date + timedelta(days=stage_spec['stage3_days'])

    # Dosage distribution:
    # Basal: 100% DAP, 100% MOP, 30% Urea
    # Stage 2: 40% Urea
    # Stage 3: 30% Urea
    stage1_urea = round(urea_bags * 0.30, 1)
    stage2_urea = round(urea_bags * 0.40, 1)
    stage3_urea = round(urea_bags * 0.30, 1)

    schedule = [
        {
            'stage_number': 1,
            'title': 'Stage 1: Basal Application at Sowing',
            'growth_phase': 'Sowing & Germination',
            'scheduled_date': date_stage1.strftime('%B %d, %Y'),
            'iso_date': date_stage1.strftime('%Y-%m-%d'),
            'day_offset': 0,
            'dap_bags': dap_bags,
            'mop_bags': mop_bags,
            'urea_bags': stage1_urea,
            'application_method': 'Band placement 5cm beside & below seeds during drilling.',
            'rationale': 'DAP and MOP provide early root elongation and cold/drought resilience. Basal urea supports early vigor without leaching.'
        },
        {
            'stage_number': 2,
            'title': f'Stage 2: Top-Dressing at {stage_spec["stage2_name"]}',
            'growth_phase': stage_spec['stage2_name'],
            'scheduled_date': date_stage2.strftime('%B %d, %Y'),
            'iso_date': date_stage2.strftime('%Y-%m-%d'),
            'day_offset': stage_spec['stage2_days'],
            'dap_bags': 0.0,
            'mop_bags': 0.0,
            'urea_bags': stage2_urea,
            'application_method': 'Broadcast immediately before scheduled irrigation or gentle rain.',
            'rationale': 'Matches peak vegetative nitrogen demand to maximize tillering capacity and canopy development.'
        },
        {
            'stage_number': 3,
            'title': f'Stage 3: Final Top-Dressing at {stage_spec["stage3_name"]}',
            'growth_phase': stage_spec['stage3_name'],
            'scheduled_date': date_stage3.strftime('%B %d, %Y'),
            'iso_date': date_stage3.strftime('%Y-%m-%d'),
            'day_offset': stage_spec['stage3_days'],
            'dap_bags': 0.0,
            'mop_bags': 0.0,
            'urea_bags': stage3_urea,
            'application_method': 'Foliar or broadcast application under dry foliage with moist soil.',
            'rationale': 'Prevents premature leaf senescence, ensuring maximum grain filling and protein synthesis.'
        }
    ]

    return schedule


def generate_ics_calendar(
    crop_type: str,
    sowing_date: datetime,
    urea_bags: float,
    dap_bags: float,
    mop_bags: float,
    delta_n_kg: float,
    delta_p_kg: float,
    delta_k_kg: float
) -> str:
    """
    Generates an RFC 5545 compliant .ics calendar file content containing all 3 split application events.
    """
    schedule = calculate_split_schedule(
        crop_type, sowing_date, urea_bags, dap_bags, mop_bags, delta_n_kg, delta_p_kg, delta_k_kg
    )

    now_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AgriOptima//4R Fertilizer Scheduler//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:AgriOptima Fertilizer Schedule",
        "X-WR-TIMEZONE:UTC",
    ]

    for item in schedule:
        event_date_str = datetime.strptime(item['iso_date'], '%Y-%m-%d').strftime('%Y%m%d')
        next_day_str = (datetime.strptime(item['iso_date'], '%Y-%m-%d') + timedelta(days=1)).strftime('%Y%m%d')
        uid = f"agrioptima-{crop_type.lower()}-stage{item['stage_number']}-{event_date_str}@agrioptima.render.com"

        fertilizer_desc = []
        if item['dap_bags'] > 0:
            fertilizer_desc.append(f"{item['dap_bags']} bags DAP (18-46-0)")
        if item['mop_bags'] > 0:
            fertilizer_desc.append(f"{item['mop_bags']} bags MOP (0-0-60)")
        if item['urea_bags'] > 0:
            fertilizer_desc.append(f"{item['urea_bags']} bags Urea (46-0-0)")

        desc_text = (
            f"AgriOptima 4R Prescription for {crop_type}\\n"
            f"Phase: {item['growth_phase']}\\n"
            f"Apply: {', '.join(fertilizer_desc)}\\n\\n"
            f"Method: {item['application_method']}\\n"
            f"Agronomic Rationale: {item['rationale']}"
        )

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{event_date_str}",
            f"DTEND;VALUE=DATE:{next_day_str}",
            f"SUMMARY:🌾 AgriOptima: Apply Fertilizer ({crop_type} - Stage {item['stage_number']})",
            f"DESCRIPTION:{desc_text}",
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM",
            "TRIGGER:-PT12H",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Reminder: Apply {crop_type} fertilizer tomorrow morning ({item['title']})",
            "END:VALARM",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def get_google_calendar_url(title: str, iso_date: str, details: str) -> str:
    """
    Constructs a 1-click Google Calendar event creation URL.
    """
    dt_clean = iso_date.replace('-', '')
    end_dt = (datetime.strptime(iso_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y%m%d')
    base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    params = {
        'text': f"🌾 AgriOptima: {title}",
        'dates': f"{dt_clean}/{end_dt}",
        'details': details,
        'sf': 'true',
        'output': 'xml'
    }
    return base + "&" + urllib.parse.urlencode(params)
