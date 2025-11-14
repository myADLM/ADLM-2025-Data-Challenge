# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY ASSAY ONLY

I Background Information:

A 510(k) Number K230944   
B Applicant MeMed Diagnostics Ltd.   
C Proprietary and Established Names MeMed BV   
D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QPS</td><td rowspan=1 colspan=1>Class II</td><td rowspan=1 colspan=1>21 CFR 866.3215 - DeviceTo Detect And MeasureNon-Microbial Analyte(S)In Human ClinicalSpecimens To Aid InAssessment Of PatientsWith Suspected Sepsis</td><td rowspan=1 colspan=1>MI - Microbiology</td></tr></table>

# II Submission/Device Overview:

# A Purpose for Submission:

The purpose of this submission is to validate the use of venous whole blood sample type and to introduce a revised master calibration curve (MCC) calibration scheme for the previously cleared MeMed BV device.

# B Measurand:

Three host immune protein biomarkers: TRAIL, IP-10, and CRP.

# C Type of Test:

Chemiluminescent immunoassay

# III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below.

# B Indication(s) for Use:

The MeMed BV test is an automated semi-quantitative immunoassay that measures three nonmicrobial (host) proteins (TRAIL, IP-10, and CRP) in adult and pediatric serum and venous whole blood samples and is intended for use in conjunction with clinical assessments and other laboratory findings as an aid to differentiate bacterial from viral infection. MeMed BV is indicated for use in patients presenting to the emergency department or urgent care center and with samples collected at hospital admission from patients with suspected acute bacterial or viral infection, who have had symptoms for less than seven days. The MeMed BV test generates a numeric score that falls within discrete interpretation bins based on the increasing likelihood of bacterial infection.

C Special Conditions for Use Statement(s): Rx - For Prescription Use Only

D Special Instrument Requirements:

MeMed Key Instrument

# IV Device/System Characteristics:

# A Device Description:

The MeMed BV (“BV Test” or the “Test”) is an In Vitro Diagnostic device that measures in parallel the concentrations of three non-microbial (host) proteins (TRAIL, IP-10 and CRP) in serum and venous whole blood samples from adult and pediatric patients presenting to the emergency department, urgent care center, and with samples collected at hospital admission from patients with suspected acute bacterial or viral infection. The test consists of an automated analyzer with built-in hardware and software that conduct chemiluminescence based analyte measurements of patient serum and venous whole blood samples and their computational integration (MeMed Key), and a disposable cartridge that contains the reagents and controls needed to detect the analytes of interest (MeMed BV cartridge). The Test generates an answer to each sample, with a test run time of approximately 15 minutes.

# B Principle of Operation:

The test system is composed of the analyzer (MeMed Key) and the cartridge, and their respective sub-components. The product is designed to allow straightforward sample-to-answer testing, with a test run time of approximately 15 minutes.

The patient’s serum or venous whole blood specimen is dispensed by the user into the designated cartridge area. The users are instructed to fill $1 0 0 \mu \mathrm { L }$ of serum sample or $1 5 0 \mu \mathrm { l }$ of venous whole blood sample, using a pipette. Each single-use cartridge is provided in a package that contains all necessary components for conducting a single patient test. This consists of the cartridge itself, all disposables (pipette tips), reagents and a waste collection well. The cartridge assembly contains both the reagents for the different assays and the pipette tips. The cartridge is a multi-cavity plastic container that is sealed off with foil and covered with a label on the foil that indicates the sample type, the test name, indication to the user where to input the sample, required sample volume, lot number, cartridge expiry date and a barcode with test data and parameters that are intended to be read by the analyzer.

The cartridge contains the several reagents in separate cavities, which are required to perform the test. Upon insertion of the cartridge, the analyzer conducts three immunoassays on a single serum or venous whole blood sample. The cartridge also securely stores all waste materials collected during the test.

The user inserts the cartridge with sample into the analyzer and is guided by the carriage caddy. The analyzer auto-reads the cartridge's barcode and verifies that the requested test matches the cartridge type, cartridge expiration date, and that the calibration curve matches the cartridge lot number. The analyzer notifies the user when specimen processing is initiated and when the user should expect the test result.

After the cartridge has been inserted, the carriage caddy system locks and guides the cartridge during the insertion phase. Once loaded, the cartridge holder is driven by the robot to the left, in position for processing.

The liquids are handled through the pipettor, which operates through measurement of displaced air volumes by means of a flow sensor, integrated directly in the pipetting head that is connected to a high-speed solenoid valve. The flow sensor is based on a differential pressure measurement across flow restriction. The cartridge is then heated through the heater block. A software-driven Proportional Integral Derivative (PID) control system is used to set and regulate the temperature of the heater block, using the center thermistor for feedback.

Once the sample has been diluted and mixed with magnetic particles, it is processed by the bead immobilizer magnet, which generates a high magnetic field strength, and allows both the reduction of immobilization time and a high percentage of bead retention per immobilization to be achieved. The sample is then washed and the chemiluminescence step takes place.

The chemiluminescence of the assay is measured by a Photo Multiplier Tube (PMT) Module, a highly sensitive light detection device. The selected PMT Module has a spectral range which matches the expected wavelength generated by the chemistry luminescence. When a PMT reading is required, the software then turns the PMT Module on and a reading is taken. Once readings have been completed, the software automatically turns the PMT Module off.

Each RLU measurement for each of the analytes is processed and translated to a concentration measurement using a calibration curve that is generated using calibration materials provided by MeMed. The process of generating a calibration curve for the modified MeMed BV device can be accomplished by using a Master curve calibration (MCC); where the 4-parameter logistic (for IP-10 and CRP) or linear (for TRAIL) calibration is created during cartridge lot manufacturing and is adjusted periodically based on the measurement of the 3 calibrator solutions as part of the standard calibration process (utilized for serum and venous whole blood sample types), compared to the expected RLUs based on the (factory defined) master curve.

When a clinical sample is run, the resulting concentrations are processed to apply a clinical correction factor, which is pre-determined for each of the analytes. This clinical correction factor takes care of any matrix-effects (in the serum or venous whole blood) which may impact the generated signal compared to the calibration curve which is run on recombinant proteins. This difference is fixed for each of the analytes and is applied as a simple linear correction factor. When the matrix- effect correction does not follow a simple linear model (as evidenced by goodness of fit metrics), a piecewise linear model is employed.

For venous whole-blood testing, the clinical correction factor includes a precalculated wholeblood to serum conversion process, whereby the raw concentrations (in whole-blood) are converted to serum- equivalent values and corrected using the clinical correction factor. This process of conversion and correction is applied in one step, encompassing both actions.

Final concentrations for each analyte are then processed to generate a Score result which places the specimen into one of five distinct bins, with higher score values corresponding to increasing likelihood of a bacterial infection.

The MeMed BV test result is a score between 0 and 100 derived from computational integration of the measurements of the three proteins TRAIL, IP-10, and CRP, where low scores are indicative of viral infection and high score of bacterial infection.

