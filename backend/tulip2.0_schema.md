# Tulip 2.0 Database Structural Schema Layout


## Table: aaa_central_bank
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| bank_name | character varying(100) |  | None |
| bank_branch | character varying(100) |  | None |
| bank_station | character varying(100) |  | None |
| fk_treasury_bank | integer |  | None |
| treasury_code | character varying(2) |  | None |
| micr_code | character varying(9) |  | None |
| ifsc_code | character varying(11) |  | None |
| old_ifsc_code | character varying(11) |  | None |
| rtgs_code | character varying(11) |  | None |
| created_by | integer |  | None |
| submitted_by | integer |  | None |
| approved_by | integer |  | None |
| created_at | timestamp with time zone |  | None |
| focal_point_branch | boolean |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| ip | character varying(50) |  | None |
| mac | character varying(20) |  | None |
| approved | boolean |  | None |
| created_date | date |  | None |
| submit_date | date |  | None |
| approve_date | date |  | None |
| fk_bank | bigint | FK | bank |

## Table: aaa_central_beneficiary
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| bid | character varying(14) |  | None |
| beneficiary_name | character varying(100) |  | None |
| ifsc | character varying(11) |  | None |
| acno | character varying(70) |  | None |
| account_type | character varying(2) |  | None |
| created_by | integer |  | None |
| submitted_by | integer |  | None |
| approved_by | integer |  | None |
| created_date | date |  | None |
| submit_date | date |  | None |
| approve_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp with time zone |  | None |
| cda_code | integer |  | None |
| office_id | integer |  | None |
| remarks | text |  | None |
| ip | character varying(50) |  | None |
| mac | character varying(20) |  | None |
| agency_type | character varying(2) |  | None |
| fk_bpd | bigint | FK | bank_pan_detail |

## Table: aaa_central_civ_employee
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| gpf_pran | character varying(16) |  | None |
| month | character varying(7) |  | None |
| employee_name | character varying(50) |  | None |
| bid | character varying(14) |  | None |
| gender | character(1) |  | None |
| category | character varying(3) |  | None |
| present_unit | character varying(14) |  | None |
| present_unit_date | date |  | None |
| division | character(1) |  | None |
| fk_status_code | integer | FK | status_code |
| status_effect_date | date |  | None |
| fk_present_desg | integer | FK | civ_designation |
| present_desg_date | date |  | None |
| date_of_birth | date |  | None |
| appointment_date | date |  | None |
| increment_date | date |  | None |
| superannuation_date | date |  | None |
| gazette | boolean |  | None |
| ph_status | boolean |  | None |
| married | boolean |  | None |
| mobile_number | character varying(12) |  | None |
| home_town | character varying(25) |  | None |
| ltc_encashment_days | integer |  | None |
| recovery_stop_date | date |  | None |
| fund_type | character(1) |  | None |
| cgeis | character(1) |  | None |
| cghs | boolean |  | None |
| cash_allowance | character(1) |  | None |
| deputation | boolean |  | None |
| approved | boolean |  | None |
| current_record | boolean |  | None |
| old_id | bigint |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| employee_type | character(1) |  | None |
| staff_type | character varying(10) |  | None |
| personal_number | character varying(16) |  | None |
| paybill_tada_medical | character varying(2) |  | None |
| hra | boolean |  | None |
| prof_tax | boolean |  | None |
| hod_no_staff_car | boolean |  | None |
| hra_class | character(1) |  | None |
| tpta_class | character varying(2) |  | None |
| spl_increment | boolean |  | None |
| hag | boolean |  | None |
| pay_level | character varying(4) |  | None |
| pan_number | character varying(10) |  | None |
| aadhar_no | character varying(70) |  | None |
| special_case | character varying(20) |  | None |
| remarks | text |  | None |
| email | character varying(50) |  | None |
| aft | boolean |  | None |
| old_pran_no | character varying(16) |  | None |
| task_no | integer |  | None |
| created_at | timestamp with time zone |  | None |
| cda_code | integer |  | None |
| office_id | integer |  | None |
| prev_cda_code | integer |  | None |
| prev_office_id | integer |  | None |
| created_by | integer |  | None |
| submitted_by | integer |  | None |
| approved_by | integer |  | None |
| created_date | date |  | None |
| submit_date | date |  | None |
| approve_date | date |  | None |
| ip | character varying(50) |  | None |
| mac | character varying(20) |  | None |
| fk_civ_employee | bigint | FK | civ_employee |
| present_basic_pay | integer |  | None |

## Table: aaa_central_unit
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| unit_code | character varying(14) |  | None |
| unit_name | character varying(100) |  | None |
| address1 | character varying(50) |  | None |
| address2 | character varying(50) |  | None |
| address3 | character varying(50) |  | None |
| station | character varying(25) |  | None |
| pin_code | character varying(6) |  | None |
| email | character varying(40) |  | None |
| phone1 | character varying(12) |  | None |
| phone2 | character varying(12) |  | None |
| fax | character varying(12) |  | None |
| co_rank | character varying(10) |  | None |
| co_name | character varying(20) |  | None |
| raised_date | date |  | None |
| closed_date | date |  | None |
| imprest_account_no | character varying(25) |  | None |
| ss_imprest_account_no | character varying(25) |  | None |
| hra_class | character varying(2) |  | None |
| tpta_class | character varying(2) |  | None |
| headquarters | boolean |  | None |
| hqrs_unit_id | integer |  | None |
| approved | boolean |  | None |
| mes_unit | boolean |  | None |
| created_at | timestamp with time zone |  | None |
| lao_code | integer |  | None |
| cda_code | integer |  | None |
| prev_cda_code | integer |  | None |
| state_code | character varying(2) |  | None |
| ration_class | character(1) |  | None |
| ddo_regn_no | character varying(10) |  | None |
| tan_number | character varying(10) |  | None |
| created_by | integer |  | None |
| submitted_by | integer |  | None |
| approved_by | integer |  | None |
| created_date | date |  | None |
| submit_date | date |  | None |
| approve_date | date |  | None |
| reason | text |  | None |
| record_status | character(1) |  | None |
| service | character varying(9) |  | None |
| raised_authority_no | character varying(50) |  | None |
| raised_authority_date | date |  | None |
| closure_authority_no | character varying(50) |  | None |
| closure_authority_date | date |  | None |
| remarks | text |  | None |
| fis_unit_code | character varying(7) |  | None |
| value1 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| nature_of_unit | character varying(10) |  | None |
| sub_area_id | integer |  | None |
| area_id | integer |  | None |
| brig_id | integer |  | None |
| divn_id | integer |  | None |
| corps_id | integer |  | None |
| command_id | integer |  | None |
| sus_no | character varying(10) |  | None |
| grant_bill_pre_post_audit | character varying(4) |  | None |
| engineering_regiment | boolean |  | None |
| coordinating_controller | character varying(2) |  | None |
| imprest_prototype_no | character varying(15) |  | None |
| ip | character varying(50) |  | None |
| mac | character varying(20) |  | None |
| local_unit_code | character varying(10) |  | None |
| closed_by_usr_date | date |  | None |
| fk_closed_by_usr | integer |  | None |
| fk_lao | integer |  | None |
| fk_unit | bigint | FK | unit |
| command | character varying(100) |  | None |
| command_code | integer |  | None |

## Table: aaa_central_vendor
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| category_code | character varying(2) |  | None |
| bid | character varying(14) |  | None |
| vendor_name | character varying(200) |  | None |
| address1 | character varying(200) |  | None |
| address2 | character varying(100) |  | None |
| address3 | character varying(100) |  | None |
| city | character varying(50) |  | None |
| state_code | character varying(2) |  | None |
| country_code | character varying(3) |  | None |
| mes_enlisted | boolean |  | None |
| enlistment_no | character varying(10) |  | None |
| vendor_class | character varying(3) |  | None |
| vendor_grade | character varying(2) |  | None |
| landline_telephone_no1 | character varying(12) |  | None |
| landline_telephone_no2 | character varying(12) |  | None |
| mobile_phone1 | character varying(10) |  | None |
| mobile_phone2 | character varying(10) |  | None |
| pan_number | character varying(10) |  | None |
| tan_number | character varying(10) |  | None |
| branch | boolean |  | None |
| parent_vendor_id | integer |  | None |
| approved | boolean |  | None |
| pin_code | character varying(6) |  | None |
| cda_code | integer |  | None |
| email_id | character varying(50) |  | None |
| gstin | character varying(15) |  | None |
| fax_number1 | character varying(12) |  | None |
| fax_number2 | character varying(12) |  | None |
| aadhar_number | character varying(12) |  | None |
| aadhar_holder_name | character varying(50) |  | None |
| remarks | text |  | None |
| mandate_form_received | boolean |  | None |
| gem_vendor_code | character varying(20) |  | None |
| msme | boolean |  | None |
| echs_unique_no | character varying(50) |  | None |
| echs_card_no | character varying(50) |  | None |
| lei | character varying(20) |  | None |
| created_by | integer |  | None |
| submitted_by | integer |  | None |
| approved_by | integer |  | None |
| created_date | date |  | None |
| submit_date | date |  | None |
| approve_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp with time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| ip | character varying(50) |  | None |
| mac | character varying(20) |  | None |
| fk_vendor | bigint | FK | vendor |
| msme_cat | character(1) |  | None |
| make_cat | character(2) |  | None |

## Table: allotment_category
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| category_code | character varying(3) |  | None |
| category_name | character varying(25) |  | None |
| section_group | character varying(15) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: allotment_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| allotment_year | character varying(9) |  | None |
| nature | character(1) |  | None |
| fk_allotment_authority | integer | FK | allotment_authority |
| fk_code_head | integer | FK | code_head |
| reference_no | character varying(100) |  | None |
| reference_date | date |  | None |
| allotment_amount | double precision |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| progressive_allotment | double precision |  | None |
| progressive_expenditure | double precision |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| month_year | character varying(7) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| code_head | character varying(9) |  | None |
| project_code | character varying(14) |  | None |
| fk_dad_office | integer | FK | dad_office |
| ca_amount_blocked | double precision |  | None |
| gem_amount_blocked | double precision |  | None |
| fk_block_by_usr | integer | FK | usr |
| block_date | date |  | None |
| block_remarks | text |  | None |
| fk_release_by_usr | integer | FK | usr |
| fk_usr | integer | FK | usr |
| release_date | date |  | None |
| release_remarks | text |  | None |
| value1 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| apr | double precision |  | None |
| may | double precision |  | None |
| jun | double precision |  | None |
| jul | double precision |  | None |
| aug | double precision |  | None |
| sep | double precision |  | None |
| oct | double precision |  | None |
| nov | double precision |  | None |
| dec | double precision |  | None |
| jan | double precision |  | None |
| feb | double precision |  | None |
| mar | double precision |  | None |
| mar13 | double precision |  | None |
| mar14 | double precision |  | None |
| mar15 | double precision |  | None |
| mer_gen_date | timestamp without time zone |  | None |
| mer_gen_month | character varying(7) |  | None |
| mer_remarks | text |  | None |
| mer_gen_seq | integer |  | None |
| major_head | character varying(10) |  | None |
| minor_head | character varying(10) |  | None |
| fk_budget_head | integer | FK | budget_head |
| lc_amount_blocked | double precision |  | None |
| fis_doc_no | character varying(50) |  | None |
| fis_date | date |  | None |
| fis_xml_file_no | text |  | None |
| fis_remarks | text |  | None |
| blocked_for_gem | boolean |  | None |
| coordinating_controller | character varying(2) |  | None |
| cbm_date | date |  | None |
| cbm_response | character varying(10) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| allot_letter_path | character varying(255) |  | None |

## Table: audited_bills
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_audit_drill | integer | FK | audit_drill |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| current_record | boolean |  | None |
| record_status | character(1) |  | None |

## Table: bank
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| bank_name | character varying(50) |  | None |
| bank_branch | character varying(50) |  | None |
| bank_station | character varying(25) |  | None |
| fk_treasury_bank | integer | FK | bank |
| treasury_code | character varying(2) |  | None |
| micr_code | character varying(9) |  | None |
| ifsc_code | character varying(11) |  | None |
| rtgs_code | character varying(11) |  | None |
| sbi | boolean |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| focal_point_branch | boolean |  | None |
| tr_bank | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| old_ifsc_code | character varying(11) |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |

## Table: bank_pan_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_vendor | integer | FK | vendor |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_bank | integer | FK | bank |
| hashed_bank_account_no | character varying(60) |  | None |
| hashed_pan_no | character varying(60) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| agency_type | character varying(2) |  | None |
| fk_unit | integer | FK | unit |
| account_type | character varying(2) |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_imprest | integer | FK | imprest |
| value1 | character varying(15) |  | None |

## Table: bank_scroll
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_fpb_bank | integer | FK | bank |
| scroll_type | character(1) |  | None |
| scroll_number | character varying(17) |  | None |
| scroll_date | date |  | None |
| scroll_amount | double precision |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| remarks | text |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_te_dak | bigint | FK | dak |
| dv_no | integer |  | None |
| dv_date | date |  | None |
| dv_section | character varying(4) |  | None |
| dv_month | character varying(7) |  | None |
| fk_section | integer | FK | section |
| total_items | integer |  | None |
| item_entry_status | character(1) |  | None |
| item_total_amount | double precision |  | None |
| fk_auditor_te | integer | FK | usr |
| fk_aao_te | integer | FK | usr |
| fk_ao_te | integer | FK | usr |
| auditor_te_date | date |  | None |
| aao_te_date | date |  | None |
| ao_te_date | date |  | None |
| te_record_status | character(1) |  | None |
| te_approved | boolean |  | None |
| te_remarks | text |  | None |
| te_reason | text |  | None |
| te_month | character varying(7) |  | None |
| fk_tr_bank | integer | FK | bank |
| sub_scroll_number | character varying(20) |  | None |
| sub_scroll_date | date |  | None |
| sub_scroll_amount | double precision |  | None |
| fk_fpb_central_bank | bigint | FK | aaa_central_bank |
| fk_tr_central_bank | bigint | FK | aaa_central_bank |

## Table: bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_contract_agreement | bigint | FK | contract_agreement |
| fk_supply_order | bigint | FK | supply_order |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| month | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| amount_disallowed | double precision |  | None |
| provisional_payment | boolean |  | None |
| verified_audit_checks | boolean |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| fk_jcda | integer | FK | usr |
| jcda_date | date |  | None |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| passed | boolean |  | None |
| cancelled | boolean |  | None |
| dp_sheet_generated | boolean |  | None |
| ss_imprest | boolean |  | None |
| lch | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_code_head | integer |  | None |
| lch_updated | boolean |  | None |
| recoveries | double precision |  | None |
| code_hd | character varying(9) |  | None |
| ca_updated | boolean |  | None |
| so_updated | boolean |  | None |
| tax_recovery_principal_amount | double precision |  | None |
| crv_no | character varying(10) |  | None |
| pv_no | character varying(10) |  | None |
| unit_paid_percent | integer |  | None |
| unit_paid_amount | double precision |  | None |
| cda_paid_percent | integer |  | None |
| cda_paid_amount | double precision |  | None |
| payment_record_type | character(1) |  | None |
| pv_date | date |  | None |
| no_of_cr_vouchers | integer |  | None |
| approved | boolean |  | None |
| skip_item_verification | boolean |  | None |
| fk_pay_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| fk_allotment_detail | integer | FK | allotment_detail |
| percentage_of_it | double precision |  | None |
| ifa_concurrence | character(1) |  | None |
| percentage_of_ld | double precision |  | None |
| ld_days | integer |  | None |
| ld_recovery_principal_amount | double precision |  | None |
| exclude_percent | integer |  | None |
| amount_excluded | double precision |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| payment_mode | character varying(3) |  | None |
| invoice_number | character varying(50) |  | None |
| invoice_date | date |  | None |
| gst5_amount | double precision |  | None |
| gst12_amount | double precision |  | None |
| gst18_amount | double precision |  | None |
| gst28_amount | double precision |  | None |
| remarks | text |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fis_unit_code | character varying(10) |  | None |
| fis_doc_no | character varying(50) |  | None |
| fis_date | date |  | None |
| fis_contract_no | character varying(50) |  | None |
| fis_contract_date | date |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_date | date |  | None |
| dp_sheet_no | integer |  | None |
| cmp_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| gem_contract_no | character varying(50) |  | None |
| gem_contract_date | date |  | None |
| gem_invoice_no | character varying(50) |  | None |
| gem_invoice_date | date |  | None |
| gem_crac_no | character varying(50) |  | None |
| gem_crac_date | date |  | None |
| gem_prc_no | character varying(50) |  | None |
| gem_prc_date | date |  | None |
| gst_type | character(1) |  | None |
| fis_bill_code | character varying(10) |  | None |
| fis_bill_date | date |  | None |
| fk_civ_employee | bigint | FK | civ_employee |
| cda_sanction_no | character varying(100) |  | None |
| cda_sanction_date | date |  | None |
| gem_rejected_dakid | character varying(18) |  | None |
| gst_applicable | character(1) |  | None |
| list_no | integer |  | None |
| list_date | date |  | None |
| capital_id | character varying(15) |  | None |
| make_type | character(1) |  | None |
| msme | character(1) |  | None |
| pol_qty | integer |  | None |
| fk_pol_fuel_type | integer | FK | pol_fuel_type |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_pay_central_unit | bigint | FK | aaa_central_unit |

## Table: bill_life_cycle_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_bill_life_cycle | integer | FK | bill_life_cycle |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_bill_type | integer | FK | bill_type |
| remarks | text |  | None |
| record_status | character(1) |  | None |
| key1 | character varying(20) |  | None |
| value1 | character varying(50) |  | None |
| key2 | character varying(20) |  | None |
| value2 | character varying(50) |  | None |

## Table: bill_nature
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_bill_type | integer | FK | bill_type |
| nature | character varying(50) |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: bill_refunds
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | integer | FK | dak |
| fk_vendor | integer | FK | vendor |
| fk_unit | integer | FK | unit |
| amount_claimed | double precision |  | None |
| reason | text |  | None |
| payment_type | character varying(1) |  | None |
| remarks | text |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| payment_mode | character varying(3) |  | None |
| fk_section | integer | FK | section |
| fk_refund_dak | integer | FK | dak |
| amount_passed | double precision |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_task_usr | integer | FK | usr |
| month | character varying(7) |  | None |
| record_status | character(1) |  | None |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| fk_recovery_code | integer | FK | recovery_code |
| fk_bank_pan_detail | bigint |  | None |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: bill_type
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| type_of_bill | character varying(50) |  | None |
| lch | boolean |  | None |
| ss_imprest | boolean |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_dak_type | integer | FK | dak_type |
| fk_task_distribution_mode | integer | FK | task_distribution_mode |
| fk_office_id | integer | FK | dad_office |
| claim_verification_type | character(1) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| fk_parent_bill_type | integer | FK | bill_type |

## Table: billing_cycle_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| value | character varying(25) |  | None |
| unit | character varying(50) |  | None |
| transaction_id | character varying(100) |  | None |
| fk_gem_bill | bigint | FK | gem_bill |
| fk_consignment_detail | bigint | FK | consignment_detail |

## Table: cash_assignment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| fk_dak | bigint | FK | dak |
| month | character varying(7) |  | None |
| amount | double precision |  | None |
| release_date | date |  | None |
| drawn_amount | double precision |  | None |
| dv_no | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_section | integer |  | None |
| fk_task_usr | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| approved | boolean |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: cash_assignment_holder
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| ca_holder_name | character varying(30) |  | None |
| rank | character varying(15) |  | None |
| specimen_signature | text |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| ca_holder_desg | character varying(50) |  | None |
| fk_treasury_bank | integer | FK | bank |
| ca_account_number | character varying(10) |  | None |
| fk_treasury_central_bank | bigint | FK | aaa_central_bank |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: cash_book_summary
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_vrhead_desc | bigint | FK | vrhead_desc |
| fk_dak | bigint | FK | dak |
| from_vrno | character varying(100) |  | None |
| to_vrno | character varying(100) |  | None |
| dr_amount | numeric(18,2) |  | None |
| cr_amount | numeric(18,2) |  | None |
| fk_section | bigint | FK | section |
| fk_office_id | bigint | FK | dad_office |
| trans_table | character varying(50) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| from_date | date |  | None |
| to_date | date |  | None |
| sign_rc | character varying(2) |  | None |
| code_head | character varying(20) |  | None |
| exclude_pm | boolean |  | None |

## Table: cash_requisition
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_section | integer | FK | section |
| fk_imprest | integer | FK | imprest |
| fk_unit | integer | FK | unit |
| fk_dak | bigint | FK | dak |
| imprest_no | character varying(15) |  | None |
| cr_no | character varying(15) |  | None |
| cr_date | date |  | None |
| amount | double precision |  | None |
| cash_in_hand | double precision |  | None |
| cash_in_bank | double precision |  | None |
| amount_passed | double precision |  | None |
| expenditure_statment_submitted | boolean |  | None |
| missing | boolean |  | None |
| cancelled | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| provisional_payment | boolean |  | None |
| verified_audit_checks | boolean |  | None |
| fk_code_head | integer | FK | code_head |
| code_hd | character varying(9) |  | None |
| fk_go | integer | FK | usr |
| fk_jcda | integer | FK | usr |
| fk_cda | integer | FK | usr |
| go_date | date |  | None |
| jcda_date | date |  | None |
| cda_date | date |  | None |
| month | character varying(7) |  | None |
| cml_exemption | integer |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: ch_booking
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_code_head | integer | FK | code_head |
| amount | double precision |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_bill | bigint | FK | bill |
| lch_updated | boolean |  | None |
| code_hd | character varying(9) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| sgst_pm_amount | double precision |  | None |
| utgst_pm_amount | double precision |  | None |
| cgst_pm_amount | double precision |  | None |
| igst_pm_amount | double precision |  | None |
| igst_import_pm_amount | double precision |  | None |
| code_head_pm_amount | double precision |  | None |
| exp_cda | double precision |  | None |
| exp_all | double precision |  | None |
| exp_sub_head | double precision |  | None |
| exp_minor_head | double precision |  | None |
| be_cd | double precision |  | None |
| re_cd | double precision |  | None |
| sub_head | character varying(15) |  | None |
| be_sub_head | double precision |  | None |
| re_sub_head | double precision |  | None |
| be_minor_head | double precision |  | None |
| re_minor_head | double precision |  | None |
| minor_head | character varying(15) |  | None |
| api_query_at | timestamp with time zone |  | None |
| budget_remarks | character varying(100) |  | None |
| parent_code_head | character varying(9) |  | None |
| cch | character(1) |  | None |
| unit_allotment | double precision |  | None |
| uuid | character varying(14) |  | None |
| budget_code_head | character varying(5) |  | None |
| response_code | numeric |  | None |

## Table: cheque_slip
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_treasury_bank | integer | FK | bank |
| fk_favour_bank | integer | FK | bank |
| payment_detail | text |  | None |
| account_no | character varying(18) |  | None |
| amount | double precision |  | None |
| npb_date | date |  | None |
| dv_no | integer |  | None |
| cheque_slip_date | date |  | None |
| dp_sheet_no | integer |  | None |
| schedule3_item_no | integer |  | None |
| fk_unit | integer | FK | unit |
| fk_schedule3 | integer | FK | schedule3 |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| selected | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| record_status | character(1) |  | None |
| email_date | timestamp without time zone |  | None |
| email_sent | boolean |  | None |
| ind_npb_date | date |  | None |
| fk_vendor | integer | FK | vendor |
| fk_consolidated_dak | bigint | FK | dak |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_treasury_bank | integer | FK | aaa_central_bank |
| fk_central_favour_bank | integer | FK | aaa_central_bank |

