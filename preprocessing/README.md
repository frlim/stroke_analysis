Scripts to clean/generate hospital performance data to feed
into Stroke triage model.

order of operations:
1. python generate_hosp_keys_and_address_from_diff_sources.py
2. python anonymize_raw_data.py
3. python cap_hospitals_to_northeast_region.py
4. python create_stroke_locations_inputs.py