• $0 \leq$ score ${ \le } 1 0$ : High likelihood of viral infection (or other non-bacterial etiology) • $1 0 <$ score ${ < } 3 5$ : Moderate likelihood of viral infection (or other non-bacterial etiology) $3 5 \leq$ score ${ \le } 6 5$ : Equivocal • $6 5 <$ score ${ \tt < } 9 0 $ : Moderate likelihood of bacterial infection (or co-infection) • $9 0 \leq$ score $\leq 1 0 0$ : High likelihood of bacterial infection (or co-infection)

V Substantial Equivalence Information:

A Predicate Device Name(s): MeMed BV   
B Predicate 510(k) Number(s): K222332

C Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp; PredicateDevice(s):</td><td colspan="1" rowspan="1">K230944</td><td colspan="1" rowspan="1">K222332</td></tr><tr><td colspan="1" rowspan="1">Device Trade Name</td><td colspan="1" rowspan="1">MeMed BV</td><td colspan="1" rowspan="1">MeMed BV</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristic Similarities</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use/IndicationsFor Use</td><td colspan="1" rowspan="1">The MeMed BV test is anautomated semi-quantitativeimmunoassay that measuresthree non-microbial (host)proteins (TRAIL, IP-10, andCRP) in adult and pediatric</td><td colspan="1" rowspan="1">The MeMed BV test is anautomated semi-quantitativeimmunoassay that measuresthree non-microbial (host)proteins (TRAIL, IP-10, andCRP) in adult and pediatric</td></tr><tr><td colspan="1" rowspan="1">b</td><td colspan="1" rowspan="1">serum and venous wholeblood samples and isintended for use inconjunction with clinicalassessments and otherlaboratory findings as an aidto differentiate bacterialfrom viral infection. MeMedBV is indicated for use inpatients presenting to theemergency department orurgent care center and withsamples collected at hospitaladmission from patients withsuspected acute bacterial orviral infection, who have hadsymptoms for less thanseven days. The MeMed BVtest generates a numericscore that falls withindiscrete interpretation binsbased on the increasinglikelihood of bacterialinfection.</td><td colspan="1" rowspan="1">serum samples and isintended for use inconjunction with clinicalassessments and otherlaboratory findings as an aidto differentiate bacterialfrom viral infection. MeMedBV is indicated for use inpatients presenting to theemergency department orurgent care center and withsamples collected at hospitaladmission from patients withsuspected acute bacterial orviral infection, who have hadsymptoms for less thanseven days. The MeMed BVtest generates a numericscore that falls withindiscrete interpretation binsbased on the increasinglikelihood of bacterialinfection.</td></tr><tr><td colspan="1" rowspan="1">User Population</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Health Care Providersrequesting samples to betested by clinical laboratorytechnicians</td></tr><tr><td colspan="1" rowspan="1">Assay Principle</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Sandwich immunoassaytechnology</td></tr><tr><td colspan="1" rowspan="1">Assay Type</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Automated</td></tr><tr><td colspan="1" rowspan="1">Test Result Reporting</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Numerical values with riskbins</td></tr><tr><td colspan="1" rowspan="1">Measurand(s)</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">TRAIL, IP-10, and CRP</td></tr><tr><td colspan="1" rowspan="1">Assay technique</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Chemiluminescentimmunoassay (CLIA)</td></tr><tr><td colspan="1" rowspan="1">Instrument</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">MeMed Key</td></tr><tr><td colspan="1" rowspan="1">Time to result</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Approximately 15 minutes</td></tr><tr><td colspan="1" rowspan="1">Calibration frequency</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Every 4 weeks</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristic Differences</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Specimen</td><td colspan="1" rowspan="1">Human serum or Venouswhole blood</td><td colspan="1" rowspan="1">Human Serum</td></tr><tr><td colspan="1" rowspan="1">Calibration scheme</td><td colspan="1" rowspan="1">Updated calibration using amodified master calibrationcurve scheme.</td><td colspan="1" rowspan="1">Legacy calibration scheme</td></tr><tr><td colspan="1" rowspan="1">Sample volume</td><td colspan="1" rowspan="1">100 μL for serum150 μL for venous wholeblood</td><td colspan="1" rowspan="1">100 μL for serum</td></tr></table>

CLSI EP17- A2: Evaluation of Detection Capability for Clinical Laboratory Measurement   
Procedures   
CLSI EP05- A3: Evaluation of Precision of Quantitative Measurement Procedures; Approved   
Guideline 3 Third Edition   
CLSI EP06-Ed2: Evaluation of the Linearity of Quantitative Measurement Procedures   
CLSI EP09c: Measurement Procedure Comparison and Bias Estimation Using Patient Samples   
62304 IEC: Medical device software - Software life cycle processes 1.1 2015   
CLSI EP25- A: EP25-A (Replaces EP25-P) - Evaluation of Stability of In Vitro Diagnostic   
Reagents; Approved Guideline   
CLSI EP07: Interference testing in clinical chemistry 3 Third Edition (2018)   
CLSI EP09c: Measurement Procedure Comparison and Bias Estimation Using Patient Samples 3   
Third Edition   
CLSI EP37: Supplemental tables for interference testing in clinical chemistry 3 First Edition   
(2018)   
CLSI EP28-A3c: Defining, Establishing, and Verifying Reference Intervals in the Clinical   
Laboratory (2014)   
CLSI EP35: Assessment of Equivalence or Suitability of Specimen Types for Medical   
Laboratory Measurement Procedures

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

1. Precision/Reproducibility:

# Serum:

To evaluate the precision of the MeMed BV assay for serum samples under the new master calibration scheme, raw data from the reproducibility study conducted to support previous clearance of the MeMed BV device (K222332) was re-analyzed.

Repeatability, intermediate precision, and reproducibility were evaluated for each measurand (TRAIL/IP- 10/CRP) of the MeMed BV Test on the MeMed Key Analyzer using a panel of specimens collected as part of a clinical study representing either infectious bacteria, infectious virus, equivocal or noninfectious scores.

The ‘infectious’ specimens were collected from non-U.S. individuals recruited to an infectious cohort as defined by the MeMed BV test intended use/indications for use under “Artemis” study protocol. The samples were collected, centrifuged within 1 hour after blood withdrawal, aliquoted $( 1 2 0 \mu \mathrm { L } )$ and frozen at $- 8 0 ^ { \circ } \mathrm { C }$ . Prior initiation of the reproducibility study, the aliquots were sent on dry ice to the participating laboratories. Each aliquot was thawed 10-15 min on a roller prior to measurement on the MeMed Key instrument.

Table 1. Reproducibility Panel Members - Serum   

<table><tr><td rowspan=1 colspan=1>Panel Member</td><td rowspan=1 colspan=1>Sample Type</td><td rowspan=1 colspan=1>Score</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>Infectious Serum Specimen</td><td rowspan=1 colspan=1>High (Score = 97)</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>Infectious Serum Specimen</td><td rowspan=1 colspan=1>Medium (Score = 51)</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>Infectious Serum Specimen</td><td rowspan=1 colspan=1>Low (Score = 1)</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>Healthy Serum Specimen</td><td rowspan=1 colspan=1>Low (Score = 4)</td></tr></table>