## Table: cht_item_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_bill | bigint | FK | bill |
| fk_contract_agreement | bigint | FK | contract_agreement |
| designation | character varying(15) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| vehicle_no | character varying(10) |  | None |
| vehicle_type | character varying(10) |  | None |
| rate | double precision |  | None |
| hours_deployed | double precision |  | None |
| amount | double precision |  | None |
| purpose | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |

## Table: civ_cea_claims
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_civ_employee_family_detail | bigint | FK | civ_employee_family_detail |
| class_name | character varying(7) |  | None |
| claim_month | character varying(7) |  | None |
| session_start_month_year | character varying(7) |  | None |
| session_end_month_year | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| dob | date |  | None |
| claim_quarter | character varying(2) |  | None |
| child_type | character varying(7) |  | None |
| gender | character varying(6) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| fk_dak | bigint | FK | dak |
| passed | boolean |  | None |
| claim_type | character varying(6) |  | None |
| fk_office_id | integer | FK | dad_office |
| transfered_to_ecs | boolean |  | None |
| relation | character varying(16) |  | None |
| fk_task_usr | integer |  | None |
| fk_unit | integer |  | None |
| income_tax | integer |  | None |
| edcess | integer |  | None |
| sec_cess | integer |  | None |
| disallow_amount | integer |  | None |
| disallow_reason | character varying(100) |  | None |
| student_name | character varying(50) |  | None |
| dak_no | character varying(18) |  | None |
| eh_cess | integer |  | None |
| pay_type | character varying(15) |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| sanction_no | character varying(100) |  | None |
| sanction_date | date |  | None |

## Table: civ_da_bonus
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dak | bigint | FK | dak |
| fk_unit | integer |  | None |
| bill_type | character varying(20) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| claim_month | character varying(7) |  | None |
| claim_amount | double precision |  | None |
| passed_amount | double precision |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| dak_no | character varying(18) |  | None |
| unit_code | character varying(10) |  | None |
| due_bp1 | integer |  | None |
| due_gp1 | integer |  | None |
| due_da1 | integer |  | None |
| due_tpt1 | integer |  | None |
| due_bp2 | integer |  | None |
| due_gp2 | integer |  | None |
| due_da2 | integer |  | None |
| due_tpt2 | integer |  | None |
| due_bp3 | integer |  | None |
| due_gp3 | integer |  | None |
| due_da3 | integer |  | None |
| due_tpt3 | integer |  | None |
| due_bp4 | integer |  | None |
| due_gp4 | integer |  | None |
| due_da4 | integer |  | None |
| due_tpt4 | integer |  | None |
| due_total_pay | integer |  | None |
| drawn_bp1 | integer |  | None |
| drawn_gp1 | integer |  | None |
| drawn_da1 | integer |  | None |
| drawn_tpt1 | integer |  | None |
| drawn_bp2 | integer |  | None |
| drawn_gp2 | integer |  | None |
| drawn_da2 | integer |  | None |
| drawn_tpt2 | integer |  | None |
| drawn_bp3 | integer |  | None |
| drawn_gp3 | integer |  | None |
| drawn_da3 | integer |  | None |
| drawn_tpt3 | integer |  | None |
| drawn_bp4 | integer |  | None |
| drawn_gp4 | integer |  | None |
| drawn_da4 | integer |  | None |
| drawn_tpt4 | integer |  | None |
| drawn_total_pay | integer |  | None |
| diff_amount | integer |  | None |
| diff_total | integer |  | None |
| nps_arr_rec | integer |  | None |
| disallow_amount | integer |  | None |
| net_amount | integer |  | None |
| remarks | text |  | None |
| misc_arr | integer |  | None |
| eol_rec | integer |  | None |
| hpl_rec | integer |  | None |
| misc_rec | integer |  | None |
| total_rec | integer |  | None |
| ceiling_amt | integer |  | None |
| adhoc_bonus | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| passed | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_civ_paybill | integer | FK | civ_paybill |
| month_one | character varying(7) |  | None |
| month_two | character varying(7) |  | None |
| month_three | character varying(7) |  | None |
| pay_diff_one | integer |  | None |
| pay_diff_two | integer |  | None |
| pay_diff_three | integer |  | None |
| pay_arr_one | integer |  | None |
| pay_arr_two | integer |  | None |
| pay_arr_three | integer |  | None |
| pay_rec_one | integer |  | None |
| pay_rec_two | integer |  | None |
| pay_rec_three | integer |  | None |
| nps_one | integer |  | None |
| nps_two | integer |  | None |
| nps_three | integer |  | None |
| nps_govt_one | integer |  | None |
| nps_govt_two | integer |  | None |
| nps_govt_three | integer |  | None |
| tpta_one | integer |  | None |
| tpta_two | integer |  | None |
| tpta_three | integer |  | None |
| tpta_diff_one | integer |  | None |
| tpta_diff_two | integer |  | None |
| tpta_diff_three | integer |  | None |
| tpta_rec_one | integer |  | None |
| tpta_rec_two | integer |  | None |
| tpta_rec_three | integer |  | None |
| tpta_arr_one | integer |  | None |
| tpta_arr_two | integer |  | None |
| tpta_arr_three | integer |  | None |
| fk_bank_pan_detail | integer | FK | bank_pan_detail |
| pay_type | character varying(15) |  | None |
| itax | integer |  | None |
| ehcess | integer |  | None |
| dad_nondad | character varying(15) |  | None |
| nps_type | character varying(20) |  | None |
| da_type | character varying(15) |  | None |
| cgeis_rec | integer |  | None |
| cghs_rec | integer |  | None |
| cghs_type | character varying(10) |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: civ_demand_register
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| demand_month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| settled | boolean |  | None |
| fk_civ_paybill | bigint | FK | civ_paybill |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| cdr_no | character varying(12) |  | None |
| fk_omro | integer | FK | omro |
| recovery_mode | character(1) |  | None |
| recovery_memo_details | text |  | None |
| dv_te_no | integer |  | None |
| settlement_month | character varying(7) |  | None |
| demand_date | date |  | None |
| settlement_date | date |  | None |
| demand_approved | boolean |  | None |
| settlement_approved | boolean |  | None |
| fk_auditor_demand | integer | FK | usr |
| fk_aao_demand | integer | FK | usr |
| fk_ao_demand | integer | FK | usr |
| auditor_demand_date | date |  | None |
| aao_demand_date | date |  | None |
| ao_demand_date | date |  | None |
| fk_auditor_settlement | integer | FK | usr |
| fk_aao_settlement | integer | FK | usr |
| fk_ao_settlement | integer | FK | usr |
| auditor_settlement_date | date |  | None |
| aao_settlement_date | date |  | None |
| ao_settlement_date | date |  | None |
| reason | text |  | None |
| recovery_memo_letter_no | character varying(50) |  | None |
| recovery_memo_letter_date | date |  | None |
| fk_settlement_dak | bigint | FK | dak |
| fk_civ_tada_ltc_bill | integer | FK | civ_tada_ltc_bill |
| journey_station | character varying(30) |  | None |
| journey_date | date |  | None |
| settlement_remarks | text |  | None |
| transcription_type | character(1) |  | None |
| demand_code_head | character varying(9) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| item_no | integer |  | None |

## Table: civ_designation
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| designation_abbr | character varying(15) |  | None |
| designation_name | character varying(50) |  | None |
| industrial | boolean |  | None |
| employee_group | character(1) |  | None |
| grade | character varying(15) |  | None |
| cgeis_group | character(1) |  | None |
| fk_merge_desg | integer | FK | civ_designation |
| six_cpc_fitment | character varying(4) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: civ_emp_allowances
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_pay_code | integer |  | None |
| description | character varying(255) |  | None |
| from_date | timestamp without time zone |  | None |
| to_date | timestamp without time zone |  | None |
| created_date | timestamp without time zone |  | None |
| current_record | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_auditor | integer | FK | usr |
| auditor_date | timestamp without time zone |  | None |
| fk_aao | integer | FK | usr |
| aao_date | timestamp without time zone |  | None |
| fk_ao | integer | FK | usr |
| ao_date | timestamp without time zone |  | None |
| record_status | character varying(1) |  | None |
| approved | boolean |  | None |
| amount | double precision |  | None |
| percentage | double precision |  | None |
| code_head | character varying(9) |  | None |
| is_one_time | boolean |  | None |
| fk_civ_paybill | integer | FK | civ_paybill |

## Table: civ_employee
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| month | character varying(7) |  | None |
| employee_name | character varying(50) |  | None |
| gender | character(1) |  | None |
| category | character varying(3) |  | None |
| fk_present_unit | integer | FK | unit |
| present_unit_date | date |  | None |
| fk_status_code | integer | FK | status_code |
| status_effect_date | date |  | None |
| fk_present_desg | integer | FK | civ_designation |
| present_desg_date | date |  | None |
| date_of_birth | date |  | None |
| appointment_date | date |  | None |
| increment_date | date |  | None |
| superannuation_date | date |  | None |
| fk_fpa_desg | integer | FK | civ_designation |
| fpa_date | date |  | None |
| gazette | boolean |  | None |
| ph_status | boolean |  | None |
| married | boolean |  | None |
| mobile_number | character varying(12) |  | None |
| home_town | character varying(25) |  | None |
| ltc_encashment_days | integer |  | None |
| recovery_stop_date | date |  | None |
| fund_type | character(1) |  | None |
| cgeis | character(1) |  | None |
| cghs | boolean |  | None |
| cash_allowance | character(1) |  | None |
| deputation | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| current_record | boolean |  | None |
| old_id | bigint |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| employee_type | character(1) |  | None |
| staff_type | character varying(10) |  | None |
| personal_number | character varying(16) |  | None |
| paybill_tada_medical | character varying(2) |  | None |
| hra | boolean |  | None |
| prof_tax | boolean |  | None |
| hod_no_staff_car | boolean |  | None |
| hra_class | character(1) |  | None |
| tpta_class | character varying(2) |  | None |
| spl_increment | boolean |  | None |
| hag | boolean |  | None |
| pay_level | character varying(2) |  | None |
| pan_number | character varying(10) |  | None |
| aadhar_no | character varying(12) |  | None |
| special_case | character varying(20) |  | None |
| remarks | text |  | None |
| email | character varying(50) |  | None |
| aft | boolean |  | None |
| old_pran_no | character varying(16) |  | None |
| fk_present_central_unit | bigint | FK | aaa_central_unit |

## Table: civ_employee_adjustment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| code_head | character varying(9) |  | None |

## Table: civ_employee_allowance_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_employee_pay_detail | bigint | FK | civ_employee_pay_detail |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_employee_arrears
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_civ_part_two_order | integer | FK | civ_part_two_order |
| fk_pay_code | integer | FK | pay_code |
| month | character varying(7) |  | None |
| due_amount | integer |  | None |
| drawn_amount | integer |  | None |
| arrear_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| code_head | character varying(9) |  | None |
| record_status | character varying(1) |  | None |
| approved | boolean |  | None |
| reason | character varying(255) |  | None |

## Table: civ_employee_earning
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| from_date | timestamp without time zone |  | None |
| to_date | timestamp without time zone |  | None |
| record_status | character varying(1) |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| code_head | character varying(9) |  | None |

## Table: civ_employee_family_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| name_of_member | character varying(50) |  | None |
| date_of_birth | date |  | None |
| fk_relation | integer | FK | relation |
| gender | character(1) |  | None |
| govt_employee | boolean |  | None |
| dependant | boolean |  | None |
| dependancy_status | character varying(10) |  | None |
| adopted | boolean |  | None |
| gpf_nomination | boolean |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| gpf_pran_ppan_no | character varying(16) |  | None |
| pension_nomination | boolean |  | None |
| cgeis_nomination | boolean |  | None |
| gpf_share | integer |  | None |
| pension_share | integer |  | None |
| cgeis_share | integer |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_employee_pay_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| basic_pay | integer |  | None |
| grade_pay | integer |  | None |
| dp | integer |  | None |
| da | integer |  | None |
| tpta | integer |  | None |
| effective | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| absent | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_employee_pay_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| fk_civ_paybill | bigint | FK | civ_paybill |
| paybill_type | character(1) |  | None |
| staff_type | character varying(2) |  | None |
| pay_month | character varying(7) |  | None |
| basic_pay | integer |  | None |
| grade_pay | integer |  | None |
| da | integer |  | None |
| hra | integer |  | None |
| tpta | integer |  | None |
| tpta_da | integer |  | None |
| fpa | integer |  | None |
| spl_allowance | integer |  | None |
| washing_allow | integer |  | None |
| hindi_allow | integer |  | None |
| gross_pay | integer |  | None |
| gpf_sub | integer |  | None |
| gpf_refund | integer |  | None |
| nps_sub | integer |  | None |
| nps_govt_contrib | integer |  | None |
| cgeis | integer |  | None |
| cghs | integer |  | None |
| rent | integer |  | None |
| prof_tax | integer |  | None |
| loans_advances | integer |  | None |
| lic | integer |  | None |
| pli | integer |  | None |
| it_rec | integer |  | None |
| edcess | integer |  | None |
| pay_recovery | integer |  | None |
| total_recovery | integer |  | None |
| net_amount | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| unit_code | character varying(10) |  | None |
| closed | boolean |  | None |
| auditor_submit | boolean |  | None |
| aao_approve | boolean |  | None |
| approved | boolean |  | None |
| fk_loan_code | integer |  | None |
| loan_hba | integer |  | None |
| loan_hba_int | integer |  | None |
| loan_scooter | integer |  | None |
| loan_scooter_int | integer |  | None |
| loan_pc | integer |  | None |
| loan_pc_int | integer |  | None |
| loan_car | integer |  | None |
| loan_car_int | integer |  | None |
| loan_festival | integer |  | None |
| loan_flood | integer |  | None |
| loan_bicycle | integer |  | None |
| loan_bicycle_int | integer |  | None |
| absent | boolean |  | None |
| furniture | integer |  | None |
| water | integer |  | None |
| electricity | integer |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| fk_office_id | integer | FK | dad_office |
| secondary_cess | integer |  | None |
| surcharge | integer |  | None |
| dak_no | character varying(18) |  | None |
| pay_arrears | integer |  | None |
| disallow_amount | integer |  | None |
| pay_arrear_disallow_reason | text |  | None |
| fk_dak | integer | FK | dak |
| medical_rec | integer |  | None |
| ltc_rec | integer |  | None |
| tada_rec | integer |  | None |
| ta_ptmove_rec | integer |  | None |
| court_attach | integer |  | None |
| misc_rec | integer |  | None |
| penal_interest | integer |  | None |
| fund_codehead | character varying(9) |  | None |
| spl_increment | integer |  | None |
| misc_arrears | integer |  | None |
| sno | integer |  | None |
| cgeis_arr_rec | integer |  | None |
| variable_increment | integer |  | None |
| special_pay | integer |  | None |
| tribal_area_allow | integer |  | None |
| spl_duty_allow | integer |  | None |
| double_hra | integer |  | None |
| remote_locality_allow | integer |  | None |
| cghs_arr_rec | integer |  | None |
| npa | integer |  | None |
| npa_da | integer |  | None |
| addl_incr | integer |  | None |
| sports_incr | integer |  | None |
| hca | integer |  | None |
| hca_da | integer |  | None |
| pm_relief | integer |  | None |
| change_reason | text |  | None |
| changed | boolean |  | None |
| new_basic | integer |  | None |
| old_new_pay | character varying(7) |  | None |
| pension_rec | integer |  | None |
| nps_type | character varying(20) |  | None |
| rent_type | character varying(15) |  | None |
| tough_area_allow | integer |  | None |
| risk_allow | integer |  | None |
| hpca | integer |  | None |
| dad_nondad | character varying(15) |  | None |
| eh_cess | integer |  | None |
| eh_cess_arr | integer |  | None |
| change_gross_net | character varying(100) |  | None |
| table_recoveries | integer |  | None |
| last_charge_dakno | character varying(16) |  | None |
| fk_bank_pan_detail | integer | FK | bank_pan_detail |
| pay_type | character varying(15) |  | None |
| ota | integer |  | None |
| cghs_type | character varying(10) |  | None |
| da_type | character varying(15) |  | None |
| nda | integer |  | None |
| nps_govt_arr | integer |  | None |
| ltc_cash_rec | integer |  | None |
| da_rate | character varying(4) |  | None |
| prof_tax_arr | integer |  | None |
| pay_nps_govt_contrib | integer |  | None |
| gpf_above_five_lakhs | character varying(3) |  | None |
| ups_sub | integer |  | None |
| ups_govt_contrib | integer |  | None |
| ups_type | character varying(20) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |

## Table: civ_employee_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| from_date | timestamp without time zone |  | None |
| to_date | timestamp without time zone |  | None |
| record_status | character varying(1) |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| code_head | character varying(9) |  | None |

## Table: civ_employee_service_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| from_date | date |  | None |
| to_date | date |  | None |
| status | character(1) |  | None |
| fk_civ_part_two_order | integer | FK | civ_part_two_order |
| fk_unit | integer | FK | unit |
| fk_civ_designation | integer | FK | civ_designation |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_fund_debit_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_fund_payment_authority | bigint | FK | civ_fund_payment_authority |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| total_instalment | integer |  | None |
| recovery_rate | integer |  | None |
| loan_amount | integer |  | None |
| balance_instalment | integer |  | None |
| balance_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | integer | FK | dak |
| gpf_pran_ppan_no | character varying(16) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_fund_payment_authority
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| authority_number | integer |  | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_fund_purpose | integer | FK | fund_purpose |
| temp_final | character(1) |  | None |
| authority_month_ending | character varying(7) |  | None |
| received_month_year | character varying(7) |  | None |
| paid_voucher_month_year | character varying(7) |  | None |
| month_ending | character varying(7) |  | None |
| instalment | integer |  | None |
| rate | double precision |  | None |
| consolidated_amount | integer |  | None |
| approval_amount | integer |  | None |
| fk_unit | integer | FK | unit |
| unit_code | character varying(14) |  | None |
| authority_status | character(1) |  | None |
| voucher_received | boolean |  | None |
| fk_dids | integer | FK | dids |
| fk_imprest | integer | FK | imprest |
| special_sanction | boolean |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| authority_date | date |  | None |
| bill_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| recovery_start_date | date |  | None |
| approved | boolean |  | None |
| transfered_to_ecs | boolean |  | None |
| batch | character varying(15) |  | None |
| discharge_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| gpf_pran_ppan_no | character varying(16) |  | None |
| fk_task_usr | integer |  | None |
| cco9_balance | integer |  | None |
| subscription | integer |  | None |
| refund | integer |  | None |
| withdrawal | integer |  | None |
| dob | date |  | None |
| doa | date |  | None |
| date_of_retirement | date |  | None |
| basic_pay | integer |  | None |
| grade_pay | integer |  | None |
| other_codehead | character varying(9) |  | None |
| pay_type | character varying(15) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: civ_fund_sub_refund
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint |  | None |
| fund_month | character varying(7) |  | None |
| gpf_no | character varying(8) |  | None |
| ref_amount | integer |  | None |
| sub_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | integer | FK | dak |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_it_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| it_recovery_amount | integer |  | None |
| cess_amount | integer |  | None |
| secondary_cess_amount | integer |  | None |
| surcharge_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | integer | FK | dak |
| eh_cess | integer |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_lf_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| rent_amount | integer |  | None |
| water_amount | integer |  | None |
| furniture_amount | integer |  | None |
| electricity_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_lic_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| recovery_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_loan_payment_authority
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_civ_loan_sanction | integer | FK | civ_loan_sanction |
| fk_imprest | integer | FK | imprest |
| fk_civ_employee | bigint | FK | civ_employee |
| authority_month_ending | character varying(7) |  | None |
| received_month_year | character varying(7) |  | None |
| paid_voucher_month_year | character varying(7) |  | None |
| month_ending | character varying(7) |  | None |
| authority_no | character varying(25) |  | None |
| authority_date | date |  | None |
| contingent_bill_no | character varying(25) |  | None |
| contingent_bill_date | date |  | None |
| approval_amount | integer |  | None |
| transfered_to_ecs | boolean |  | None |
| batch | character varying(15) |  | None |
| voucher_received | boolean |  | None |
| fk_dids | integer | FK | dids |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| authority_status | character(1) |  | None |
| fk_office_id | integer | FK | dad_office |
| instalment_number | character(1) |  | None |
| instalment_date | date |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| payment_instalments | integer |  | None |
| total_instalments | integer |  | None |
| recovery_rate | integer |  | None |
| recovery_date | date |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_amount | integer |  | None |
| sanction_date | date |  | None |
| outright_plot_construction | character(1) |  | None |
| fk_loan_code | integer | FK | loan_code |
| fk_unit | integer | FK | unit |
| dak_no | character varying(18) |  | None |
| pay_type | character varying(15) |  | None |
| instalment_amount | integer |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_loan_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| fk_civ_loan_sanction | integer | FK | civ_loan_sanction |
| recovery_month | integer |  | None |
| recovery_year | integer |  | None |
| recovery_amount | integer |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | integer | FK | dak |
| loan_code_abbr | character varying(3) |  | None |
| total_loan_amount | integer |  | None |
| total_instalments | integer |  | None |
| instalments_recovered | integer |  | None |
| balance_amount | integer |  | None |
| recovery_date | date |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_loan_sanction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| sanction_amount | integer |  | None |
| payment_instalment_count | integer |  | None |
| recovery_rate | integer |  | None |
| recovery_instalment_count | integer |  | None |
| balance_principal | integer |  | None |
| balance_interest | integer |  | None |
| fk_loan_code | integer | FK | loan_code |
| recovery_date | date |  | None |
| fk_dak | bigint | FK | dak |
| total_instalment_count | integer |  | None |
| arrears_recovery | boolean |  | None |
| sanction_unit | character varying(10) |  | None |
| progressive_amount | integer |  | None |
| fk_original_sanction | integer | FK | civ_loan_sanction |
| installment1_amount | integer |  | None |
| installment1_date | date |  | None |
| installment2_amount | integer |  | None |
| installment2_date | date |  | None |
| installment3_amount | integer |  | None |
| installment3_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| bulk_approval | boolean |  | None |
| outright_plot_construction | character(1) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_lpc
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| transaction_month | character varying(7) |  | None |
| lpc_date | date |  | None |
| lpc_month | character varying(7) |  | None |
| pay_level | character varying(3) |  | None |
| basic_pay | integer |  | None |
| da | integer |  | None |
| tpta | integer |  | None |
| hra | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| lpc_reason | character varying(25) |  | None |
| struck_off_date | date |  | None |
| paid_upto_date | date |  | None |
| unit_posted_to | character varying(200) |  | None |
| org_posted_to | character varying(200) |  | None |
| authority_no | character varying(200) |  | None |
| file_no | character varying(200) |  | None |
| accommodation | character varying(200) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_lpc_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_lpc | bigint | FK | civ_lpc |
| lpc_month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| fk_loan_code | integer | FK | loan_code |
| sanction_amount | integer |  | None |
| recovered_amount | integer |  | None |
| total_instalment | integer |  | None |
| recovered_instalment | integer |  | None |
| sanction_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| outstanding_amount | integer |  | None |
| outstanding_instalment | integer |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_medical_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| employee_category | character varying(18) |  | None |
| employee_number | character varying(16) |  | None |
| designation | character varying(15) |  | None |
| employee_name | character varying(50) |  | None |
| ip_op_number | character varying(20) |  | None |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| inpatient_outpatient | character(1) |  | None |
| claim_type | character(1) |  | None |
| fk_civ_employee_family_detail | integer | FK | civ_employee_family_detail |
| name_of_patient | character varying(50) |  | None |
| relationship | character varying(25) |  | None |
| place_fell_ill | character varying(15) |  | None |
| fk_vendor | integer | FK | vendor |
| from_period | date |  | None |
| to_period | date |  | None |
| medical_test_name | text |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| penal_interest | integer |  | None |
| amount_disallowed | integer |  | None |
| adjustment_amount | integer |  | None |
| credit_status | character(1) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| final_claim_received | boolean |  | None |
| fk_final_claim | bigint | FK | civ_medical_bill |
| credit_settled | boolean |  | None |
| posted_in_demand_register | boolean |  | None |
| fk_punching_medium | bigint | FK | punching_medium |
| created_at | timestamp without time zone |  | None |
| last_modified_date | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| passed | boolean |  | None |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| hospital_category | character varying(15) |  | None |
| hospital_sub_category | character varying(20) |  | None |
| manual_rejection | boolean |  | None |
| remarks | text |  | None |
| disallowance_details | text |  | None |
| advance_date | date |  | None |
| payment_to_whom | character varying(2) |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| processed_month | character varying(7) |  | None |
| mro_received | boolean |  | None |
| final_adjustment_settled | boolean |  | None |
| recoveries | integer |  | None |
| verified_audit_checks | boolean |  | None |
| code_hd | character varying(9) |  | None |
| batch | character varying(20) |  | None |
| transfered_to_ecs | boolean |  | None |
| audit_report_required | boolean |  | None |
| ar_sanctioned_received | boolean |  | None |
| audit_report_amount | double precision |  | None |
| audit_report_date | date |  | None |
| audit_report_approved | boolean |  | None |
| rejection_reason | text |  | None |
| cghs_card_no | character varying(10) |  | None |
| cghs_referral_date | date |  | None |
| cghs_referral_renewed | boolean |  | None |
| cghs_referral_letter_enclosed | boolean |  | None |
| dept_permission_letter_enclosed | boolean |  | None |
| day_care_treatment | boolean |  | None |
| bill_already_rejected_before | boolean |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| payment_authority_number | integer |  | None |
| payment_authority_date | date |  | None |
| pao_unit_name | character varying(50) |  | None |
| pao_unit_address1 | character varying(30) |  | None |
| pao_unit_address2 | character varying(30) |  | None |
| pao_unit_pincode | character varying(15) |  | None |
| voucher_no | character varying(15) |  | None |
| voucher_date | date |  | None |
| hospital_name | text |  | None |
| pa_ack_no | character varying(25) |  | None |
| pa_ack_date | date |  | None |
| pa_ack_received | boolean |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_allotment_detail | integer |  | None |
| project_code | character varying(14) |  | None |
| itax_amount | integer |  | None |
| he_cess | integer |  | None |
| taxable_amount | integer |  | None |
| advance_amount | integer |  | None |
| cdr_id | character varying(30) |  | None |
| mro_no | character varying(17) |  | None |
| mro_date | date |  | None |
| mro_amount | double precision |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| cmp_date | date |  | None |
| provisional_payment | boolean |  | None |
| prov_authority_number | character(25) |  | None |
| prov_authority_date | date |  | None |
| dept_permission_date | date |  | None |
| illness_details | text |  | None |
| stage | integer |  | None |
| pa_status | character(1) |  | None |
| fk_vendor_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_unit_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_emp_bank_pan_detail | bigint | FK | bank_pan_detail |
| vendor_amount | integer |  | None |
| unit_amount | integer |  | None |
| employee_amount | integer |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_vendor_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_unit_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_emp_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| cghs_referral_letter_location | character varying(256) |  | None |
| stage_completed | character varying(256) |  | None |
| dep_permission_letter_location | character varying(255) |  | None |

