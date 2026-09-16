-- 013_cms_ma_measures_full.sql
-- FULL CMS Medicare Advantage measure catalog (HEDIS + Star Ratings + Part D).
-- Operator requirement (2026-09-15): "Plus any other cms measures for Medicare advantage"
--
-- Supersedes the 7-measure starter set in 011 by adding the rest of the CMS MA
-- universe. Existing codes (AWV/MAMMO/CRC/DEXA/EYE/A1C/BP) are preserved and
-- enriched with their official HEDIS/CMS identifiers.
--
-- measure_family groups them the way CMS/NCQA publish them.
-- star_measure marks the ones actually in the Star Ratings (they carry weight).
-- part = 'C' (health plan) or 'D' (drug plan).

ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS cms_id        TEXT;
ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS measure_family TEXT;
ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS star_measure  BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS star_weight   NUMERIC;
ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS part          TEXT DEFAULT 'C';
ALTER TABLE quality_measures ADD COLUMN IF NOT EXISTS source_year   INTEGER DEFAULT 2026;

-- map the existing seven onto their official identifiers
UPDATE quality_measures SET cms_id='AWV',   measure_family='Preventive',   star_measure=true,  star_weight=1, part='C' WHERE measure_code='AWV';
UPDATE quality_measures SET cms_id='BCS-E', measure_family='Cancer Screening', star_measure=true, star_weight=1, part='C' WHERE measure_code='MAMMO';
UPDATE quality_measures SET cms_id='COL-E', measure_family='Cancer Screening', star_measure=true, star_weight=1, part='C' WHERE measure_code='CRC';
UPDATE quality_measures SET cms_id='OSW',   measure_family='Older Adults',  star_measure=true,  star_weight=1, part='C' WHERE measure_code='DEXA';
UPDATE quality_measures SET cms_id='EED',   measure_family='Diabetes',      star_measure=true,  star_weight=1, part='C' WHERE measure_code='EYE';
UPDATE quality_measures SET cms_id='HBD',   measure_family='Diabetes',      star_measure=true,  star_weight=1, part='C' WHERE measure_code='A1C';
UPDATE quality_measures SET cms_id='CBP',   measure_family='Cardiovascular',star_measure=true,  star_weight=1, part='C' WHERE measure_code='BP';

INSERT INTO quality_measures
 (measure_code, measure_label, cadence_months, min_age, max_age, sex_includes,
  requires_dx_group, cms_id, measure_family, star_measure, star_weight, part, cpt_hints, notes, sort_order)