For each measurand, TRAIL, IP-10, and CRP, the acceptance criteria for measurements was CV $\leq 1 5 \%$ . These acceptance criteria were not applicable to IP-10 and CRP concentration of healthy specimens since the concentrations were expected to be below the LoQ of IP-10 and CRP assays. The acceptance criterion for the device score was set at $\mathrm { S D } < 1 2 . 5$ score units.

The results of the repeatability, intermediate precision and reproducibility studies for serum sample type are summarized below.

Table 2. Reproducibility Study Results-Serum   

<table><tr><td rowspan=1 colspan=4></td><td rowspan=1 colspan=2>Repeatability</td><td rowspan=1 colspan=2>IntermediatePrecision</td><td rowspan=1 colspan=2>Reproducibility</td></tr><tr><td rowspan=1 colspan=1>Panelmember</td><td rowspan=1 colspan=1>Measurandor score</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>N</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>CV%</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>CV%</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>CV%</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>49</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>6.1</td><td rowspan=1 colspan=1>3.2</td><td rowspan=1 colspan=1>6.4</td><td rowspan=1 colspan=1>3.4</td><td rowspan=1 colspan=1>7.0</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>7.4</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>7.4</td><td rowspan=1 colspan=1>4.6</td><td rowspan=1 colspan=1>7.7</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>165</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>7.7</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1>7.8</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1>8.4</td><td rowspan=1 colspan=1>5.1</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>55</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>3.8</td><td rowspan=1 colspan=1>6.9</td><td rowspan=1 colspan=1>3.8</td><td rowspan=1 colspan=1>7.1</td><td rowspan=1 colspan=1>4.3</td><td rowspan=1 colspan=1>7.9</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>475</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>22.5</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1>26.3</td><td rowspan=1 colspan=1>5.5</td><td rowspan=1 colspan=1>27.3</td><td rowspan=1 colspan=1>5.7</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>414</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>22.3</td><td rowspan=1 colspan=1>5.4</td><td rowspan=1 colspan=1>23.6</td><td rowspan=1 colspan=1>5.7</td><td rowspan=1 colspan=1>24.1</td><td rowspan=1 colspan=1>5.8</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>1,574</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>74.7</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1>90.4</td><td rowspan=1 colspan=1>5.7</td><td rowspan=1 colspan=1>102.9</td><td rowspan=1 colspan=1>6.5</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>190.1</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>18.9</td><td rowspan=1 colspan=1>9.9</td><td rowspan=1 colspan=1>20.1</td><td rowspan=1 colspan=1>10.6</td><td rowspan=1 colspan=1>21.6</td><td rowspan=1 colspan=1>11.3</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>59.8</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>4.8</td><td rowspan=1 colspan=1>8.1</td><td rowspan=1 colspan=1>5.3</td><td rowspan=1 colspan=1>8.8</td><td rowspan=1 colspan=1>5.4</td><td rowspan=1 colspan=1>9.0</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>29.5</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>8.0</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>8.1</td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1>8.2</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>1.0</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>98</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>1.2</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>1.2</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>1.4</td><td rowspan=1 colspan=1>NA1</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>61</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>6.4</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>6.4</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>6.6</td><td rowspan=1 colspan=1>NA1</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>NA1</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>2.0</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>2.0</td><td rowspan=1 colspan=1>NA1</td><td rowspan=1 colspan=1>2.2</td><td rowspan=1 colspan=1>NA1</td></tr></table>

$^ { 1 } { \mathrm { C V } }$ analysis was not considered for the logistic scale of the MeMed BV Score. The acceptance criterion for the score was set to be $\mathrm { S D } < 1 2 . 5$ score units which reflects a small probability of scores falling into nonadjacent bins.

An additional study was performed to estimate lot-to-lot variance for each measurand and the test result for four panel members using serum samples under the new master calibration scheme, raw data from the lot-to-lot variability study conducted to support clearance of the original MeMed BV device (K222332) was re-analyzed.

The lot-to-lot study was performed on 3 days as follows: Operator 1 at Site 1 conducted three runs per day for each of the four panel members using two lots of cartridges on the same Analyzer. Two calibration lots were used, one for each cartridge lot. External controls were run daily using one lot of EC reagents. Results from the lot variability study are included in Table 3 below.

Table 3. Lot-to-Lot Variability Study Results- Serum   

<table><tr><td rowspan=2 colspan=1>Panelmember</td><td rowspan=2 colspan=1>Measurandor score</td><td rowspan=2 colspan=1>Mean</td><td rowspan=2 colspan=1>N</td><td rowspan=1 colspan=2>Between Lots</td></tr><tr><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>CV%</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>45</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>55</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>152</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>7.0</td><td rowspan=1 colspan=1>4.6</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>49</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>2.8</td><td rowspan=1 colspan=1>5.7</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>460</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>27.8</td><td rowspan=1 colspan=1>6.0</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>17.8</td><td rowspan=1 colspan=1>4.5</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>1,502</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>135.2</td><td rowspan=1 colspan=1>9.0</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>184.0</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>19.8</td><td rowspan=1 colspan=1>10.7</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>57.2</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>27.7</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>1.0</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>0.0</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>98</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>NA</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>67</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>NA</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>NA</td></tr><tr><td rowspan=1 colspan=1>D</td><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>18</td><td rowspan=1 colspan=1>2.3</td><td rowspan=1 colspan=1>NA</td></tr></table>

The serum reproducibility and lot-to-lot variability results comply with the pre-established acceptance criteria for score and individual analytes.

# Venous whole blood (WB):

Since, whole Blood (WB) specimens are unstable and prone to hemolysis when undergoing a freeze-thaw cycle, the evaluation of MeMed BV precision with WB specimens evaluated fresh samples prepared at a single site and on a single day.

The ‘infectious’ specimens were collected from non-U.S. individuals recruited to an infectious cohort as defined by the MeMed BV test intended use/indications for use. Each specimen was analyzed in four runs on five different analyzers (in total 20 repeats) using one cartridge lot. The study was performed in one laboratory in Israel (MeMed Lab) with a single operator. Calibration was performed on the first day on each analyzer; one calibrator lot was used.

Table 4. Patient specimens (panel members)- WB   

<table><tr><td rowspan=1 colspan=1>Panel member</td><td rowspan=1 colspan=1>Sample type</td><td rowspan=1 colspan=1>Score</td></tr><tr><td rowspan=1 colspan=1>A</td><td rowspan=1 colspan=1>InfectiousVenousWB Specimen</td><td rowspan=1 colspan=1>High (Score = 100)</td></tr><tr><td rowspan=1 colspan=1>B</td><td rowspan=1 colspan=1>InfectiousVenousWB Specimen</td><td rowspan=1 colspan=1>Medium (Score = 38)</td></tr><tr><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>InfectiousVenousWBSpecimen</td><td rowspan=1 colspan=1>Low (Score = 1)</td></tr></table>

