# Tulip 2.0 Positive Supervision Log

Append-only record of reviewer-accepted anomalies. Each block feeds the
next scan so the Isolation Forest and autoencoder give added focus to
confirmed patterns. Do not edit or reorder existing entries.

## ACCEPTED 2026-06-17T16:46:25+00:00 — dak:1544299
- table: dak
- source_record_id: 1544299
- anomaly_score: 100.0 (isolation 7.412567313712204 / autoencoder 100.0)
- reviewer_feedback: (none)
- explanation: This data profile looks highly anomalous because it involves a large transaction of Rs 16,333,341, which is extremely high compared to the median amount of Rs 13,820 in the latest 10,000 usable records. Additionally, this transaction is 4355.6 times the median amount for its specific 'fk_section' and 99 times the median amount for its 'fk_dak_type', indicating a significant deviation from normal patterns.
```json
{"transaction_id": "dak:1544299", "table_name": "dak", "source_record_id": "1544299", "anomaly_score": 100.0, "isolation_score": 7.412567313712204, "autoencoder_score": 100.0, "engineered_feature_values": {"group_frequency": 6.104793232414985, "ratio_to_median": 1181.8625904486253, "dak_dak_fk_dak_type_dak_type_table_name_frequency": 7.3777589082278725, "dak_dak_fk_section_section_section_name_frequency": 6.951772164398911, "dak_dak_fk_dak_type_dak_type_dak_type_abbr_frequency": 6.137727054086234, "dak_amount_to_dak_fk_dak_type_dak_type_table_name_median": 234.60702384372306, "dak_amount_to_dak_fk_section_section_section_name_median": 1784.9670509808207, "dak_dak_fk_section_section_dak_type_sequential_frequency": 8.740016691519521, "dak_amount_to_dak_fk_dak_type_dak_type_dak_type_abbr_median": 1.0, "dak_amount_to_dak_fk_section_section_dak_type_sequential_median": 1.0}, "reviewer_feedback": "", "accepted_at": "2026-06-17T16:46:25+00:00"}
```

## ACCEPTED 2026-06-17T16:46:41+00:00 — dak:1544354
- table: dak
- source_record_id: 1544354
- anomaly_score: 100.0 (isolation 0.692526279143646 / autoencoder 100.0)
- reviewer_feedback: (none)
- explanation: This data profile looks highly anomalous because the transaction amount of Rs 3,454,138 is extremely high compared to the median amount of Rs 13,820 for the same 'fk_dak_type', and it is also significantly higher than the median amount for the same 'fk_office_id'. This places the transaction in the 97.2th percentile among the latest 10,000 usable dak records, indicating a highly unusual financial pattern.
```json
{"transaction_id": "dak:1544354", "table_name": "dak", "source_record_id": "1544354", "anomaly_score": 100.0, "isolation_score": 0.692526279143646, "autoencoder_score": 100.0, "engineered_feature_values": {"group_frequency": 5.869296913133774, "ratio_to_median": 249.93762662807526, "dak_dak_fk_dak_type_dak_type_table_name_frequency": 4.61512051684126, "dak_dak_fk_section_section_section_name_frequency": 5.869296913133774, "dak_dak_fk_dak_type_dak_type_dak_type_abbr_frequency": 6.137727054086234, "dak_amount_to_dak_fk_dak_type_dak_type_table_name_median": 17.780272613091192, "dak_amount_to_dak_fk_section_section_section_name_median": 1.0, "dak_dak_fk_section_section_dak_type_sequential_frequency": 7.392647520721623, "dak_amount_to_dak_fk_dak_type_dak_type_dak_type_abbr_median": 1.0, "dak_amount_to_dak_fk_section_section_dak_type_sequential_median": 168.13366433021807}, "reviewer_feedback": "", "accepted_at": "2026-06-17T16:46:41+00:00"}
```