## Table: civ_medical_bill_treatment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_medical_bill | bigint | FK | civ_medical_bill |
| cghs_code | character varying(50) |  | None |
| procedure | character varying(500) |  | None |
| occurrence | integer |  | None |
| admitted_amount | numeric(15,2) |  | None |
| claimed_amount | numeric(15,2) |  | None |
| disallowance | numeric(15,2) |  | None |
| remarks | character varying(1000) |  | None |
| created_at | timestamp without time zone |  | None |
| category | character varying(255) |  | None |
| fk_medical_treatment_details | bigint | FK | civ_medical_treatment_details |

## Table: civ_medical_treatment_details
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_medical_bill | bigint | FK | civ_medical_bill |
| bill_type | character varying(50) |  | None |
| package_type | character varying(50) |  | None |
| hospital_type | character varying(50) |  | None |
| employee_basic_pay | double precision |  | None |
| entitled_ward | character varying(50) |  | None |
| opted_ward | character varying(50) |  | None |
| created_at | timestamp without time zone |  | None |
| total_admitted | double precision |  | None |
| total_claimed | double precision |  | None |
| total_disallowance | double precision |  | None |

## Table: civ_monthly_pay
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_paybill | bigint | FK | civ_paybill |
| employee_type | character(1) |  | None |
| month | character varying(7) |  | None |
| gross_pay | integer |  | None |
| total_debit | integer |  | None |
| net_pay | integer |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| income_tax | integer |  | None |
| lic | integer |  | None |
| pli | integer |  | None |
| nps | integer |  | None |
| gpf | integer |  | None |
| ptax | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_nps
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| ppan | character varying(16) |  | None |
| pran | character varying(12) |  | None |
| ppan_allotment_date | date |  | None |
| pran_allotment_date | date |  | None |
| nps_recovery_start_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| current_record | boolean |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_nps_adjustment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_civ_nps | bigint | FK | civ_nps |
| month | character varying(7) |  | None |
| revised_subscription | integer |  | None |
| change_type | character(1) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_nps_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| fk_civ_nps | bigint | FK | civ_nps |
| emp_contribution | integer |  | None |
| govt_contribution | integer |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| recovery_type | character(1) |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| uploaded | boolean |  | None |
| uploaded_month_ending | character varying(7) |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | integer | FK | dak |
| nps_ups | character varying(4) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_pa_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_section | integer | FK | section |
| fk_civ_pa_emp | bigint | FK | civ_pa_emp |
| fk_dak | bigint | FK | dak |
| pa_type | character(1) |  | None |
| pa_amount | integer |  | None |
| pa_number | character varying(25) |  | None |
| pa_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| ddo_type | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| remarks | text |  | None |
| reason | text |  | None |

## Table: civ_part_two_order
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| gpf_pran_no | character varying(11) |  | None |
| description | character varying(8) |  | None |
| order_no | character varying(25) |  | None |
| order_date | date |  | None |
| fk_section | integer | FK | section |
| fk_order_category | integer |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| field1 | character varying(10) |  | None |
| field2 | character varying(10) |  | None |
| field3 | character varying(10) |  | None |
| received_date | date |  | None |
| processed_date | date |  | None |
| reviewed_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| audit_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_paybill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_unit | integer | FK | unit |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| month | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| amount_disallowed | double precision |  | None |
| provisional_payment | boolean |  | None |
| verified_audit_checks | boolean |  | None |
| sysgenerated_bill_amount | double precision |  | None |
| last_charge | double precision |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| fk_jcda | integer | FK | usr |
| jcda_date | date |  | None |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| passed | boolean |  | None |
| regular_pay_bill | boolean |  | None |
| fk_punching_medium | bigint | FK | punching_medium |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| last_charge_month_year | character varying(7) |  | None |
| table_name | character varying(30) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| last_paybill_dakidno | character varying(18) |  | None |
| spb_type | character varying(15) |  | None |

## Table: civ_pli_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| month | character varying(7) |  | None |
| recovery_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_pm_cs
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| fk_civ_paybill | bigint | FK | civ_paybill |
| fk_dak | bigint | FK | dak |
| dak_no | character varying(18) |  | None |
| paybill_type | character varying(25) |  | None |
| unit_code | character varying(50) |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| pay_month | character varying(7) |  | None |
| officers_amt | integer |  | None |
| ind_amt | integer |  | None |
| nonind_amt | integer |  | None |
| mfad_amt | integer |  | None |
| mfpt_amt | integer |  | None |
| mftemp_amt | integer |  | None |
| cv_amt | integer |  | None |
| gross | integer |  | None |
| gpf_sub_refund | integer |  | None |
| nps_sub | integer |  | None |
| nps_govt_contrib | integer |  | None |
| cgeis | integer |  | None |
| cghs | integer |  | None |
| prof_tax | integer |  | None |
| loan_hba | integer |  | None |
| loan_hba_int | integer |  | None |
| loan_scooter | integer |  | None |
| loan_scooter_int | integer |  | None |
| loan_pc | integer |  | None |
| loan_pc_int | integer |  | None |
| loan_car | integer |  | None |
| loan_car_int | integer |  | None |
| loan_festival | integer |  | None |
| loan_flood | integer |  | None |
| loan_bicycle | integer |  | None |
| loan_bicycle_int | integer |  | None |
| rent | integer |  | None |
| furniture | integer |  | None |
| water | integer |  | None |
| electricity | integer |  | None |
| medical | integer |  | None |
| ltc | integer |  | None |
| tada | integer |  | None |
| court_attachment | integer |  | None |
| lic | integer |  | None |
| pli | integer |  | None |
| it_rec | integer |  | None |
| edcess | integer |  | None |
| secondary_cess | integer |  | None |
| surcharge | integer |  | None |
| disallow_amount | integer |  | None |
| net_amount | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| remarks | text |  | None |
| death_retirement | character varying(10) |  | None |
| cgeis_savings | integer |  | None |
| penal_interest | integer |  | None |
| emp_name | character varying(50) |  | None |
| ltc_officers | integer |  | None |
| ltc_nonind | integer |  | None |
| ltc_ind | integer |  | None |
| tada_td_one | integer |  | None |
| tada_pt_move | integer |  | None |
| tada_td_two | integer |  | None |
| npb_date | date |  | None |
| pm_generated | boolean |  | None |
| dad_gpf_rec | integer |  | None |
| rnd_gpf_rec | integer |  | None |
| festival_ind | integer |  | None |
| misc_nonind | integer |  | None |
| misc_ind | integer |  | None |
| ind_npb_date | date |  | None |
| misc_officers | integer |  | None |
| lic_ind | integer |  | None |
| lic_conser | integer |  | None |
| ptax_ind | integer |  | None |
| ptax_conser | integer |  | None |
| misc_conser | integer |  | None |
| festival_conser | integer |  | None |
| court_attach_off | integer |  | None |
| court_attach_ind | integer |  | None |
| court_attach_conser | integer |  | None |
| net_amount_ind | integer |  | None |
| file_number | character varying(100) |  | None |
| immediate_relief | integer |  | None |
| fk_task_usr | integer | FK | usr |
| from_date | date |  | None |
| to_date | date |  | None |
| sanction_no | character varying(100) |  | None |
| sanction_amount | integer |  | None |
| sanction_date | date |  | None |
| pcdahq_gpf_sub | integer |  | None |
| pcdarnd_gpf_sub | integer |  | None |
| meerut_gpf_sub | integer |  | None |
| rndblr_gpf_sub | integer |  | None |
| dad_loan_hba | integer |  | None |
| dad_loan_hba_int | integer |  | None |
| dad_loan_scooter | integer |  | None |
| dad_loan_scooter_int | integer |  | None |
| dad_loan_pc | integer |  | None |
| dad_loan_pc_int | integer |  | None |
| dad_loan_car | integer |  | None |
| dad_loan_car_int | integer |  | None |
| dad_nps_sub | integer |  | None |
| rnd_nps_sub | integer |  | None |
| af_nps_sub | integer |  | None |
| navy_nps_sub | integer |  | None |
| misc_receipt | integer |  | None |
| pension_rec | integer |  | None |
| gpf_navy | integer |  | None |
| dad_cghs | integer |  | None |
| dad_cgeis | integer |  | None |
| pay_type | character varying(15) |  | None |
| rent_cpwd | integer |  | None |
| water_cpwd | integer |  | None |
| elec_cpwd | integer |  | None |
| rent_fys | integer |  | None |
| water_fys | integer |  | None |
| elec_fys | integer |  | None |
| festival_others | integer |  | None |
| dad_rent | integer |  | None |
| dad_water_elec | integer |  | None |
| gpf_pcdarnd | integer |  | None |
| eh_cess | integer |  | None |
| gpf_navy_anc | integer |  | None |
| dad_nps_govt | integer |  | None |
| rnd_nps_govt | integer |  | None |
| af_nps_govt | integer |  | None |
| navy_nps_govt | integer |  | None |
| fk_specimen_signature | integer | FK | specimen_signature |
| table_rec | integer |  | None |
| gpf_nonafhq | integer |  | None |
| gpf_navalhqrs | integer |  | None |
| gpf_fysorg | integer |  | None |
| gpf_mesdgbr | integer |  | None |
| gpf_modsec | integer |  | None |
| gpf_mindepfund | integer |  | None |
| gpf_pcdahqfund | integer |  | None |
| gpf_pcdahqfd | integer |  | None |
| pcdahq_cghsnav | integer |  | None |
| nps_fys | integer |  | None |
| nps_fys_govt | integer |  | None |
| ltc_cash_off | integer |  | None |
| ltc_cash_nonind | integer |  | None |
| ltc_cash_ind | integer |  | None |
| rnd_gpf_sus | integer |  | None |
| aft_allowance | integer |  | None |
| aft_rent | integer |  | None |
| ups_sub | integer |  | None |
| ups_govt_contrib | integer |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: civ_summary
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| month | character varying(7) |  | None |
| total_earnings | double precision |  | None |
| total_deductions | double precision |  | None |
| it_recovery | double precision |  | None |
| gross_pay | double precision |  | None |
| table_recoveries | double precision |  | None |
| net_pay | double precision |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character varying(1) |  | None |
| created_at | timestamp with time zone |  | None |
| fk_civ_paybill | integer | FK | civ_paybill |
| current_month_closed | boolean |  | None |
| ifsc_code | character varying(11) |  | None |
| acno | character varying(255) |  | None |
| remarks | text |  | None |

## Table: civ_supplementary_claims
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dak | bigint | FK | dak |
| bill_type | character varying(20) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| claim_month | character varying(7) |  | None |
| claim_amount | double precision |  | None |
| passed_amount | double precision |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| passed | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| dak_no | character varying(18) |  | None |
| spb_type | character varying(15) |  | None |
| unit_code | character varying(14) |  | None |
| fk_unit | integer |  | None |
| new_basic_pay | integer |  | None |
| new_grade_pay | integer |  | None |
| new_spl_incr | integer |  | None |
| new_hra | integer |  | None |
| new_tptl | integer |  | None |
| new_da | integer |  | None |
| new_misc_arr | integer |  | None |
| new_total_pay | integer |  | None |
| old_basic_pay | integer |  | None |
| old_grade_pay | integer |  | None |
| old_spl_incr | integer |  | None |
| old_hra | integer |  | None |
| old_tptl | integer |  | None |
| old_da | integer |  | None |
| old_misc_arr | integer |  | None |
| old_total_pay | integer |  | None |
| diff_amount | integer |  | None |
| nps_arr_rec | integer |  | None |
| it_rec | integer |  | None |
| edcess | integer |  | None |
| secondary_cess | integer |  | None |
| disallow_amount | integer |  | None |
| net_amount | integer |  | None |
| remarks | text |  | None |
| earned_leave | integer |  | None |
| hpl | integer |  | None |
| total_leave | integer |  | None |
| rent | integer |  | None |
| furniture | integer |  | None |
| water | integer |  | None |
| electricity | integer |  | None |
| fpa_date | date |  | None |
| cgeis_savings | integer |  | None |
| cgeis_insurance | integer |  | None |
| cgeis_type | character varying(15) |  | None |
| ptii_no | integer |  | None |
| ptii_date | date |  | None |
| immediate_relief | integer |  | None |
| cgeis_rec | integer |  | None |
| cghs_rec | integer |  | None |
| fk_task_usr | integer | FK | usr |
| pay_type | character varying(15) |  | None |
| eh_cess | integer |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_civ_paybill | integer | FK | civ_paybill |

## Table: civ_tada_ltc_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| fk_section | integer | FK | section |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| claim_type | character(1) |  | None |
| claim_date | date |  | None |
| journey_station_from | character varying(30) |  | None |
| journey_station_to | character varying(30) |  | None |
| mode_of_journey | character varying(5) |  | None |
| block_year | character varying(9) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | integer |  | None |
| advance_amount | integer |  | None |
| amount_disallowed | integer |  | None |
| penal_interest | integer |  | None |
| adjustment_amount | integer |  | None |
| posted_in_demand_register | boolean |  | None |
| mro_received | boolean |  | None |
| final_adjustment_received | boolean |  | None |
| final_adjustment_settled | boolean |  | None |
| fk_final_adjustment | bigint | FK | civ_tada_ltc_bill |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| fk_go | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| go_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| passed | boolean |  | None |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| foreign_travel | boolean |  | None |
| recoveries | integer |  | None |
| claim_preference_type | character(1) |  | None |
| claim_at_old_rates | boolean |  | None |
| processed_month | character varying(7) |  | None |
| period_from | date |  | None |
| period_to | date |  | None |
| no_of_days | integer |  | None |
| type_of_ltc | character varying(2) |  | None |
| verified_audit_checks | boolean |  | None |
| code_hd | character varying(9) |  | None |
| provisional_payment | boolean |  | None |
| multiple_mode_of_journey | boolean |  | None |
| composite_transfer_grant | integer |  | None |
| luggage_weight | real |  | None |
| luggage_amount | integer |  | None |
| class_of_travel | character varying(15) |  | None |
| journey_start_date | date |  | None |
| journey_end_date | date |  | None |
| travelling_charges | integer |  | None |
| payment_mode | character varying(3) |  | None |
| fk_cdr | integer | FK | civ_demand_register |
| project_code | character varying(14) |  | None |
| fk_allotment_detail | integer |  | None |
| month | character varying(7) |  | None |
| payment_record_type | character(1) |  | None |
| fk_booking_unit | bigint | FK | unit |
| booking_project_code | character varying(10) |  | None |
| mro_amount | integer |  | None |
| mro_dak_id | character varying(15) |  | None |
| movement_order_no | character varying(35) |  | None |
| movement_order_date | date |  | None |
| stage | integer |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_date | date |  | None |
| dp_sheet_no | integer |  | None |
| cmp_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| pa_number | character varying(100) |  | None |
| pa_date | date |  | None |
| value1 | character varying(100) |  | None |
| employee_type | character varying(3) |  | None |
| fk_vendor | bigint | FK | vendor |
| vendor_amount | integer |  | None |
| other_amount | integer |  | None |
| multiple_code_head | boolean |  | None |
| fk_pa_dad_office | integer | FK | dad_office |
| pa_status | character(1) |  | None |
| fk_vendor_gstin | bigint | FK | vendor_gstin |
| ht_block_year | character varying(9) |  | None |
| cv_in_lieu_of_ltc | boolean |  | None |
| no_of_members | integer |  | None |
| emp_category | character varying(3) |  | None |
| round_trip_fare_per_person | integer |  | None |
| total_fare | integer |  | None |
| leave_encash_amount | integer |  | None |
| total_value | integer |  | None |
| full_cash_benefit_exp | integer |  | None |
| share_of_leave_encash | double precision |  | None |
| share_of_fare_total | double precision |  | None |
| actual_amount_spent | integer |  | None |
| amount_of_cash_benefit | integer |  | None |
| encash_advance | integer |  | None |
| fare_advance | integer |  | None |
| encash_code_head | character varying(9) |  | None |
| encash_paid | boolean |  | None |
| calendar_year | integer |  | None |
| it_recovery_amount | integer |  | None |
| it_eh_cess_amount | integer |  | None |
| encash_share_amount | integer |  | None |
| fare_share_amount | integer |  | None |
| spl_ltc_paid_dakid | character varying(18) |  | None |
| spl_ltc_encash_paid | integer |  | None |
| spl_ltc_fare_paid | integer |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_booking_unit | integer | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| stage_completed | character varying(256) |  | None |
| fk_booking_central_unit | bigint | FK | aaa_central_unit |
| sanction_details | text |  | None |

## Table: civ_tada_ltc_bill_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_civ_tada_ltc_bill | bigint | FK | civ_tada_ltc_bill |
| mode_of_journey | character varying(5) |  | None |
| onward_journey_start_date | date |  | None |
| onward_journey_start_time | character varying(5) |  | None |
| onward_journey_end_date | date |  | None |
| onward_journey_end_time | character varying(5) |  | None |
| return_journey_start_date | date |  | None |
| return_journey_start_time | character varying(5) |  | None |
| return_journey_end_date | date |  | None |
| return_journey_end_time | character varying(5) |  | None |
| journey_order | integer |  | None |
| no_of_journey_da | double precision |  | None |
| journey_da_amount | integer |  | None |
| no_of_stay_da | double precision |  | None |
| stay_da_amount | integer |  | None |
| food_charges | integer |  | None |
| lodging_charges | integer |  | None |
| rma_rate | real |  | None |
| rma_distance | real |  | None |
| rma_amount | integer |  | None |
| no_of_dependants | integer |  | None |
| distance_between_station | integer |  | None |
| composite_transfer_grant | integer |  | None |
| luggage_weight | real |  | None |
| luggage_amount | integer |  | None |
| type_of_vehicle | character varying(15) |  | None |
| fk_usr | integer | FK | usr |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| station_from | character varying(30) |  | None |
| station_to | character varying(30) |  | None |
| travelling_charges | integer |  | None |
| class_of_travel | character varying(15) |  | None |
| fk_family_detail | integer | FK | civ_employee_family_detail |
| block_year | character varying(9) |  | None |
| calendar_year | character varying(9) |  | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| relation_name | character varying(15) |  | None |
| ltc_type | character varying(2) |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: cml
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_imprest | integer | FK | imprest |
| cml_amount | double precision |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| letter_no | character varying(25) |  | None |
| letter_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: cmp_scroll
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| cda_code | character varying(6) |  | None |
| cda_name | character varying(25) |  | None |
| sub_office_code | character varying(6) |  | None |
| sub_office_name | character varying(25) |  | None |
| beneficiary_name | character varying(40) |  | None |
| account_no | character varying(100) |  | None |
| ifsc_code | character varying(11) |  | None |
| micr_code | character varying(9) |  | None |
| account_type | character varying(2) |  | None |
| amount | double precision |  | None |
| payment_reference_no | character varying(12) |  | None |
| npb_date | date |  | None |
| vendor_code | character varying(4) |  | None |
| vendor_address | character varying(50) |  | None |
| bill_no | character varying(25) |  | None |
| dak_no | character varying(20) |  | None |
| bill_date | date |  | None |
| narration | character varying(100) |  | None |
| email | character varying(50) |  | None |
| cell_no | character varying(12) |  | None |
| addl_field | character varying(25) |  | None |
| payment_status | character varying(2) |  | None |
| payment_mode | character varying(4) |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| cmp_reference_no | character varying(25) |  | None |
| scroll_no | character varying(4) |  | None |
| scroll_date | date |  | None |
| cmp_remarks | character varying(50) |  | None |
| cmp_month | character varying(7) |  | None |
| cmp_linked | boolean |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| fk_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| usr_date | date |  | None |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_ecs | integer | FK | ecs |
| fk_ecs_sub_office | integer | FK | ecs_sub_office |
| fk_gem_bill | integer | FK | gem_bill |
| bank_scroll_file_no | character varying(100) |  | None |
| linked_date | timestamp without time zone |  | None |