For each measurand, TRAIL, IP-10, and CRP, the acceptance criteria for measurements was CV $\leq 1 2 \%$ . The acceptance criterion for the Test score was set at $\mathrm { S D } < 1 2 . 5$ score units. The WB precision results are summarized below:

Table 5. Precision study results-WB   

<table><tr><td rowspan=1 colspan=1>Sample</td><td rowspan=1 colspan=1>Parameter</td><td rowspan=1 colspan=1>Average</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=4 colspan=1>A</td><td rowspan=1 colspan=1>TRAIL (pg/mL)</td><td rowspan=1 colspan=1>24.6</td><td rowspan=1 colspan=1>1.7</td><td rowspan=1 colspan=1>6.9%</td></tr><tr><td rowspan=1 colspan=1>IP-10 (pg/mL)</td><td rowspan=1 colspan=1>402.8</td><td rowspan=1 colspan=1>23.3</td><td rowspan=1 colspan=1>5.8%</td></tr><tr><td rowspan=1 colspan=1>CRP (mg/L)</td><td rowspan=1 colspan=1>201.6</td><td rowspan=1 colspan=1>24.1</td><td rowspan=1 colspan=1>12.0%</td></tr><tr><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>99.9</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>NA</td></tr><tr><td rowspan=4 colspan=1>B</td><td rowspan=1 colspan=1>TRAIL (pg/mL)</td><td rowspan=1 colspan=1>38.4</td><td rowspan=1 colspan=1>1.8</td><td rowspan=1 colspan=1>4.6%</td></tr><tr><td rowspan=1 colspan=1>IP-10 (pg/mL)</td><td rowspan=1 colspan=1>273.0</td><td rowspan=1 colspan=1>13.9</td><td rowspan=1 colspan=1>5.1%</td></tr><tr><td rowspan=1 colspan=1>CRP (mg/L)</td><td rowspan=1 colspan=1>9.1</td><td rowspan=1 colspan=1>0.4</td><td rowspan=1 colspan=1>4.0%</td></tr><tr><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>64.1</td><td rowspan=1 colspan=1>3.0</td><td rowspan=1 colspan=1>NA</td></tr><tr><td rowspan=4 colspan=1>C</td><td rowspan=1 colspan=1>TRAIL (pg/mL)</td><td rowspan=1 colspan=1>200.0</td><td rowspan=1 colspan=1>12.6</td><td rowspan=1 colspan=1>6.3%</td></tr><tr><td rowspan=1 colspan=1>IP-10(pg/mL)</td><td rowspan=1 colspan=1>557.0</td><td rowspan=1 colspan=1>17.5</td><td rowspan=1 colspan=1>3.1%</td></tr><tr><td rowspan=1 colspan=1>CRP(mg/L)</td><td rowspan=1 colspan=1>19.4</td><td rowspan=1 colspan=1>1.0</td><td rowspan=1 colspan=1>5.3%</td></tr><tr><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>1.0</td><td rowspan=1 colspan=1>0.0</td><td rowspan=1 colspan=1>NA</td></tr></table>

The WB precision results comply with the pre-established acceptance criteria for score and individual analytes.

# 2. Linearity:

A study was performed to assess the linearity of measurement for each of the three measurands (TRAIL/IP-10/CRP) in serum and venous whole blood with acceptance criteria for bias due to non-linearity or less than $1 5 \%$ or $1 0 \mathrm { m g / L }$ for CRP, $1 5 \%$ or $1 0 \ : \mathrm { p g / m L }$ for TRAIL and $20 \%$ or 50 $\mathrm { { \ p g / m L } }$ for IP-10 of the value corresponding to the linear fit (predicted). The study was performed in one laboratory with two MeMed Key analyzer (one analyzer per cartridge lot), two lots of cartridges, one lot of calibration reagents and one lot of External Control reagents. Calibration was performed before initiating the study for each cartridge lot. External Controls were run daily.

Five replicates of eleven dilutions of each MeMed BV test measurand were measured in the linearity study. The order of measurement of the dilution series was randomized. The range of concentrations tested spanned the applicable range for determination of the MeMed BV score and were $1 0 0 { - } 2 0 0 0 \ \mathrm { p g / m L }$ for $\mathrm { I P - 1 0 , 1 5 - 3 0 0 \ p g / m L }$ for TRAIL, and $1 { - } 2 5 0 ~ \mu \mathrm { g / m L }$ for CRP.

Linearity for all MeMed BV measurands fell within the study acceptance criteria for the serum as well as the venous whole blood sample testing.

# 3. Analytical Specificity/Interference:

Interfering substances and cross-reactants were evaluated as part of the prior 510(k) submission (K222332). Since there is no change in cartridge reagents (antibody or assay formulation), this study was not repeated.

