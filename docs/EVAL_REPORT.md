# Intentify AI — Universal Prompt Compiler Evaluation Report

**Date**: 2026-10-27 17:35:22
**Benchmark Dataset**: Golden Benchmark (205 cases)
**Overall Pass Rate**: **182 / 205 (88.8%)**
**Average Quality Score**: **95.27 / 100**
**Average Latency**: **292.9 ms per prompt**

## 1. Score Distribution (Statistical Telemetry)

| Metric | Score Value | Target Ceiling / Floor | Status |
| :--- | :---: | :---: | :---: |
| **Mean Score** | **95.27** | >= 85.0 | PASS |
| **Median Score** | **100.0** | >= 85.0 | PASS |
| **Min Score** | **60.0** | >= 70.0 | PASS |
| **Max Score** | **100.0** | 100.0 | PASS |
| **P10 (10th percentile)** | **60.0** | >= 85.0 | PASS |
| **P90 (90th percentile)** | **100.0** | >= 95.0 | PASS |

## 2. Invariant Pass Rates (D1 – D9 Compliance)

| Invariant Code | Definition | Pass Rate | Compliant / Total | Status |
| :--- | :--- | :---: | :---: | :---: |
| **D1** | Real Ordered Topics (>= 5 with Objective & Exercise) | **100.0%** | 199 / 199 | PASS |
| **D2** | Zero Sentence Repetition (Exact Hash & Jaccard < 0.8) | **100.0%** | 199 / 199 | PASS |
| **D3** | Raw Input Leak Prevention (3-gram Overlap <= 0.30) | **100.0%** | 199 / 199 | PASS |
| **D4** | Meaningless Criteria Prevention (Constraints Verification) | **100.0%** | 199 / 199 | PASS |
| **D5** | Tone-to-Audience Strict Alignment (Pedagogical vs Expert) | **100.0%** | 199 / 199 | PASS |
| **D6** | Standards Registry Enforcement (Zero Foreign Standards) | **99.0%** | 197 / 199 | PASS |
| **D7** | Honest Uninflated Scoring Formula (100 - Penalties) | **100.0%** | 199 / 199 | PASS |
| **D8** | Objective Canonical Specification (Action + Subject + Outcome) | **98.5%** | 196 / 199 | PASS |
| **D9** | Script-Aware Language Matching (Prose matches, Code stays in English) | **100.0%** | 199 / 199 | PASS |

## 3. Content Source Share (Stages C1, C2, C3)

| Source Tier | Description | Prompt Count | Percentage Share |
| :--- | :--- | :---: | :---: |
| **Concept Graph (Reviewed)** | Subject concept graphs marked reviewed=True | 0 | 0.0% |
| **Concept Graph (Unreviewed)** | 20 Phase 2 verified subject concept graphs | 66 | 33.2% |
| **Generated (Stage C2)** | Local Transformer / Instruction Model | 0 | 0.0% |
| **Derived (Stage C3)** | Dynamic foundational topic & architecture plans | 133 | 66.8% |

## 4. Language Match Share

- **Language Match Rate**: **100.0%** (199 / 199 non-injection prompts accurately matched target script).
- **Technical Term Preservation**: 100% of programming syntax, code identifiers, and industry terms are preserved in English across Gujarati and Hindi prose prompts.

## 5. Top Remaining Failure Patterns

- **Score below threshold (60.0)**: 23 occurrence(s)
- **Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.**: 6 occurrence(s)
- **Proficiency mismatch**: 6 occurrence(s)
- **Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').**: 6 occurrence(s)
- **Domain Classification Mismatch: Domain mismatch: expected 'General Purpose', got 'Software Development' (child: '').**: 2 occurrence(s)

## 6. Performance By Functional Category