## Table: code_head
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_section | integer | FK | section |
| fk_unit_category | integer | FK | unit_category |
| code_head_type | character varying(3) |  | None |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| major_head | character varying(4) |  | None |
| sub_major_head | character varying(2) |  | None |
| minor_head | character varying(3) |  | None |
| sub_head | character varying(3) |  | None |
| category_head | character varying(2) |  | None |
| detail_head | character varying(5) |  | None |
| code_head | character varying(9) |  | None |
| receipt_charge | character varying(2) |  | None |
| description | character varying(200) |  | None |
| record_status | character(1) |  | None |
| sub_type | character varying(2) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| remarks | text |  | None |
| fk_dak_type | integer | FK | dak_type |
| fk_unit | integer | FK | unit |
| fk_office_id | integer | FK | dad_office |
| lch | boolean |  | None |
| sector | character(1) |  | None |
| sub_sector | character varying(3) |  | None |
| specific_to_unit | boolean |  | None |
| dad_pm_group | character varying(4) |  | None |
| non_dad_pm_group | character varying(4) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| project_code | character varying(14) |  | None |
| reason | text |  | None |
| nature | character varying(10) |  | None |
| fk_budget_head | integer | FK | budget_head |
| type_of_bill | character varying(25) |  | None |
| sub_type_of_bill | character varying(25) |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: consignment_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| transaction_id | character varying(100) |  | None |
| consignee_fname | character varying(200) |  | None |
| consignee_lastname | character varying(200) |  | None |
| consignee_state | character varying(50) |  | None |
| consignee_district | character varying(50) |  | None |
| consignee_pin | character varying(6) |  | None |
| consignee_address | character varying(200) |  | None |
| consignee_mobile | character varying(15) |  | None |
| fk_gem_bill | bigint | FK | gem_bill |

## Table: contingency_claims
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| fk_bill_type | integer | FK | bill_type |
| code_head | character varying(9) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| amount | double precision |  | None |
| fk_vendor | integer | FK | vendor |
| month_ending | character varying(7) |  | None |
| fk_bpd | bigint | FK | bank_pan_detail |
| fin_year | character varying(9) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| value1 | character varying(50) |  | None |
| value2 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| int_number2 | integer |  | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: contract_agreement
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_cfa | integer | FK | cfa |
| ca_no | character varying(100) |  | None |
| ca_date | date |  | None |
| ca_details | text |  | None |
| fk_contract_type | integer | FK | contract_type |
| from_date | date |  | None |
| to_date | date |  | None |
| amount | double precision |  | None |
| closed | boolean |  | None |
| ammended | boolean |  | None |
| sub_contract | boolean |  | None |
| fk_original_contract_agreement | bigint | FK | contract_agreement |
| progressive_amount_claimed | double precision |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| fk_task_usr | integer | FK | usr |
| fk_section | integer | FK | section |
| approved | boolean |  | None |
| enclosure_to_bill | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| sanction_date | date |  | None |
| sd_waived | boolean |  | None |
| estimated_cost | double precision |  | None |
| admin_approval_amount | double precision |  | None |
| tech_sanction_amount | double precision |  | None |
| received_date | date |  | None |
| deviation_order_no | character varying(25) |  | None |
| deviation_order_date | date |  | None |
| amendment_no | character varying(25) |  | None |
| amendment_date | date |  | None |
| last_review_fk_auditor | integer | FK | usr |
| last_review_fk_aao | integer | FK | usr |
| last_review_fk_ao | integer | FK | usr |
| last_review_auditor_date | date |  | None |
| last_review_aao_date | date |  | None |
| last_review_ao_date | date |  | None |
| last_review_approved | boolean |  | None |
| code_head1 | character varying(9) |  | None |
| code_head2 | character varying(9) |  | None |
| code_head3 | character varying(9) |  | None |
| old_ca_number | character varying(20) |  | None |
| paid_outside_tulip | double precision |  | None |
| fk_vendor_bpd | bigint | FK | bank_pan_detail |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |

## Table: cr_book_issue
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_section | integer | FK | section |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_imprest | integer | FK | imprest |
| fk_cr_book | integer | FK | cr_book |
| issue_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: crv
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| crv_no | character varying(50) |  | None |
| crv_date | date |  | None |
| fk_dak | integer | FK | dak |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| invoice_no | character varying(30) |  | None |
| invoice_date | date |  | None |
| qty_accepted | integer |  | None |
| delivery_date | date |  | None |

## Table: crv_schedule
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_bill | bigint | FK | bill |
| month | character varying(7) |  | None |
| forwarding_letter_no | character varying(50) |  | None |
| forwarding_letter_date | date |  | None |
| fk_lao | integer | FK | dad_office |
| acknowledged_by_lao | boolean |  | None |
| acknowledgement_letter_no | character varying(50) |  | None |
| acknowledgement_letter_date | date |  | None |
| remarks | text |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| crv_date | date |  | None |
| crv_amount | double precision |  | None |
| crv_no | character varying(25) |  | None |

## Table: customs_duty_payment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| month_year | character varying(7) |  | None |
| code_head | character varying(9) |  | None |
| tr6_challan_no | character varying(25) |  | None |
| tr6_challan_date | date |  | None |
| amount_claimed | double precision |  | None |
| amount_disallowed | double precision |  | None |
| amount_passed | double precision |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| service_command | character varying(10) |  | None |
| sanctioning_authority_name | character varying(50) |  | None |
| sanctioning_authority_rank | character varying(25) |  | None |
| sanctioning_unit_name | character varying(50) |  | None |
| sanctioning_unit_code | character varying(10) |  | None |
| payment_description | text |  | None |
| payment_mode | character varying(8) |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_vendor | integer | FK | vendor |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| port_type | character varying(10) |  | None |
| port_name | character varying(100) |  | None |
| cb_no | character varying(50) |  | None |
| cb_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| provisional_payment | boolean |  | None |
| payment_to | character(1) |  | None |
| gst_applicable | character(1) |  | None |
| igst_import_rate | double precision |  | None |
| igst_import | double precision |  | None |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_unit | integer | FK | aaa_central_unit |
| icegate_ref_no | character varying(50) |  | None |

## Table: dad_bulk_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| transaction_month | character varying(7) |  | None |
| fk_dak | bigint | FK | dak |
| fk_bill_type | integer | FK | bill_type |
| code_hd | character varying(9) |  | None |
| transaction_code | character varying(2) |  | None |
| amount | integer |  | None |
| it_amount | integer |  | None |
| cess_amount | integer |  | None |
| sec_cess_amount | integer |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| reason | text |  | None |
| fk_office_id | integer | FK | dad_office |
| from_date | date |  | None |
| to_date | date |  | None |
| eh_cess | integer |  | None |

## Table: dad_cea_claims
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_paybill | bigint | FK | dad_paybill |
| fk_dad_employee_family_detail | bigint | FK | dad_employee_family_detail |
| class_name | character varying(7) |  | None |
| claim_month | character varying(7) |  | None |
| session_start_month_year | character varying(6) |  | None |
| session_end_month_year | character varying(6) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | bigint | FK | dak |
| amount_disallowed | integer |  | None |
| approved | boolean |  | None |
| verified_audit_checks | boolean |  | None |
| claim_period_from | date |  | None |
| claim_period_to | date |  | None |
| fk_bill_type | integer | FK | bill_type |
| paid_month | character varying(7) |  | None |
| dv_no | integer |  | None |
| payment_mode | character varying(3) |  | None |
| recoveries | integer |  | None |
| fk_task_usr | integer | FK | usr |
| payment_type | character(1) |  | None |
| fk_public_fund_office | integer | FK | dad_office |

## Table: dad_cea_claims_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_cea_claims | integer | FK | dad_cea_claims |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_employee_family_detail | bigint | FK | dad_employee_family_detail |
| class_name | character varying(7) |  | None |
| detention_no | integer |  | None |
| session_start_month_year | character varying(6) |  | None |
| session_end_month_year | character varying(6) |  | None |
| claim_period_from | date |  | None |
| claim_period_upto | date |  | None |
| amount_claimed | integer |  | None |
| amount_passed | integer |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| claim_type | character varying(6) |  | None |
| amount_disallowed | integer |  | None |
| fk_dak | bigint | FK | dak |
| cea_amount_passed | integer |  | None |
| hossub_amount_passed | integer |  | None |

## Table: dad_complaint_cases
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| complainant | character varying(50) |  | None |
| complaint_source | character varying(25) |  | None |
| whether_departmental_complainant | boolean |  | None |
| fk_dad_employee | bigint | FK | dad_employee |
| case_file_no | text |  | None |
| subject | text |  | None |
| complaint_involvment | character varying(10) |  | None |
| fk_dad_employee_complaint_against | bigint | FK | dad_employee |
| receipt_date | date |  | None |
| type_of_complaint | character varying(10) |  | None |
| case_status | text |  | None |
| investigation_required | boolean |  | None |
| investigating_agency | character varying(50) |  | None |
| ministry_reference_no | character varying(50) |  | None |
| ministry_reference_date | date |  | None |
| cvc_reference_no | character varying(50) |  | None |
| cvc_reference_date | date |  | None |
| whether_disciplinary_case_formed | boolean |  | None |
| action_taken | text |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| approved | boolean |  | None |
| fk_usr_level1 | integer | FK | usr |
| fk_usr_level2 | integer | FK | usr |
| fk_usr_submitted_by | integer | FK | usr |
| fk_usr_approved_by | integer | FK | usr |
| fk_usr | integer | FK | usr |
| level1_usr_date | date |  | None |
| level2_usr_date | date |  | None |
| submitted_by_usr_date | date |  | None |
| approved_by_usr_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: dad_contingency_bills
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_dad_office | integer | FK | dad_office |
| fk_bill_type | integer | FK | bill_type |
| fk_contract_agreement | bigint | FK | contract_agreement |
| fk_supply_order | bigint | FK | supply_order |
| expenditure_month | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| fk_vendor | integer | FK | vendor |
| payment_type | character(1) |  | None |
| payment_mode | character varying(3) |  | None |
| amount_passed | double precision |  | None |
| amount_disallowed | double precision |  | None |
| recoveries | double precision |  | None |
| fk_code_head | integer | FK | code_head |
| code_head_str | character varying(9) |  | None |
| verified_audit_checks | boolean |  | None |
| record_status | character(1) |  | None |
| fk_task_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_fund_debit_office | integer | FK | dad_office |
| trans_type | character varying(2) |  | None |
| multiple_trans | boolean |  | None |
| fk_public_fund_office | integer | FK | dad_office |
| fk_dad_employee | integer | FK | dad_employee |
| stage | integer |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| cmp_date | date |  | None |
| gst_type | character(1) |  | None |
| gst5_amount | double precision |  | None |
| gst12_amount | double precision |  | None |
| gst18_amount | double precision |  | None |
| gst28_amount | double precision |  | None |
| gem_contract_no | character varying(50) |  | None |
| gem_contract_date | date |  | None |
| gem_crac_no | character varying(50) |  | None |
| gem_crac_date | date |  | None |
| gem_invoice_no | character varying(50) |  | None |
| gem_invoice_date | date |  | None |
| gem_prc_no | character varying(50) |  | None |
| gem_prc_date | date |  | None |
| nature | character varying(50) |  | None |
| sgst_pm_amount | double precision |  | None |
| utgst_pm_amount | double precision |  | None |
| cgst_pm_amount | double precision |  | None |
| igst_pm_amount | double precision |  | None |
| igst_import_pm_amount | double precision |  | None |
| code_head_pm_amount | double precision |  | None |
| make_type | character(1) |  | None |
| msme | character(1) |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: dad_court_attachment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| judgement_no | character varying(50) |  | None |
| judgement_date | date |  | None |
| court_details | text |  | None |
| brief_judgement | text |  | None |
| attachment_amount | integer |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| beneficiary_name | character varying(100) |  | None |
| gender | character(1) |  | None |
| beneficiary_age | integer |  | None |
| fk_relation | integer | FK | relation |
| payment_mode | character varying(6) |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| beneficiary_phone_no | character varying(12) |  | None |
| beneficiary_email | character varying(100) |  | None |
| beneficiary_address | text |  | None |
| created_at | timestamp without time zone |  | None |
| remarks | text |  | None |
| month_ending | character varying(7) |  | None |
| fk_office_id | integer | FK | dad_office |
| recovery_type | character(1) |  | None |
| nature | character(1) |  | None |
| fk_beneficiary | integer | FK | vendor |
| reason | text |  | None |
| fk_office_public_fund | integer | FK | bank_pan_detail |
| fk_central_vendor_beneficiary | integer | FK | aaa_central_vendor |

## Table: dad_demand_register
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_office | integer | FK | dad_office |
| demand_month | character varying(7) |  | None |
| fk_pay_code | integer | FK | pay_code |
| amount | integer |  | None |
| settled | boolean |  | None |
| fk_dad_paybill | bigint | FK | dad_paybill |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| cdr_no | character varying(12) |  | None |
| fk_omro | integer | FK | omro |
| recovery_mode | character(1) |  | None |
| recovery_memo_details | text |  | None |
| dv_te_no | integer |  | None |
| settlement_month | character varying(7) |  | None |
| demand_date | date |  | None |
| settlement_date | date |  | None |
| demand_approved | boolean |  | None |
| settlement_approved | boolean |  | None |
| fk_auditor_demand | integer | FK | usr |
| fk_aao_demand | integer | FK | usr |
| fk_ao_demand | integer | FK | usr |
| auditor_demand_date | date |  | None |
| aao_demand_date | date |  | None |
| ao_demand_date | date |  | None |
| fk_auditor_settlement | integer | FK | usr |
| fk_aao_settlement | integer | FK | usr |
| fk_ao_settlement | integer | FK | usr |
| auditor_settlement_date | date |  | None |
| aao_settlement_date | date |  | None |
| ao_settlement_date | date |  | None |
| reason | text |  | None |
| demand_origin | character varying(3) |  | None |
| advance_type | character varying(6) |  | None |
| authority_no | character varying(100) |  | None |
| authority_date | date |  | None |
| fk_settlement_dak | bigint | FK | dak |
| fk_office_id | integer | FK | dad_office |
| settlement_remarks | text |  | None |
| transcription_type | character(1) |  | None |
| demand_code_head | character varying(9) |  | None |

## Table: dad_employee
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| account_no | character varying(8) |  | None |
| month | character varying(7) |  | None |
| employee_name | character varying(50) |  | None |
| gender | character(1) |  | None |
| category | character varying(3) |  | None |
| fk_present_office | integer | FK | dad_office |
| present_office_date | date |  | None |
| fk_status_code | integer | FK | status_code |
| status_effect_date | date |  | None |
| fk_present_desg | integer | FK | dad_designation |
| present_desg_date | date |  | None |
| date_of_birth | date |  | None |
| appointment_date | date |  | None |
| increment_date | date |  | None |
| superannuation_date | date |  | None |
| gazette | boolean |  | None |
| ph_status | boolean |  | None |
| married | boolean |  | None |
| edp_trained | boolean |  | None |
| pension_scheme | character varying(3) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| current_record | boolean |  | None |
| old_id | bigint |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| roster_no | integer |  | None |
| service_group | character(1) |  | None |
| fk_dad_office_station | integer | FK | dad_office_station |
| hometown | character varying(50) |  | None |
| fk_office_id | integer | FK | dad_office |
| pink_list_no | character varying(7) |  | None |
| fk_previous_desg | integer | FK | dad_designation |
| pay_bill_group_id | integer |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| cgeis_recovery | boolean |  | None |
| cgeis_group | character(1) |  | None |
| cghs_recovery | boolean |  | None |
| fk_present_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| disability_percentage | double precision |  | None |
| pan_number | character varying(10) |  | None |
| height | character varying(10) |  | None |
| identification_mark | character varying(15) |  | None |
| fk_ph_category | integer | FK | ph_category |
| ex_service | boolean |  | None |
| idas_allot_year | character varying(4) |  | None |

## Table: dad_employee_arrears
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_part_two_order | integer | FK | dad_part_two_order |
| fk_pay_code | integer | FK | pay_code |
| month_ending | character varying(7) |  | None |
| due_amount | integer |  | None |
| drawn_amount | integer |  | None |
| arrear_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| paid | boolean |  | None |
| round_off_amount | boolean |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| payment_type | character(1) |  | None |
| fk_dad_paybill | bigint | FK | dad_paybill |
| fk_dak | bigint | FK | dak |
| number1 | integer |  | None |
| value1 | character varying(20) |  | None |

## Table: dad_fund_payment_authority
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| authority_number | integer |  | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_fund_purpose | integer | FK | fund_purpose |
| temp_final | character(1) |  | None |
| authority_month_ending | character varying(7) |  | None |
| received_month_year | character varying(7) |  | None |
| paid_voucher_month_year | character varying(7) |  | None |
| month_ending | character varying(7) |  | None |
| instalment | integer |  | None |
| rate | double precision |  | None |
| consolidated_amount | integer |  | None |
| approval_amount | integer |  | None |
| fk_unit | integer | FK | unit |
| unit_code | character varying(10) |  | None |
| authority_status | character(1) |  | None |
| voucher_received | boolean |  | None |
| fk_dids | integer | FK | dids |
| fk_imprest | integer | FK | imprest |
| special_sanction | boolean |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| authority_date | date |  | None |
| bill_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| recovery_start_date | date |  | None |
| approved | boolean |  | None |
| transfered_to_ecs | boolean |  | None |
| batch | character varying(15) |  | None |
| discharge_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| gpf_pran_ppan_no | character varying(16) |  | None |
| cco9_balance | integer |  | None |
| subscription | integer |  | None |
| refund | integer |  | None |
| withdrawal | integer |  | None |
| fk_task_usr | integer |  | None |
| account_no | character varying(8) |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| gpf_rule | character varying(25) |  | None |
| withdrawal_last_five_years | character(1) |  | None |
| auditor_remarks | text |  | None |
| aao_remarks | text |  | None |
| ao_remarks | text |  | None |
| go_remarks | text |  | None |
| sub_from | character varying(7) |  | None |
| sub_to | character varying |  | None |
| refund_from | character varying(7) |  | None |
| refund_to | character varying(7) |  | None |
| former_service | boolean |  | None |
| basicpay | integer |  | None |
| gradepay | integer |  | None |
| online | boolean |  | None |
| outstanding_amount | integer |  | None |
| adv_specific_type | character varying(15) |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: dad_it_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| recovery_month | character varying(7) |  | None |
| it_recovery_amount | integer |  | None |
| cess_amount | integer |  | None |
| secondary_cess_amount | integer |  | None |
| surcharge_amount | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_usr | integer | FK | usr |
| recovery_type | character(1) |  | None |
| fk_dad_paybill | integer | FK | dad_paybill |
| fk_dak | bigint | FK | dak |
| record_status | character(1) |  | None |
| eh_cess | integer |  | None |

## Table: dad_leave_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_leave_type | integer | FK | leave_type |
| fk_dad_leave_register | bigint | FK | dad_leave_register |
| fk_applicant | integer | FK | dad_employee |
| from_date_applied | date |  | None |
| to_date_applied | date |  | None |
| leave_days_applied | integer |  | None |
| from_date_sanctioned | date |  | None |
| to_date_sanctioned | date |  | None |
| leave_days_sanctioned | integer |  | None |
| fk_recommended_by | integer | FK | usr |
| fk_sanctioned_by | integer | FK | usr |
| pre_sanctioned | boolean |  | None |
| leave_reason | text |  | None |
| leave_address | text |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| transaction_type | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| part_two_order_generated | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| opening_balance | integer |  | None |
| closing_balance | integer |  | None |
| part_two_order_no | integer |  | None |
| part_two_order_date | date |  | None |
| recommended_date | date |  | None |
| sanction_date | date |  | None |
| leave_mode | character varying(15) |  | None |
| hqrs_leaving_permission | boolean |  | None |
| hqrs_leaving_date | date |  | None |
| hqrs_leaving_time | character varying(4) |  | None |
| recommended | boolean |  | None |
| sanctioned | boolean |  | None |
| mls_month | character varying(7) |  | None |
| fk_submitted_by | integer | FK | usr |
| submtd_dt | date |  | None |
| fk_aao | integer | FK | usr |
| aao_dt | date |  | None |
| fk_ao | integer | FK | usr |
| ao_dt | date |  | None |
| fk_mo_level_1 | integer | FK | usr |
| mo_lev1_dt | date |  | None |
| fk_mo_level_2 | integer | FK | usr |
| mo_lev2_dt | date |  | None |
| fk_mo_level_3 | integer | FK | usr |
| mo_lev3_dt | date |  | None |
| fk_mo_level_4 | integer | FK | usr |
| mo_lev4_dt | date |  | None |
| fk_sub_off_ic | integer |  | None |
| sub_off_ic_dt | date |  | None |
| fk_cancelled_by | integer | FK | usr |
| cancelled_dt | date |  | None |
| cancel_reason | text |  | None |

## Table: dad_loan_payment_authority
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_loan_sanction | integer | FK | dad_loan_sanction |
| fk_dad_employee | bigint | FK | dad_employee |
| received_month | character varying(7) |  | None |
| processed_month | character varying(7) |  | None |
| authority_no | character varying(25) |  | None |
| authority_date | date |  | None |
| contingent_bill_no | character varying(25) |  | None |
| contingent_bill_date | date |  | None |
| approval_amount | integer |  | None |
| transfered_to_ecs | boolean |  | None |
| voucher_received | boolean |  | None |
| fk_dids | integer | FK | dids |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| fk_task_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| authority_status | character(1) |  | None |
| fk_office_id | integer | FK | dad_office |
| batch | character varying(15) |  | None |
| account_no | character varying(8) |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| sanction_amount | integer |  | None |
| payment_instalments | integer |  | None |
| total_instalments | integer |  | None |
| recovery_rate | integer |  | None |
| recovery_date | date |  | None |
| outright_plot_construction | character(1) |  | None |
| fk_loan_code | integer |  | None |
| instalment_number | character(1) |  | None |
| instalment_date | date |  | None |
| dak_no | character varying(16) |  | None |
| instalment_amount | integer |  | None |

## Table: dad_loan_sanction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| month | character varying(7) |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| sanction_amount | integer |  | None |
| payment_instalment_count | integer |  | None |
| recovery_rate | integer |  | None |
| recovery_instalment_count | integer |  | None |
| balance_principal | integer |  | None |
| balance_interest | integer |  | None |
| fk_loan_code | integer | FK | loan_code |
| recovery_date | date |  | None |
| fk_dak | bigint | FK | dak |
| total_instalment_count | integer |  | None |
| arrears_recovery | boolean |  | None |
| sanction_unit | character varying(10) |  | None |
| progressive_amount | integer |  | None |
| fk_original_sanction | integer | FK | dad_loan_sanction |
| installment1_amount | integer |  | None |
| installment1_date | date |  | None |
| installment2_amount | integer |  | None |
| installment2_date | date |  | None |
| installment3_amount | integer |  | None |
| installment3_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| account_no | character varying(8) |  | None |
| interest_rate | integer |  | None |
| fk_dad_paybill | integer | FK | dad_paybill |
| fk_task_usr | integer | FK | usr |
| fk_public_fund_office | integer | FK | dad_office |
| fk_closedby_auditor | integer | FK | usr |
| closedby_auditor_date | date |  | None |
| fk_closedby_aao | integer | FK | usr |
| closedby_aao_date | date |  | None |
| fk_closedby_ao | integer | FK | usr |
| closedby_ao_date | date |  | None |
| close_approved | boolean |  | None |
| close_remarks | text |  | None |
| sgst | double precision |  | None |
| cgst | double precision |  | None |
| utgst | double precision |  | None |
| igst | double precision |  | None |
| utsav_card_issue_date | date |  | None |
| fk_utsav_card_update_by | integer | FK | usr |
| last_instalment_amount | integer |  | None |
| hba_acquisition_type | character(1) |  | None |
| hba_payment_amount | integer |  | None |
| close_reason | character varying(10) |  | None |
| card_service_charge | integer |  | None |