Hook effect for serum specimens was also evaluated as part of the prior 510(k) submission (K222332). A Hook effect study for venous whole blood specimens evaluated contrived samples containing high levels of each measurand (at the upper limit of quantitation (ULOQ and higher concentrations) and prepared by spiking protein rich buffer with recombinant proteins. For each concentration level, three runs were measured on one analyzer on the same day.

Table 6. Hook Effect Study Analyte Concentrations- WB   

<table><tr><td rowspan=1 colspan=1>Samples</td><td rowspan=1 colspan=1>TRAIL (pg/ml)</td><td rowspan=1 colspan=1>IP-10 (pg/ml)</td><td rowspan=1 colspan=1>CRP (mg/L)</td></tr><tr><td rowspan=1 colspan=1>Sample 1 (ULOQ)</td><td rowspan=1 colspan=1>283</td><td rowspan=1 colspan=1>5,582</td><td rowspan=1 colspan=1>303</td></tr><tr><td rowspan=1 colspan=1>Sample 2</td><td rowspan=1 colspan=1>478</td><td rowspan=1 colspan=1>6,500</td><td rowspan=1 colspan=1>372</td></tr><tr><td rowspan=1 colspan=1>Sample 3</td><td rowspan=1 colspan=1>667</td><td rowspan=1 colspan=1>7,307</td><td rowspan=1 colspan=1>410</td></tr><tr><td rowspan=1 colspan=1>Sample 4</td><td rowspan=1 colspan=1>821</td><td rowspan=1 colspan=1>8,046</td><td rowspan=1 colspan=1>462</td></tr></table>

Table 7. Hook Effect Study Results- WB   

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=3>Analyzer Measurement (RLUs)</td></tr><tr><td rowspan=1 colspan=1>Samples</td><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>CRP</td></tr><tr><td rowspan=1 colspan=1>Sample 1 (ULOQ)</td><td rowspan=1 colspan=1>3,671,325</td><td rowspan=1 colspan=1>10,293,660</td><td rowspan=1 colspan=1>7,109,370</td></tr><tr><td rowspan=1 colspan=1>Sample 2</td><td rowspan=1 colspan=1>6,189,605</td><td rowspan=1 colspan=1>11,987,250</td><td rowspan=1 colspan=1>8,755,138</td></tr><tr><td rowspan=1 colspan=1>Sample 3</td><td rowspan=1 colspan=1>8,621,900</td><td rowspan=1 colspan=1>13,475,810</td><td rowspan=1 colspan=1>9,676,356</td></tr><tr><td rowspan=1 colspan=1>Sample 4</td><td rowspan=1 colspan=1>10,611,703</td><td rowspan=1 colspan=1>14,839,404</td><td rowspan=1 colspan=1>10,900,659</td></tr></table>

No significant loss of signal was observed for the evaluated specimens containing high analyte concentrations. Therefore, no Hook effect was observed for the MeMed BV test with WB specimens.

# 4. Assay Reportable Range:

Not applicable

5. Traceability, Stability, Expected Values (Controls, Calibrators, or Methods):

# Calibrators

The calibration is a process used to generate the calibration curve and must be repeated every four weeks and/or when introducing a new test cartridge lot. The calibration curve translates RLU measurements to concentration of each analyte. A calibration is unique to a device and a cartridge lot. The calibrators are in effect synthetic samples which can be measured by the device using the normal cartridge. Each calibrator is a solution of the 3 analytes introduced as recombinant proteins. Each calibration set includes three vials that represent high, medium, and low values of the analyte ranges that impact the MeMed BV test score. Calibrators are provided by MeMed in vials which need to be stored in normal refrigerators $\left( 2 \mathrm { - } 8 ^ { \circ } \mathrm { C } \right)$ . All three analytes are traceable to a standard. The TRAIL analyte is traced to international biological reference standard, NIBSC code: 04/166. The CRP analyte is traced to international standard, IFCC/BCR/CAP CRM 474. The IP-10 analyte is traced to an internal standard prepared by R&D Systems (Cat. #890836) due to the unavailability of international standards for IP-10. The material was produced following ISO Guide 34:2009. Value assignment is validated and tested by a contract manufacturer (MicroCoat) for the quantification of secondary internal standard and for the quantification of master lot and user calibrators using MeMed Key analyzer.

The quality indicators (i.e., max/min slope, max/min intercept, min slope, and $\mathtt { R } ^ { 2 }$ ) represent specifications for calibration curves created with released cartridges. These thresholds are established for each lot of cartridges during manufacturing (based on actual performance of the produced lot). The data is then encoded to the cartridge barcode, to be read by the analyzer when running a calibration. Failure to meet these thresholds (during run-time of a calibration) will fail the calibration. In case of a calibration failure the device will issue a failure message to the user and will prevent the failed cartridge-lot from running. The device will only run with cartridges from a lot which has a valid calibration. It is possible to calibrate more than one cartridge lot.

# Calibration equivalency study:

Updates to the MeMed BV assay included changes to the assay calibration scheme. A study was conducted to evaluate correlation between the new calibration scheme (MCC) and the legacy calibration method. Briefly, one hundred serum specimens with known TRAIL, CRP and IP-10 concentrations were evaluated using both calibration methods on three separate analyzers, 1 repeat per analyzer.

![](images/43f6a470ab1dd6e457c7f72cf4229ec35ba4fc0c0e6af91cf4caf935b706ffe8.jpg)  
Figure 1. Deming regression analysis $( \lambda { = } 1 )$

Table 8. Estimate of bias at the four cut-off points between the bins   

<table><tr><td rowspan=1 colspan=1>Level</td><td rowspan=1 colspan=1>Bias</td><td rowspan=1 colspan=1>LCI</td><td rowspan=1 colspan=1>UCI</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>-0.57</td><td rowspan=1 colspan=1>-0.90</td><td rowspan=1 colspan=1>-0.37</td></tr><tr><td rowspan=1 colspan=1>35</td><td rowspan=1 colspan=1>-0.57</td><td rowspan=1 colspan=1>-0.83</td><td rowspan=1 colspan=1>-0.39</td></tr><tr><td rowspan=1 colspan=1>65</td><td rowspan=1 colspan=1>-0.56</td><td rowspan=1 colspan=1>-0.79</td><td rowspan=1 colspan=1>-0.37</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>-0.55</td><td rowspan=1 colspan=1>-0.82</td><td rowspan=1 colspan=1>-0.32</td></tr></table>

None of the scores for samples evaluated in the study shifted to a non-adjacent reporting bin due to change in calibration curve scheme. The legacy calibration and the MCC methods can be considered equivalent methods for producing BV Scores.

# Controls

The MeMed BV External controls are intended for quality control testing in clinical laboratories. The control set includes two control vials containing purified TRAIL, IP-10, and CRP antigens in a protein buffer. One vial corresponds to a bacterial MeMed BV test score (expected score 90- 100) and one vial corresponds to a viral MeMed BV test score (expected score 0-10). The

software evaluates each control and notifies the user whether the evaluation is completed successfully.

# Reagent Stability

Real-time, in use, and shipping stability of the test cartridge, calibrator and external control were validated to support the original clearance K210254. Since there is no change to these components, the stability studies were not repeated.

# Specimen Stability

Serum specimen stability and freeze-thaw stability were evaluated under the original clearance K210254 and was not re-evaluated due to no change in serum specimen processing workflow.

A study was conducted to demonstrate the appropriate handling conditions from venous whole blood draw to sample input into the cartridge. The study was conducted in one laboratory on four days, one day per panel member using four WB samples representing two samples with ‘low’ scores and two samples with ‘high’ scores. Two MeMed Key analyzers and one lot of cartridges were used. Calibration was performed at the beginning of the study using one lot of calibration reagents. Stability was assessed for each MeMed BV Test measurand (TRAIL/IP-10/CRP) as well as the MeMed BV Test resulting score.

Table 9. Specimen Stability Study Results- WB   

<table><tr><td rowspan=1 colspan=1>Sample</td><td rowspan=1 colspan=1>Incubation timebefore testing(Minutes)</td><td rowspan=1 colspan=1>Mean TRAIL(pg/mL)</td><td rowspan=1 colspan=1>Mean CRP(mg/L)</td><td rowspan=1 colspan=1>Mean IP-10(pg/mL)</td><td rowspan=1 colspan=1>Mean Score</td></tr><tr><td rowspan=6 colspan=1>High Score #1</td><td rowspan=1 colspan=1>1 - 10</td><td rowspan=1 colspan=1>30.8</td><td rowspan=1 colspan=1>176.9</td><td rowspan=1 colspan=1>107.4</td><td rowspan=1 colspan=1>99.0</td></tr><tr><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>30.3</td><td rowspan=1 colspan=1>170.1</td><td rowspan=1 colspan=1>110.1</td><td rowspan=1 colspan=1>99.5</td></tr><tr><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>27.9</td><td rowspan=1 colspan=1>167.0</td><td rowspan=1 colspan=1>109.7</td><td rowspan=1 colspan=1>99.0</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>26.9</td><td rowspan=1 colspan=1>191.0</td><td rowspan=1 colspan=1>102.9</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>23.9</td><td rowspan=1 colspan=1>178.6</td><td rowspan=1 colspan=1>107.0</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>150</td><td rowspan=1 colspan=1>23.2</td><td rowspan=1 colspan=1>177.7</td><td rowspan=1 colspan=1>115.5</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=6 colspan=1>High score #2</td><td rowspan=1 colspan=1>1 - 10</td><td rowspan=1 colspan=1>17.2</td><td rowspan=1 colspan=1>189.1</td><td rowspan=1 colspan=1>1677.1</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>16.9</td><td rowspan=1 colspan=1>166.3</td><td rowspan=1 colspan=1>1676.3</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>15.3</td><td rowspan=1 colspan=1>143.9</td><td rowspan=1 colspan=1>1571.8</td><td rowspan=1 colspan=1>99.5</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>14.0</td><td rowspan=1 colspan=1>161.6</td><td rowspan=1 colspan=1>1600.8</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>15.0</td><td rowspan=1 colspan=1>176.0</td><td rowspan=1 colspan=1>1808.8</td><td rowspan=1 colspan=1>100.0</td></tr><tr><td rowspan=1 colspan=1>150</td><td rowspan=1 colspan=1>17.2</td><td rowspan=1 colspan=1>155.8</td><td rowspan=1 colspan=1>1660.1</td><td rowspan=1 colspan=1>99.5</td></tr><tr><td rowspan=6 colspan=1>Low Score #1</td><td rowspan=1 colspan=1>1 - 10</td><td rowspan=1 colspan=1>191.3</td><td rowspan=1 colspan=1>76.5</td><td rowspan=1 colspan=1>1027.9</td><td rowspan=1 colspan=1>2.5</td></tr><tr><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>191.1</td><td rowspan=1 colspan=1>69.2</td><td rowspan=1 colspan=1>1088.2</td><td rowspan=1 colspan=1>2.5</td></tr><tr><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>170.3</td><td rowspan=1 colspan=1>74.1</td><td rowspan=1 colspan=1>1076.6</td><td rowspan=1 colspan=1>3.5</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>177.0</td><td rowspan=1 colspan=1>70.7</td><td rowspan=1 colspan=1>1039.1</td><td rowspan=1 colspan=1>3.0</td></tr><tr><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>164.5</td><td rowspan=1 colspan=1>70.8</td><td rowspan=1 colspan=1>1007.8</td><td rowspan=1 colspan=1>4.0</td></tr><tr><td rowspan=1 colspan=1>150</td><td rowspan=1 colspan=1>166.6</td><td rowspan=1 colspan=1>69.1</td><td rowspan=1 colspan=1>1067.4</td><td rowspan=1 colspan=1>3.5</td></tr><tr><td rowspan=6 colspan=1>Low Score #2</td><td rowspan=1 colspan=1>1 - 10</td><td rowspan=1 colspan=1>113.5</td><td rowspan=1 colspan=1>32.2</td><td rowspan=1 colspan=1>1467.2</td><td rowspan=1 colspan=1>6.5</td></tr><tr><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>106.9</td><td rowspan=1 colspan=1>30.5</td><td rowspan=1 colspan=1>1436.0</td><td rowspan=1 colspan=1>7.5</td></tr><tr><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>104.0</td><td rowspan=1 colspan=1>32.1</td><td rowspan=1 colspan=1>1391.3</td><td rowspan=1 colspan=1>9.0</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>106.1</td><td rowspan=1 colspan=1>33.6</td><td rowspan=1 colspan=1>1513.0</td><td rowspan=1 colspan=1>8.0</td></tr><tr><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>107.5</td><td rowspan=1 colspan=1>32.0</td><td rowspan=1 colspan=1>1500.5</td><td rowspan=1 colspan=1>8.0</td></tr><tr><td rowspan=1 colspan=1>150</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>N/A</td></tr></table>

No significant deviations were observed over the course of the study. These data support specimen storage for up to 120 mins at room temperature before testing.

# 6. Detection Limit:

For evaluated specimens with analyte levels below the limit of quantitation, the limit of quantitation value will be used to generate the MeMed BV score. Therefore, a limit of detection and a limit of blank was not evaluated.

# Limit of Quantitation

To establish equivalence between the new calibration scheme, raw data collected in a previous LoQ study to support the original clearance of the MeMed BV device (K222332) was reanalyzed using the new master calibration curve scheme. No significant differences in study results were observed when relying upon the new calibration scheme.

Additionally, a new study was conducted using two cartridge lots (per each test script) with one MeMed Key analyzer. Each sample was tested three times on three non-consecutive days. Because there are no serum or whole blood specimens with residual analyte levels for each of the three measurands one order of magnitude lower than the analytical range of the measurement procedure, a protein buffer (calibrator matrix) was employed as the blank samples. Four target concentrations were prepared as represented in table below.

Table 10. LoQ Study Panel Members   

<table><tr><td rowspan=1 colspan=1>Sample</td><td rowspan=1 colspan=1>Concentration</td><td rowspan=1 colspan=1>TRAIL (pg/ml)</td><td rowspan=1 colspan=1>IP-10 (pg/ml)</td><td rowspan=1 colspan=1>CRP (mg/L)</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>X0.8 of LLOQ</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>80</td><td rowspan=1 colspan=1>0.8</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>X0.9 of LLOQ</td><td rowspan=1 colspan=1>13.5</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>0.9</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>X1.0 of LLOQ</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>X1.1 of LLOQ</td><td rowspan=1 colspan=1>16.5</td><td rowspan=1 colspan=1>110</td><td rowspan=1 colspan=1>1.1</td></tr></table>

The TE (total error) was calculated for each of the four concentration levels for three analytes as $2 \textbf { x }$ SD observed (Westgard model with bias $\scriptstyle  = 0$ ) with acceptance criteria as $\mathrm { T E } < 3 0 \%$ for TRAIL and CRP and $\Gamma \mathrm { E } < 4 0 \%$ for IP-10.

Table 11. LoQ Study Results   

<table><tr><td colspan="2" rowspan="1">Cartridge Lot</td><td colspan="3" rowspan="1">Lot 1</td><td colspan="3" rowspan="1">Lot 2</td></tr><tr><td colspan="1" rowspan="1">Sample</td><td colspan="1" rowspan="1">Parameter</td><td colspan="1" rowspan="1">TRAIL(pg/mL)</td><td colspan="1" rowspan="1">IP-10(pg/mL)</td><td colspan="1" rowspan="1">CRP(mg/L)</td><td colspan="1" rowspan="1">TRAIL(pg/mL)</td><td colspan="1" rowspan="1">IP-10(pg/mL)</td><td colspan="1" rowspan="1">CRP(mg/L)</td></tr><tr><td colspan="1" rowspan="4">1</td><td colspan="1" rowspan="1">Mean</td><td colspan="1" rowspan="1">12.19</td><td colspan="1" rowspan="1">79.42</td><td colspan="1" rowspan="1">0.87</td><td colspan="1" rowspan="1">11.90</td><td colspan="1" rowspan="1">67.08</td><td colspan="1" rowspan="1">0.94</td></tr><tr><td colspan="1" rowspan="1">STD</td><td colspan="1" rowspan="1">0.91</td><td colspan="1" rowspan="1">5.26</td><td colspan="1" rowspan="1">0.05</td><td colspan="1" rowspan="1">0.43</td><td colspan="1" rowspan="1">2.69</td><td colspan="1" rowspan="1">0.06</td></tr><tr><td colspan="1" rowspan="1">CV (%)</td><td colspan="1" rowspan="1">7%</td><td colspan="1" rowspan="1">7%</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">4%</td><td colspan="1" rowspan="1">4%</td><td colspan="1" rowspan="1">6%</td></tr><tr><td colspan="1" rowspan="1">TE (%)</td><td colspan="1" rowspan="1">15%</td><td colspan="1" rowspan="1">13%</td><td colspan="1" rowspan="1">11%</td><td colspan="1" rowspan="1">7%</td><td colspan="1" rowspan="1">8%</td><td colspan="1" rowspan="1">12%</td></tr><tr><td colspan="1" rowspan="4">2</td><td colspan="1" rowspan="1">Mean</td><td colspan="1" rowspan="1">13.70</td><td colspan="1" rowspan="1">92.33</td><td colspan="1" rowspan="1">1.03</td><td colspan="1" rowspan="1">13.28</td><td colspan="1" rowspan="1">80.41</td><td colspan="1" rowspan="1">1.07</td></tr><tr><td colspan="1" rowspan="1">STD</td><td colspan="1" rowspan="1">0.57</td><td colspan="1" rowspan="1">5.91</td><td colspan="1" rowspan="1">0.09</td><td colspan="1" rowspan="1">0.73</td><td colspan="1" rowspan="1">4.05</td><td colspan="1" rowspan="1">0.05</td></tr><tr><td colspan="1" rowspan="1">CV (%)</td><td colspan="1" rowspan="1">4%</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">8%</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">5%</td><td colspan="1" rowspan="1">4%</td></tr><tr><td colspan="1" rowspan="1">TE (%)</td><td colspan="1" rowspan="1">8%</td><td colspan="1" rowspan="1">13%</td><td colspan="1" rowspan="1">17%</td><td colspan="1" rowspan="1">11%</td><td colspan="1" rowspan="1">10%</td><td colspan="1" rowspan="1">9%</td></tr><tr><td colspan="1" rowspan="2">3</td><td colspan="1" rowspan="1">Mean</td><td colspan="1" rowspan="1">14.38</td><td colspan="1" rowspan="1">96.75</td><td colspan="1" rowspan="1">1.07</td><td colspan="1" rowspan="1">14.86</td><td colspan="1" rowspan="1">94.79</td><td colspan="1" rowspan="1">1.19</td></tr><tr><td colspan="1" rowspan="1">STD</td><td colspan="1" rowspan="1">0.40</td><td colspan="1" rowspan="1">6.90</td><td colspan="1" rowspan="1">0.05</td><td colspan="1" rowspan="1">0.77</td><td colspan="1" rowspan="1">4.89</td><td colspan="1" rowspan="1">0.05</td></tr><tr><td colspan="1" rowspan="2"></td><td colspan="1" rowspan="1">CV (%)</td><td colspan="1" rowspan="1">3%</td><td colspan="1" rowspan="1">7%</td><td colspan="1" rowspan="1">5%</td><td colspan="1" rowspan="1">5%</td><td colspan="1" rowspan="1">5%</td><td colspan="1" rowspan="1">4%</td></tr><tr><td colspan="1" rowspan="1">TE (%)</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">14%</td><td colspan="1" rowspan="1">10%</td><td colspan="1" rowspan="1">10%</td><td colspan="1" rowspan="1">10%</td><td colspan="1" rowspan="1">8%</td></tr><tr><td colspan="1" rowspan="4">4</td><td colspan="1" rowspan="1">Mean</td><td colspan="1" rowspan="1">16.34</td><td colspan="1" rowspan="1">107.29</td><td colspan="1" rowspan="1">1.23</td><td colspan="1" rowspan="1">16.06</td><td colspan="1" rowspan="1">107.11</td><td colspan="1" rowspan="1">1.31</td></tr><tr><td colspan="1" rowspan="1">STD</td><td colspan="1" rowspan="1">0.60</td><td colspan="1" rowspan="1">6.28</td><td colspan="1" rowspan="1">0.08</td><td colspan="1" rowspan="1">0.67</td><td colspan="1" rowspan="1">5.09</td><td colspan="1" rowspan="1">0.07</td></tr><tr><td colspan="1" rowspan="1">CV (%)</td><td colspan="1" rowspan="1">4%</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">6%</td><td colspan="1" rowspan="1">4%</td><td colspan="1" rowspan="1">5%</td><td colspan="1" rowspan="1">5%</td></tr><tr><td colspan="1" rowspan="1">TE (%)</td><td colspan="1" rowspan="1">7%</td><td colspan="1" rowspan="1">12%</td><td colspan="1" rowspan="1">13%</td><td colspan="1" rowspan="1">8%</td><td colspan="1" rowspan="1">10%</td><td colspan="1" rowspan="1">10%</td></tr></table>

The results show that MeMed BV test passed the acceptance criteria of TE for all samples tested. For the defined LLOQ concentration levels of TRAIL, CRP, and IP10 (TRAIL $1 5 ~ \mathrm { p g / m L }$ , CRP 1 $\mathrm { m g / L }$ , $\mathrm { I P 1 0 ~ 1 0 0 ~ p g / m L } )$ established in the original clearance (K210254) the results achieved the following maximal TE values: TRAIL $10 \%$ , CRP $10 \%$ , and $1 \mathrm { P l } 0 1 4 \%$ .

# 7. Assay Cut-Off:

The assay cut-offs remain unchanged from the previously cleared version of the MeMed BV Device. Please see the published decision summary for K210254 for additional details.

# 8. Carry-Over:

Carry over for serum specimen was evaluated under the original clearance K210254 and was not re-evaluated due to no change in serum specimen processing workflow. A study was performed to evaluate the risk of carry-over between multiple cartridges evaluated on the MeMed Key instrument for venous whole blood specimen. Specifically, a low score (“L”) and high score (“H”) clinical specimen were evaluated according to the following sequences:

1) H, H, H, H, H, L, H, L, H, L, H, L, H, L, H   
2) L, L, L, L, L, H, L, H, L, H, L, H, L, H, L.