## ACCEPTED 2026-06-18T05:30:03+00:00 — dak:1038489
- table: dak
- source_record_id: 1038489
- anomaly_score: 100.0 (isolation -1.9104250502309519 / autoencoder 100.0)
- reviewer_feedback: (none)
- explanation: This transaction of Rs 589,450 is highly unusual, being 51.7 times the median amount for its section and 55.8 times the median for its dak type, placing it in the 91.9th percentile among recent records. It closely matches the confirmed anomaly pattern seen in prior accepted cases, where large, outlier amounts deviate dramatically from expected values within specific sections and dak types.
```json
{"transaction_id": "dak:1038489", "table_name": "dak", "source_record_id": "1038489", "anomaly_score": 100.0, "isolation_score": -1.9104250502309519, "autoencoder_score": 100.0, "engineered_feature_values": {"dak_age_days": 15.378612037037039, "dak_created_hour": 2.0, "dak_created_day_of_week": 1.0, "dak_amount_ratio_to_median": 36.10498591204214, "dak_amount_ratio_to_group_median_by_unit": 67.36571428571429, "dak_amount_ratio_to_group_median_by_section": 51.70614035087719, "dak_amount_ratio_to_group_median_by_dak_type": 55.81912878787879, "dak_amount_ratio_to_group_median_by_central_unit": 67.36571428571429, "dak_dak_fk_dak_type_dak_type_table_name_frequency": 7.616775808698373, "dak_dak_fk_section_section_section_name_frequency": 7.641564441260972, "dak_dak_fk_dak_type_dak_type_dak_type_abbr_frequency": 6.461468176353717, "dak_amount_to_dak_fk_dak_type_dak_type_table_name_median": 37.02575376884422, "dak_amount_to_dak_fk_section_section_section_name_median": 36.129328838492185, "dak_dak_fk_section_section_dak_type_sequential_frequency": 8.747034264178168, "dak_amount_to_dak_fk_dak_type_dak_type_dak_type_abbr_median": 1.0, "dak_amount_to_dak_fk_section_section_dak_type_sequential_median": 48.173422687152666}, "reviewer_feedback": "", "accepted_at": "2026-06-18T05:30:03+00:00"}
```

## ACCEPTED 2026-06-18T05:30:21+00:00 — dak:1038488
- table: dak
- source_record_id: 1038488
- anomaly_score: 100.0 (isolation 12.466742091740194 / autoencoder 100.0)
- reviewer_feedback: (none)
- explanation: This transaction of Rs 4,454,640 is extremely high compared to typical amounts, being 390.8 times the median for its section and 421.8 times the median for its dak type, placing it far above normal patterns. It closely matches a previously confirmed anomaly pattern involving a similarly large, outlier transaction with extreme ratios to group medians.
```json
{"transaction_id": "dak:1038488", "table_name": "dak", "source_record_id": "1038488", "anomaly_score": 100.0, "isolation_score": 12.466742091740194, "autoencoder_score": 100.0, "engineered_feature_values": {"dak_age_days": 15.390054791666666, "dak_created_hour": 2.0, "dak_created_day_of_week": 1.0, "dak_amount_ratio_to_median": 272.8555678059537, "dak_amount_ratio_to_group_median_by_unit": 509.1017142857143, "dak_amount_ratio_to_group_median_by_section": 390.7578947368421, "dak_amount_ratio_to_group_median_by_dak_type": 421.84090909090907, "dak_amount_ratio_to_group_median_by_central_unit": 509.1017142857143, "dak_dak_fk_dak_type_dak_type_table_name_frequency": 7.616775808698373, "dak_dak_fk_section_section_section_name_frequency": 7.641564441260972, "dak_dak_fk_dak_type_dak_type_dak_type_abbr_frequency": 6.461468176353717, "dak_amount_to_dak_fk_dak_type_dak_type_table_name_median": 279.8140703517588, "dak_amount_to_dak_fk_section_section_section_name_median": 273.03953417100826, "dak_dak_fk_section_section_dak_type_sequential_frequency": 8.747034264178168, "dak_amount_to_dak_fk_dak_type_dak_type_dak_type_abbr_median": 1.0, "dak_amount_to_dak_fk_section_section_dak_type_sequential_median": 364.0601503759398}, "reviewer_feedback": "", "accepted_at": "2026-06-18T05:30:21+00:00"}
```