## Table: dad_medical_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_office | integer | FK | dad_office |
| month | character varying(7) |  | None |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| claim_type | character(1) |  | None |
| fk_dad_employee_family_detail | integer | FK | dad_employee_family_detail |
| name_of_patient | character varying(50) |  | None |
| relationship | character varying(25) |  | None |
| place_fell_ill | character varying(15) |  | None |
| fk_vendor | integer | FK | vendor |
| inpatient_outpatient | character(1) |  | None |
| from_period | date |  | None |
| to_period | date |  | None |
| medical_test_name | character varying(25) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| penal_interest | integer |  | None |
| amount_disallowed | integer |  | None |
| adjustment_amount | integer |  | None |
| credit_status | character(1) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| final_claim_received | boolean |  | None |
| fk_final_claim | bigint | FK | dad_medical_bill |
| credit_settled | boolean |  | None |
| posted_in_demand_register | boolean |  | None |
| fk_punching_medium | bigint | FK | punching_medium |
| created_at | timestamp without time zone |  | None |
| last_modified_date | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| hospital_category | character varying(15) |  | None |
| hospital_sub_category | character varying(20) |  | None |
| manual_rejection | boolean |  | None |
| remarks | text |  | None |
| disallowance_details | text |  | None |
| advance_date | date |  | None |
| payment_to_whom | character(2) |  | None |
| fk_bank_pan_detail | bigint |  | None |
| processed_month | character varying(7) |  | None |
| mro_received | boolean |  | None |
| final_adjustment_settled | boolean |  | None |
| recoveries | integer |  | None |
| verified_audit_checks | boolean |  | None |
| code_hd | character varying(9) |  | None |
| batch | character varying(20) |  | None |
| transfered_to_ecs | boolean |  | None |
| fk_section | integer |  | None |
| passed | boolean |  | None |
| rejection_reason | text |  | None |
| cghs_card_no | character varying(10) |  | None |
| cghs_referral_date | date |  | None |
| cghs_referral_renewed | boolean |  | None |
| cghs_referral_letter_enclosed | boolean |  | None |
| dept_permission_letter_no | character varying(20) |  | None |
| ip_op_number | character varying(20) |  | None |
| dept_permission_letter_enclosed | boolean |  | None |
| bill_already_rejected_before | boolean |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| day_care_treatment | boolean |  | None |
| payment_authority_number | integer |  | None |
| payment_authority_date | date |  | None |
| letter_of_credit_date | date |  | None |
| hospital_name | text |  | None |
| itax_amount | integer |  | None |
| he_cess | integer |  | None |
| taxable_amount | integer |  | None |
| fk_task_usr | integer | FK | usr |
| advance_amount | integer |  | None |
| ddr_id | character varying(30) |  | None |
| fk_office_public_fund | integer | FK | dad_office |
| mro_no | character varying(17) |  | None |
| mro_date | date |  | None |
| mro_amount | double precision |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| cmp_date | date |  | None |
| provisional_payment | boolean |  | None |
| prov_authority_number | character(25) |  | None |
| prov_authority_date | date |  | None |
| fk_fund_booking_office | integer | FK | dad_office |
| fk_vendor_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_office_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_emp_bank_pan_detail | bigint | FK | bank_pan_detail |
| vendor_amount | integer |  | None |
| office_amount | integer |  | None |
| employee_amount | integer |  | None |
| dept_permission_date | date |  | None |
| illness_details | text |  | None |
| stage | integer |  | None |
| pa_status | character(1) |  | None |
| fk_emp_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_office_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_vendor_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: dad_monthly_pay
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_paybill | bigint | FK | dad_paybill |
| pay_bill_month | character varying(7) |  | None |
| home_pay | integer |  | None |
| total_debit | integer |  | None |
| gross_pay | integer |  | None |
| table_recoveries | integer |  | None |
| net_pay | integer |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| income_tax | integer |  | None |
| gpf | integer |  | None |
| nps | integer |  | None |
| pli | integer |  | None |
| lic | integer |  | None |
| ptax | integer |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| pay_bill_group | character varying(7) |  | None |
| cgeis | integer |  | None |
| cghs | integer |  | None |
| debit_adjustment | integer |  | None |
| credit_adjustment | integer |  | None |
| lfee | integer |  | None |
| loans | integer |  | None |
| npb_date | date |  | None |
| payslip_sent_by_mail | boolean |  | None |
| payslip_generated | boolean |  | None |
| employee_type | character(1) |  | None |
| paybill_type | character(1) |  | None |
| fk_pay_bill_office_id | integer | FK | dad_office |
| emp_office_id | integer |  | None |
| emp_desg_abbr | character varying(15) |  | None |
| pay_band | character varying(5) |  | None |
| pay_level | character varying(3) |  | None |
| ifsc_code | character varying(11) |  | None |
| bank_account_no | character varying(60) |  | None |
| fk_usr | integer | FK | usr |
| usr_date | date |  | None |
| transcription_type | character(1) |  | None |
| fk_dak | bigint | FK | dak |
| int_number1 | integer |  | None |
| value1 | character varying(50) |  | None |
| nps_gc | integer |  | None |
| value2 | character varying(50) |  | None |
| int_number2 | integer |  | None |
| date1 | date |  | None |
| ctrl_id | integer |  | None |
| account_no | character varying(7) |  | None |
| gpf_pran | character varying(16) |  | None |

## Table: dad_nps_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| month_ending | character varying(7) |  | None |
| fk_dad_nps_gpf_detail | bigint | FK | dad_nps_gpf_detail |
| emp_contribution | integer |  | None |
| govt_contribution | integer |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| recovery_type | character(1) |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| uploaded | boolean |  | None |
| uploaded_month_ending | character varying(7) |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dad_paybill | integer | FK | dad_paybill |
| transcription_type | character(1) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| arrear_amount | integer |  | None |
| fk_dak | integer | FK | dak |
| upload_batch | character varying(15) |  | None |
| pm_voucher_no | integer |  | None |
| pm_section_code | integer |  | None |
| upload_date | date |  | None |

## Table: dad_office
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_cda_office | integer | FK | dad_office |
| cda_code | character varying(2) |  | None |
| office_code | character varying(4) |  | None |
| fk_dad_office_type | integer | FK | dad_office_type |
| office_name | character varying(75) |  | None |
| address1 | character varying(50) |  | None |
| address2 | character varying(50) |  | None |
| address3 | character varying(50) |  | None |
| station | character varying(25) |  | None |
| pin_code | character varying(6) |  | None |
| phone1 | character varying(12) |  | None |
| phone2 | character varying(12) |  | None |
| fax | character varying(12) |  | None |
| email | character varying(40) |  | None |
| wan_id | character varying(15) |  | None |
| website_address | character varying(40) |  | None |
| originating_code_head | character varying(9) |  | None |
| responding_code_head | character varying(9) |  | None |
| training_institute | boolean |  | None |
| sub_office | boolean |  | None |
| sub_office_section_code | character varying(5) |  | None |
| fk_lao_code | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_dad_office_station | integer | FK | dad_office_station |
| fk_dad_organization | integer | FK | dad_organization |
| fk_state | integer | FK | state |
| fk_country | integer | FK | country |
| geography | character varying(10) |  | None |
| last_working_day_of_week | character varying(3) |  | None |
| fk_pli | integer | FK | vendor |
| fk_lic | integer | FK | vendor |
| fk_cto | integer | FK | vendor |
| ddo_regn_no | character varying(10) |  | None |
| tulip_implemented | boolean |  | None |
| pli_recovery_nature | character(1) |  | None |
| lic_recovery_nature | character(1) |  | None |
| cto_recovery_nature | character(1) |  | None |
| fk_office_public_fund | integer | FK | bank_pan_detail |
| status | character(1) |  | None |
| reason | text |  | None |
| uuid | character varying(14) |  | None |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor_cto | integer | FK | aaa_central_vendor |
| fk_central_vendor_pli | integer | FK | aaa_central_vendor |
| fk_central_vendor_lic | integer | FK | aaa_central_vendor |
| orig_office_id | integer |  | None |
| src_office_id | integer |  | None |

## Table: dad_pay_recovery
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_section | integer | FK | section |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_pay_code | integer | FK | pay_code |
| month_ending | character varying(7) |  | None |
| total_recovery_amount | integer |  | None |
| total_installment | integer |  | None |
| recovery_rate | integer |  | None |
| recovered_during_month | integer |  | None |
| outstanding_amount | integer |  | None |
| current_installment | integer |  | None |
| outstanding_installment | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| value1 | character varying(50) |  | None |
| value2 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| int_number2 | integer |  | None |
| mro_amount | integer |  | None |
| fk_mro_dak | bigint | FK | dak |

## Table: dad_paybill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_dad_office | integer | FK | dad_office |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| month | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | double precision |  | None |
| amount_disallowed | double precision |  | None |
| provisional_payment | boolean |  | None |
| verified_audit_checks | boolean |  | None |
| sysgenerated_bill_amount | double precision |  | None |
| last_charge | double precision |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| fk_jcda | integer | FK | usr |
| jcda_date | date |  | None |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| regular_pay_bill | boolean |  | None |
| fk_code_head | integer | FK | code_head |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| addl_information1 | character varying(15) |  | None |
| addl_information2 | character varying(15) |  | None |
| addl_information3 | character varying(15) |  | None |
| encashment_from_date | date |  | None |
| fk_dad_employee | bigint | FK | dad_employee |
| encashment_days | integer |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| payment_record_type | character(1) |  | None |
| fk_office_public_fund | integer | FK | dad_office |
| recoveries | double precision |  | None |
| ucc_code | character varying(6) |  | None |
| sys_generated | boolean |  | None |
| pb_description | character varying(100) |  | None |
| pb_no | integer |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_date | date |  | None |
| dp_sheet_no | integer |  | None |
| cmp_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| pb_month | character varying(7) |  | None |
| remarks | text |  | None |
| fk_dad_employee_ne | bigint | FK | dad_employee_ne |

## Table: dad_pli
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| month_ending | character varying(7) |  | None |
| trans_type | character varying(3) |  | None |
| batch_no | integer |  | None |
| proposal_no | character varying(10) |  | None |
| policy_no | character varying(20) |  | None |
| policy_date | date |  | None |
| maturity_date | date |  | None |
| policy_amount | integer |  | None |
| mature_amount | integer |  | None |
| premium_rate | integer |  | None |
| premium_status | character(1) |  | None |
| last_premium_month | character varying(2) |  | None |
| last_premium_year | character varying(4) |  | None |
| surrender_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| arrears_required | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| policy_nature | character(1) |  | None |
| lic_branch_code | character varying(4) |  | None |
| lic_branch_address | character varying(100) |  | None |

## Table: dad_pli_adjustment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_pli | bigint | FK | dad_pli |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| month | character varying(7) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| amount | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: dad_rti_cases
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| communication_source_type | character varying(15) |  | None |
| communication_received_from_office | character varying(35) |  | None |
| name_of_applicant | character varying(50) |  | None |
| rti_application_date | date |  | None |
| fk_section | integer | FK | section |
| reply_scheduled_date | date |  | None |
| reminder1_date | date |  | None |
| reminder2_date | date |  | None |
| reminder3_date | date |  | None |
| information_sought | text |  | None |
| interim_reply_date | date |  | None |
| reply_date | date |  | None |
| reply_authority | character varying(25) |  | None |
| reply_approving_authority | character varying(25) |  | None |
| record_status | character(1) |  | None |
| reply_status | character(1) |  | None |
| remarks | text |  | None |
| forwarded_to_other_office | boolean |  | None |
| forwarding_letter_no | character varying(50) |  | None |
| forwarding_letter_date | date |  | None |
| forwarded_information_received_date | date |  | None |
| forwarded_information_received_letter | character varying(50) |  | None |
| approved | boolean |  | None |
| fk_usr_level1 | integer | FK | usr |
| fk_usr_level2 | integer | FK | usr |
| fk_usr_submitted_by | integer | FK | usr |
| fk_usr_approved_by | integer | FK | usr |
| fk_usr | integer | FK | usr |
| level1_usr_date | date |  | None |
| level2_usr_date | date |  | None |
| submitted_by_usr_date | date |  | None |
| approved_by_usr_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| forwarded_to_other_office_name | character varying(100) |  | None |

## Table: dad_table_recovery_beneficiary
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_pay_code | integer | FK | pay_code |
| fk_vendor | integer | FK | vendor |
| fk_bank_pan_detail | integer | FK | bank_pan_detail |
| record_status | character(1) |  | None |
| record_type | character(1) |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: dad_tada_ltc_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_bill_type | integer | FK | bill_type |
| fk_bill_nature | integer | FK | bill_nature |
| fk_section | integer | FK | section |
| fk_dad_employee | bigint | FK | dad_employee |
| claim_type | character(1) |  | None |
| claim_date | date |  | None |
| journey_station_from | character varying(30) |  | None |
| journey_station_to | character varying(30) |  | None |
| mode_of_journey | character varying(5) |  | None |
| block_year | character varying(9) |  | None |
| amount_claimed | double precision |  | None |
| amount_passed | integer |  | None |
| advance_amount | integer |  | None |
| amount_disallowed | integer |  | None |
| penal_interest | integer |  | None |
| adjustment_amount | integer |  | None |
| posted_in_demand_register | boolean |  | None |
| mro_received | boolean |  | None |
| final_adjustment_received | boolean |  | None |
| final_adjustment_settled | boolean |  | None |
| fk_final_adjustment | bigint | FK | dad_tada_ltc_bill |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| fk_go | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| go_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| last_modified_by | integer |  | None |
| passed | boolean |  | None |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| foreign_travel | boolean |  | None |
| recoveries | integer |  | None |
| claim_preference_type | character(1) |  | None |
| claim_at_old_rates | boolean |  | None |
| processed_month | character varying(7) |  | None |
| period_from | date |  | None |
| period_to | date |  | None |
| no_of_days | integer |  | None |
| type_of_ltc | character varying(2) |  | None |
| verified_audit_checks | boolean |  | None |
| code_hd | character varying(9) |  | None |
| provisional_payment | boolean |  | None |
| multiple_mode_of_journey | boolean |  | None |
| composite_transfer_grant | integer |  | None |
| luggage_weight | real |  | None |
| luggage_amount | integer |  | None |
| class_of_travel | character varying(15) |  | None |
| journey_start_date | date |  | None |
| journey_end_date | date |  | None |
| travelling_charges | integer |  | None |
| payment_mode | character varying(3) |  | None |
| fk_cdr | integer | FK | dad_demand_register |
| payment_record_type | character(1) |  | None |
| fk_office_public_fund | integer | FK | dad_office |
| foreign_tada_amount | integer |  | None |
| ucc_code | character varying(6) |  | None |
| stage | integer |  | None |
| mro_amount | integer |  | None |
| mro_dak_id | character varying(15) |  | None |
| office_order_no | character varying(15) |  | None |
| office_order_date | date |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_vendor | integer | FK | vendor |
| vendor_amount | integer |  | None |
| other_amount | integer |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| cmp_date | date |  | None |
| ht_block_year | character varying(9) |  | None |
| cv_in_lieu_of_ltc | boolean |  | None |
| no_of_members | integer |  | None |
| emp_category | character varying(3) |  | None |
| round_trip_fare_per_person | integer |  | None |
| total_fare | integer |  | None |
| leave_encash_amount | integer |  | None |
| total_value | integer |  | None |
| full_cash_benefit_exp | integer |  | None |
| share_of_leave_encash | double precision |  | None |
| share_of_fare_total | double precision |  | None |
| actual_amount_spent | integer |  | None |
| amount_of_cash_benefit | integer |  | None |
| encash_advance | integer |  | None |
| fare_advance | integer |  | None |
| calendar_year | integer |  | None |
| encash_share_amount | integer |  | None |
| fare_share_amount | integer |  | None |
| it_recovery_amount | integer |  | None |
| it_eh_cess_amount | integer |  | None |
| spl_ltc_paid_dakid | character varying(18) |  | None |
| spl_ltc_encash_paid | integer |  | None |
| spl_ltc_fare_paid | integer |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: dad_tada_ltc_bill_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dad_tada_ltc_bill | bigint | FK | dad_tada_ltc_bill |
| mode_of_journey | character varying(5) |  | None |
| onward_journey_start_date | date |  | None |
| onward_journey_start_time | character varying(5) |  | None |
| onward_journey_end_date | date |  | None |
| onward_journey_end_time | character varying(5) |  | None |
| return_journey_start_date | date |  | None |
| return_journey_start_time | character varying(5) |  | None |
| return_journey_end_date | date |  | None |
| return_journey_end_time | character varying(5) |  | None |
| journey_order | integer |  | None |
| no_of_journey_da | double precision |  | None |
| journey_da_amount | integer |  | None |
| no_of_stay_da | double precision |  | None |
| stay_da_amount | integer |  | None |
| food_charges | integer |  | None |
| lodging_charges | integer |  | None |
| rma_rate | real |  | None |
| rma_distance | real |  | None |
| rma_amount | integer |  | None |
| no_of_dependants | integer |  | None |
| distance_between_station | integer |  | None |
| composite_transfer_grant | integer |  | None |
| luggage_weight | real |  | None |
| luggage_amount | integer |  | None |
| type_of_vehicle | character varying(15) |  | None |
| fk_usr | integer | FK | usr |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| station_from | character varying(30) |  | None |
| station_to | character varying(30) |  | None |
| travelling_charges | integer |  | None |
| class_of_travel | character varying(15) |  | None |
| fk_dak | bigint | FK | dak |
| fk_family_detail | integer | FK | dad_employee_family_detail |
| fk_dad_employee | bigint | FK | dad_employee |
| ltc_type | character varying(2) |  | None |
| block_year | character varying(9) |  | None |
| relation_name | character varying(15) |  | None |

## Table: dak
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| list_no | integer |  | None |
| dakid_no | character varying(18) |  | None |
| fk_section | integer | FK | section |
| fk_dak_type | integer | FK | dak_type |
| fk_bill_type | integer | FK | bill_type |
| fk_unit | integer | FK | unit |
| fk_imprest | integer | FK | imprest |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_civ_employee | bigint | FK | civ_employee |
| emp_no | character varying(8) |  | None |
| gpf_pran_ppan_no | character varying(16) |  | None |
| dad_account_no | character varying(8) |  | None |
| reference_no | character varying(100) |  | None |
| reference_date | date |  | None |
| subject | text |  | None |
| bill_no | character varying(30) |  | None |
| bill_date | date |  | None |
| amount | double precision |  | None |
| disposal_no | character varying(100) |  | None |
| disposal_date | date |  | None |
| fk_outward_dak | bigint | FK | outward_dak |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| fk_dak_entry_usr | integer | FK | usr |
| fk_usr | integer | FK | usr |
| task_no | character varying(6) |  | None |
| rescheduled | boolean |  | None |
| fk_old_dak | bigint | FK | dak |
| multiple_entry | boolean |  | None |
| temp_dak_id | character varying(50) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| month_year | character varying(7) |  | None |
| dak_year | character varying(9) |  | None |
| priority | integer |  | None |
| list_date | date |  | None |
| fk_vendor | integer | FK | vendor |
| sender_name | character varying(50) |  | None |
| sender_city | character varying(20) |  | None |
| mode_of_receipt | character varying(20) |  | None |
| regn_no | character varying(15) |  | None |
| security_grading | character varying(20) |  | None |
| gem_bill | boolean |  | None |
| fis_doc_no | character varying(50) |  | None |
| fis_date | date |  | None |
| fis_code_head | character varying(9) |  | None |
| fis_xml_file_no | text |  | None |
| fk_fis_imported_by | integer | FK | usr |
| fis_imported_at | timestamp without time zone |  | None |
| pfms_bill | boolean |  | None |
| pfms_sanction_id | character varying(50) |  | None |
| pfms_sanction_date | date |  | None |
| fk_auditor_disposal | integer | FK | usr |
| fk_aao_disposal | integer | FK | usr |
| fk_ao_disposal | integer | FK | usr |
| auditor_disposal_date | date |  | None |
| aao_disposal_date | date |  | None |
| ao_disposal_date | date |  | None |
| kpi_bill_type | character varying(10) |  | None |
| msme_cat | character varying(1) |  | None |
| make_cat | character varying(2) |  | None |
| exp_cat | character varying(1) |  | None |
| codehead | character varying(9) |  | None |
| major_head | character varying(4) |  | None |
| uuid | character varying(14) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| file_path | character varying |  | None |

## Table: dak_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| dak_year | character varying(9) |  | None |
| dakid_no | character varying(16) |  | None |
| multiple_sections | boolean |  | None |
| fk_section | integer | FK | section |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| fk_go | integer | FK | usr |
| fk_jcda | integer | FK | usr |
| fk_cda | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| go_date | date |  | None |
| jcda_date | date |  | None |
| cda_date | date |  | None |
| auditor_remarks | text |  | None |
| aao_remarks | text |  | None |
| ao_remarks | text |  | None |
| go_remarks | text |  | None |
| jcda_remarks | text |  | None |
| cda_remarks | text |  | None |
| fk_auditor_presub | integer | FK | usr |
| fk_aao_presub | integer | FK | usr |
| fk_ao_presub | integer | FK | usr |
| fk_go_presub | integer | FK | usr |
| fk_jcda_presub | integer | FK | usr |
| auditor_presub_date | date |  | None |
| aao_presub_date | date |  | None |
| ao_presub_date | date |  | None |
| go_presub_date | date |  | None |
| jcda_presub_date | date |  | None |
| auditor_presub_remarks | text |  | None |
| aao_presub_remarks | text |  | None |
| ao_presub_remarks | text |  | None |
| go_presub_remarks | text |  | None |
| jcda_presub_remarks | text |  | None |
| fk_task_usr | integer | FK | usr |
| record_status | character(1) |  | None |
| resub_no | integer |  | None |
| resubmitted | boolean |  | None |
| approved | boolean |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dad_office | integer | FK | dad_office |
| org_id | integer |  | None |
| created_at | timestamp without time zone |  | None |

## Table: dak_type
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak_category | integer | FK | dak_category |
| fk_section | integer | FK | section |
| description | character varying(30) |  | None |
| fk_bill_type | integer | FK | bill_type |
| bill_no_req | boolean |  | None |
| task_marking_at_rsec | boolean |  | None |
| fk_task_distribution_mode | integer | FK | task_distribution_mode |
| created_at | timestamp without time zone |  | None |
| table_name | text |  | None |
| fk_office_id | integer | FK | dad_office |
| common | boolean |  | None |
| specific_to_section | boolean |  | None |
| fk_teller_dest_section | integer | FK | section |
| dak_type_abbr | character varying(3) |  | None |
| record_status | character(1) |  | None |

## Table: debit_scroll
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| scroll_id | character varying(20) |  | None |
| scroll_no | character varying(10) |  | None |
| fk_bank | integer | FK | bank |
| scroll_date | date |  | None |
| amount | double precision |  | None |
| cheque_no | character varying(25) |  | None |
| cheque_date | date |  | None |
| fk_schedule3 | integer | FK | schedule3 |
| linked | boolean |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_usr | integer | FK | usr |
| fk_central_bank | bigint | FK | aaa_central_bank |

## Table: deductions
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| transaction_id | character varying(100) |  | None |
| type | text |  | None |
| name | text |  | None |
| amount | double precision |  | None |
| reason | text |  | None |
| fk_gem_bill | bigint | FK | gem_bill |
| addl_details | character varying(10) |  | None |