VALUES
 -- ---------- Cancer screening ----------
 ('CCS','Cervical cancer screening',36,21,64,'F',NULL,'CCS-E','Cancer Screening',true,1,'C',
  ARRAY['88141','88142','88143','87624'],'Cervical cytology every 3 yr, or hrHPV co-test every 5 yr.',10),

 -- ---------- Immunizations ----------
 ('FLU','Annual influenza vaccination',12,65,NULL,NULL,NULL,'FLU','Immunization',true,1,'C',
  ARRAY['90686','90688','G0008'],'One per flu season (Jul–Jun).',20),
 ('PNA','Pneumococcal vaccination',NULL,65,NULL,NULL,NULL,'PNA','Immunization',true,1,'C',
  ARRAY['90670','90732','G0009'],'One-time series; revaccination per ACIP.',21),
 ('COVID','COVID-19 vaccination',12,NULL,NULL,NULL,NULL,'COVID','Immunization',false,NULL,'C',
  ARRAY['91300','91301'],'Current season per ACIP guidance.',22),
 ('Tdap','Td/Tdap vaccination',120,NULL,NULL,NULL,NULL,'Tdap','Immunization',false,NULL,'C',
  ARRAY['90715'],'Tetanus booster every 10 years.',23),
 ('SHING','Shingles (RZV) vaccination',NULL,50,NULL,NULL,NULL,'SHING','Immunization',false,NULL,'C',
  ARRAY['90750'],'Two-dose series, age 50+.',24),

 -- ---------- Diabetes (full CDC suite) ----------
 ('KED','Kidney health evaluation for patients with diabetes',12,NULL,NULL,NULL,'Diabetes','KED','Diabetes',true,1,'C',
  ARRAY['82043','82042','83036'],'eGFR + uACR at least annually.',30),
 ('BPD','Blood pressure control for patients with diabetes',12,18,75,NULL,'Diabetes','BPD','Diabetes',false,NULL,'C',
  ARRAY['3074F','3075F'],'BP <140/90 for members with diabetes.',31),
 ('SPD','Statin therapy for patients with diabetes',12,40,75,NULL,'Diabetes','SPD','Diabetes',false,NULL,'C',
  ARRAY['4010F'],'Statin prescribed/active for diabetics 40-75.',32),
 ('DSME','Diabetes self-management education',NULL,NULL,NULL,NULL,'Diabetes','DSMES','Diabetes',false,NULL,'C',
  ARRAY['G0108','G0109'],'Referral/attendance for DSMT.',33),

 -- ---------- Cardiovascular ----------
 ('SPC','Statin therapy for patients with cardiovascular disease',12,21,75,NULL,'Selected Cardiovascular','SPC','Cardiovascular',false,NULL,'C',
  ARRAY['4010F'],'Statin for members with CVD.',40),
 ('PBH','Persistence of beta-blocker treatment after heart attack',6,NULL,NULL,NULL,'Selected Cardiovascular','PBH','Cardiovascular',false,NULL,'C',
  ARRAY[''],'Beta-blocker persistence >=80% for 180 days post-MI.',41),
 ('OMW','Osteoporosis management in women who had a fracture',6,50,64,'F',NULL,'OMW','Older Adults',true,1,'C',
  ARRAY['77080','20610'],'DEXA or osteoporosis therapy within 180 days of fracture.',42),
 ('RISKFALL','Reducing the risk of falling',12,65,NULL,NULL,NULL,'FALL','Older Adults',true,1,'C',
  ARRAY['1100F','1101F'],'Fall risk assessment + plan of care. HOS-survey based.',43),

 -- ---------- Behavioral health ----------
 ('FUH','Follow-up after hospitalization for mental illness',NULL,6,NULL,NULL,NULL,'FUH','Behavioral Health',false,NULL,'C',
  ARRAY['98960','99401'],'7-day and 30-day follow-up after inpatient psych discharge.',50),
 ('FUM','Follow-up after ED visit for mental illness',NULL,6,NULL,NULL,NULL,'FUM','Behavioral Health',false,NULL,'C',
  ARRAY['98960'],'7-day and 30-day follow-up after ED visit for mental illness.',51),
 ('AMM','Antidepressant medication management',NULL,18,NULL,NULL,'Selected Mental Health','AMM','Behavioral Health',false,NULL,'C',
  ARRAY['G8431','G8510'],'Acute (84d) and continuation (180d) phase treatment.',52),
 ('SSD','Diabetes screening for people with schizophrenia or bipolar',12,18,64,NULL,'Selected Mental Health','SSD','Behavioral Health',false,NULL,'C',
  ARRAY['83036'],'Glucose/A1c screening for members on antipsychotics.',53),
 ('SMC','Cardiovascular monitoring for people with CVD and schizophrenia',12,18,64,NULL,'Selected Mental Health','SMC','Behavioral Health',false,NULL,'C',
  ARRAY['80061'],'LDL-C screening for members with CVD + schizophrenia/bipolar.',54),
 ('SAA','Adherence to antipsychotic medication',NULL,18,NULL,NULL,'Selected Mental Health','SAA','Behavioral Health',false,NULL,'C',
  ARRAY[''],'>=80% PDC for antipsychotics.',55),
 ('SUDC','Substance use disorder treatment penetration',NULL,NULL,NULL,NULL,NULL,'SUDC','Behavioral Health',false,NULL,'C',
  ARRAY['H0015','H0020'],'Engagement/initiation of SUD treatment.',56),

 -- ---------- Medication / transitions ----------
 ('MRP','Medication reconciliation post-discharge',1,18,NULL,NULL,NULL,'MRP','Transitions of Care',true,1,'C',
  ARRAY['1111F','99495'],'Med rec within 30 days of discharge.',60),
 ('TRC','Transitions of care',NULL,18,NULL,NULL,NULL,'TRC','Transitions of Care',false,NULL,'C',
  ARRAY['99495','99496'],'Notification, reconciliation, engagement, and plan doc after discharge.',61),
 ('PCR','Plan all-cause readmissions',NULL,18,64,NULL,NULL,'PCR','Utilization',false,NULL,'C',
  ARRAY[''],'Risk-adjusted 30-day readmission ratio (lower is better).',62),
 ('DDE','Potentially harmful drug-drug interactions',NULL,65,NULL,NULL,NULL,'DDE','Part D',false,NULL,'D',
  ARRAY[''],'Members on interacting drug pairs.',63),
 ('SUPD','Statin use in persons with diabetes',12,40,75,NULL,'Diabetes','SUPD','Part D',false,NULL,'D',
  ARRAY['4010F'],'At least one statin fill in the measurement year.',64),
 ('MPF','Medication price finder / cost transparency',NULL,NULL,NULL,NULL,NULL,'MPF','Part D',false,NULL,'D',
  ARRAY[''],'Member use of cost-comparison tool.',65),
 ('MTM','Medication therapy management program completion',12,NULL,NULL,NULL,NULL,'MTM','Part D',false,NULL,'D',
  ARRAY['99605'],'CMR completion for targeted members.',66),
 ('PDC_DIAB','Medication adherence: diabetes',12,18,NULL,NULL,'Diabetes','PDC-DR','Part D',false,NULL,'D',
  ARRAY[''],'>=80% proportion of days covered for oral hypoglycemics.',67),
 ('PDC_RASA','Medication adherence: hypertension (RAS antagonists)',12,18,NULL,NULL,NULL,'PDC-RASA','Part D',false,NULL,'D',
  ARRAY[''],'>=80% PDC for ACEi/ARB/renin inhibitors.',68),
 ('PDC_STATIN','Medication adherence: statins',12,18,NULL,NULL,NULL,'PDC-STA','Part D',false,NULL,'D',
  ARRAY[''],'>=80% PDC for statin therapy.',69),

 -- ---------- Older adults / special needs ----------
 ('COA_MEDREV','Care for older adults: medication review',12,66,NULL,NULL,NULL,'COA','Older Adults',false,NULL,'C',
  ARRAY['1159F','1160F'],'Annual medication review for members 66+.',70),
 ('COA_FUNC','Care for older adults: functional status assessment',12,66,NULL,NULL,NULL,'COA','Older Adults',false,NULL,'C',
  ARRAY['1170F'],'Annual functional status assessment.',71),
 ('COA_PAIN','Care for older adults: pain screening',12,66,NULL,NULL,NULL,'COA','Older Adults',false,NULL,'C',
  ARRAY['1125F','1126F'],'Annual pain screening.',72),
 ('SNP_CARE','SNP care management',12,NULL,NULL,NULL,NULL,'SNP','Special Needs',false,NULL,'C',
  ARRAY['99487','T1016'],'C-SNP/D-SNP care management requirement.',73),
 ('ADVANCE','Advance care planning',NULL,65,NULL,NULL,NULL,'ACP','Older Adults',false,NULL,'C',
  ARRAY['99497','99498'],'Documented advance care plan discussion.',74),

 -- ---------- Utilization / appropriateness ----------
 ('APP','Use of imaging studies for low back pain',NULL,18,50,NULL,NULL,'APP','Utilization',false,NULL,'C',
  ARRAY['72100'],'Avoid imaging within 28 days for uncomplicated low back pain.',80),
 ('URI','Appropriate treatment for upper respiratory infection',NULL,3,64,NULL,NULL,'URI','Utilization',false,NULL,'C',
  ARRAY[''],'Avoid antibiotics for URI.',81),
 ('AAB','Avoidance of antibiotic treatment for acute bronchitis',NULL,3,64,NULL,NULL,'AAB','Utilization',false,NULL,'C',
  ARRAY[''],'Avoid antibiotics for acute bronchitis/bronchiolitis.',82),
 ('AMR','Asthma medication ratio',12,5,64,NULL,NULL,'AMR','Respiratory',false,NULL,'C',
  ARRAY[''],'Controller-to-total asthma medication ratio >=0.5.',83),

 -- ---------- Access / experience (survey-based) ----------
 ('CAHPS','CAHPS member experience survey',12,NULL,NULL,NULL,NULL,'CAHPS','Experience',true,2,'C',
  ARRAY[''],'Getting needed care, appointments, care coordination, ratings. Survey-based.',90),
 ('HOS','Health Outcomes Survey (physical/mental health)',24,NULL,NULL,NULL,NULL,'HOS','Experience',true,1,'C',
  ARRAY[''],'Physical and mental health improvement. Survey-based.',91),
 ('MPS','Monitoring physical activity',12,65,NULL,NULL,NULL,'MPS','Experience',true,1,'C',
  ARRAY[''],'Discussed exercise; survey-based.',92),
 ('BLADDER','Improving bladder control',12,65,NULL,NULL,NULL,'BCS','Experience',true,1,'C',
  ARRAY[''],'Discussed urinary incontinence. Survey-based.',93),
 ('PLANCHOICE','Plan makes it easier to get appointments / care',12,NULL,NULL,NULL,NULL,'CAHPS','Experience',false,NULL,'C',
  ARRAY[''],'Access composite.',94)

ON CONFLICT (measure_code) DO UPDATE
    SET measure_label = EXCLUDED.measure_label, cadence_months = EXCLUDED.cadence_months,
        min_age = EXCLUDED.min_age, max_age = EXCLUDED.max_age,
        sex_includes = EXCLUDED.sex_includes, requires_dx_group = EXCLUDED.requires_dx_group,
        cms_id = EXCLUDED.cms_id, measure_family = EXCLUDED.measure_family,
        star_measure = EXCLUDED.star_measure, star_weight = EXCLUDED.star_weight,
        part = EXCLUDED.part, cpt_hints = EXCLUDED.cpt_hints,
        notes = EXCLUDED.notes, sort_order = EXCLUDED.sort_order;

CREATE OR REPLACE VIEW v_cms_measure_catalog AS
SELECT measure_family, count(*) AS measures,
       count(*) FILTER (WHERE star_measure) AS star_measures,
       sum(star_weight) FILTER (WHERE star_measure) AS star_weight_total,
       string_agg(measure_code, ', ' ORDER BY sort_order) AS codes
FROM quality_measures
GROUP BY measure_family
ORDER BY measure_family;