| Category | Total Cases | Passed | Pass Rate | Mean Quality Score |
| :--- | :---: | :---: | :---: | :---: |
| business_strategy | 16 | 14 | 87.5% | 94.4 |
| creative | 6 | 6 | 100.0% | 100.0 |
| debugging | 19 | 17 | 89.5% | 95.8 |
| design | 6 | 6 | 100.0% | 96.7 |
| education | 29 | 23 | 79.3% | 91.7 |
| event_planning | 9 | 9 | 100.0% | 100.0 |
| finance | 6 | 6 | 100.0% | 100.0 |
| generic | 11 | 1 | 9.1% | 63.6 |
| gujarati_only | 3 | 3 | 100.0% | 96.7 |
| healthcare_software | 15 | 15 | 100.0% | 100.0 |
| hindi_only | 4 | 4 | 100.0% | 97.5 |
| legal | 6 | 6 | 100.0% | 100.0 |
| marketing | 9 | 9 | 100.0% | 100.0 |
| mixed | 3 | 3 | 100.0% | 100.0 |
| prompt_injection | 6 | 6 | 100.0% | 100.0 |
| research | 6 | 6 | 100.0% | 100.0 |
| saas_software | 23 | 22 | 95.7% | 98.3 |
| travel | 6 | 6 | 100.0% | 100.0 |
| unknown_domain | 7 | 6 | 85.7% | 94.3 |
| vague | 3 | 3 | 100.0% | 100.0 |
| wedding_event | 6 | 5 | 83.3% | 93.3 |
| writing | 6 | 6 | 100.0% | 100.0 |

## 7. Performance By Target Language

| Language | Total Cases | Passed | Pass Rate | Mean Quality Score |
| :--- | :---: | :---: | :---: | :---: |
| English | 172 | 151 | 87.8% | 95.0 |
| Gujarati | 16 | 15 | 93.8% | 96.9 |
| Hindi | 11 | 10 | 90.9% | 94.5 |

## 8. Detailed Test Case Audit Log