## Table: delivery_challan
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| dc_type | character varying(10) |  | None |
| fk_vendor | integer | FK | vendor |
| dc_no | character varying(30) |  | None |
| dc_date | date |  | None |
| fk_product | integer | FK | product |
| qty_unit | character varying(6) |  | None |
| demand_no | character varying(100) |  | None |
| boc_no | character varying(100) |  | None |
| dc_pdf_name | character varying(50) |  | None |
| fk_pol_invoice | integer | FK | pol_invoice |
| created_at | timestamp without time zone |  | None |
| credit_verification_data | text |  | None |
| crv_no | character varying(30) |  | None |
| crv_date | date |  | None |
| ship_desc | character varying(50) |  | None |
| port_name | character varying(50) |  | None |
| indent_no | character varying(30) |  | None |
| indent_date | date |  | None |
| indent_pdf_name | character varying(50) |  | None |
| crv_pdf_name | character varying(50) |  | None |
| bdn_no | character varying(30) |  | None |
| bdn_date | date |  | None |
| bdn_pdf_name | character varying(50) |  | None |
| fk_dak | bigint | FK | dak |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: demand_intimation
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_imprest | integer | FK | imprest |
| cr_no | character varying(10) |  | None |
| cr_date | date |  | None |
| cr_amount | double precision |  | None |
| cr_paid_date | date |  | None |
| cr_month | character varying(2) |  | None |
| cr_year | character varying(4) |  | None |
| cr_type | character varying(5) |  | None |
| ack_no | character varying(25) |  | None |
| ack_date | date |  | None |
| amount_tallied | boolean |  | None |
| imprest_account_no | character varying(5) |  | None |
| cr_npb_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: deposit_work
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| fk_mro_dak | bigint | FK | dak |
| code_head | character varying(9) |  | None |
| work_description | text |  | None |
| work_id | character varying(50) |  | None |
| project_cost | double precision |  | None |
| opening_balance | double precision |  | None |
| amount | double precision |  | None |
| received_month | character varying(7) |  | None |
| progressive_expenditure | double precision |  | None |
| fin_year | character varying(9) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| record_type | character(1) |  | None |
| progressive_allotment | double precision |  | None |
| int_number1 | integer |  | None |
| value1 | character varying(50) |  | None |
| value2 | character varying(50) |  | None |
| work_type | character(1) |  | None |
| reference_no | character varying(50) |  | None |
| reference_date | date |  | None |
| nature | character varying(2) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: deposit_work_transaction
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| job_description | text |  | None |
| job_id | character varying(50) |  | None |
| fk_dak | bigint | FK | dak |
| fk_deposit_work | integer | FK | deposit_work |
| code_head | character varying(9) |  | None |
| amount_claimed | double precision |  | None |
| processed_month | character varying(7) |  | None |
| fin_year | character varying(9) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| voucher_no | character varying(50) |  | None |
| voucher_date | date |  | None |
| ca_no | character varying(50) |  | None |
| ca_date | date |  | None |
| so_no | character varying(50) |  | None |
| so_date | date |  | None |
| bill_description | text |  | None |
| payment_type | character(1) |  | None |
| payment_mode | character varying(3) |  | None |
| fk_vendor | bigint | FK | vendor |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_task_usr | integer | FK | usr |
| amount_passed | double precision |  | None |
| disallowance | integer |  | None |
| recoveries | integer |  | None |
| payment_amount | double precision |  | None |
| gst5_amount | double precision |  | None |
| gst12_amount | double precision |  | None |
| gst18_amount | double precision |  | None |
| gst28_amount | double precision |  | None |
| gst_type | character(1) |  | None |
| tax_recovery_principal_amount | double precision |  | None |
| verified_audit_checks | boolean |  | None |
| fk_section | integer | FK | section |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| value1 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: dhr
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| employee_type | character varying(5) |  | None |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_civ_employee | bigint | FK | civ_employee |
| category | character varying(4) |  | None |
| financial_year | character varying(9) |  | None |
| army_no | character varying(8) |  | None |
| check_digit | character(1) |  | None |
| rank | character varying(6) |  | None |
| section | integer |  | None |
| loanee_name | character varying(25) |  | None |
| loan_code_abbr | character varying(8) |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| amount_principal | integer |  | None |
| amount_interest | integer |  | None |
| opening_balance_principal | integer |  | None |
| opening_balance_interest | integer |  | None |
| recovery_rate | integer |  | None |
| payment_date | date |  | None |
| voucher_no | character varying(10) |  | None |
| voucher_date | date |  | None |
| total_instalment | integer |  | None |
| instalment_recovered | integer |  | None |
| instalment_recovered_in_year | integer |  | None |
| recovery_principal_in_year | integer |  | None |
| recovery_interest_in_year | integer |  | None |
| recovery_principal_progressive | integer |  | None |
| recovery_interest_progressive | integer |  | None |
| closing_balance_principal | integer |  | None |
| closing_balance_interest | integer |  | None |
| remarks | text |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| gpf_pran_ppan_no | character varying(16) |  | None |
| dad_account_no | character varying(7) |  | None |
| fk_verified_posted_by | integer | FK | usr |
| cda_code | character varying(2) |  | None |
| section_code | character varying(4) |  | None |
| verified_posted_on | date |  | None |
| fk_pao | integer | FK | dad_office |
| fk_unit | integer | FK | unit |
| fk_pbor | integer | FK | pbor |
| fk_dids | integer | FK | dids |
| dids_adj_amount | integer |  | None |
| month_year | character varying(7) |  | None |
| ack_received | boolean |  | None |
| ack_lt_no | character varying(50) |  | None |
| ack_lt_dt | date |  | None |
| rate_of_interest | double precision |  | None |
| fk_previous_dhr | integer | FK | dhr |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: dids
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| dids_no | character varying(16) |  | None |
| fk_cda | integer | FK | usr |
| dids_amount | double precision |  | None |
| dids_date | date |  | None |
| accepted_amount | double precision |  | None |
| balance_amount | double precision |  | None |
| original_responding | character(1) |  | None |
| originating_no | character varying(16) |  | None |
| originating_date | date |  | None |
| responding_no | character varying(16) |  | None |
| responding_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: disallowance
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_disallowance_code | integer | FK | disallowance_code |
| amount | integer |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |
| fk_treatment_disallowance | integer |  | None |

## Table: dmro
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_bank_scroll | integer | FK | bank_scroll |
| fk_section | integer | FK | section |
| section_code | character varying(4) |  | None |
| fk_unit | integer | FK | unit |
| fk_dad_office | integer | FK | dad_office |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dad_employee | bigint | FK | dad_employee |
| received_month | character varying(7) |  | None |
| min_no | character varying(17) |  | None |
| scroll_date | date |  | None |
| name_of_issuing_officer | character varying(50) |  | None |
| depositers_name | character varying(50) |  | None |
| bank_tr_receipt_no | character varying(25) |  | None |
| bank_tr_receipt_date | date |  | None |
| amount | double precision |  | None |
| adjustment_month | character varying(7) |  | None |
| te_no | character varying(10) |  | None |
| fk_omro | integer | FK | omro |
| omro_adjusted | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remittance_details | text |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_treasury_bank | integer | FK | bank |
| fk_office_id | integer | FK | dad_office |
| approved | boolean |  | None |
| fk_omro_dak | bigint | FK | dak |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_central_treasury_bank | bigint | FK | aaa_central_bank |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: echs_demand_register
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| fk_settlement_dak | bigint | FK | dak |
| demand_settlement_id | character varying(50) |  | None |
| demand_settlement_date | date |  | None |
| cda_code | character varying(2) |  | None |
| rc_code | character varying(25) |  | None |
| demand_claim_id | character varying(50) |  | None |
| demand_claim_date | date |  | None |
| fk_vendor | integer | FK | vendor |
| amount | double precision |  | None |
| settled_settlement_id | character varying(50) |  | None |
| settled_claim_id | character varying(50) |  | None |
| demand_approved | boolean |  | None |
| settlement_approved | boolean |  | None |
| manual_settlement | boolean |  | None |
| settled | boolean |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| record_status | character(1) |  | None |
| fk_auditor_demand | integer | FK | usr |
| fk_aao_demand | integer | FK | usr |
| fk_ao_demand | integer | FK | usr |
| demand_auditor_date | date |  | None |
| demand_aao_date | date |  | None |
| demand_ao_date | date |  | None |
| fk_auditor_settled | integer | FK | usr |
| fk_aao_settled | integer | FK | usr |
| fk_ao_settled | integer | FK | usr |
| settled_auditor_date | date |  | None |
| settled_aao_date | date |  | None |
| settled_ao_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dad_office | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: echs_hospital_it_details
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| cda_code | character varying(2) |  | None |
| rc_code | character varying(25) |  | None |
| fk_vendor | integer | FK | vendor |
| pan_number | character varying(10) |  | None |
| certificate_no | character varying(25) |  | None |
| reference_no | character varying(100) |  | None |
| reference_date | date |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| cancellation_date | date |  | None |
| payable_amount | double precision |  | None |
| progressive_paid_amount | double precision |  | None |
| it_section | character varying(25) |  | None |
| it_percentage | double precision |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dad_office | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: echs_medical_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| month_year | character varying(7) |  | None |
| settlement_id | character varying(50) |  | None |
| settlement_date | date |  | None |
| cda_code | character varying(2) |  | None |
| rc_code | character varying(25) |  | None |
| claim_id | character varying(50) |  | None |
| claim_date | date |  | None |
| echs_card_no | character varying(50) |  | None |
| echs_unique_no | character varying(50) |  | None |
| patient_id | character varying(50) |  | None |
| patient_name | character varying(50) |  | None |
| ex_serviceman_rank | character varying(50) |  | None |
| ex_serviceman_name | character varying(50) |  | None |
| relation | character varying(25) |  | None |
| hosp_adm_date | date |  | None |
| hosp_disch_date | date |  | None |
| ip_op_emer | character varying(10) |  | None |
| amount_claimed | double precision |  | None |
| echs_approved_amount | double precision |  | None |
| amount_disallowed | double precision |  | None |
| recoveries | integer |  | None |
| tds_on_amount_admissible | integer |  | None |
| bpa_service_fees | double precision |  | None |
| bpa_penalty | double precision |  | None |
| igst_on_bpa_service_fees | double precision |  | None |
| cgst_on_bpa_service_fees | double precision |  | None |
| sgst_on_bpa_service_fees | double precision |  | None |
| utgst_on_bpa_service_fees | double precision |  | None |
| tds_on_bpa_service_fees | integer |  | None |
| tds_igst | integer |  | None |
| tds_cgst | integer |  | None |
| tds_sgst | integer |  | None |
| tds_utgst | integer |  | None |
| hospital_discount | double precision |  | None |
| hospital_recovery_amount | double precision |  | None |
| recovery_against_settlement_id | character varying(50) |  | None |
| recovery_against_claim_id | character varying(50) |  | None |
| payee_category | character varying(10) |  | None |
| payee_name | character varying(100) |  | None |
| payee_address | character varying(100) |  | None |
| payee_station | character varying(50) |  | None |
| pin_code | character varying(6) |  | None |
| payee_bank_ifsc_code | character varying(11) |  | None |
| payee_bank_account_no | character varying(25) |  | None |
| payee_bank_account_type | character varying(2) |  | None |
| payee_pan_no | character varying(10) |  | None |
| payee_email_address | character varying(50) |  | None |
| payee_mobile_no | character varying(20) |  | None |
| hospital_paid_amount | double precision |  | None |
| bpa_paid_amount | double precision |  | None |
| fk_bpa_vendor | integer | FK | vendor |
| fk_vendor | integer | FK | vendor |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| remarks | character varying(100) |  | None |
| reason | text |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_task_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| cmp_date | date |  | None |
| fk_consolidated_dak | bigint | FK | dak |
| fk_office_id | integer | FK | dad_office |
| fk_dad_office | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_go | integer | FK | usr |
| fk_jcda | integer | FK | usr |
| go_date | date |  | None |
| jcda_date | date |  | None |
| cda_recovery_amount | double precision |  | None |
| cda_recovery_settlement_id | character varying(50) |  | None |
| cda_recovery_claim_id | character varying(150) |  | None |
| hospital_it_rate | double precision |  | None |
| fk_echs_hospital_it_details | integer | FK | echs_hospital_it_details |
| hospital_recovery_in_this_claim | double precision |  | None |
| hospital_recovery_in_total_amount | double precision |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_bpa_vendor | integer | FK | aaa_central_vendor |

## Table: ecs
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_dak | bigint | FK | dak |
| month | character varying(7) |  | None |
| amount | double precision |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| fk_ecs_payment_type | integer | FK | ecs_payment_type |
| cmp_file_gen_date | date |  | None |
| npb_date | date |  | None |
| fk_schedule3 | integer | FK | schedule3 |
| fk_cheque_slip | bigint | FK | cheque_slip |
| payment_reference_no | character varying(15) |  | None |
| to_be_paid | boolean |  | None |
| file_no | character varying(25) |  | None |
| released | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| cmp_reference_no | character varying(20) |  | None |
| scroll_no | character varying(10) |  | None |
| scroll_date | date |  | None |
| record_status | character(1) |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| rollback | boolean |  | None |
| fk_auditor_rej | integer | FK | usr |
| auditor_date_rej | date |  | None |
| fk_aao_rej | integer | FK | usr |
| aao_date_rej | date |  | None |
| fk_ao_rej | integer | FK | usr |
| ao_date_rej | date |  | None |
| fk_auditor_accounts_rej | integer | FK | usr |
| auditor_date_accounts_rej | date |  | None |
| fk_aao_accounts_rej | integer | FK | usr |
| aao_date_accounts_rej | date |  | None |
| fk_ao_accounts_rej | integer | FK | usr |
| ao_date_accounts_rej | date |  | None |
| rejection_status | character(1) |  | None |
| rejection_approved_ds | boolean |  | None |
| rejection_approved_as | boolean |  | None |
| rejection_reason | text |  | None |
| cda13_no | character varying(10) |  | None |
| cda13_date | date |  | None |
| rejection_scroll_no | character varying(20) |  | None |
| rejection_scroll_date | date |  | None |
| cmp_rejection_reason | text |  | None |
| rollback_approved | boolean |  | None |
| sub_office_code | character varying(6) |  | None |
| fk_cda13_bpd | bigint | FK | bank_pan_detail |
| table_recoveries | integer |  | None |
| cmp_payment_status | character varying(2) |  | None |
| echs_sid | character varying(50) |  | None |
| echs_claim_id | character varying(50) |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_cda13_central_beneficiary | bigint | FK | aaa_central_beneficiary |

## Table: ecs_bulk
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_dak | bigint | FK | dak |
| month | character varying(7) |  | None |
| amount | double precision |  | None |
| table_recoveries | integer |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| npb_date | date |  | None |
| sub_office_code | character varying(6) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: ecs_payment_mode
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| payment_mode | character varying(10) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: ecs_payment_type
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| payment_type | character varying(6) |  | None |
| description | character varying(25) |  | None |
| code_head | character varying(9) |  | None |
| fk_bank | integer | FK | bank |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_bank | bigint | FK | aaa_central_bank |

## Table: ecs_sub_office
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| cda_code | character varying(6) |  | None |
| army_no | character varying(8) |  | None |
| check_digit | character(1) |  | None |
| sub_office_code | character varying(6) |  | None |
| pao_code | character varying(10) |  | None |
| beneficiary_name | character varying(40) |  | None |
| account_no | character varying(100) |  | None |
| ifsc_code | character varying(11) |  | None |
| micr_code | character varying(9) |  | None |
| amount | double precision |  | None |
| payment_reference_no | character varying(12) |  | None |
| npb_date | date |  | None |
| dak_no | character varying(20) |  | None |
| narration | character varying(100) |  | None |
| payment_mode | character varying(4) |  | None |
| cmp_reference_no | character varying(25) |  | None |
| cmp_month | character varying(7) |  | None |
| cmp_linked | boolean |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| fk_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| usr_date | date |  | None |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| cmp_gen_date | date |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| scroll_no | character varying(4) |  | None |
| scroll_date | date |  | None |
| cmp_remarks | character varying(50) |  | None |
| bank_scroll_file_no | character varying(100) |  | None |

## Table: emro
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| cda_code | character varying(2) |  | None |
| sub_office_code | character varying(4) |  | None |
| min_no | character varying(17) |  | None |
| transaction_no | character varying(25) |  | None |
| transaction_date | date |  | None |
| organisation | character varying(100) |  | None |
| depositor_name | character varying(100) |  | None |
| personnnel_no | character varying(50) |  | None |
| pcdao_no | character varying(50) |  | None |
| mobile_no | character varying(12) |  | None |
| address | character varying(240) |  | None |
| amount | double precision |  | None |
| payment_nature | character varying(100) |  | None |
| emro_office | character varying(100) |  | None |
| remarks | text |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dad_office | integer | FK | dad_office |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| te_no_accounts_sec | integer |  | None |
| te_month_accounts_sec | character varying(7) |  | None |
| te_date_accounts_sec | date |  | None |
| fk_dak_accounts_sec | bigint | FK | dak |
| fk_audit_sec | integer | FK | section |
| te_no_audit_sec | integer |  | None |
| te_month_audit_sec | character varying(7) |  | None |
| te_date_audit_sec | date |  | None |
| fk_dak_audit_sec | bigint | FK | dak |
| remarks_accounts_sec | text |  | None |
| remarks_audit_sec | text |  | None |
| service_head | character varying(9) |  | None |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| fk_auditor_audit_sec | integer | FK | usr |
| fk_aao_audit_sec | integer | FK | usr |
| fk_ao_audit_sec | integer | FK | usr |
| fk_auditor_accounts_sec | integer | FK | usr |
| fk_aao_accounts_sec | integer | FK | usr |
| fk_ao_accounts_sec | integer | FK | usr |
| auditor_date_audit_sec | date |  | None |
| aao_date_audit_sec | date |  | None |
| ao_date_audit_sec | date |  | None |
| auditor_date_accounts_sec | date |  | None |
| aao_date_accounts_sec | date |  | None |
| ao_date_accounts_sec | date |  | None |
| record_status_audit | character(1) |  | None |
| record_status_accounts | character(1) |  | None |
| approved_audit | boolean |  | None |
| approved_accounts | boolean |  | None |
| reason_audit_sec | text |  | None |
| reason_accounts | text |  | None |
| scroll_date | date |  | None |
| office_name_emro_relates | character varying(100) |  | None |
| dad_organisation | character varying(100) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: esec_bills
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| fk_bill_type | integer | FK | bill_type |
| expenditure_month | character varying(7) |  | None |
| amount_claimed | double precision |  | None |
| fk_vendor | integer | FK | vendor |
| payment_type | character(1) |  | None |
| payment_mode | character varying(3) |  | None |
| amount_passed | double precision |  | None |
| amount_disallowed | integer |  | None |
| recoveries | integer |  | None |
| fk_code_head | integer | FK | code_head |
| code_head_str | character varying(9) |  | None |
| verified_audit_checks | boolean |  | None |
| record_status | character(1) |  | None |
| fk_task_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| fk_bill_nature | integer | FK | bill_nature |
| fk_cto | integer | FK | vendor |
| fk_lwc | integer | FK | vendor |
| fk_allotment_detail | integer |  | None |
| fk_allotment_category | integer |  | None |
| fk_pay_unit | integer | FK | unit |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_pay_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor_cto | integer | FK | aaa_central_vendor |
| fk_central_vendor_lwc | integer | FK | aaa_central_vendor |

## Table: esec_final_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_contract_agreement | integer | FK | contract_agreement |
| voucher_no | character varying(25) |  | None |
| voucher_date | date |  | None |
| bill_amount | double precision |  | None |
| passed_amount | double precision |  | None |
| paid_amount | double precision |  | None |
| recoveries_amount | double precision |  | None |
| rar_pend_post_audit_vrno | character varying(25) |  | None |
| rar_pend_post_audit_date | date |  | None |
| rar_pend_post_audit_amount | double precision |  | None |
| rar_amount_paid_after_final_bill | double precision |  | None |
| retention_money_bgb_amount | double precision |  | None |
| retention_money_bgb_valid_date | date |  | None |
| te_demand_no | character varying(25) |  | None |
| te_demand_os_amt | double precision |  | None |
| te_demand_ca_no | character varying(25) |  | None |
| fk_task_usr | integer | FK | usr |
| fk_section | integer | FK | section |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: estate_occupancy_request
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_dad_employee | bigint | FK | dad_employee |
| employee_name | character varying(25) |  | None |
| fk_dad_designation | integer | FK | dad_designation |
| fk_dad_office | integer | FK | dad_office |
| appointment_date | date |  | None |
| basic_pay | integer |  | None |
| grade_pay | integer |  | None |
| date_from_which_drawing | date |  | None |
| date_of_birth | date |  | None |
| fk_dad_estate | integer | FK | dad_estate |
| request_type | character(1) |  | None |
| committee_approval_required | boolean |  | None |
| seniority_priority | integer |  | None |
| seniority_as_on_date | date |  | None |
| approval_status | character(1) |  | None |
| qtr_committee_date | date |  | None |
| allotment_letter_issue_date | date |  | None |
| allotment_acknowledgement_date | date |  | None |
| accepted_by_allottee | boolean |  | None |
| acceptance_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| remarks | text |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: front_office_query
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_section | integer | FK | section |
| fk_vendor | integer | FK | vendor |
| query_date | timestamp without time zone |  | None |
| fk_dak | bigint | FK | dak |
| query_from | character varying(100) |  | None |
| remarks | text |  | None |
| fk_usr | integer | FK | usr |
| fk_unit | integer | FK | unit |
| fk_project | integer | FK | project |
| fk_office_id | bigint | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: fta
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| project_code | character varying(14) |  | None |
| fk_dak | bigint | FK | dak |
| name_of_institute | character varying(100) |  | None |
| location | character varying(50) |  | None |
| course_name | character varying(100) |  | None |
| name_of_participant | character varying(100) |  | None |
| rank | character varying(50) |  | None |
| employee_id_no | character varying(50) |  | None |
| nationality | character varying(25) |  | None |
| embassy_name | character varying(25) |  | None |
| duration_from | date |  | None |
| duration_to | date |  | None |
| amount | double precision |  | None |
| processed_month | character varying(7) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: gem_bill
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| version | character varying(5) |  | None |
| order_id | character varying(25) |  | None |
| transaction_id | character varying(100) |  | None |
| buyer_org | character varying(50) |  | None |
| buyer_name | character varying(200) |  | None |
| buyer_address | character varying(200) |  | None |
| cda_code | character varying(2) |  | None |
| sub_office_code | character varying(4) |  | None |
| unit_code | character varying(14) |  | None |
| project_code | character varying(14) |  | None |
| code_head | character varying(9) |  | None |
| sub_category | character varying(50) |  | None |
| vendor_name | character varying(200) |  | None |
| vendor_address | character varying(200) |  | None |
| vendor_code | character varying(20) |  | None |
| vendor_district | character varying(30) |  | None |
| vendor_state | character varying(50) |  | None |
| vendor_pincode | character varying(6) |  | None |
| vendor_bank_account_no | character varying(25) |  | None |
| vendor_bank_ifsc_code | character varying(11) |  | None |
| vendor_enc_bank_account | character varying(60) |  | None |
| vendor_enc_bank_ifsc | character varying(30) |  | None |
| vendor_pan | character varying(10) |  | None |
| vendor_gstn | character varying(15) |  | None |
| supply_order_no | character varying(50) |  | None |
| supply_order_date | date |  | None |
| designation_financial | character varying(50) |  | None |
| ifd_concurrance | character(1) |  | None |
| ifd_diary_no | character varying(200) |  | None |
| ifd_diary_date | date |  | None |
| sanction_no | character varying(100) |  | None |
| sanction_date | date |  | None |
| product_code | character varying(20) |  | None |
| product_name | character varying(200) |  | None |
| product_brand | character varying(200) |  | None |
| quantity_ordered | double precision |  | None |
| unit_price | double precision |  | None |
| total_value | double precision |  | None |
| quantity_unit_type | character varying(25) |  | None |
| supplied_quantity | double precision |  | None |
| accepted_quantity | double precision |  | None |
| receipt_no | character varying(50) |  | None |
| frieght_charge | double precision |  | None |
| bill_amount | double precision |  | None |
| ld_days | double precision |  | None |
| ld_amount | double precision |  | None |
| created_at | timestamp without time zone |  | None |
| bill_date | date |  | None |
| expected_delivery_date | date |  | None |
| actual_delivery_date | date |  | None |
| invoice_no | character varying(50) |  | None |
| invoice_date | date |  | None |
| crac_no | character varying(50) |  | None |
| crac_date | date |  | None |
| prc_no | character varying(50) |  | None |
| prc_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| approved | boolean |  | None |
| recoveries | double precision |  | None |
| disallowance | double precision |  | None |
| amount_passed | double precision |  | None |
| amount_to_be_paid | double precision |  | None |
| gst5_amount | double precision |  | None |
| gst12_amount | double precision |  | None |
| gst18_amount | double precision |  | None |
| gst28_amount | double precision |  | None |
| gst_type | character(1) |  | None |
| dv_no | integer |  | None |
| dv_month | character varying(7) |  | None |
| dp_sheet_date | date |  | None |
| dp_sheet_no | integer |  | None |
| cmp_date | date |  | None |
| cmp_batch | character varying(25) |  | None |
| payment_reference_no | character varying(12) |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| payment_status | character varying(10) |  | None |
| failure_reason | text |  | None |
| deduction | boolean |  | None |
| deduction_amount | double precision |  | None |
| transaction_month | character varying(7) |  | None |
| honeyb_response | character varying(10) |  | None |
| payment_by | character varying(10) |  | None |
| fk_dad_office | integer | FK | dad_office |
| receipt_date | date |  | None |
| gem_invoice_no | character varying(50) |  | None |
| bill_no | character varying(50) |  | None |
| sub_cat_id | character varying(3) |  | None |
| buyer_district | character varying(50) |  | None |
| buyer_email | character varying(50) |  | None |
| buyer_gstn | character varying(15) |  | None |
| buyer_mobile | character varying(15) |  | None |
| buyer_pincode | character varying(6) |  | None |
| buyer_state | character varying(50) |  | None |
| dp_short_name | character varying(100) |  | None |
| seller_id | character varying(100) |  | None |
| demand_id | character varying(200) |  | None |
| order_date | date |  | None |
| order_amount | double precision |  | None |
| order_status | character varying(100) |  | None |
| honeyb_bill_response | character varying(10) |  | None |
| final_bill_date | date |  | None |
| is_ulpo | character varying(5) |  | None |
| rejected_bill_no | character varying(100) |  | None |
| section_code | integer |  | None |
| provisional_payment | boolean |  | None |
| pp_processed_date | date |  | None |
| pp_regularized_date | date |  | None |
| pp_sanction_no | character varying(100) |  | None |
| pp_sanction_date | date |  | None |
| capital_id | character varying(15) |  | None |
| make_type | character(1) |  | None |
| msme | character(1) |  | None |
| payment_pushed_date | timestamp without time zone |  | None |
| sdac_number | character varying(255) |  | None |
| sdac_date | date |  | None |
| crac_number | character varying(255) |  | None |
| billing_cycle | character varying(255) |  | None |
| svc_applicable | character varying(10) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| generated | boolean |  | None |
| excess_applicable | character varying(10) |  | None |

