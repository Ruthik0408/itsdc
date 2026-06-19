# GEM Bill Feature Rules

Build one ML feature row per `gem_bill`.

Scope:
- Payment category: `GEM_BILLS`
- Dak section filter: `dak.fk_section IN (113, 127, 128, 129, 219, 348)`
- Default date filter: `dak.list_date BETWEEN :start_date AND :end_date`
- Main flow: `dak -> gem_bill -> gem_product -> cheque_slip -> punching_medium -> schedule3 -> ecs`

Confirmed relation rules:
- `gem_bill.fk_dak = dak.id`
- `cheque_slip.fk_dak = dak.id`
- `punching_medium.fk_dak = dak.id`
- `schedule3.fk_dak = dak.id`
- `ecs.fk_dak = dak.id`
- `gem_product.fk_gem_bill = gem_bill.id` when available; `gem_product.transaction_id = gem_bill.transaction_id` is fallback context.
- `ch_booking.fk_dak`, `disallowance.fk_dak`, `recoveries.fk_dak`, and `gst_tds.fk_dak` link to `dak.id`.

Do not feed raw identifiers or free-text reason fields into Isolation Forest. Keep them only for review.

Required review identifiers:
- `gem_bill_id`, `dak_id`, `dakid_no`, `transaction_id`, `order_id`, `supply_order_no`, `crac_no`
- `invoice_no`, `gem_invoice_no`, `unit_id`, `unit_code`, `vendor_name`, `vendor_pan`
- `bill_amount`, `amount_passed`, `amount_to_be_paid`
- `gem_bill_record_status`, `dak_record_status`, `approved`, `payment_status`, `reason`, `failure_reason`

Feature groups:
- Table flow: `has_dak`, `has_gem_bill`, `has_gem_product`, `has_ch_booking`, `has_cheque_slip`, `has_punching_medium`, `has_schedule3`, `has_ecs`, skipped-stage flags, and `flow_anomaly_score`.
- Mandatory fields: unit, MSME, make type, Dak, transaction id, CRAC, order/supply order, final bill date, vendor, encrypted bank account/IFSC, products, product code, code head, and positive bill amount.
- Dak validation: missing Dak, Dak id not starting with `G`, Dak type not GEM where available, duplicate Dak, invalid Dak protocol.
- Duplicates: transaction id, GEM invoice, CRAC, order/CRAC, supply order, and offline/DAD duplicate proxies where those tables exist.
- CRAC/order: normalized CRAC/order/supply order mismatch, total paid against same order, overpayment amount and ratio.
- Dates: final bill date, office GEM start date if a real source exists, bill/final chronology, future dates.
- Vendor/bank/GSTIN: missing vendor, bank, IFSC, invalid IFSC length, missing PAN/GSTIN, GST TDS with missing GSTIN, bank/PAN reuse patterns.
- Product/code-head/amount: product count, product total, freight, GST, service flag, missing product/code head, invalid code head length, R&D project-code proxy, bill/product total mismatch.
- Budget/ch_booking: valid booking count, missing booking, amount total/diff, fund verification proxy.
- GST/recovery/deduction: disallowance, recoveries, GST TDS totals, missing GST TDS bill amount/type, expected amount passed/payable, mismatch flags.
- PM/cheque: valid PM/cheque counts, generated flags, generated without valid bill, PM/cheque mismatch, approved without payment stages, PM not tallied, PM after rejection.
- Schedule3/ECS: final stage exists flags, ECS without earlier stages, approved bill without ECS, ECS for invalid/rejected bills, payment completed flow.
- Approval: capital/proxy approval level features where hierarchy exists; otherwise auditor/AAO/AO/GO presence proxies.
- Rejection: rejection started/final approved, missing rejection reason, Dak rejected, payment failure, rejected bill with payment stages, rejected bill approved but Dak not rejected.
- Advanced GEM patterns: timing gaps, possible threshold splitting, shared vendor bank/PAN patterns, duplicate product/order similarity fallback, unit/vendor amount outliers, code-head anomalies, rejected reprocessing, approval/user-stage inconsistencies, month-end/FY-end concentration, repeated round amounts, duplicate UTR/payment references, PM/cheque/schedule amount mismatch, product price/freight/GST anomalies.
- Final counters: required, duplicate, flow, amount, budget, GST/recovery, PM/cheque, approval, rejection, total violations, weighted rule risk, and likely-risk flags.
- Advanced counters: `timing_anomaly_count`, `threshold_anomaly_count`, `vendor_bank_anomaly_count`, `product_similarity_anomaly_count`, `unit_behavior_anomaly_count`, `vendor_behavior_anomaly_count`, `code_head_anomaly_count`, `rejected_reprocess_anomaly_count`, `user_behavior_anomaly_count`, `month_end_anomaly_count`, `repeated_amount_anomaly_count`, `advanced_ecs_payment_anomaly_count`, `pm_cheque_amount_mismatch_count`, `product_price_anomaly_count`, `extra_pattern_anomaly_count`, and `extra_pattern_risk_score`.

Weights:
- Duplicate violations: 5
- ECS/payment flow violations: 5
- Approved without PM/cheque/payment completion: 5
- Amount mismatch: 4
- Budget/ch_booking missing: 4
- CRAC/order mismatch: 4
- Rejection workflow mismatch: 4
- Missing required fields: 2
- GST/recovery mismatch: 3
- Advanced high-risk patterns such as threshold splitting and shared vendor bank accounts: 6
- Advanced ECS/rejected reprocess patterns: 5
- Advanced PM/cheque/product similarity/product price mismatches: 4
- Advanced timing, unit/vendor/code-head/user behavior patterns: 3
- Repeated round amounts and month-end concentration: 1-2