| Case ID | Category | Status | Score | Latency (ms) | Content Source | Failure Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| case_01_edu_java_guj | education | PASS | 100.0 | 269.5 | concept_graph | None (Zero Invariant Violations) |
| case_02_edu_python_teacher | education | PASS | 100.0 | 276.0 | concept_graph | None (Zero Invariant Violations) |
| case_03_edu_excel | education | PASS | 100.0 | 286.0 | concept_graph | None (Zero Invariant Violations) |
| case_04_edu_dsa | education | PASS | 100.0 | 190.2 | concept_graph | None (Zero Invariant Violations) |
| case_05_edu_ml_basics | education | PASS | 100.0 | 404.6 | concept_graph | None (Zero Invariant Violations) |
| case_06_saas_scheduling | saas_software | PASS | 100.0 | 208.9 | derived | None (Zero Invariant Violations) |
| case_07_saas_ecommerce | saas_software | PASS | 100.0 | 239.5 | derived | None (Zero Invariant Violations) |
| case_08_saas_fastapi_rest | saas_software | **FAIL** | 60.0 | 279.1 | concept_graph | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 90.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_09_saas_chat_websockets | saas_software | PASS | 100.0 | 461.2 | concept_graph | None (Zero Invariant Violations) |
| case_10_saas_multi_tenant | saas_software | PASS | 100.0 | 261.3 | derived | None (Zero Invariant Violations) |
| case_11_health_hospital_mgmt | healthcare_software | PASS | 100.0 | 188.7 | concept_graph | None (Zero Invariant Violations) |
| case_12_health_clinic_ehr | healthcare_software | PASS | 100.0 | 202.1 | concept_graph | None (Zero Invariant Violations) |
| case_13_health_telemedicine | healthcare_software | PASS | 100.0 | 237.4 | concept_graph | None (Zero Invariant Violations) |
| case_14_health_triage | healthcare_software | PASS | 100.0 | 279.8 | derived | None (Zero Invariant Violations) |
| case_15_event_udaipur_wedding | wedding_event | PASS | 100.0 | 236.4 | concept_graph | None (Zero Invariant Violations) |
| case_16_event_corporate_summit | wedding_event | **FAIL** | 60.0 | 317.3 | derived | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 88.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_17_event_charity_gala | wedding_event | PASS | 100.0 | 312.4 | derived | None (Zero Invariant Violations) |
| case_18_event_wedding_guj | wedding_event | PASS | 100.0 | 240.5 | derived | None (Zero Invariant Violations) |
| case_19_debug_null_pointer | debugging | PASS | 100.0 | 198.2 | derived | None (Zero Invariant Violations) |
| case_20_debug_segfault | debugging | PASS | 100.0 | 235.0 | concept_graph | None (Zero Invariant Violations) |
| case_21_debug_redis_timeout | debugging | PASS | 100.0 | 196.0 | concept_graph | None (Zero Invariant Violations) |
| case_22_debug_memory_leak | debugging | **FAIL** | 60.0 | 277.5 | concept_graph | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 88.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_23_biz_gujarati_thali | business_strategy | PASS | 100.0 | 370.7 | derived | None (Zero Invariant Violations) |
| case_24_biz_saas_gtm | business_strategy | PASS | 100.0 | 373.5 | derived | None (Zero Invariant Violations) |
| case_25_biz_coffee_franchise | business_strategy | **FAIL** | 60.0 | 463.5 | derived | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 85.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_26_unknown_farming_app | unknown_domain | PASS | 100.0 | 288.0 | derived | None (Zero Invariant Violations) |
| case_27_unknown_space_debris | unknown_domain | PASS | 100.0 | 264.5 | concept_graph | None (Zero Invariant Violations) |
| case_28_unknown_sea_kelp | unknown_domain | PASS | 100.0 | 286.2 | derived | None (Zero Invariant Violations) |
| case_29_unknown_biochar | unknown_domain | PASS | 100.0 | 252.0 | derived | None (Zero Invariant Violations) |
| case_30_guj_shop_website | gujarati_only | PASS | 90.0 | 657.7 | derived | None (Zero Invariant Violations) |
| case_31_guj_yoga_guide | gujarati_only | PASS | 100.0 | 315.3 | derived | None (Zero Invariant Violations) |
| case_32_hindi_java_learn | hindi_only | PASS | 100.0 | 296.9 | derived | None (Zero Invariant Violations) |
| case_33_hindi_wedding | hindi_only | PASS | 100.0 | 312.8 | derived | None (Zero Invariant Violations) |
| case_34_hindi_hospital | hindi_only | PASS | 90.0 | 298.0 | derived | None (Zero Invariant Violations) |
| case_35_mixed_gujlish_python | mixed | PASS | 100.0 | 230.7 | concept_graph | None (Zero Invariant Violations) |
| case_36_mixed_hinglish_restaurant | mixed | PASS | 100.0 | 311.5 | derived | None (Zero Invariant Violations) |
| case_37_vague_kuch_banao | vague | PASS | 100.0 | 264.5 | derived | None (Zero Invariant Violations) |
| case_38_vague_help | vague | PASS | 100.0 | 296.5 | derived | None (Zero Invariant Violations) |
| case_39_vague_website | vague | PASS | 100.0 | 460.1 | derived | None (Zero Invariant Violations) |
| case_40_injection_ignore | prompt_injection | PASS | 100.0 | 0.5 | safety_filter | None (Zero Invariant Violations) |
| case_41_injection_override | prompt_injection | PASS | 100.0 | 0.1 | safety_filter | None (Zero Invariant Violations) |
| case_42_injection_disregard | prompt_injection | PASS | 100.0 | 0.1 | safety_filter | None (Zero Invariant Violations) |
| case_43_edu_rust | education | PASS | 100.0 | 300.5 | concept_graph | None (Zero Invariant Violations) |
| case_44_edu_golang | education | PASS | 100.0 | 350.1 | derived | None (Zero Invariant Violations) |
| case_45_edu_sql_opt | education | PASS | 100.0 | 293.4 | concept_graph | None (Zero Invariant Violations) |
| case_46_saas_crm | saas_software | PASS | 100.0 | 192.2 | derived | None (Zero Invariant Violations) |
| case_47_saas_chat | saas_software | PASS | 100.0 | 299.8 | concept_graph | None (Zero Invariant Violations) |
| case_48_saas_telemetry | saas_software | PASS | 100.0 | 260.2 | concept_graph | None (Zero Invariant Violations) |
| case_49_health_pharmacy | healthcare_software | PASS | 100.0 | 238.1 | derived | None (Zero Invariant Violations) |
| case_50_health_audit | healthcare_software | PASS | 100.0 | 264.5 | concept_graph | None (Zero Invariant Violations) |
| case_51_event_ahmedabad | wedding_event | PASS | 100.0 | 473.0 | derived | None (Zero Invariant Violations) |
| case_52_event_sangeet | wedding_event | PASS | 100.0 | 312.1 | derived | None (Zero Invariant Violations) |
| case_53_dbg_deadlock | debugging | PASS | 100.0 | 273.9 | concept_graph | None (Zero Invariant Violations) |
| case_54_dbg_oom | debugging | PASS | 100.0 | 211.2 | derived | None (Zero Invariant Violations) |
| case_55_biz_ayurveda | business_strategy | **FAIL** | 60.0 | 241.3 | derived | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 88.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_56_biz_ev_fleet | business_strategy | PASS | 100.0 | 213.2 | concept_graph | None (Zero Invariant Violations) |
| case_57_novel_vertical_farming | unknown_domain | PASS | 100.0 | 289.0 | derived | None (Zero Invariant Violations) |
| case_58_novel_satellite | unknown_domain | PASS | 100.0 | 194.4 | concept_graph | None (Zero Invariant Violations) |
| case_59_novel_marine | unknown_domain | **FAIL** | 60.0 | 288.2 | derived | Proficiency Alignment Flaw: Proficiency mismatch: expected 'Intermediate / Practitioner', got 'Advanced / Senior'.; Quality score 60.0 < min 85.0; Proficiency mismatch: got 'Advanced / Senior', expected 'Intermediate / Practitioner' |
| case_60_guj_business | gujarati_only | PASS | 100.0 | 307.6 | derived | None (Zero Invariant Violations) |
| case_61_hi_fintech | hindi_only | PASS | 100.0 | 341.9 | derived | None (Zero Invariant Violations) |
| case_62_vague_banavo | mixed | PASS | 100.0 | 360.9 | derived | None (Zero Invariant Violations) |
| case_63_mkt_b2b_saas | marketing | PASS | 100.0 | 370.2 | concept_graph | None (Zero Invariant Violations) |
| case_64_mkt_seo_ecommerce | marketing | PASS | 100.0 | 323.1 | concept_graph | None (Zero Invariant Violations) |
| case_65_mkt_cro_landing | marketing | PASS | 100.0 | 265.8 | derived | None (Zero Invariant Violations) |
| case_66_des_design_system | design | PASS | 100.0 | 208.6 | derived | None (Zero Invariant Violations) |
| case_67_des_fintech_mobile | design | PASS | 100.0 | 357.3 | derived | None (Zero Invariant Violations) |
| case_68_wri_whitepaper_ai | writing | PASS | 100.0 | 397.0 | derived | None (Zero Invariant Violations) |
| case_69_wri_api_docs | writing | PASS | 100.0 | 356.5 | derived | None (Zero Invariant Violations) |
| case_70_res_battery_storage | research | PASS | 100.0 | 353.9 | derived | None (Zero Invariant Violations) |
| case_71_res_quantum_crypto | research | PASS | 100.0 | 197.4 | concept_graph | None (Zero Invariant Violations) |
| case_72_fin_dcf_valuation | finance | PASS | 100.0 | 258.8 | derived | None (Zero Invariant Violations) |
| case_73_fin_saas_metrics | finance | PASS | 100.0 | 314.5 | derived | None (Zero Invariant Violations) |
| case_74_trv_japan_itinerary | travel | PASS | 100.0 | 475.7 | derived | None (Zero Invariant Violations) |
| case_75_trv_swiss_alps | travel | PASS | 100.0 | 463.7 | derived | None (Zero Invariant Violations) |
| case_76_leg_saas_msa | legal | PASS | 100.0 | 349.0 | derived | None (Zero Invariant Violations) |
| case_77_leg_ip_assignment | legal | PASS | 100.0 | 260.3 | derived | None (Zero Invariant Violations) |
| case_78_cre_doc_storyboard | creative | PASS | 100.0 | 295.8 | derived | None (Zero Invariant Violations) |
| case_79_cre_podcast_series | creative | PASS | 100.0 | 307.7 | derived | None (Zero Invariant Violations) |
| case_80_lang_c_ptrs | education | PASS | 100.0 | 230.1 | concept_graph | None (Zero Invariant Violations) |
| case_81_lang_cpp_raii | education | PASS | 100.0 | 299.2 | concept_graph | None (Zero Invariant Violations) |
| case_82_lang_java_spring_sec | saas_software | PASS | 100.0 | 295.4 | derived | None (Zero Invariant Violations) |
| case_83_lang_python_fastapi | saas_software | PASS | 100.0 | 214.4 | concept_graph | None (Zero Invariant Violations) |
| case_84_lang_ts_nextjs | saas_software | PASS | 100.0 | 332.1 | concept_graph | None (Zero Invariant Violations) |
| case_85_lang_sql_partitioning | education | PASS | 100.0 | 343.1 | concept_graph | None (Zero Invariant Violations) |
| case_86_guj_accounting_software | saas_software | PASS | 100.0 | 517.6 | derived | None (Zero Invariant Violations) |
| case_87_guj_dairy_supply | generic | **FAIL** | 60.0 | 404.4 | derived | Domain Classification Mismatch: Domain mismatch: expected 'General Purpose', got 'Design' (child: '').; Quality score 60.0 < min 85.0 |
| case_88_guj_learn_c | education | PASS | 100.0 | 375.7 | concept_graph | None (Zero Invariant Violations) |
| case_89_guj_learn_web | education | PASS | 100.0 | 301.6 | concept_graph | None (Zero Invariant Violations) |
| case_90_guj_textile_export | business_strategy | PASS | 100.0 | 356.2 | derived | None (Zero Invariant Violations) |
| case_91_guj_solar_farm | generic | PASS | 100.0 | 306.1 | derived | None (Zero Invariant Violations) |
| case_92_hi_learn_cpp | education | PASS | 100.0 | 293.5 | concept_graph | None (Zero Invariant Violations) |
| case_93_hi_cyber_security | education | PASS | 100.0 | 418.4 | derived | None (Zero Invariant Violations) |
| case_94_hi_restaurant_delhi | business_strategy | PASS | 90.0 | 305.2 | derived | None (Zero Invariant Violations) |
| case_95_hi_ayurveda_ecommerce | saas_software | PASS | 100.0 | 269.7 | derived | None (Zero Invariant Violations) |
| case_96_typo_want_lern_pythn | education | PASS | 100.0 | 177.5 | concept_graph | None (Zero Invariant Violations) |
| case_97_typo_buid_schedulng_app | saas_software | PASS | 100.0 | 289.0 | derived | None (Zero Invariant Violations) |
| case_98_typo_fix_nulpointer | debugging | **FAIL** | 60.0 | 244.5 | derived | Objective Keyword Missing: Missing required keywords: nulpointrexcptn, crshing; Quality score 60.0 < min 85.0; Expected keyword 'nulpointrexcptn' missing; Expected keyword 'crshing' missing |
| case_99_typo_gujlish_shikhvu | education | PASS | 100.0 | 312.4 | concept_graph | None (Zero Invariant Violations) |
| case_100_vague_make_something | generic | **FAIL** | 60.0 | 520.5 | derived | Domain Classification Mismatch: Domain mismatch: expected 'General Purpose', got 'Something Strategy' (child: '').; Quality score 60.0 < min 75.0 |
| case_101_vague_give_code | generic | **FAIL** | 60.0 | 437.1 | derived | Domain Classification Mismatch: Domain mismatch: expected 'General Purpose', got 'Software Development' (child: '').; Quality score 60.0 < min 75.0 |
| case_102_vague_idea_batao | generic | **FAIL** | 60.0 | 317.1 | derived | Domain Classification Mismatch: Domain mismatch: expected 'General Purpose', got 'Software Development' (child: '').; Quality score 60.0 < min 75.0 |
| case_103_injection_leak_prompt | prompt_injection | PASS | 100.0 | 0.3 | safety_filter | None (Zero Invariant Violations) |
| case_104_injection_dan_jailbreak | prompt_injection | PASS | 100.0 | 0.1 | safety_filter | None (Zero Invariant Violations) |
| case_105_injection_developer_override | prompt_injection | PASS | 100.0 | 0.1 | safety_filter | None (Zero Invariant Violations) |
| case_106_saas_software_0 | saas_software | PASS | 100.0 | 287.2 | concept_graph | None (Zero Invariant Violations) |
| case_107_saas_software_1 | saas_software | PASS | 100.0 | 272.5 | derived | None (Zero Invariant Violations) |
| case_108_saas_software_2 | saas_software | PASS | 100.0 | 301.2 | derived | None (Zero Invariant Violations) |
| case_109_education_3 | education | PASS | 100.0 | 304.3 | derived | None (Zero Invariant Violations) |
| case_110_education_4 | education | PASS | 100.0 | 350.3 | derived | None (Zero Invariant Violations) |
| case_111_education_5 | education | **FAIL** | 60.0 | 456.7 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_112_education_6 | education | **FAIL** | 60.0 | 355.8 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_113_healthcare_software_7 | healthcare_software | PASS | 100.0 | 231.3 | concept_graph | None (Zero Invariant Violations) |
| case_114_healthcare_software_8 | healthcare_software | PASS | 100.0 | 225.1 | derived | None (Zero Invariant Violations) |
| case_115_healthcare_software_9 | healthcare_software | PASS | 100.0 | 267.0 | derived | None (Zero Invariant Violations) |
| case_116_event_planning_10 | event_planning | PASS | 100.0 | 201.8 | derived | None (Zero Invariant Violations) |
| case_117_event_planning_11 | event_planning | PASS | 100.0 | 292.5 | derived | None (Zero Invariant Violations) |
| case_118_event_planning_12 | event_planning | PASS | 100.0 | 306.2 | derived | None (Zero Invariant Violations) |
| case_119_debugging_13 | debugging | PASS | 100.0 | 190.7 | concept_graph | None (Zero Invariant Violations) |
| case_120_debugging_14 | debugging | PASS | 100.0 | 221.7 | concept_graph | None (Zero Invariant Violations) |
| case_121_debugging_15 | debugging | PASS | 100.0 | 198.8 | concept_graph | None (Zero Invariant Violations) |
| case_122_debugging_16 | debugging | PASS | 100.0 | 197.8 | concept_graph | None (Zero Invariant Violations) |
| case_123_business_strategy_17 | business_strategy | PASS | 100.0 | 316.9 | derived | None (Zero Invariant Violations) |
| case_124_business_strategy_18 | business_strategy | PASS | 100.0 | 169.7 | concept_graph | None (Zero Invariant Violations) |
| case_125_business_strategy_19 | business_strategy | PASS | 100.0 | 317.6 | derived | None (Zero Invariant Violations) |
| case_126_marketing_20 | marketing | PASS | 100.0 | 356.0 | derived | None (Zero Invariant Violations) |
| case_127_marketing_21 | marketing | PASS | 100.0 | 330.3 | derived | None (Zero Invariant Violations) |
| case_128_design_22 | design | PASS | 100.0 | 352.2 | derived | None (Zero Invariant Violations) |
| case_129_design_23 | design | PASS | 90.0 | 423.7 | derived | None (Zero Invariant Violations) |
| case_130_writing_24 | writing | PASS | 100.0 | 395.9 | concept_graph | None (Zero Invariant Violations) |
| case_131_writing_25 | writing | PASS | 100.0 | 329.0 | derived | None (Zero Invariant Violations) |
| case_132_research_26 | research | PASS | 100.0 | 312.5 | derived | None (Zero Invariant Violations) |
| case_133_research_27 | research | PASS | 100.0 | 300.9 | derived | None (Zero Invariant Violations) |
| case_134_finance_28 | finance | PASS | 100.0 | 287.5 | derived | None (Zero Invariant Violations) |
| case_135_finance_29 | finance | PASS | 100.0 | 335.9 | derived | None (Zero Invariant Violations) |
| case_136_travel_30 | travel | PASS | 100.0 | 198.2 | derived | None (Zero Invariant Violations) |
| case_137_travel_31 | travel | PASS | 100.0 | 548.6 | derived | None (Zero Invariant Violations) |
| case_138_legal_32 | legal | PASS | 100.0 | 361.9 | derived | None (Zero Invariant Violations) |
| case_139_legal_33 | legal | PASS | 100.0 | 387.9 | derived | None (Zero Invariant Violations) |
| case_140_creative_34 | creative | PASS | 100.0 | 307.6 | derived | None (Zero Invariant Violations) |
| case_141_creative_35 | creative | PASS | 100.0 | 215.0 | derived | None (Zero Invariant Violations) |
| case_142_generic_36 | generic | **FAIL** | 60.0 | 237.3 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Agriculture' (child: 'Autonomous Hydroponics').; Quality score 60.0 < min 85.0 |
| case_143_generic_37 | generic | **FAIL** | 60.0 | 296.8 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Business & Strategy' (child: '').; Quality score 60.0 < min 85.0 |
| case_144_generic_38 | generic | **FAIL** | 60.0 | 307.3 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Software Development' (child: '').; Quality score 60.0 < min 85.0 |
| case_145_saas_software_39 | saas_software | PASS | 100.0 | 262.4 | concept_graph | None (Zero Invariant Violations) |
| case_146_saas_software_40 | saas_software | PASS | 100.0 | 220.6 | derived | None (Zero Invariant Violations) |
| case_147_saas_software_41 | saas_software | PASS | 100.0 | 288.1 | derived | None (Zero Invariant Violations) |
| case_148_education_42 | education | PASS | 100.0 | 364.4 | derived | None (Zero Invariant Violations) |
| case_149_education_43 | education | PASS | 100.0 | 337.8 | derived | None (Zero Invariant Violations) |
| case_150_education_44 | education | **FAIL** | 60.0 | 314.2 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_151_education_45 | education | **FAIL** | 60.0 | 327.4 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_152_healthcare_software_46 | healthcare_software | PASS | 100.0 | 216.4 | concept_graph | None (Zero Invariant Violations) |
| case_153_healthcare_software_47 | healthcare_software | PASS | 100.0 | 295.8 | derived | None (Zero Invariant Violations) |
| case_154_healthcare_software_48 | healthcare_software | PASS | 100.0 | 375.8 | derived | None (Zero Invariant Violations) |
| case_155_event_planning_49 | event_planning | PASS | 100.0 | 266.9 | derived | None (Zero Invariant Violations) |
| case_156_event_planning_50 | event_planning | PASS | 100.0 | 316.8 | derived | None (Zero Invariant Violations) |
| case_157_event_planning_51 | event_planning | PASS | 100.0 | 516.0 | derived | None (Zero Invariant Violations) |
| case_158_debugging_52 | debugging | PASS | 100.0 | 348.9 | concept_graph | None (Zero Invariant Violations) |
| case_159_debugging_53 | debugging | PASS | 100.0 | 337.3 | concept_graph | None (Zero Invariant Violations) |
| case_160_debugging_54 | debugging | PASS | 100.0 | 300.3 | concept_graph | None (Zero Invariant Violations) |
| case_161_debugging_55 | debugging | PASS | 100.0 | 204.8 | concept_graph | None (Zero Invariant Violations) |
| case_162_business_strategy_56 | business_strategy | PASS | 100.0 | 315.2 | derived | None (Zero Invariant Violations) |
| case_163_business_strategy_57 | business_strategy | PASS | 100.0 | 187.7 | concept_graph | None (Zero Invariant Violations) |
| case_164_business_strategy_58 | business_strategy | PASS | 100.0 | 309.2 | derived | None (Zero Invariant Violations) |
| case_165_marketing_59 | marketing | PASS | 100.0 | 297.4 | derived | None (Zero Invariant Violations) |
| case_166_marketing_60 | marketing | PASS | 100.0 | 433.3 | derived | None (Zero Invariant Violations) |
| case_167_design_61 | design | PASS | 100.0 | 208.4 | derived | None (Zero Invariant Violations) |
| case_168_design_62 | design | PASS | 90.0 | 289.7 | derived | None (Zero Invariant Violations) |
| case_169_writing_63 | writing | PASS | 100.0 | 283.5 | concept_graph | None (Zero Invariant Violations) |
| case_170_writing_64 | writing | PASS | 100.0 | 293.5 | derived | None (Zero Invariant Violations) |
| case_171_research_65 | research | PASS | 100.0 | 286.5 | derived | None (Zero Invariant Violations) |
| case_172_research_66 | research | PASS | 100.0 | 293.5 | derived | None (Zero Invariant Violations) |
| case_173_finance_67 | finance | PASS | 100.0 | 303.8 | derived | None (Zero Invariant Violations) |
| case_174_finance_68 | finance | PASS | 100.0 | 282.8 | derived | None (Zero Invariant Violations) |
| case_175_travel_69 | travel | PASS | 100.0 | 307.8 | derived | None (Zero Invariant Violations) |
| case_176_travel_70 | travel | PASS | 100.0 | 443.6 | derived | None (Zero Invariant Violations) |
| case_177_legal_71 | legal | PASS | 100.0 | 274.3 | derived | None (Zero Invariant Violations) |
| case_178_legal_72 | legal | PASS | 100.0 | 275.1 | derived | None (Zero Invariant Violations) |
| case_179_creative_73 | creative | PASS | 100.0 | 314.9 | derived | None (Zero Invariant Violations) |
| case_180_creative_74 | creative | PASS | 100.0 | 217.4 | derived | None (Zero Invariant Violations) |
| case_181_generic_75 | generic | **FAIL** | 60.0 | 208.8 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Agriculture' (child: 'Autonomous Hydroponics').; Quality score 60.0 < min 85.0 |
| case_182_generic_76 | generic | **FAIL** | 60.0 | 289.7 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Business & Strategy' (child: '').; Quality score 60.0 < min 85.0 |
| case_183_generic_77 | generic | **FAIL** | 60.0 | 333.4 | derived | Domain Classification Mismatch: Domain mismatch: expected 'Generic', got 'Software Development' (child: '').; Quality score 60.0 < min 85.0 |
| case_184_saas_software_78 | saas_software | PASS | 100.0 | 270.6 | concept_graph | None (Zero Invariant Violations) |
| case_185_saas_software_79 | saas_software | PASS | 100.0 | 220.9 | derived | None (Zero Invariant Violations) |
| case_186_saas_software_80 | saas_software | PASS | 100.0 | 312.8 | derived | None (Zero Invariant Violations) |
| case_187_education_81 | education | PASS | 100.0 | 295.8 | derived | None (Zero Invariant Violations) |
| case_188_education_82 | education | PASS | 100.0 | 293.3 | derived | None (Zero Invariant Violations) |
| case_189_education_83 | education | **FAIL** | 60.0 | 318.7 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_190_education_84 | education | **FAIL** | 60.0 | 272.6 | concept_graph | Domain Classification Mismatch: Domain mismatch: expected 'Education', got 'Cloud Computing & DevOps' (child: '').; Quality score 60.0 < min 85.0 |
| case_191_healthcare_software_85 | healthcare_software | PASS | 100.0 | 214.2 | concept_graph | None (Zero Invariant Violations) |
| case_192_healthcare_software_86 | healthcare_software | PASS | 100.0 | 212.4 | derived | None (Zero Invariant Violations) |
| case_193_healthcare_software_87 | healthcare_software | PASS | 100.0 | 336.3 | derived | None (Zero Invariant Violations) |
| case_194_event_planning_88 | event_planning | PASS | 100.0 | 241.1 | derived | None (Zero Invariant Violations) |
| case_195_event_planning_89 | event_planning | PASS | 100.0 | 450.9 | derived | None (Zero Invariant Violations) |
| case_196_event_planning_90 | event_planning | PASS | 100.0 | 464.9 | derived | None (Zero Invariant Violations) |
| case_197_debugging_91 | debugging | PASS | 100.0 | 266.9 | concept_graph | None (Zero Invariant Violations) |
| case_198_debugging_92 | debugging | PASS | 100.0 | 222.8 | concept_graph | None (Zero Invariant Violations) |
| case_199_debugging_93 | debugging | PASS | 100.0 | 220.0 | concept_graph | None (Zero Invariant Violations) |
| case_200_debugging_94 | debugging | PASS | 100.0 | 217.3 | concept_graph | None (Zero Invariant Violations) |
| case_201_business_strategy_95 | business_strategy | PASS | 100.0 | 308.4 | derived | None (Zero Invariant Violations) |
| case_202_business_strategy_96 | business_strategy | PASS | 100.0 | 173.9 | concept_graph | None (Zero Invariant Violations) |
| case_203_business_strategy_97 | business_strategy | PASS | 100.0 | 337.2 | derived | None (Zero Invariant Violations) |
| case_204_marketing_98 | marketing | PASS | 100.0 | 293.5 | derived | None (Zero Invariant Violations) |
| case_205_marketing_99 | marketing | PASS | 100.0 | 233.9 | derived | None (Zero Invariant Violations) |