## Table: gem_product
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| transaction_id | character varying(100) |  | None |
| product_code | character varying(200) |  | None |
| product_name | character varying(200) |  | None |
| product_brand | character varying(200) |  | None |
| quantity_ordered | double precision |  | None |
| unit_price | double precision |  | None |
| total_value | double precision |  | None |
| quantity_unit_type | character varying(25) |  | None |
| supplied_quantity | double precision |  | None |
| accepted_quantity | double precision |  | None |
| frieght_charge | double precision |  | None |
| expected_delivery_date | date |  | None |
| actual_delivery_date | date |  | None |
| project_code | character varying(14) |  | None |
| code_head | character varying(9) |  | None |
| sub_category | character varying(50) |  | None |
| sub_cat_id | character varying(3) |  | None |
| fk_gem_bill | bigint | FK | gem_bill |
| sgst | double precision |  | None |
| cgst | double precision |  | None |
| cess | double precision |  | None |
| freight_sgst | double precision |  | None |
| freight_cgst | double precision |  | None |
| freight_cess | double precision |  | None |
| hsn_code | character varying(100) |  | None |
| fk_consignment_detail | bigint | FK | consignment_detail |
| utgst | double precision |  | None |
| freight_utgst | double precision |  | None |
| igst | double precision |  | None |
| freight_igst | double precision |  | None |
| offering_type | character varying(10) |  | None |
| product_category_id | text |  | None |
| product_category_name | text |  | None |
| contract_start_date | date |  | None |
| contract_end_date | date |  | None |
| invoice_from_date | date |  | None |
| invoice_to_date | date |  | None |
| type_of_service_bill | character varying(20) |  | None |
| tds_under_gst | character varying(10) |  | None |
| tds_under_incometax | character varying(10) |  | None |

## Table: gembill_payment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_bill | integer | FK | bill |
| fk_gem_bill | integer | FK | gem_bill |
| order_id | character varying(25) |  | None |
| transaction_id | character varying(100) |  | None |
| bill_no | character varying(50) |  | None |
| cda_code | character varying(2) |  | None |
| unit_code | character varying(10) |  | None |
| bill_amount | double precision |  | None |
| bill_date | date |  | None |
| final_bill_date | date |  | None |
| supply_order_no | character varying(50) |  | None |
| supply_order_date | date |  | None |
| crac_no | character varying(50) |  | None |
| crac_date | date |  | None |
| gem_invoice_no | character varying(50) |  | None |
| invoice_no | character varying(50) |  | None |
| invoice_date | date |  | None |
| created_at_honeyb | date |  | None |
| days_due | character varying(10) |  | None |
| recoveries | double precision |  | None |
| disallowance | double precision |  | None |
| amount_passed | double precision |  | None |
| amount_to_be_paid | double precision |  | None |
| payment_reference_no | character varying(12) |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| payment_status | character varying(10) |  | None |
| failure_reason | text |  | None |
| deduction | boolean |  | None |
| deduction_amount | double precision |  | None |
| paid_online_offline | character varying(10) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: gst_booking
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_bill | bigint | FK | bill |
| code_head | character varying(9) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| gst_type | character varying(5) |  | None |
| gst5_amount | double precision |  | None |
| gst12_amount | double precision |  | None |
| gst18_amount | double precision |  | None |
| gst28_amount | double precision |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| gst3_amount | double precision |  | None |

## Table: gst_tds
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_vendor | integer | FK | vendor |
| bill_amount | double precision |  | None |
| tds_igst | double precision |  | None |
| tds_cgst | double precision |  | None |
| tds_sgst | double precision |  | None |
| tds_utgst | double precision |  | None |
| gst_type | character varying(6) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| upload_batch | character varying(50) |  | None |
| upload_date | date |  | None |
| cpin_no | character varying(50) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_vendor_gstin | bigint | FK | vendor_gstin |
| gst_tds_rate_percent | double precision |  | None |
| tds_igst_import | double precision |  | None |
| invoice_no | character varying(25) |  | None |
| invoice_date | date |  | None |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: gst_tds_payment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_vendor | integer | FK | vendor |
| bill_amount | double precision |  | None |
| tds_igst | double precision |  | None |
| tds_cgst | double precision |  | None |
| tds_sgst | double precision |  | None |
| tds_utgst | double precision |  | None |
| total_tds_recovery | double precision |  | None |
| cpin_no | character varying(50) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| created_at | timestamp without time zone |  | None |
| total_records | integer |  | None |
| payment_mode | character(1) |  | None |
| processed_month | character varying(7) |  | None |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| tds_igsti | double precision |  | None |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: iaf_cda13
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| cda13_no | character varying(10) |  | None |
| cda13_date | date |  | None |
| fk_schedule3 | integer | FK | schedule3 |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| old_dak_id | character varying(15) |  | None |
| payment_type | character varying(2) |  | None |
| fk_bank_pan_detail | integer | FK | bank_pan_detail |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| amount | double precision |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| fk_section | integer | FK | section |
| section_code | integer |  | None |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_imprest | integer | FK | imprest |
| fk_dad_office | integer | FK | dad_office |
| rejected_cmp_reference_no | character varying(20) |  | None |
| rejected_cheque_no | character varying(15) |  | None |
| rejection_type | character(1) |  | None |
| multiple_cmp_rejection | character(1) |  | None |
| item_amount | double precision |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |

## Table: imprest
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| imprest_acno | character varying(25) |  | None |
| authority_no | character varying(15) |  | None |
| authority_date | date |  | None |
| fk_bank | integer | FK | bank |
| imprest_bank_acno | character varying(15) |  | None |
| opening_date | date |  | None |
| closing_date | date |  | None |
| closing_authority_no | character varying(50) |  | None |
| closing_authority_date | date |  | None |
| fk_dak | bigint | FK | dak |
| task_holder | character varying(3) |  | None |
| closing_reason | text |  | None |
| fk_unit | integer | FK | unit |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| pao_code | character varying(3) |  | None |
| cda_code | character varying(2) |  | None |
| imprest_type | character varying(2) |  | None |
| fk_central_bank | bigint | FK | aaa_central_bank |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: imprest_account
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_imprest | integer | FK | imprest |
| opening_balance | integer |  | None |
| total_credit | integer |  | None |
| total_debit | integer |  | None |
| closing_balance | integer |  | None |
| account_month | character varying(2) |  | None |
| account_year | character varying(4) |  | None |
| compilation_month | character varying(2) |  | None |
| compilation_year | character varying(4) |  | None |
| voucher_no | integer |  | None |
| audited | boolean |  | None |
| fk_dak | bigint | FK | dak |
| acknowledgement_number | character varying(25) |  | None |
| acknowledgement_date | date |  | None |
| surprise_check_number | character varying(25) |  | None |
| surprise_check_date | date |  | None |
| fk_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |

## Table: imprest_holder
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_imprest | integer | FK | imprest |
| imprest_holder_name | character varying(30) |  | None |
| imprest_holder_rank | character varying(15) |  | None |
| designation | character varying(15) |  | None |
| specimen_signature | text |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| sanction_no | character varying(25) |  | None |
| sanction_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: imprest_schedule
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| schedule_no | character varying(50) |  | None |
| schedule_date | date |  | None |
| fk_dak | bigint | FK | dak |
| fk_vrhead_desc | bigint | FK | vrhead_desc |
| voucher_nos | character varying(255) |  | None |
| sign_rc | character varying(2) |  | None |
| code_head | character varying(20) |  | None |
| amount | numeric(15,2) |  | None |
| section_group | character varying(50) |  | None |
| return_date | date |  | None |
| fk_auditor | bigint | FK | usr |
| auditor_date | date |  | None |
| fk_aao | bigint | FK | usr |
| aao_date | date |  | None |

## Table: it_recovery_others
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| month | character varying(7) |  | None |
| it_recovery_amount | integer |  | None |
| cess_amount | integer |  | None |
| secondary_cess_amount | integer |  | None |
| surcharge_amount | integer |  | None |
| created_by | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: it_register
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_bill | bigint | FK | bill |
| fk_code_head | integer | FK | code_head |
| fk_schedule3 | integer | FK | schedule3 |
| fk_punching_medium | bigint | FK | punching_medium |
| paid_month | character varying(7) |  | None |
| amount_100_percent | double precision |  | None |
| amount_95_percent | double precision |  | None |
| amount_90_percent | double precision |  | None |
| amount_5_percent | double precision |  | None |
| amount_10_percent | double precision |  | None |
| amount_98_percent | double precision |  | None |
| amount_2_percent | double precision |  | None |
| amount_on_which_it_tobe_recovered | double precision |  | None |
| it_recovery_amount | double precision |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: it_saving_others
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_vendor | integer | FK | vendor |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_it_saving_section | integer | FK | it_saving_section |
| amount | double precision |  | None |
| assessment_year | character varying(9) |  | None |
| payment_date | date |  | None |
| voucher_no | character varying(25) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: lch_expenditure
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_code_head | integer | FK | code_head |
| financial_year | character varying(9) |  | None |
| month | character varying(7) |  | None |
| amount | double precision |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| rollback | boolean |  | None |
| rollback_date | date |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| code_head_str | character varying(9) |  | None |
| opening_balance | double precision |  | None |
| closing_balance | double precision |  | None |
| project_code | character varying(14) |  | None |
| fk_allotment_detail | integer | FK | allotment_detail |
| fk_unit | integer | FK | unit |
| reviewed | boolean |  | None |
| review_date | date |  | None |
| fk_dad_office | integer | FK | dad_office |
| pm_code_head | character varying(9) |  | None |
| dv_no | integer |  | None |
| adjustment | boolean |  | None |
| approved | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_old_dak | integer | FK | dak |
| adj_type | character(1) |  | None |
| adj_trans_type | character(1) |  | None |
| int_number1 | integer |  | None |
| value1 | character varying(50) |  | None |
| value2 | character varying(50) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: lp_item
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_office | integer | FK | dad_office |
| item_description | character varying(25) |  | None |
| unit | character varying(10) |  | None |
| case_pack | integer |  | None |
| rate | double precision |  | None |
| fk_vendor | integer | FK | vendor |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: ltc_cv_invoice_detail
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| record_type | character varying(3) |  | None |
| fk_dak | bigint | FK | dak |
| fk_dad_tada_ltc_bill | bigint | FK | dad_tada_ltc_bill |
| fk_civ_tada_ltc_bill | bigint | FK | civ_tada_ltc_bill |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_civ_employee | bigint | FK | civ_employee |
| invoice_no | character varying(50) |  | None |
| fk_unit | integer | FK | unit |
| fk_dad_office | integer | FK | dad_office |
| invoice_date | date |  | None |
| gstin_no | character varying(15) |  | None |
| vendor_name | character varying(100) |  | None |
| item_desc | character varying(100) |  | None |
| total_amount | integer |  | None |
| gst_rate | double precision |  | None |
| igst_amount | double precision |  | None |
| sgst_amount | double precision |  | None |
| cgst_amount | double precision |  | None |
| utgst_amount | double precision |  | None |
| record_status | character varying(1) |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| mode_of_payment | character varying(25) |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: master_price
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_filling_station | integer | FK | filling_station |
| fk_vendor | integer | FK | vendor |
| mpl_no | character varying(30) |  | None |
| mpl_from_date | date |  | None |
| mpl_to_date | date |  | None |
| qty_unit | character varying(6) |  | None |
| fk_product | integer | FK | product |
| billing_type | character(1) |  | None |
| mpl_price | double precision |  | None |
| mpl_discount | double precision |  | None |
| local_tax | double precision |  | None |
| vat | double precision |  | None |
| gst | double precision |  | None |
| net_price | double precision |  | None |
| created_at | timestamp without time zone |  | None |
| xml_file_name | character varying(100) |  | None |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: medical_tests
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_medical_rate | integer | FK | medical_rate |
| amount | integer |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: ncc_contingency_claims
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_unit | integer | FK | unit |
| fk_group_hq_unit | integer | FK | unit |
| batch_no | character varying(20) |  | None |
| month_ending | character varying(7) |  | None |
| project_code | character varying(14) |  | None |
| fk_bill_type | integer | FK | bill_type |
| code_head | character varying(9) |  | None |
| cadet_no | character varying(20) |  | None |
| cadet_name | character varying(100) |  | None |
| parent_name | character varying(100) |  | None |
| name_of_edn_institution | character varying(200) |  | None |
| wing | character varying(10) |  | None |
| backward_district | boolean |  | None |
| aadhar_no | character varying(12) |  | None |
| mobile_no | character varying(15) |  | None |
| email_id | character varying(50) |  | None |
| mandate_form_number | character varying(20) |  | None |
| mandate_form_received | boolean |  | None |
| fin_year | character varying(9) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| amount | integer |  | None |
| ifsc | character varying(11) |  | None |
| acno | character varying(60) |  | None |
| fk_vendor | integer | FK | vendor |
| fk_bpd | bigint | FK | bank_pan_detail |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| value1 | character varying(50) |  | None |
| value2 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| int_number2 | integer |  | None |
| fk_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_group_hq_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: nidhi_trans
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_civ_employee | bigint | FK | civ_employee |
| batch_no | integer |  | None |
| gpf_no | integer |  | None |
| gpf_cd | character(1) |  | None |
| trans_code | character(1) |  | None |
| emp_type | character varying(3) |  | None |
| cda_code | integer |  | None |
| unit | character varying(14) |  | None |
| comp_month | character varying(7) |  | None |
| dvno | integer |  | None |
| pbill_month | character varying(7) |  | None |
| sign1 | character varying(2) |  | None |
| sub | integer |  | None |
| sign2 | character varying(2) |  | None |
| refund | integer |  | None |
| status | character varying(10) |  | None |
| pbill_no | character varying(50) |  | None |
| section_code | character varying(6) |  | None |
| vr_class | integer |  | None |
| rc | character varying(2) |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |
| reason | text |  | None |
| fk_usr | integer | FK | usr |
| api_call | timestamp with time zone |  | None |
| api_response | integer |  | None |
| created_at | timestamp with time zone |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_auditor | integer |  | None |
| fk_aao | integer |  | None |
| fk_sao | integer |  | None |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| sao_date | date |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| transcription_type | character(1) |  | None |

## Table: nps_upload_voucher
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_section | integer | FK | section |
| pm_section_code | character varying(4) |  | None |
| upload_month | character varying(7) |  | None |
| no_of_records | integer |  | None |
| upload_amount | double precision |  | None |
| employee_type | character varying(6) |  | None |
| fk_dak | bigint | FK | dak |
| fk_vendor | integer | FK | vendor |
| fk_bank_pan_detail | bigint | FK | bank_pan_detail |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| reason | text |  | None |
| paofin | character varying(30) |  | None |
| nps_gc | double precision |  | None |
| nps_ec | double precision |  | None |
| interest_on_late_upload | double precision |  | None |
| cda_sanction_no | character varying(50) |  | None |
| cda_sanction_date | date |  | None |
| pension_code_head | character varying(9) |  | None |
| ec_code_head | character varying(9) |  | None |
| gc_code_head | character varying(9) |  | None |
| fk_unit | integer | FK | unit |
| fk_bill_type | integer | FK | bill_type |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dad_employee | bigint | FK | dad_employee |
| other_employee_details | character varying(100) |  | None |
| payment_to | character varying(2) |  | None |
| remarks | text |  | None |
| pension_scheme | character varying(3) |  | None |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: omro
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_bank | integer | FK | bank |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| section_code | character varying(4) |  | None |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dad_employee | bigint | FK | dad_employee |
| fk_dad_office | integer | FK | dad_office |
| fk_unit | integer | FK | unit |
| fk_dmro | integer | FK | dmro |
| min_no | character varying(17) |  | None |
| mro_date | date |  | None |
| memo_no | character varying(30) |  | None |
| memo_date | date |  | None |
| received_month | character varying(7) |  | None |
| adjustment_month | character varying(7) |  | None |
| voucher_number | character varying(15) |  | None |
| voucher_date | date |  | None |
| amount | double precision |  | None |
| remittance_detail | text |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| other_depositor_detail | character varying(100) |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| item_amount | double precision |  | None |
| depositor_type | character varying(6) |  | None |
| fk_vendor | bigint | FK | vendor |
| pan_no | character varying(10) |  | None |
| it_amount | integer |  | None |
| project_code | character varying(14) |  | None |
| personal_claim_status | character(1) |  | None |
| personal_claim_settlement_dak_id | character(15) |  | None |
| mro_type | character(1) |  | None |
| adjusted_in_claim | double precision |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_bank | bigint | FK | aaa_central_bank |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |
| fk_go | integer |  | None |
| fk_jcda | integer |  | None |
| fk_cda | integer |  | None |
| go_date | date |  | None |
| jcda_date | date |  | None |
| cda_date | date |  | None |

## Table: outward_dak
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| despatch_date | date |  | None |
| fk_usr_rsec | integer | FK | usr |
| despatch_mode | character varying(15) |  | None |
| receipt_no | character varying(25) |  | None |
| receipt_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: pay_code
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| pay_code | character varying(6) |  | None |
| description | character varying(40) |  | None |
| debit_credit | character(1) |  | None |
| receipt_charge | character(1) |  | None |
| code_head | character varying(9) |  | None |
| taxable | boolean |  | None |
| pay_module | character varying(3) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| personal | boolean |  | None |
| project_head | character varying(7) |  | None |
| created_at | timestamp without time zone |  | None |
| group_head | character varying(7) |  | None |
| fk_office_id | integer | FK | dad_office |
| dad_pm_group | character varying(4) |  | None |
| non_dad_pm_group | character varying(4) |  | None |
| sort_order | integer |  | None |

## Table: pol_fuel_type
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fuel_grade | character varying(20) |  | None |
| fuel_type | character varying(30) |  | None |
| ppd_available | boolean |  | None |
| created_at | timestamp without time zone |  | None |

## Table: pol_invoice
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| invoice_no | character varying(30) |  | None |
| invoice_date | date |  | None |
| fk_product | integer | FK | product |
| qty_unit | character varying(6) |  | None |
| invoice_quantity | double precision |  | None |
| base_rate | double precision |  | None |
| applied_charges | double precision |  | None |
| fk_filling_station | integer | FK | filling_station |
| billing_type | character(1) |  | None |
| invoice_amount | double precision |  | None |
| dr_note_amount | double precision |  | None |
| cr_note_amount | double precision |  | None |
| overhead_amount | double precision |  | None |
| inv_pdf_name | character varying(50) |  | None |
| dr_note_pdf_name | character varying(50) |  | None |
| cr_note_pdf_name | character varying(50) |  | None |
| utr_no | character varying(20) |  | None |
| utr_date | date |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| fk_contract_agreement | integer | FK | contract_agreement |
| fk_supply_order | integer | FK | supply_order |
| fk_bill | integer | FK | bill |
| xml_file_name | character varying(100) |  | None |
| created_at | timestamp without time zone |  | None |
| utr_xml_file | character varying(75) |  | None |
| discount_rate | double precision |  | None |
| basic_amount | double precision |  | None |
| discount_amount | double precision |  | None |
| tax_amount | double precision |  | None |
| pto_charges_amount | double precision |  | None |
| delivery_charges_amount | double precision |  | None |
| invoice_net_amount | double precision |  | None |
| delivery_mode | character(1) |  | None |
| fk_dak | bigint | FK | dak |