For both sequences evaluated, no significant difference was observed in assay score for either the high or low clinical specimens. These data support that no carry over occurs in the MeMed Key instrument with the MeMed BV assay cartridges.

# Lead Reviewer or Consulting Reviewer Comments for Internal Discussion Only

The Carry-over study results are acceptable.

# B Comparison Studies:

# 1. Method Comparison with Predicate Device:

The equivalency between whole blood and serum sample type for the MeMed BV test was established by a prospective, multi-center study where matched serum and venous whole blood specimens were collected from 216 prospectively recruited subjects from 5 medical centers (2 in the US and 3 in Israel). The study population comprised hospital admitted, emergency department, and urgent care center patients over the age of 90 days, with clinical suspicion of acute bacterial or viral infection.

Results from paired sample testing were evaluated with Passing Bablok regression analysis and the following pre-defined acceptance criteria was applied to the clinically relevant measure of the test, BV score: a slope in the range of 0.9-1.1 and an intercept in the range of -5 to 5.

Table 12. Passing Bablok Regression Analysis Results –MeMed BV Test (Whole blood) Results Compared to the Predicate Device (MeMed BV Test-Serum)   

<table><tr><td rowspan=1 colspan=1>Analyte</td><td rowspan=1 colspan=1>Samplesize</td><td rowspan=1 colspan=1>Slope (95% CI)</td><td rowspan=1 colspan=1>Y-intercept(95% CI)</td></tr><tr><td rowspan=1 colspan=1>TRAIL</td><td rowspan=1 colspan=1>216</td><td rowspan=1 colspan=1>0.99[0.97 - 1.01]</td><td rowspan=1 colspan=1>0.522 [-0.37 - 2.34]</td></tr><tr><td rowspan=1 colspan=1>IP-10</td><td rowspan=1 colspan=1>216</td><td rowspan=1 colspan=1>1.00[0.96 -1.04]</td><td rowspan=1 colspan=1>-6.53[-12.75 - 3.71]</td></tr><tr><td rowspan=1 colspan=1>CRP</td><td rowspan=1 colspan=1>216</td><td rowspan=1 colspan=1>0.87[0.85 - 0.90]</td><td rowspan=1 colspan=1>2.76[2.21 - 3.06]</td></tr><tr><td rowspan=1 colspan=1>Score</td><td rowspan=1 colspan=1>216</td><td rowspan=1 colspan=1>1.00 [0.99 - 1.00]</td><td rowspan=1 colspan=1>0.00 [0.00 - 0.06]</td></tr></table>