## ACCEPTED 2026-06-18T05:30:42+00:00 — bill:183892
- table: bill
- source_record_id: 183892
- anomaly_score: 4.1768741833197565 (isolation 4.1768741833197565 / autoencoder None)
- reviewer_feedback: (none)
- explanation: bill record 183892.0 was flagged because amount_claimed is Rs 43,522,815.00, placing it around the 100.0th percentile among the latest 10,000 usable bill records. The table median is Rs 40,037.00 and the 95th percentile is Rs 1,321,401.95. Isolation score: 4.18; higher values are more unusual within this scan.
```json
{"transaction_id": "bill:183892", "table_name": "bill", "source_record_id": "183892", "anomaly_score": 4.1768741833197565, "isolation_score": 4.1768741833197565, "autoencoder_score": null, "engineered_feature_values": {}, "reviewer_feedback": "", "accepted_at": "2026-06-18T05:30:42+00:00"}
```

## ACCEPTED 2026-06-18T05:30:57+00:00 — punching_medium:1607618
- table: punching_medium
- source_record_id: 1607618
- anomaly_score: 4.240402653340292 (isolation 4.240402653340292 / autoencoder None)
- reviewer_feedback: (none)
- explanation: punching_medium record 1607618.0 was flagged because amount is Rs 1,324,600.00, placing it around the 97.4th percentile among the latest 10,000 usable punching_medium records. The table median is Rs 6,700.00 and the 95th percentile is Rs 543,337.00. Isolation score: 4.24; higher values are more unusual within this scan.
```json
{"transaction_id": "punching_medium:1607618", "table_name": "punching_medium", "source_record_id": "1607618", "anomaly_score": 4.240402653340292, "isolation_score": 4.240402653340292, "autoencoder_score": null, "engineered_feature_values": {}, "reviewer_feedback": "", "accepted_at": "2026-06-18T05:30:57+00:00"}
```

## ACCEPTED 2026-06-18T06:28:17+00:00 — bill:183859
- table: bill
- source_record_id: 183859
- anomaly_score: 100.0 (isolation 11.939051931848043 / autoencoder 100.0)
- reviewer_feedback: (none)
- explanation: bill record 183859 was flagged because amount_claimed is Rs 9,053,549.00, placing it around the 99.6th percentile among the latest 10,000 usable bill records. The table median is Rs 40,068.00 and the 95th percentile is Rs 1,321,401.95. Context check: fk_dak=717743 appears only once in the scanned sample; it is 37.2x this fk_section's median amount (Rs 243,080.00). Isolation score: 11.94; higher values are more unusual within this scan. Second-pass relationship score: 100.00; row pattern error 272.881954 is above the learned cutoff 0.843409, so this row remains anomalous after checking the full feature pattern.
```json
{"transaction_id": "bill:183859", "table_name": "bill", "source_record_id": "183859", "anomaly_score": 100.0, "isolation_score": 11.939051931848043, "autoencoder_score": 100.0, "engineered_feature_values": {"bill_bill_fk_dak_dak_sender_name_frequency": 0.0, "amount_claimed_ratio_to_group_median_by_unit": 20.366289794302375, "bill_bill_fk_dak_dak_record_status_frequency": 9.17895289873455, "amount_claimed_ratio_to_group_median_by_vendor": 1.0, "bill_amount_to_bill_fk_dak_dak_sender_name_median": 0.0, "bill_amount_to_bill_fk_dak_dak_record_status_median": 226.338725, "bill_bill_fk_section_section_section_name_frequency": 4.859812404361672, "bill_amount_to_bill_fk_section_section_section_name_median": 60.44978173330122, "bill_bill_fk_section_section_dak_type_sequential_frequency": 7.786136437783072, "bill_amount_to_bill_fk_section_section_dak_type_sequential_median": 219.3337532554055}, "reviewer_feedback": "", "accepted_at": "2026-06-18T06:28:17+00:00"}
```