## Table: provisional_payment
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_cfa | integer | FK | cfa |
| fk_code_head | integer | FK | code_head |
| fk_unit | integer | FK | unit |
| month | character varying(7) |  | None |
| sanction_amount | double precision |  | None |
| cfa_sanction_no | character varying(100) |  | None |
| cfa_sanction_date | date |  | None |
| record_status | character(1) |  | None |
| remarks | text |  | None |
| reason | text |  | None |
| regularized | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| fk_go | integer | FK | usr |
| fk_cda | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| go_date | date |  | None |
| cda_date | date |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| cd_head | character varying(9) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| fk_dad_office | integer | FK | dad_office |
| payment_date | date |  | None |
| fund_allotment_date | date |  | None |
| project_code | character varying(14) |  | None |
| approved | boolean |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: punching_medium
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_unit | integer | FK | unit |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| batch_no | integer |  | None |
| pm_month_year | character varying(7) |  | None |
| pm_section | integer |  | None |
| cda_code | integer |  | None |
| voucher_class | integer |  | None |
| voucher_no | integer |  | None |
| category_head | character varying(2) |  | None |
| code_head | character varying(3) |  | None |
| detail_head | character varying(2) |  | None |
| sign_rc | character varying(2) |  | None |
| amount | double precision |  | None |
| pm_date | date |  | None |
| responding_cda_code | integer |  | None |
| responding_cda_section | integer |  | None |
| passed | boolean |  | None |
| dpsheet_generated | boolean |  | None |
| neft_generated | boolean |  | None |
| fk_dids | integer | FK | dids |
| imprest_account | integer |  | None |
| naration | text |  | None |
| cancelled | boolean |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| fk_go | integer | FK | usr |
| fk_jcda | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| go_date | date |  | None |
| jcda_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| detail_code_head | character varying(9) |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_consolidated_dak | bigint | FK | dak |
| upload_file_generated | boolean |  | None |
| upload_file_gen_date | date |  | None |
| upload_batch | character varying(20) |  | None |
| verified_with_aic | boolean |  | None |
| fk_allotment_detail | integer | FK | allotment_detail |
| project_code | character varying(14) |  | None |
| ucc_code | character varying(6) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| fund_availability_before | double precision |  | None |
| fund_availability_after | double precision |  | None |
| value1 | character varying(100) |  | None |
| value2 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| int_number2 | integer |  | None |
| budget_allotment | double precision |  | None |
| gst_parent_code_head | character varying(9) |  | None |
| fk_dad_office | integer | FK | dad_office |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| nature | character varying(10) |  | None |
| cmp_batch | character varying(25) |  | None |
| ncs_transaction_id | character varying(25) |  | None |
| ncs_old_transaction_id | character varying(25) |  | None |
| ncs_response | character varying(10) |  | None |
| old_upload_batch | character varying(15) |  | None |
| ncs_remarks | character varying(200) |  | None |
| capital_id | character varying(15) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: ration_money
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| ic_no | character varying(8) |  | None |
| ic_check_digit | character(1) |  | None |
| ic_name | character varying(25) |  | None |
| ic_rank | character varying(8) |  | None |
| fk_unit | integer | FK | unit |
| from_date | date |  | None |
| to_date | date |  | None |
| amount_claimed | double precision |  | None |
| arrears_new | character(1) |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| passed | boolean |  | None |
| month | character varying(7) |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_bill | bigint | FK | bill |
| ration_rate | character varying(3) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: recoveries
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_recovery_code | integer | FK | recovery_code |
| amount | integer |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| code_head | character varying(9) |  | None |
| tax_recoverable_amount | double precision |  | None |
| remarks | text |  | None |
| recovery_rule | character varying(10) |  | None |
| recovery_percentage | double precision |  | None |
| recovery_for_days | integer |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_vendor | integer | FK | vendor |
| recovery_month | character varying(7) |  | None |
| contract_amount | double precision |  | None |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: recovery_code
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| recovery_description | character varying(100) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| code_head | character varying(9) |  | None |
| sign_rc | character varying(2) |  | None |
| fk_section | integer | FK | section |
| refund_sign_rc | character varying(2) |  | None |
| recovery_category | character varying(3) |  | None |
| record_status | character(1) |  | None |
| tax_slab | character varying(10) |  | None |

## Table: rejection
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_rejection_detail | integer | FK | rejection_detail |
| amount | integer |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| letter_no | character varying(50) |  | None |
| reference_no | character varying(100) |  | None |
| letter_date | date |  | None |
| reference_date | date |  | None |
| remarks | text |  | None |
| current_record | boolean |  | None |
| sr_code | character varying(3) |  | None |

## Table: rent
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| sync_id | integer |  | None |
| fk_dak | bigint | FK | dak |
| fk_civ_employee | bigint | FK | civ_employee |
| fk_dad_employee | bigint | FK | dad_employee |
| cda_code | character varying(2) |  | None |
| unit_code | character varying(14) |  | None |
| dad_nondad | character varying(10) |  | None |
| gpf_pran_account_no | character varying(16) |  | None |
| name | character varying(100) |  | None |
| designation | character varying(50) |  | None |
| uabso | character varying(50) |  | None |
| quarter_no | character varying(50) |  | None |
| station | character varying(75) |  | None |
| bill_no | character varying(75) |  | None |
| bill_date | date |  | None |
| lf_crfl | character varying(35) |  | None |
| lf_rate | double precision |  | None |
| lfee_from_date | date |  | None |
| lfee_to_date | date |  | None |
| lfee_amount | integer |  | None |
| elec_from_date | date |  | None |
| elec_to_date | date |  | None |
| uc_type | character varying(10) |  | None |
| elec_units | double precision |  | None |
| elec_amount | integer |  | None |
| water_from_date | date |  | None |
| water_to_date | date |  | None |
| water_amount | integer |  | None |
| furniture_from_date | date |  | None |
| furniture_to_date | date |  | None |
| furniture_amount | integer |  | None |
| misc_charges | integer |  | None |
| rent_bill_total | integer |  | None |
| batch_no | character varying(10) |  | None |
| month_ending | character varying(7) |  | None |
| transaction_type | character varying(1) |  | None |
| upload_file_name | text |  | None |
| fk_usr | integer | FK | usr |
| usr_date | date |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |
| approved | boolean |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| rejection_reason | text |  | None |
| sl_no_of_item | integer |  | None |
| debited_me | character varying(7) |  | None |
| status | character varying(50) |  | None |
| recovery_mode | character varying(50) |  | None |
| garrage_from_date | date |  | None |
| garrage_to_date | date |  | None |
| garrage_charge | integer |  | None |
| servant_from_date | date |  | None |
| servant_to_date | date |  | None |
| servant_charge | integer |  | None |
| qtr_pool | character varying(20) |  | None |
| sync_status | integer |  | None |
| accept_rej_hold | character varying(20) |  | None |
| preprocess_record_status | character(1) |  | None |
| preprocess_approved | boolean |  | None |
| fk_central_civ_employee | integer | FK | aaa_central_civ_employee |

## Table: schedule3
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_section | integer | FK | section |
| fk_dad_office | integer | FK | dad_office |
| month | character varying(7) |  | None |
| dp_sheet_no | integer |  | None |
| dp_sheet_date | date |  | None |
| schedule3_item_no | integer |  | None |
| dv_no_from | integer |  | None |
| dv_no_to | integer |  | None |
| schedule3_amount | double precision |  | None |
| npb_date | date |  | None |
| cheque_no | character varying(25) |  | None |
| cheque_date | date |  | None |
| cheque_status | character(1) |  | None |
| remarks | text |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| transcription_type | character(1) |  | None |
| linked_with_scroll | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| section_code | integer |  | None |
| fk_cheque_slip | bigint | FK | cheque_slip |
| cmp_batch | character varying(25) |  | None |
| fk_dak | bigint | FK | dak |
| record_status | character(1) |  | None |
| fk_ecs_payment_mode | integer | FK | ecs_payment_mode |
| treasury_bank_acno | character varying(20) |  | None |
| treasury_bank_ifsc | character varying(11) |  | None |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_sh3_usr | integer | FK | usr |
| fk_auditor_rej | integer | FK | usr |
| auditor_date_rej | date |  | None |
| fk_aao_rej | integer | FK | usr |
| aao_date_rej | date |  | None |
| fk_ao_rej | integer | FK | usr |
| ao_date_rej | date |  | None |
| fk_auditor_accounts_rej | integer | FK | usr |
| auditor_date_accounts_rej | date |  | None |
| fk_aao_accounts_rej | integer | FK | usr |
| aao_date_accounts_rej | date |  | None |
| fk_ao_accounts_rej | integer | FK | usr |
| ao_date_accounts_rej | date |  | None |
| rejection_status | character(1) |  | None |
| rejection_approved_ds | boolean |  | None |
| rejection_approved_as | boolean |  | None |
| rejection_reason | text |  | None |
| cda13_no | character varying(10) |  | None |
| cda13_date | date |  | None |
| rejection_scroll_no | character varying(20) |  | None |
| rejection_scroll_date | date |  | None |
| beneficiary_detail_other_chq | character varying(100) |  | None |
| fk_cda13_bpd | bigint | FK | bank_pan_detail |
| upload_batch | character varying(20) |  | None |
| ncs_response_code | character varying(3) |  | None |
| fk_cda13_central_beneficiary | bigint | FK | aaa_central_beneficiary |
| fk_central_unit | bigint | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: section
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| section_name | character varying(20) |  | None |
| section_group | character varying(15) |  | None |
| dak_group_dest | character varying(4) |  | None |
| dak_group_src | character varying(2) |  | None |
| dak_entry | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_task_distribution_mode | integer | FK | task_distribution_mode |
| task_marking_at_rsec | boolean |  | None |
| dak_type_sequential | boolean |  | None |
| dak_entry_status | character(1) |  | None |
| record_status | character(1) |  | None |
| fk_usr | integer | FK | usr |
| remarks | text |  | None |
| last_update_date | timestamp without time zone |  | None |

## Table: security_deposit
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_contract_agreement | bigint | FK | contract_agreement |
| fk_supply_order | bigint | FK | supply_order |
| fk_vendor | integer | FK | vendor |
| sd_form | character varying(50) |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| amount | double precision |  | None |
| released | boolean |  | None |
| release_date | date |  | None |
| fk_add_auditor | integer | FK | usr |
| fk_add_aao | integer | FK | usr |
| fk_add_ao | integer | FK | usr |
| add_auditor_date | date |  | None |
| add_aao_date | date |  | None |
| add_ao_date | date |  | None |
| record_status | character(1) |  | None |
| transcription_type | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| fk_release_auditor | integer | FK | usr |
| fk_release_aao | integer | FK | usr |
| fk_release_ao | integer | FK | usr |
| release_aao_date | date |  | None |
| release_auditor_date | date |  | None |
| release_ao_date | date |  | None |
| approved | boolean |  | None |
| sdr_no | character varying(50) |  | None |
| sdr_date | date |  | None |
| add_submitted | boolean |  | None |
| release_submitted | boolean |  | None |
| fk_original_security_deposit | bigint | FK | security_deposit |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: specimen_signature
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| fk_cfa | integer | FK | cfa |
| fk_bill_type | integer | FK | bill_type |
| fk_office_id | integer | FK | dad_office |
| fk_section | integer | FK | section |
| signatory_type | character(1) |  | None |
| signatory_name | character varying(100) |  | None |
| signatory_designation | character varying(30) |  | None |
| authority_letter_no | character varying(100) |  | None |
| authority_letter_date | date |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| scanned_signature | bytea |  | None |
| fk_usr | integer | FK | usr |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| current_record | boolean |  | None |
| approved | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_vendor | integer | FK | vendor |
| fk_filling_station | integer | FK | filling_station |
| public_key | text |  | None |
| finger_print | text |  | None |
| fk_allotment_authority | integer | FK | allotment_authority |
| ss_file_name | character varying(100) |  | None |
| signatory_code | character varying(30) |  | None |
| remarks | text |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: ss_imprest
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit | integer | FK | unit |
| account_no | character varying(25) |  | None |
| month | character varying(7) |  | None |
| opening_balance | double precision |  | None |
| amount_paid | double precision |  | None |
| amount_spent | double precision |  | None |
| closing_balance | double precision |  | None |
| closed | boolean |  | None |
| fk_aao | integer | FK | usr |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_dak | bigint | FK | dak |
| account_type | character(1) |  | None |
| fk_auditor | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| reason | text |  | None |
| fk_central_unit | bigint | FK | aaa_central_unit |

## Table: status_code
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| status_name | character varying(15) |  | None |
| status_code | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: supply_order
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_cfa | integer | FK | cfa |
| reference_no | character varying(30) |  | None |
| reference_date | date |  | None |
| fk_supply_order_type | integer | FK | supply_order_type |
| supply_order_no | character varying(50) |  | None |
| supply_order_date | date |  | None |
| amount | double precision |  | None |
| ld_percentage | double precision |  | None |
| ld_type | character varying(5) |  | None |
| ld_waived | boolean |  | None |
| ld_waiver_authority | integer |  | None |
| scheduled_delivery_date | date |  | None |
| actual_delivery_date | date |  | None |
| extension_granted | boolean |  | None |
| extension_granting_authority | integer |  | None |
| amount_claimed_through_bill | double precision |  | None |
| so_closed | boolean |  | None |
| ammended | boolean |  | None |
| fk_original_supply_order | integer | FK | supply_order |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| fk_contract_agreement | bigint | FK | contract_agreement |
| skip_item_verification | boolean |  | None |
| paid_outside_tulip | double precision |  | None |
| fk_vendor_bpd | bigint | FK | bank_pan_detail |
| fk_supply_order_payment_terms | integer |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |
| fk_central_beneficiary | integer | FK | aaa_central_beneficiary |

## Table: supply_order_item_supplied
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_supply_order | bigint | FK | supply_order |
| fk_supply_order_item_desc | bigint | FK | supply_order_item_desc |
| supply_date | date |  | None |
| crv_no | character varying(10) |  | None |
| item_supplied | integer |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| remarks | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_bill | bigint | FK | bill |
| crv_date | date |  | None |

## Table: supply_order_rejection
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dak | bigint | FK | dak |
| fk_rejection_detail | integer | FK | rejection_detail |
| amount | integer |  | None |
| fk_usr | integer | FK | usr |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| letter_no | character varying(50) |  | None |
| reference_no | character varying(100) |  | None |
| letter_date | date |  | None |
| reference_date | date |  | None |
| remarks | text |  | None |
| current_record | boolean |  | None |

## Table: transfer_entry
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| fk_section | integer | FK | section |
| fk_task_usr | integer | FK | usr |
| fk_unit | integer | FK | unit |
| fk_vendor | integer | FK | vendor |
| fk_dad_office | integer | FK | dad_office |
| received_month | character varying(7) |  | None |
| section_code | integer |  | None |
| voucher_class | integer |  | None |
| te_month | character varying(7) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| amount | double precision |  | None |
| voucher_no | integer |  | None |
| fk_auditor | integer | FK | usr |
| auditor_date | date |  | None |
| fk_aao | integer | FK | usr |
| aao_date | date |  | None |
| fk_ao | integer | FK | usr |
| ao_date | date |  | None |
| fk_go | integer | FK | usr |
| go_date | date |  | None |
| fk_jcda | integer | FK | usr |
| jcda_date | date |  | None |
| fk_cda | integer | FK | usr |
| cda_date | date |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| approved | boolean |  | None |
| lch | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| project_code | character varying(14) |  | None |
| it_principal_amount | double precision |  | None |
| te_type | character(1) |  | None |
| narration | text |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: transfer_entry_trans
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_dak | bigint | FK | dak |
| month_ending | character varying(7) |  | None |
| fk_unit | integer | FK | unit |
| code_head | character varying(9) |  | None |
| fk_allotment_category | integer | FK | allotment_category |
| amount | double precision |  | None |
| fund_availability | double precision |  | None |
| sign_rc | character varying(2) |  | None |
| code_head_type | character(1) |  | None |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| reason | text |  | None |
| fk_office_id | integer | FK | dad_office |
| fk_usr | integer | FK | usr |
| parent_code_head | character varying(9) |  | None |
| fk_central_unit | integer | FK | aaa_central_unit |

## Table: unit
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_unit_category | integer | FK | unit |
| unit_code | character varying(10) |  | None |
| unit_name | character varying(75) |  | None |
| address1 | character varying(50) |  | None |
| address2 | character varying(50) |  | None |
| address3 | character varying(50) |  | None |
| station | character varying(25) |  | None |
| pin_code | character varying(6) |  | None |
| email | character varying(40) |  | None |
| phone1 | character varying(12) |  | None |
| phone2 | character varying(12) |  | None |
| fax | character varying(12) |  | None |
| co_rank | character varying(10) |  | None |
| co_name | character varying(20) |  | None |
| raised_date | date |  | None |
| closed_date | date |  | None |
| imprest_account_no | character varying(25) |  | None |
| ss_imprest_account_no | character varying(25) |  | None |
| hra_class | character varying(2) |  | None |
| tpta_class | character varying(2) |  | None |
| headquarters | boolean |  | None |
| fk_hqrs_unit | integer | FK | unit |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| mes_unit | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_lao | integer | FK | dad_office |
| fk_office_id | integer | FK | dad_office |
| fk_lic | integer | FK | vendor |
| fk_ptax | integer | FK | vendor |
| fk_pli | integer | FK | vendor |
| fk_state | integer | FK | state |
| ration_class | character(1) |  | None |
| ddo_regn_no | character varying(10) |  | None |
| tan_number | character varying(10) |  | None |
| reason | text |  | None |
| record_status | character(1) |  | None |
| service | character varying(9) |  | None |
| raised_authority_no | character varying(50) |  | None |
| raised_authority_date | date |  | None |
| closure_authority_no | character varying(50) |  | None |
| closure_authority_date | date |  | None |
| remarks | text |  | None |
| fk_closed_by_usr | integer | FK | usr |
| closed_by_usr_date | date |  | None |
| fis_unit_code | character varying(7) |  | None |
| value1 | character varying(50) |  | None |
| int_number1 | integer |  | None |
| nature_of_unit | character varying(10) |  | None |
| fk_sub_area | integer | FK | unit_command |
| fk_area | integer | FK | unit_command |
| fk_brig | integer | FK | unit_command |
| fk_divn | integer | FK | unit_command |
| fk_corps | integer | FK | unit_command |
| fk_command | integer | FK | unit_command |
| sus_no | character varying(10) |  | None |
| grant_bill_pre_post_audit | character varying(4) |  | None |
| engineering_regiment | boolean |  | None |
| coordinating_controller | character varying(2) |  | None |
| imprest_prototype_no | character varying(15) |  | None |
| uuid | character varying(14) |  | None |

## Table: usr
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| usr_name | character varying(50) |  | None |
| login_name | character varying(15) |  | None |
| account_no | character varying(8) |  | None |
| fk_dad_designation | integer | FK | dad_designation |
| head_of_office | boolean |  | None |
| gender | character(1) |  | None |
| fk_section | integer | FK | section |
| previous_link | integer |  | None |
| phone1 | character varying(15) |  | None |
| phone2 | character varying(15) |  | None |
| phone3 | character varying(15) |  | None |
| email | character varying(50) |  | None |
| enabled | boolean |  | None |
| from_date | date |  | None |
| to_date | date |  | None |
| salt | character varying(4) |  | None |
| hashed_password | character varying(60) |  | None |
| fk_usr | integer | FK | usr |
| last_password_changed_date | timestamp without time zone |  | None |
| last_successful_login | timestamp without time zone |  | None |
| last_failed_login | timestamp without time zone |  | None |
| failed_attempts | integer |  | None |
| ip_address_1 | character varying(15) |  | None |
| ip_address_2 | character varying(15) |  | None |
| ip_address_3 | character varying(15) |  | None |
| last_logged_in_ip_address | character varying(15) |  | None |
| hashed_password_used_1 | character varying(60) |  | None |
| hashed_password_used_2 | character varying(255) |  | None |
| hashed_password_used_3 | character varying(255) |  | None |
| ip_address_last_successful_login | character varying(15) |  | None |
| ip_address_last_failed_login | character varying(15) |  | None |
| scanned_signature | text |  | None |
| logged_in | boolean |  | None |
| reset_password | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| functional_usr | boolean |  | None |
| rol | character varying(60) |  | None |
| fk_parent_office | integer | FK | dad_office |
| record_status | character(1) |  | None |
| reason | text |  | None |
| hashed_spring_password | character varying(255) |  | None |
| reset_spring_password | boolean |  | None |

## Table: vendor
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_vendor_category | integer | FK | vendor_category |
| vendor_name | character varying(100) |  | None |
| address1 | character varying(100) |  | None |
| address2 | character varying(75) |  | None |
| city | character varying(30) |  | None |
| state | character varying(30) |  | None |
| mes_enlisted | boolean |  | None |
| enlistment_no | character varying(10) |  | None |
| vendor_class | character varying(3) |  | None |
| vendor_grade | character varying(2) |  | None |
| landline_telephone_no1 | character varying(12) |  | None |
| landline_telephone_no2 | character varying(12) |  | None |
| mobile_phone1 | character varying(10) |  | None |
| mobile_phone2 | character varying(10) |  | None |
| pan_number | character varying(10) |  | None |
| tan_number | character varying(10) |  | None |
| branch | boolean |  | None |
| fk_parent_vendor | integer | FK | vendor |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| last_modified_at | timestamp without time zone |  | None |
| fk_last_modified_by_usr | integer | FK | usr |
| pin_code | character varying(6) |  | None |
| fk_office_id | integer | FK | dad_office |
| old_vendor_no | integer |  | None |
| address3 | character varying(75) |  | None |
| email_id | character varying(50) |  | None |
| gstin | character varying(15) |  | None |
| fax_number1 | character varying(12) |  | None |
| fax_number2 | character varying(12) |  | None |
| aadhar_number | character varying(12) |  | None |
| aadhar_holder_name | character varying(50) |  | None |
| remarks | text |  | None |
| mandate_form_received | boolean |  | None |
| gem_vendor_code | character varying(20) |  | None |
| msme | boolean |  | None |
| allow_other_vendor_gstin | boolean |  | None |
| echs_unique_no | character varying(50) |  | None |
| lei | character varying(20) |  | None |
| msme_cat | character varying(1) |  | None |
| make_cat | character varying(2) |  | None |

## Table: vendor_category
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| category_name | character varying(30) |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |
| category_code | character varying(2) |  | None |

## Table: vendor_demand_register
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_dad_office | integer | FK | dad_office |
| fk_dak | bigint | FK | dak |
| demand_creation_mode | character(1) |  | None |
| recovery_mode | character(1) |  | None |
| cdr_no | character varying(12) |  | None |
| fk_vendor | bigint | FK | vendor |
| demand_month | character varying(7) |  | None |
| amount | integer |  | None |
| settled | boolean |  | None |
| fk_bill | bigint | FK | bill |
| fk_omro | integer | FK | omro |
| record_status | character(1) |  | None |
| created_at | timestamp without time zone |  | None |
| remarks | text |  | None |
| dv_te_no | integer |  | None |
| settlement_month | character varying(7) |  | None |
| demand_date | date |  | None |
| demand_approved | boolean |  | None |
| settlement_approved | boolean |  | None |
| settlement_date | date |  | None |
| fk_auditor_demand | integer | FK | usr |
| fk_aao_demand | integer | FK | usr |
| fk_ao_demand | integer | FK | usr |
| auditor_demand_date | date |  | None |
| aao_demand_date | date |  | None |
| ao_demand_date | date |  | None |
| fk_auditor_settlement | integer | FK | usr |
| fk_aao_settlement | integer | FK | usr |
| auditor_settlement_date | date |  | None |
| aao_settlement_date | date |  | None |
| ao_settlement_date | date |  | None |
| reason | text |  | None |
| fk_ao_settlement | integer | FK | usr |
| fk_central_vendor | integer | FK | aaa_central_vendor |

## Table: vendor_gstin
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | bigint | PK | None |
| fk_vendor | integer | FK | vendor |
| gstin | character varying(15) |  | None |
| gstin_state_code | character varying(2) |  | None |
| gstin_state_name | character varying(50) |  | None |
| fk_auditor | integer | FK | usr |
| fk_aao | integer | FK | usr |
| fk_ao | integer | FK | usr |
| auditor_date | date |  | None |
| aao_date | date |  | None |
| ao_date | date |  | None |
| approved | boolean |  | None |
| record_status | character(1) |  | None |
| reason | text |  | None |
| created_at | timestamp without time zone |  | None |
| fk_office_id | integer | FK | dad_office |

## Table: vendor_section
| Column Name | Data Type | Key Mapping | References Table |
|---|---|---|---|
| id | integer | PK | None |
| fk_section | integer | FK | section |
| fk_vendor | integer | FK | vendor |
| current_record | boolean |  | None |
| created_at | timestamp without time zone |  | None |
| fk_usr | integer | FK | usr |
| fk_office_id | integer | FK | dad_office |
| record_status | character(1) |  | None |
| fk_central_vendor | integer | FK | aaa_central_vendor |