The Passing Bablok regression analysis comparing the BV scores for the tested serum and venous whole blood specimens yielded a slope of 1.00, $9 5 \%$ CI 0.99-1.00 and intercept of 0.00, $9 5 \%$ CI 0.00-0.06 which was well within the pre-defined acceptance criteria. Additional regression analyses of individual measurand values for IP-10 and CRP assay indicated intercept and slope values, respectively, outside of pre-defined acceptance criteria; however, no systemic bias was observed in the overall score values which is the clinically relevant test result. Therefore, the expected clinical impact of the observed bias is expected to be minimal.

Additional analyses were performed to calculate the estimated bias at each cutoff point and the corresponding $9 5 \%$ confidence intervals for the bias at each point. Results are provided in Table 2 below. Bias was calculated based on regression analysis, with the ratio of error variances set at $\lambda { = } 1$ . Confidence bands were computed using bootstrap samples and the accelerated bias correction (BCa) method.

Table 13. Bias Analysis –Bias Estimates for the MeMed BV Score Value at Relevant Cutoffs   

<table><tr><td rowspan=1 colspan=1>Cutoff</td><td rowspan=1 colspan=1>Estimate</td><td rowspan=1 colspan=2>95% CI</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>0.46</td><td rowspan=1 colspan=1>-0.60</td><td rowspan=1 colspan=1>1.41</td></tr><tr><td rowspan=1 colspan=1>35</td><td rowspan=1 colspan=1>-0.02</td><td rowspan=1 colspan=1>-0.96</td><td rowspan=1 colspan=1>0.90</td></tr><tr><td rowspan=1 colspan=1>65</td><td rowspan=1 colspan=1>-0.60</td><td rowspan=1 colspan=1>-1.63</td><td rowspan=1 colspan=1>0.39</td></tr><tr><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>-1.09</td><td rowspan=1 colspan=1>-2.28</td><td rowspan=1 colspan=1>0.06</td></tr></table>

Further analysis of the study data was conducted to assess the potential impact of sample type on score assignment to risk bins reported by the MeMed BV test was assessed. The acceptance criteria were pre-defined as less than $5 \%$ of the paired serum and whole blood samples demonstrating a score deviation that causes a patient to be assigned to a nonadjacent bin.

Table 14. MeMed BV Device (Whole blood) Bin Results – Comparison to the Predicate Device (MeMed BV Test-Serum)   

<table><tr><td colspan="1" rowspan="2">MeMedBV results(WB)</td><td colspan="5" rowspan="1">MeMed BV results(Serum)-Predicate</td></tr><tr><td colspan="1" rowspan="1">Bin1</td><td colspan="1" rowspan="1">Bin2</td><td colspan="1" rowspan="1">Bin3</td><td colspan="1" rowspan="1">Bin4</td><td colspan="1" rowspan="1">Bin5</td></tr><tr><td colspan="1" rowspan="1">Bin1</td><td colspan="1" rowspan="1">64</td><td colspan="1" rowspan="1">1</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td></tr><tr><td colspan="1" rowspan="1">Bin2</td><td colspan="1" rowspan="1">6</td><td colspan="1" rowspan="1">21</td><td colspan="1" rowspan="1">1</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td></tr><tr><td colspan="1" rowspan="1">Bin3</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">18</td><td colspan="1" rowspan="1">4</td><td colspan="1" rowspan="1">0</td></tr><tr><td colspan="1" rowspan="1">Bin4</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">6</td><td colspan="1" rowspan="1">22</td><td colspan="1" rowspan="1">6</td></tr><tr><td colspan="1" rowspan="1">Bin5</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">0</td><td colspan="1" rowspan="1">2</td><td colspan="1" rowspan="1">63</td></tr><tr><td colspan="1" rowspan="1">Agreement</td><td colspan="1" rowspan="1">91.4%(64/70)</td><td colspan="1" rowspan="1">91.3%(21/23)</td><td colspan="1" rowspan="1">72.0%(18/25)</td><td colspan="1" rowspan="1">78.6%(22/28)</td><td colspan="1" rowspan="1">91.3%(63/69)</td></tr></table>

None of the test results for the whole blood samples evaluated shifted to a non-adjacent reporting bin when compared to the test results for the matching serum samples using the MeMed BV device. Cumulatively, the data summarized above establish equivalent performance between the whole blood and serum samples when tested using the MeMed BV device.

The above analysis demonstrates equivalent performance of serum and WB samples on the MeMed BV device.

# C Clinical Studies:

# 1. Clinical Sensitivity:

Clinical validation of the MeMed BV device in their intended use population was previously reviewed under K210254. Please refer to the published decision summary for additional clinical validation information. The purpose of this 510(k) submission is to establish matrix equivalence between serum and venous whole blood specimens using the MeMed BV assay.

# 2. Clinical Specificity:

See Clinical Sensitivity section C.1 above.

3. Other Clinical Supportive Data (When 1. and 2. Are Not Applicable):

Not applicable.

# D Clinical Cut-Off:

Clinical performance of the MeMed BV device in their intended use population was previously established in K210254. Please refer to the published decision summary for information regarding the relevant clinical cut-offs of the MeMed BV device.

# E Expected Values/Reference Range:

Clinical performance of the MeMed BV device in their intended use population was previously established in K210254. Please refer to the published decision summary for information regarding the expected values for the MeMed BV device.

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.