# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYASSAY AND INSTRUMENT

I Background Information:

A 510(k) Number K234070   
B Applicant Dexcom, Inc.   
C Proprietary and Established Names Stelo Glucose Biosensor System   
D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>SAF</td><td rowspan=1 colspan=1>Class II</td><td rowspan=1 colspan=1>21 CFR 862.1355 -Integrated ContinuousGlucose MonitoringSystem</td><td rowspan=1 colspan=1>CH - ClinicalChemistry</td></tr></table>

II Submission/Device Overview:

A Purpose for Submission: New device   
B Measurand: Glucose in Interstitial Fluid   
C Type of Test: Quantitative, amperometric assay (Glucose Oxidase)

# III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below.

# B Indication(s) for Use:

The Stelo Glucose Biosensor System is an over-the-counter (OTC) integrated Continuous Glucose Monitor (iCGM) intended to continuously measure, record, analyze, and display glucose values in people 18 years and older not on insulin. The Stelo Glucose Biosensor System helps to detect normal (euglycemic) and low or high (dysglycemic) glucose levels. The Stelo Glucose Biosensor System may also help the user better understand how lifestyle and behavior modification, including diet and exercise, impact glucose excursion.

The user is not intended to take medical action based on the device output without consultation with a qualified healthcare professional.

# C Special Conditions for Use Statement(s):

OTC - Over The Counter

No MRI/CT/diathermy — MR unsafe: Don't wear any Stelo Glucose Biosensor system component during magnetic resonance imaging (MRI) or high-frequency electrical heat (diathermy) treatment. However, it's safe to have a CT scan if you keep the sensor out of the scanned area and cover the sensor with a lead apron during the scan. The Stelo Glucose Biosensor system hasn't been tested in those situations when used during an MRI scan, diathermy, or in the scanned area of a CT scan. The magnetic fields and heat could damage Stelo Glucose Biosensor system components, which may cause inaccurate sensor readings.

With the Stelo Glucose Biosensor system, you can take a standard or maximum acetaminophen dose of 1 gram $\left( 1 , 0 0 0 \mathrm { m g } \right)$ every 6 hours and still use the Stelo Glucose Biosensor system. Taking higher than the maximum dose of acetaminophen (e.g. $> 1$ gram every 6 hours in adults) may affect the sensor readings and make them look higher than they really are.

If you are taking hydroxyurea, your sensor readings will be higher than your actual glucose. The level of inaccuracy depends on the amount of hydroxyurea in your body. Talk to your physician about alternative glucose monitoring approaches.

Don't use if you have problematic hypoglycemia. The Stelo Glucose Biosensor system hasn't been designed for these populations. Consult with your healthcare provider to discuss which Dexcom product is right for you.

Don't use if you are on dialysis. The Stelo Glucose Biosensor system performance hasn't been evaluated in these populations and sensor readings may be inaccurate.

Only insert your sensor on the back of your upper arm. Don't wear your sensor on other sites (such as your abdomen), as it may not work as expected.

# D Special Instrument Requirements:

Not applicable.

# A Device Description:

The Stelo Glucose Biosensor System System is a home use device that is intended to continuously measure the glucose in the interstitial fluid, calculate the glucose reading and make this value available to the user. The Stelo System can reliably and securely transmit glucose measurement data to authorized digitally connected devices. The Stelo System is not intended to be used in conjunction with insulin devices such as insulin pens and Automated Insulin Dosing (AID) systems.

The Stelo System is based on the same principle of operation, fundamental design, and physical characteristics as the G7 CGM System, Dexcom’s most recent prescription integrated continuous glucose monitoring (iCGM) system (predicate device: K231081). The Stelo System comprises the following two subsystems:

1. Glucose Sensing Subsystem (GSS): Wearable (Sensor, Transmitter, and Patch) and Applicator The sensor is a small and flexible wire inserted by the applicator into subcutaneous tissue where it converts glucose into electric current. The transmitter is pre-connected to the sensor and is worn on the body by the adhesive patch. The transmitter measures the electric current produced by the sensor and converts these measurements into estimated glucose values (EGV) using an onboard algorithm. The transmitter sends glucose data to a mobile application. Each GSS box also includes an overpatch, which is a general adhesive tape that helps with the adhesion of the wearable to the user’s body.

2. Mobile Applications Subsystem (MAS): iOS and Android Mobile Application (App) The App provides in-app guidance for the user on how to apply and set up the wearable and how to create a user account. Once the set-up has been completed, the App receives information from the transmitter and acts as a user interface by indicating the system state (e.g., warm-up period, signal loss, etc.) and displaying glucose readings and trend graphs.

# Stelo Glucose Sensing Subsystem (GSS)

The Stelo GSS has the same hardware design as the predicate device (G7 GSS); the devices use the same sensor, patch, applicator, and transmitter hardware. In addition, the Stelo transmitter firmware has the same primary responsibilities as the predicate G7 transmitter firmware.

While the firmware modes, firmware modules, wireless communication requirements, and algorithm inputs/outputs of the Stelo transmitter firmware remain the same as the predicate device, the Stelo transmitter firmware includes the following differences:

• No optional calibration o The Stelo transmitter firmware is factory calibrated only and does not use any Blood Glucose (BG) entered by the lay user for calibration.   
Device connectivity restrictions o The Stelo transmitter firmware does not pair/connect to an additional dedicated primary display device (e.g., a receiver), insulin pens, AID systems, or other

unauthorized devices. The Stelo transmitter can only pair/connect to the user’s (personal) smartphone. Extended (15.5 days) device wear duration o The Stelo transmitter firmware supports a sensor wear duration of 15 days, compared to 10 days for the predicate. Algorithm modifications o The algorithm was modified to support the extended wear duration while maintaining the accuracy of the device. Additional algorithm modifications and parameter optimizations were also introduced to help improve the user experience (e.g., reducing jitteriness of glucose readings displayed in the trend graph and better handling of edge cases or specific scenarios users may encounter in the field).

# Stelo Mobile Application System (MAS)

The Stelo MAS consists of the Stelo app that is available on both iOS and Android platforms. The app can be downloaded to a compatible, Bluetooth Low Energy (BLE)-enabled smart device. The Stelo app was developed using the same software development kit (SDK) as the predicate device (G7 app) and inherited the main functionality and UI elements: in-app onboarding, current glucose value, trend graph, in-app Clarity card, event logging, and connectivity to Dexcom’s cloud servers. The following main UI elements were tailored to the Stelo user population:

Stelo app onboarding o Similar to the predicate device, the Stelo app includes an onboarding experience to guide users through inserting the wearable and setting up the app. Instructions and safety information are tailored to the Stelo user population.   
App update interval o The Stelo app wirelessly receives glucose information from the transmitter every five minutes. All the sensor readings are then displayed on the mobile app every 15 minutes   
Narrowed displayed glucose range o Similar to the predicate device, the sensor measures glucose values within the 40- $4 0 0 \mathrm { m g / d L }$ range and sends the glucose data to the Stelo app. The Stelo app then narrows the displayed glucose values to $7 0 { - } 2 5 0 \ \mathrm { m g / d L }$ . The displayed glucose range is intended to provide the glucose range pertinent to the Stelo user population who may not often have glucose values less than $7 0 \mathrm { m g / d L }$ and more than $2 5 0 \mathrm { m g / d L }$ . Glucose values below this range are reported as “Below 70 $\mathrm { m g / d L ^ { \prime \prime } }$ and glucose values above this range are reported as “Above $2 5 0 \mathrm { m g / d L }$ .”   
Insights o The user can review their latest time in range (day by day and at the end of a session) through "Insights," a feature that calculates how much time the user's glucose was in range during the preceding day(s). The Insights also present suggestions for how the user can increase the time in range. Insights are delivered to the user as an out-of-app notification and can also be accessed from within the Stelo app.   
Alerts removal o Glucose alerts and alarms (e.g., Urgent Low Alarm, Urgent Low Soon, Low, High, Rising Fast, and Falling Fast Alerts) are not included in the Stelo app,

unlike the predicate G7 app. The Stelo app provides lock screen and in-app visual notifications to the user such as Bluetooth off, Signal Loss, or Sensor Expired.

# B Principle of Operation:

The Stelo Glucose Biosensor System detects glucose levels from the fluid just beneath the skin (interstitial fluid). The sensor probe continuously measures glucose concentration in the interstitial fluid via an enzymatic electrochemical reaction using glucose oxidase. The enzyme, glucose oxidase, catalyzes the oxidation of glucose and produces hydrogen peroxide. The production of hydrogen peroxide generates an electrical current that is proportionate to the interstitial glucose concentration. The transmitter converts the signal using an algorithm to a glucose value read in $\mathrm { m g / d L }$ , which is then transmitted to the mobile application for the user to see and use accordingly.

# C Instrument Description Information:

1. Instrument Name: Stelo Glucose Biosensor System

2. Specimen Identification: Not applicable.

3. Specimen Sampling and Handling: Not applicable.

4. Calibration: The Stelo Glucose Biosensor System is factory calibrated. Users may not enter optional calibrations based on fingerstick blood glucose values.

5. Quality Control:

Not applicable.

This medical device product has functions subject to FDA premarket review as well as functions that are not subject to FDA premarket review. For this application, if the product has functions that are not subject to FDA premarket review, FDA assessed those functions only to the extent that they either could adversely impact the safety and effectiveness of the functions subject to FDA premarket review or they are included as a labeled positive impact that was considered in the assessment of the functions subject to FDA premarket review.

# V Substantial Equivalence Information:

A Predicate Device Name(s): Dexcom G7 Continuous Glucose Monitoring (CGM) System

# B Predicate 510(k) Number(s):

# K231081

C Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp; PredicateDevice(s):</td><td colspan="1" rowspan="1">K234070</td><td colspan="1" rowspan="1">K231081</td></tr><tr><td colspan="1" rowspan="1">Device Trade Name</td><td colspan="1" rowspan="1">Stelo GlucoseBiosensor System</td><td colspan="1" rowspan="1">Dexcom G7 ContinuousGlucose Monitoring(CGM) System</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristic Similarities</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use/IndicationsFor Use</td><td colspan="1" rowspan="1">Automatically measureglucose in bodily fluidscontinuously for aspecified period of time</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Use Setting</td><td colspan="1" rowspan="1">Home use</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristic Differences</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use Population</td><td colspan="1" rowspan="1">Persons who are not oninsulin therapy age 18years and older</td><td colspan="1" rowspan="1">Persons with diabetesage 2 years and older</td></tr><tr><td colspan="1" rowspan="1">Type of Use</td><td colspan="1" rowspan="1">Over-the-counter use</td><td colspan="1" rowspan="1">Prescription use</td></tr><tr><td colspan="1" rowspan="1">Sensor Calibration</td><td colspan="1" rowspan="1">Factory calibrated only</td><td colspan="1" rowspan="1">Factory calibrated withoptional manualcalibration</td></tr><tr><td colspan="1" rowspan="1">Sensor Useful Life</td><td colspan="1" rowspan="1">Up to 15 days with 12hour grace period(automatic sensor shutoff</td><td colspan="1" rowspan="1">Up to 10 days with 12hours grace period(automatic sensor shutoff)</td></tr><tr><td colspan="1" rowspan="1">Primary Display Device</td><td colspan="1" rowspan="1">Mobile app</td><td colspan="1" rowspan="1">Mobile app or receiver</td></tr><tr><td colspan="1" rowspan="1">Displayed Range</td><td colspan="1" rowspan="1">70-250 mg/dL</td><td colspan="1" rowspan="1">40-400 mg/dL</td></tr><tr><td colspan="1" rowspan="1">Display Device UpdateInterval</td><td colspan="1" rowspan="1">Every 15 minutes</td><td colspan="1" rowspan="1">Every 5 minutes</td></tr><tr><td colspan="1" rowspan="1">Glucose Alerts and Alarms</td><td colspan="1" rowspan="1">None</td><td colspan="1" rowspan="1">Mandatory Alarms:Urgent LowOptional Alerts: UrgentLow Soon, LowGlucose, High Glucose,Falling Fast, Rising Fast</td></tr><tr><td colspan="1" rowspan="1">Compatibility withConnected Devices</td><td colspan="1" rowspan="1">Compatible withdigitally connecteddevices excluding</td><td colspan="1" rowspan="1">Compatible withdigitally connecteddevices including</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">insulin devices such asinsulin pens and AIDsystems</td><td colspan="1" rowspan="1">insulin devices.</td></tr><tr><td colspan="1" rowspan="1">Connectivity with cloud-based applications</td><td colspan="1" rowspan="1">The App cancommunicate wirelesslyto Dexcom Clarity.</td><td colspan="1" rowspan="1">The App cancommunicate wirelesslyto Dexcom Clarity andDexcom Follow App.</td></tr></table>

# VI Standards/Guidance Documents Referenced:

1. ISO 14971 Third Edition 2019-12: Medical devices - Application of risk management to medical devices   
2. IEC 62304 62304 Edition 1.1 2015-06 CONSOLIDATED VERSION: Medical device software - Software life cycle processes   
3. ANSI AAMI ES60601-1:2005/(R)2012 & A1:2012 C1:2009/(R)2012 & A2:2010/(R)2012 (Cons. Text) [Incl. AMD2:2021]: Medical electrical equipment – Part 1: General requirements for basic safety and essential performance   
4. IEC 60601-1-2 Edition 4.1 2020-09 CONSOLIDATED VERSION: Medical electrical equipment - Part 1-2: General requirements for basic safety and essential performance   
5. IEC 60601-1-6 Edition 3.2 2020-07 CONSOLIDATED VERSION: Medical electrical equipment - Part 1-6: General requirements for basic safety and essential performance   
6. IEC 60601-1-11 Edition 2.1 2020-07 CONSOLIDATED VERSION: Medical electrical equipment - Part 1-11: General requirements for basic safety and essential performance   
7. ISO 14155 Third Edition 2020-07: Clinical investigation of medical devices for human subjects - Good clinical practice   
8. IEC 1162366-1 Edition 1.1 2020-06 CONSOLIDATED VERSION: Medical devices - Part 1: Application of usability engineering to medical devices   
9. ISO 10993-1 Fifth edition 2018-08: Biological evaluation of medical devices - Part 1: Evaluation and testing within a risk management process   
10. ISO 10993-2 Second edition 2006-07-15: Biological Evaluation of medical devices - Part 2: Animal welfare requirements   
11. ISO 10993-3 Third edition 2014-10-1: Biological evaluation of medical devices - Part 3: Tests for genotoxicity carcinogenicity and reproductive toxicity   
12. ISO 10993-5 Third edition 2009-06-01 Biological evaluation of medical devices - Part 5: Tests for in vitro cytotoxicity   
13. ISO 10993-6 Third edition 2016-12-01: Biological evaluation of medical devices -- Part 6: Tests for local effects after implantation   
14. ISO 10993-7 Second edition 2008-10-15 Biological evaluation of medical devices - Part 7: Ethylene oxide sterilization residuals   
15. ISO 10993-10 Third Edition 2010-08-01 Biological evaluation of medical devices - Part 10: Tests for irritation and skin sensitization   
16. ISO 10993-11 Third edition 2017-09 Biological evaluation of medical devices - Part 11: Tests for systemic toxicity   
17. ISO 10993-12 Fourth edition 2012-07-01 Biological evaluation of medical devices - Part 12: Sample preparation and reference materials   
18. ISO 10993-17 First edition 2002-12-01 Biological evaluation of medical devices - Part 17: Establishment of allowable limits for leachable substances

19. ISO 10993-18 Second edition 2020-01 Biological evaluation of medical devices - Part 18: Chemical characterization of medical device materials within a risk management process

20. ISO 11607-1 Second edition 2019-02 Packaging for terminally sterilized medical devices - Part 1: Requirements for materials sterile barrier systems and packaging systems

21. ISO 11607-2 Second edition 2019-02 Packaging for terminally sterilized medical devices - Part 2: Validation requirements for forming sealing and assembly processes

22. ISO 11135 Second edition 2014-07-15 Sterilization of health-care products - Ethylene oxide - Requirements for the development, validation, and routine control of a sterilization process for medical devices

23. ISO 11737-1 Third edition 2018-01 [including AMD:21] Sterilization of health care products - Microbiological methods - Part 1: Determination of a population of microorganisms on products

24. ISO 11737-2 Third edition 2019-12 Sterilization of medical devices - Microbiological methods - Part 2: Tests of sterility performed in the definition, validation and maintenance of a sterilization process

25. ISO 15223-1 Fourth edition 2021-07 Medical devices - Symbols to be used with information to be supplied by the manufacturer - Part 1: General requirements

26. ASTM D4169-22 Standard Practice for Performance Testing of Shipping Containers and Systems

27. ASTM F2503-23 Standard Practice for Marking Medical Devices and Other Items for Safety in the Magnetic Resonance Environment

28. ISO 23908 First edition 2011-06-11 Sharps injury protection - Requirements and test methods - Sharps protection features for single-use hypodermic needles, introducers for catheters and needles used for blood sampling

29. IEC 62133-2 Edition 1.0 2017-02: Secondary cells and batteries containing alkaline or other non-acid electrolytes - Safety requirements for portable sealed secondary cells, and for batteries made from them, for use in portable applications – Part 2: Lithium systems

30. IEC TR 60601-4-2 Edition 1.0 2016-05 Medical electrical equipment - Part 4-2:

Guidance and interpretation - Electromagnetic immunity: performance of medical electrical equipment and medical electrical systems

31. AIM Standard 7351731 Rev. 3.00 2021-06-04 Medical Electrical Equipment and System Electromagnetic Immunity Test for Exposure to Radio Frequency Identification Readers

32. IEEE ANSI USEMCSC C63.27-2021 American National Standard for Evaluation of Wireless Coexistence

33. AAMI TIR69:2017/(R2020) Technical Information Report Risk management of radiofrequency wireless coexistence for medical devices and systems

34. IEC 60417:2002 Graphical symbols for use on equipment

35. ANSI AAMI HE75:2009/(R)2018 Human factors engineering – Design of medical devices

36. ISO 11138-1 Third edition 2017-03 Sterilization of health care products – Biological indicators – Part 1: General requirements

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

1. Precision/Reproducibility:

Stelo Glucose Biosensor performance was evaluated in clinical studies described below in section C(3). A subset of subjects wore two Stelo Glucose Biosensor at the same time $( \mathrm { N } { = } 1 8$ ). Precision was evaluated by comparing the glucose reading from the two Systems worn by the same subject on the backs of both upper arms.

The mean paired absolute relative difference (between the 2 concurrently worn devices) was $8 . 8 \%$ and the mean coefficient of variation (mean $\% C V _ { \perp }$ ) was $6 . 2 \%$ .

# Precision Analysis

<table><tr><td rowspan=1 colspan=1>Matched Pairs (n)</td><td rowspan=1 colspan=1>63,024</td></tr><tr><td rowspan=1 colspan=1>Number of subjects (N)</td><td rowspan=1 colspan=1>18</td></tr><tr><td rowspan=1 colspan=1>Paired absolute difference (mg/dL)</td><td rowspan=1 colspan=1>13.3</td></tr><tr><td rowspan=1 colspan=1>Paired absolute relative difference (%)</td><td rowspan=1 colspan=1>8.8</td></tr><tr><td rowspan=1 colspan=1>Coefficient of variation (%)</td><td rowspan=1 colspan=1>6.2</td></tr></table>

2. Linearity:

The measurement range of the System is $4 0 { \cdot } 4 0 0 \ \mathrm { m g / d L }$ and the reportable range is 70-250 $\mathrm { m g / d L }$ . Data supporting this claimed measurement range was generated in the clinical study described in Section C(3) below.

# 3. Analytical Specificity/Interference:

Users of the Stelo Glucose Biosensor System can take a standard or maximum dose of acetaminophen (up to 1 gram every 6 hours in adults) and still use the Stelo System readings. Sensor glucose readings will be falsely higher if the user is taking more than a standard acetaminophen dose.

Sensor glucose readings will also be falsely higher if the user is taking hydroxyurea. Users should talk to their physician about alternative glucose monitoring approaches if they are taking hydroxyurea.

4. Assay Reportable Range: See Linearity section above.

5. Traceability, Stability, Expected Values (Controls, Calibrators, or Methods):

The Stelo GSS (sensor and transmitter) has a storage shelf-life of up to 10 months. Shelf life was evaluated at $8 6 \mathrm { { ^ \circ F } }$ . Sensors should be stored at $3 6 ^ { \circ } - 8 6 ^ { \circ } \mathrm { F }$ and $10 \mathrm { - } 9 0 \%$ relative humidity.

6. Detection Limit:

If a glucose measurement is less than $7 0 \mathrm { m g / d L }$ , the result is displayed by the system as “Below $7 0 \mathrm { m g / d L }$ .” If a glucose measurement exceeds $2 5 0 \mathrm { m g / d L }$ , result is displayed as “Above $2 5 0 \mathrm { m g / d L }$ .” Users can view historical results across the full device measurement range $4 0 { - } 4 0 0 ~ \mathrm { m g / d L } )$ via Dexcom Clarity, a cloud-based software available on the web and on apps.

7. Assay Cut-Off: Not applicable

8. Accuracy (Instrument): Not applicable.

9. Carry-Over: Not applicable.

# B Comparison Studies:

1. Method Comparison with Predicate Device:

Not applicable. Accuracy is determined by comparing device values to an FDA cleared laboratory grade glucose analyzer (Yellow Springs Instrument 2300 STAT Plus™ Glucose Analyzer) and referred to as the “comparator method” in Section C(3) below.

2. Matrix Comparison: Not applicable. Interstitial fluid is the only indicated matrix.

# C Clinical Studies:

1. Clinical Sensitivity: Not applicable.

2. Clinical Specificity: Not applicable.

3. Other Clinical Supportive Data (When 1. and 2. Are Not Applicable):

The sponsor conducted a pivotal study to evaluate the safety and effectiveness of the Stelo Glucose Biosensor system for up to 15.5 days. The study was conducted in the United States at six clinic sites. Although the real-time reporting range of the system is $7 0 { - } 2 5 0 \ \mathrm { m g / d L }$ , users can view the full device measurement range of $4 0 { \mathrm { - } } 4 0 0 \ \mathrm { m g / d L }$ retrospectively via

Dexcom Clarity. Therefore, the device performance across the full measuring range was included in the analyses below and considered in the substantial equivalence determination.

# iCGM Reading Accuracy to Comparator

Below are the percent of values $1 5 \% / 1 5 \mathrm { m g / d L }$ , and $4 0 \% / 4 0 \ : \mathrm { m g / d L }$ stratified by glucose ranges of $< 7 0$ , 70-180, and ${ \mathrm { > } } 1 8 0 { \mathrm { m g / d L } }$ for the iCGM and comparator. The $9 5 \%$ CI in the below tables is the $9 5 \%$ confidence interval (two-sided, alpha $= 0 . 0 5$ ) and the $9 5 \%$ LB is the lower bound of $9 5 \%$ confidence limit (one-sided, alpha $= 0 . 0 5 ,$ ).

Percent and Point Accuracy Between iCGM and Comparator by iCGM Glucose Range $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=1>iCGMGlucoseRange1(mg/dL)</td><td rowspan=1 colspan=1>MatchedPairs (N)</td><td rowspan=1 colspan=1>PercentWithin 15mg/dL(95% LB)</td><td rowspan=1 colspan=1>Percentwithin 40mg/dL(95% LB)</td><td rowspan=1 colspan=1>Percentwithin15%(95% LB)</td><td rowspan=1 colspan=1>Percentwithin40%(95% LB)</td><td rowspan=1 colspan=1>Mean Bias(mg/dL)(95% CI)</td></tr><tr><td rowspan=1 colspan=1>&lt;70</td><td rowspan=1 colspan=1>1,807</td><td rowspan=1 colspan=1>92.0 (88.2)</td><td rowspan=1 colspan=1>99.3 (98.1)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>-6.9(-9.3, -4.5)</td></tr><tr><td rowspan=1 colspan=1>70-180</td><td rowspan=1 colspan=1>10,902</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>84.3 (82.0)</td><td rowspan=1 colspan=1>99.6 (99.4)</td><td rowspan=1 colspan=1>-5.2(-7.4, -2.9)</td></tr><tr><td rowspan=1 colspan=1>&gt;180</td><td rowspan=1 colspan=1>7,621</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>88.1 (84.4)</td><td rowspan=1 colspan=1>99.9 (99.8)</td><td rowspan=1 colspan=1>-3.3(-6.0, -0.6)</td></tr></table>

1 iCGM readings are within $4 0 { \cdot } 4 0 0 \ \mathrm { m g / d L }$ , inclusive

Percent and Point Accuracy Between iCGM and Comparator by Comparator Glucose Ranges $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=1>ComparatorGlucoseRange(mg/dL)</td><td rowspan=1 colspan=1>MatchedPairs1 (N)</td><td rowspan=1 colspan=1>PercentWithin 15mg/dL(95% LB)</td><td rowspan=1 colspan=1>Percentwithin 40mg/dL(95% LB)</td><td rowspan=1 colspan=1>Percentwithin15%(95% LB)</td><td rowspan=1 colspan=1>Percentwithin40%(95% LB)</td><td rowspan=1 colspan=1>Mean Bias(mg/dL)(95% CI)</td></tr><tr><td rowspan=1 colspan=1>&lt;70</td><td rowspan=1 colspan=1>2,008</td><td rowspan=1 colspan=1>93.9 (91.6)</td><td rowspan=1 colspan=1>99.9 (99.0)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>-1.3(-3.4, 0.7)</td></tr><tr><td rowspan=1 colspan=1>70-180</td><td rowspan=1 colspan=1>10,463</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>86.0 (83.8)</td><td rowspan=1 colspan=1>99.7 (99.5)</td><td rowspan=1 colspan=1>-3.2(-5.2,-1.1)</td></tr><tr><td rowspan=1 colspan=1>&gt;180</td><td rowspan=1 colspan=1>7,859</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>86.7 (82.8)</td><td rowspan=1 colspan=1>99.9 (99.6)</td><td rowspan=1 colspan=1>-7.5(-10.3, -4.7)</td></tr></table>

1 iCGM readings are within $4 0 { \cdot } 4 0 0 \ \mathrm { m g / d L }$ , inclusive

The Stelo percent and point accuracy between iCGM and the comparator is comparable to that of the predicate G7 CGM System (K213919).

The percent of values within $20 \%$ of comparator method were calculated across the measuring range overall.

Percent of iCGM Values within $2 0 \%$ of Comparator Glucose $\bf ( N { = } 1 3 0 )$ .   

<table><tr><td rowspan=1 colspan=1>iCGM Glucose Range</td><td rowspan=1 colspan=1>Matched Pairs (n)</td><td rowspan=1 colspan=1>Percent within 20%(95% LB)</td></tr><tr><td rowspan=1 colspan=1>40-400 mg/dL</td><td rowspan=1 colspan=1>20,330</td><td rowspan=1 colspan=1>93.1 (91.2)</td></tr></table>

Percent of values within $1 5 \% / 1 5 \mathrm { m g / d L }$ , $2 0 \% / 2 0 \ \mathrm { m g / d L }$ , and $4 0 \% / 4 0 \mathrm { m g / d L }$ stratified by glucose ranges of ${ < } 5 4$ , 54-69, 70-180, 181-250, and ${ > } 2 5 0 \ \mathrm { m g / d L }$ for iCGM and comparator were also provided.

System Accuracy to Comparator Within iCGM Glucose Ranges $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=1>iCGMGlucoseRange1(mg/dL)</td><td rowspan=1 colspan=1>MatchedPairs (N)</td><td rowspan=1 colspan=1>PercentWithin15mg/dL</td><td rowspan=1 colspan=1>PercentWithin20mg/dL</td><td rowspan=1 colspan=1>Percentwithin40mg/dL</td><td rowspan=1 colspan=1>Percentwithin15%</td><td rowspan=1 colspan=1>Percentwithin20%</td><td rowspan=1 colspan=1>Percentwithin40%</td><td rowspan=1 colspan=1>MeanBias(mg/dL)</td><td rowspan=1 colspan=1>MARD(%)</td></tr><tr><td rowspan=1 colspan=1>&lt;54</td><td rowspan=1 colspan=1>288</td><td rowspan=1 colspan=1>70.5</td><td rowspan=1 colspan=1>84.7</td><td rowspan=1 colspan=1>99.7</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>••</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>-10.3</td><td rowspan=1 colspan=1>17.4</td></tr><tr><td rowspan=1 colspan=1>54-69</td><td rowspan=1 colspan=1>1,519</td><td rowspan=1 colspan=1>92.6</td><td rowspan=1 colspan=1>96.4</td><td rowspan=1 colspan=1>99.5</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>-2.2</td><td rowspan=1 colspan=1>9.2</td></tr><tr><td rowspan=1 colspan=1>70-180</td><td rowspan=1 colspan=1>10,902</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>84.8</td><td rowspan=1 colspan=1>93.3</td><td rowspan=1 colspan=1>99.6</td><td rowspan=1 colspan=1>-1.1</td><td rowspan=1 colspan=1>8.5</td></tr><tr><td rowspan=1 colspan=1>181-250</td><td rowspan=1 colspan=1>3,301</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>84.3</td><td rowspan=1 colspan=1>91.5</td><td rowspan=1 colspan=1>100.0</td><td rowspan=1 colspan=1>-11.3</td><td rowspan=1 colspan=1>8.3</td></tr><tr><td rowspan=1 colspan=1>&gt;250</td><td rowspan=1 colspan=1>4,320</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>91.6</td><td rowspan=1 colspan=1>96.8</td><td rowspan=1 colspan=1>100.0</td><td rowspan=1 colspan=1>-9.2</td><td rowspan=1 colspan=1>6.8</td></tr></table>

1 CGM readings are within $4 0 { \mathrm { - } } 4 0 0 ~ \mathrm { m g / d L }$ , inclusive.

System Accuracy to Comparator Within Comparator Glucose Ranges $\bf ( N { = } 1 3 0 )$ )   

<table><tr><td rowspan=1 colspan=1>iCGMGlucoseRange(mg/dL)</td><td rowspan=1 colspan=1>MatchedPairs1(N)</td><td rowspan=1 colspan=1>PercentWithin15mg/dL</td><td rowspan=1 colspan=1>PercentWithin20mg/dL</td><td rowspan=1 colspan=1>Percentwithin40mg/dL</td><td rowspan=1 colspan=1>Percentwithin15%</td><td rowspan=1 colspan=1>Percentwithin20%</td><td rowspan=1 colspan=1>Percentwithin40%</td><td rowspan=1 colspan=1>MeanBias(mg/dL)</td><td rowspan=1 colspan=1>MARD(%)</td></tr><tr><td rowspan=1 colspan=1>&lt;54</td><td rowspan=1 colspan=1>206</td><td rowspan=1 colspan=1>88.8</td><td rowspan=1 colspan=1>93.2</td><td rowspan=1 colspan=1>98.5</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>6.0</td><td rowspan=1 colspan=1>15.4</td></tr><tr><td rowspan=1 colspan=1>54-69</td><td rowspan=1 colspan=1>1,802</td><td rowspan=1 colspan=1>94.1</td><td rowspan=1 colspan=1>97.8</td><td rowspan=1 colspan=1>100.0</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>1.8</td><td rowspan=1 colspan=1>10.0</td></tr><tr><td rowspan=1 colspan=1>70-180</td><td rowspan=1 colspan=1>10,463</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>86.2</td><td rowspan=1 colspan=1>93.8</td><td rowspan=1 colspan=1>99.7</td><td rowspan=1 colspan=1>-0.3</td><td rowspan=1 colspan=1>8.2</td></tr><tr><td rowspan=1 colspan=1>181-250</td><td rowspan=1 colspan=1>2,988</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>88.0</td><td rowspan=1 colspan=1>94.9</td><td rowspan=1 colspan=1>99.9</td><td rowspan=1 colspan=1>-6.5</td><td rowspan=1 colspan=1>7.4</td></tr><tr><td rowspan=1 colspan=1>&gt;250</td><td rowspan=1 colspan=1>4,871</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>86.1</td><td rowspan=1 colspan=1>92.5</td><td rowspan=1 colspan=1>99.9</td><td rowspan=1 colspan=1>-15.8</td><td rowspan=1 colspan=1>8.0</td></tr></table>

1 CGM readings are within $4 0 { \mathrm { - } } 4 0 0 ~ \mathrm { m g / d L }$ , inclusive.

# Concurrence

Concurrence of iCGM values compared to the comparator method across the entire measuring range was also evaluated. iCGM glucose ranges of ${ < } 4 0$ , 40-60, 61-80, 81-120, 121-160, 161-200, 201-250, 251-300, 301-350, 351-400, and ${ \scriptstyle > 4 0 0 } \mathrm { m g / d L }$ were evaluated against the comparator glucose ranges and the percentages of iCGM values within those ranges were reported in the following tables.

Concurrence of iCGM and Comparator by iCGM Glucose Range $\bf ( N { = } 1 3 0 )$ .   

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=11>Comparator Glucose Values (mg/dL)</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>iCGM(mgdL</td><td rowspan=1 colspan=1>&lt;40</td><td rowspan=1 colspan=1>40-60</td><td rowspan=1 colspan=1>61-80</td><td rowspan=1 colspan=1>81-120</td><td rowspan=1 colspan=1>121-160</td><td rowspan=1 colspan=1>161-200</td><td rowspan=1 colspan=1>201-250</td><td rowspan=1 colspan=1>251-300</td><td rowspan=1 colspan=1>301-350</td><td rowspan=1 colspan=1>351-400</td><td rowspan=1 colspan=1>&gt;400</td><td rowspan=1 colspan=1>Total</td></tr><tr><td rowspan=1 colspan=1>&lt;40</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>2363.9%</td><td rowspan=1 colspan=1>1233.3%</td><td rowspan=1 colspan=1>12.8%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>36</td></tr><tr><td rowspan=1 colspan=1>40-60</td><td rowspan=1 colspan=1>10.1%</td><td rowspan=1 colspan=1>40755.4%</td><td rowspan=1 colspan=1>30841.9%</td><td rowspan=1 colspan=1>192.6%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>735</td></tr><tr><td rowspan=1 colspan=1>61-80</td><td rowspan=1 colspan=1>→</td><td rowspan=1 colspan=1>27610.4%</td><td rowspan=1 colspan=1>1,99575.1%</td><td rowspan=1 colspan=1>38114.3%</td><td rowspan=1 colspan=1>40.2%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2,656</td></tr><tr><td rowspan=1 colspan=1>81-120</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>130.3%</td><td rowspan=1 colspan=1>54012.0%</td><td rowspan=1 colspan=1>3,42676.1%</td><td rowspan=1 colspan=1>50311.2%</td><td rowspan=1 colspan=1>130.3%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>30.1%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>4,500</td></tr><tr><td rowspan=1 colspan=1>121-160</td><td rowspan=1 colspan=1>→</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>46813.2%</td><td rowspan=1 colspan=1>2,58472.9%</td><td rowspan=1 colspan=1>46813.2%</td><td rowspan=1 colspan=1>230.6%</td><td rowspan=1 colspan=1>20.1%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>3,547</td></tr><tr><td rowspan=1 colspan=1>161-200</td><td rowspan=1 colspan=1>−</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>30.1%</td><td rowspan=1 colspan=1>35315.2%</td><td rowspan=1 colspan=1>1,48764.1%</td><td rowspan=1 colspan=1>44419.1%</td><td rowspan=1 colspan=1>321.4%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2,320</td></tr><tr><td rowspan=1 colspan=1>201-250</td><td rowspan=1 colspan=1>→</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>2049.1%</td><td rowspan=1 colspan=1>1,35059.9%</td><td rowspan=1 colspan=1>57125.4%</td><td rowspan=1 colspan=1>1195.3%</td><td rowspan=1 colspan=1>70.3%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2,252</td></tr><tr><td rowspan=1 colspan=1>251-300</td><td rowspan=1 colspan=1>→</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1857.9%</td><td rowspan=1 colspan=1>1,29955.6%</td><td rowspan=1 colspan=1>77233.0%</td><td rowspan=1 colspan=1>803.4%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2,336</td></tr><tr><td rowspan=1 colspan=1>301-350</td><td rowspan=1 colspan=1>−</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>20512.9%</td><td rowspan=1 colspan=1>1,11470.2%</td><td rowspan=1 colspan=1>26116.4%</td><td rowspan=1 colspan=1>80.5%</td><td rowspan=1 colspan=1>1,588</td></tr><tr><td rowspan=1 colspan=1>351-400</td><td rowspan=1 colspan=1>−</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>12932.6%</td><td rowspan=1 colspan=1>24962.9%</td><td rowspan=1 colspan=1>184.5%</td><td rowspan=1 colspan=1>396</td></tr><tr><td rowspan=1 colspan=1>&gt;400</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>11.6%</td><td rowspan=1 colspan=1>3659.0%</td><td rowspan=1 colspan=1>2439.3%</td><td rowspan=1 colspan=1>61</td></tr></table>

Concurrence of iCGM and Comparator by Comparator Glucose Range $\bf ( N { = } 1 3 0 )$ .   

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=4></td><td rowspan=1 colspan=7>Comparator Glucose Values (mg/dL)</td></tr><tr><td rowspan=1 colspan=1>iCGM(mg/dL</td><td rowspan=1 colspan=1>&lt;40</td><td rowspan=1 colspan=1>40-60</td><td rowspan=1 colspan=1>61-80</td><td rowspan=1 colspan=1>81-120</td><td rowspan=1 colspan=1>121-160</td><td rowspan=1 colspan=1>161-200</td><td rowspan=1 colspan=1>201-250</td><td rowspan=1 colspan=1>251-300</td><td rowspan=1 colspan=1>301-350</td><td rowspan=1 colspan=1>351-400</td><td rowspan=1 colspan=1>&gt;400</td></tr><tr><td rowspan=1 colspan=1>&lt;40</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>233.2%</td><td rowspan=1 colspan=1>120.4%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>40-60</td><td rowspan=1 colspan=1>150.0%</td><td rowspan=1 colspan=1>40756.6%</td><td rowspan=1 colspan=1>30810.8%</td><td rowspan=1 colspan=1>190.4%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>61-80</td><td rowspan=1 colspan=1>---</td><td rowspan=1 colspan=1>27638.4%</td><td rowspan=1 colspan=1>1,99569.9%</td><td rowspan=1 colspan=1>3818.9%</td><td rowspan=1 colspan=1>40.1%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>81-120</td><td rowspan=1 colspan=1>150.0%</td><td rowspan=1 colspan=1>131.8%</td><td rowspan=1 colspan=1>54018.9%</td><td rowspan=1 colspan=1>3,42679.7%</td><td rowspan=1 colspan=1>50314.6%</td><td rowspan=1 colspan=1>130.6%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>30.1%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>121-160</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>46810.9%</td><td rowspan=1 colspan=1>2,58475.0%</td><td rowspan=1 colspan=1>46821.5%</td><td rowspan=1 colspan=1>231.1%</td><td rowspan=1 colspan=1>20.1%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>161-200</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>30.1%</td><td rowspan=1 colspan=1>35310.2%</td><td rowspan=1 colspan=1>1,48768.5%</td><td rowspan=1 colspan=1>44422.2%</td><td rowspan=1 colspan=1>321.5%</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>201-250</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>2049.4%</td><td rowspan=1 colspan=1>1,35067.4%</td><td rowspan=1 colspan=1>57127.0%</td><td rowspan=1 colspan=1>1195.6%</td><td rowspan=1 colspan=1>71.1%</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>251-300</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1859.2%</td><td rowspan=1 colspan=1>1,29961.5%</td><td rowspan=1 colspan=1>77236.1%</td><td rowspan=1 colspan=1>8012.6%</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>301-350</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2059.7%</td><td rowspan=1 colspan=1>1,11452.1%</td><td rowspan=1 colspan=1>26141.2%</td><td rowspan=1 colspan=1>816.0%</td></tr><tr><td rowspan=1 colspan=1>351-400</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1296.0%</td><td rowspan=1 colspan=1>24939.3%</td><td rowspan=1 colspan=1>1836.0%</td></tr><tr><td rowspan=1 colspan=1>&gt;400</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>365.7%</td><td rowspan=1 colspan=1>2448.0%</td></tr><tr><td rowspan=1 colspan=1>Total</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>719</td><td rowspan=1 colspan=1>2,856</td><td rowspan=1 colspan=1>4,298</td><td rowspan=1 colspan=1>3,445</td><td rowspan=1 colspan=1>2,172</td><td rowspan=1 colspan=1>2,003</td><td rowspan=1 colspan=1>2,112</td><td rowspan=1 colspan=1>2,137</td><td rowspan=1 colspan=1>633</td><td rowspan=1 colspan=1>50</td></tr></table>

# Trend Accuracy

Trend accuracy describes the accuracy of the sensor during times of rapidly changing glucose and is characterized by slopes, such as from $> 2 \mathrm { m g / d L / m i n }$ to $< - 2 ~ \mathrm { m g / d L / m i n }$ . Trend accuracy was assessed by the concurrence rate of the glucose rate of change (changes in $\mathrm { m g / d L }$ of glucose per minute) determined by the iCGM values and the corresponding comparator values for each iCGM-comparator measurement pair.

Trend Accuracy Between iCGM and Comparator $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=6>Comparator Rate Range (mg/dL/min)</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>iCGM RateRange(mg/dL/min)N (Row %)</td><td rowspan=1 colspan=1>&lt;-2</td><td rowspan=1 colspan=1>[-2,-1)</td><td rowspan=1 colspan=1>[-1,-0)</td><td rowspan=1 colspan=1>[0,1]</td><td rowspan=1 colspan=1>(1,2]</td><td rowspan=1 colspan=1>&gt;2</td><td rowspan=1 colspan=1>Number ofPairediCGM-Comparator(Row N)</td></tr><tr><td rowspan=1 colspan=1>&lt;-2</td><td rowspan=1 colspan=1>80(31.5%)</td><td rowspan=1 colspan=1>99(39.0%)</td><td rowspan=1 colspan=1>57(22.4%)</td><td rowspan=1 colspan=1>14(5.5%)</td><td rowspan=1 colspan=1>2 (0.8%)</td><td rowspan=1 colspan=1>2(0.8%)</td><td rowspan=1 colspan=1>254</td></tr><tr><td rowspan=1 colspan=1>[-2,-1)</td><td rowspan=1 colspan=1>96(7.0%)</td><td rowspan=1 colspan=1>618(45.0%)</td><td rowspan=1 colspan=1>574(41.8%)</td><td rowspan=1 colspan=1>77(5.6%)</td><td rowspan=1 colspan=1>7 (0.5%)</td><td rowspan=1 colspan=1>1(0.1%)</td><td rowspan=1 colspan=1>1,373</td></tr><tr><td rowspan=1 colspan=1>[-1,0)</td><td rowspan=1 colspan=1>40(0.4%)</td><td rowspan=1 colspan=1>590(6.6%)</td><td rowspan=1 colspan=1>6,563(73.2%)</td><td rowspan=1 colspan=1>1,666(18.6%)</td><td rowspan=1 colspan=1>100(1.1%)</td><td rowspan=1 colspan=1>11(0.1%)</td><td rowspan=1 colspan=1>8,970</td></tr><tr><td rowspan=1 colspan=1>[0,1]</td><td rowspan=1 colspan=1>12(0.2%)</td><td rowspan=1 colspan=1>73(1.1%)</td><td rowspan=1 colspan=1>1,661(24.2%)</td><td rowspan=1 colspan=1>4,392(64.0%)</td><td rowspan=1 colspan=1>652(9.5%)</td><td rowspan=1 colspan=1>69(1.0%)</td><td rowspan=1 colspan=1>6,859</td></tr><tr><td rowspan=1 colspan=1>(1,2]</td><td rowspan=1 colspan=1>1(0.1%)</td><td rowspan=1 colspan=1>8(0.5%)</td><td rowspan=1 colspan=1>84(4.9%)</td><td rowspan=1 colspan=1>542(31.8%)</td><td rowspan=1 colspan=1>822(48.3%)</td><td rowspan=1 colspan=1>246(14.4%)</td><td rowspan=1 colspan=1>1,703</td></tr><tr><td rowspan=1 colspan=1>&gt;2</td><td rowspan=1 colspan=1>0(0.0%)</td><td rowspan=1 colspan=1>3(0.4%)</td><td rowspan=1 colspan=1>18(2.7%)</td><td rowspan=1 colspan=1>78(11.6%)</td><td rowspan=1 colspan=1>209(31.1%)</td><td rowspan=1 colspan=1>365(54.2%)</td><td rowspan=1 colspan=1>673</td></tr><tr><td rowspan=1 colspan=1>Number ofPairediCGM-Comparator(Column N)</td><td rowspan=1 colspan=1>229</td><td rowspan=1 colspan=1>1,391</td><td rowspan=1 colspan=1>8,957</td><td rowspan=1 colspan=1>6,769</td><td rowspan=1 colspan=1>1,792</td><td rowspan=1 colspan=1>694</td><td rowspan=1 colspan=1>19,832</td></tr></table>

Note: RoC was calculated using comparator data with consecutive measurements greater than 5 minutes.

# Agreement when iCGM Reads “Below $\mathbf { 7 0 ~ m g / d L ^ { 9 9 } }$ or “Above $2 5 0 ~ \mathrm { m g / d L }$ ”

The Stelo Glucose Biosensor System reports glucose readings between 70 and $2 5 0 \mathrm { m g / d L }$ . When the system determines the sensor reading is below $7 0 \mathrm { m g / d L }$ , it displays “Below 70 $\mathrm { m g / d L ^ { \prime \prime } }$ on the mobile app. When the system determines the sensor reading is above 250 $\mathrm { m g / d L }$ , it displays “Above $2 5 0 \mathrm { m g / d L } ^ { \mathrm { , } }$ on the mobile app. Because the System does not display glucose values below $7 0 \mathrm { m g / d L }$ or above $2 5 0 \mathrm { m g / d L }$ , the comparisons to the actual blood glucose levels (as determined by the comparator method) when the iCGM value is classified as “Below $7 0 \mathrm { m g / d L ^ { \prime \prime } }$ or “Above $2 5 0 \mathrm { m g / d L ^ { 3 } }$ is evaluated separately, and the cumulative percentages of when the comparator values were less than certain glucose values (for “Below $7 0 \mathrm { m g / d L ^ { \prime \prime } } )$ and when comparator values were greater than certain glucose values (for “Above $2 5 0 \mathrm { m g / d L ^ { \prime \prime } } )$ are presented in the table below.

Distribution of Comparator for iCGM Readings “Below $\mathbf { 7 0 ~ m g / d L ^ { 9 9 } }$ or “Above 250 mg/dL” $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=2></td><td rowspan=1 colspan=2></td><td rowspan=1 colspan=3>Comparator (mg/dL)</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>iCGMReadings</td><td rowspan=1 colspan=1>iCGM-ComparatorPairs</td><td rowspan=1 colspan=1>&lt;80</td><td rowspan=1 colspan=1>&lt;90</td><td rowspan=1 colspan=1>&lt;100</td><td rowspan=1 colspan=1>&lt;110</td><td rowspan=1 colspan=1>≥110</td><td rowspan=1 colspan=1>Total</td></tr><tr><td rowspan=2 colspan=1>Below 70mg/dL&quot;</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>1740</td><td rowspan=1 colspan=1>1814</td><td rowspan=1 colspan=1>1833</td><td rowspan=1 colspan=1>1841</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1843</td></tr><tr><td rowspan=1 colspan=1>CumulativePercent</td><td rowspan=1 colspan=1>94</td><td rowspan=1 colspan=1>98</td><td rowspan=1 colspan=1>99</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=2></td><td rowspan=1 colspan=2></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>iCGMReadings</td><td rowspan=1 colspan=1>iCGM-ComparatorPairs</td><td rowspan=1 colspan=1>&gt;200</td><td rowspan=1 colspan=1>&gt;180</td><td rowspan=1 colspan=1>&gt;160</td><td rowspan=1 colspan=1>&gt;130</td><td rowspan=1 colspan=1>≤130</td><td rowspan=1 colspan=1>Total</td></tr><tr><td rowspan=2 colspan=1>&quot;Above250mg/dL&quot;</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>4381</td><td rowspan=1 colspan=1>4381</td><td rowspan=1 colspan=1>4381</td><td rowspan=1 colspan=1>4381</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>4381</td></tr><tr><td rowspan=1 colspan=1>CumulativePercent</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1></td></tr></table>

# Sensor Stability

Sensor stability describes the performance over the sensor’s intended lifetime (up to 15 days, including the optional 12-hour grace period). Performance was estimated by calculating the percentage of iCGM readings within $1 5 \mathrm { m g / d L }$ or $1 5 \%$ $( 1 5 / 1 5 \% )$ , $2 0 \mathrm { m g / d L }$ or $20 \%$ $( 2 0 / 2 0 \% )$ , and $4 0 \mathrm { m g / d L }$ or $40 \%$ $( 4 0 / 4 0 \% )$ of the laboratory comparator values during the beginning (Day 1 to 3), early middle (Day 4 to 7), late middle (Day 9 to 12), and end (Day 13 to the first half of Day 15) of the System lifecycle. The mean of the absolute relative difference was evaluated over the sensor life within the measuring range.

Accuracy of iCGM vs Comparator by Wear Period $\bf ( N { = } 1 3 0 )$   

<table><tr><td rowspan=1 colspan=1>Wear period</td><td rowspan=1 colspan=1>Matchedpairs (n)</td><td rowspan=1 colspan=1>MARD (%)</td><td rowspan=1 colspan=1>%15/15 (%)</td><td rowspan=1 colspan=1>%20/20 (%)</td><td rowspan=1 colspan=1>%40/40 (%)</td></tr><tr><td rowspan=1 colspan=1>Beginning</td><td rowspan=1 colspan=1>5,718</td><td rowspan=1 colspan=1>9.1</td><td rowspan=1 colspan=1>83.6</td><td rowspan=1 colspan=1>92.4</td><td rowspan=1 colspan=1>99.7</td></tr><tr><td rowspan=1 colspan=1>Early middle</td><td rowspan=1 colspan=1>5,509</td><td rowspan=1 colspan=1>7.8</td><td rowspan=1 colspan=1>89.2</td><td rowspan=1 colspan=1>95.2</td><td rowspan=1 colspan=1>99.9</td></tr><tr><td rowspan=1 colspan=1>Late middle</td><td rowspan=1 colspan=1>5,197</td><td rowspan=1 colspan=1>7.3</td><td rowspan=1 colspan=1>90.4</td><td rowspan=1 colspan=1>96.0</td><td rowspan=1 colspan=1>99.9</td></tr><tr><td rowspan=1 colspan=1>End</td><td rowspan=1 colspan=1>3,906</td><td rowspan=1 colspan=1>9.1</td><td rowspan=1 colspan=1>85.1</td><td rowspan=1 colspan=1>92.1</td><td rowspan=1 colspan=1>99.7</td></tr></table>

# Sensor Life

A total of 131 sensors worn on the arm by adult subjects were evaluated to determine the percentage of sensors that lasted through the 15-day sensor life. Of the 131 Sensors, $7 3 . 5 \%$ of evaluable sensors lasted until the final day of use. Some sensors were excluded from this analysis if they were intentionally removed prior to day 15. For example, on or before day 15, 60 sensors were intentionally removed by the sponsor as part of the clinical study. 26 Sensors $( 1 9 . 8 \% )$ had “early sensor shut-off” (ESS), which is when a sensor automatically ends a sensor session as a result of self-diagnostics. Survival rates were calculated using the Kaplan Meier method.

Summary of System Survival by Day with 15-day Wear Period (N Subject=13 0)   

<table><tr><td rowspan=1 colspan=1>Day of wear</td><td rowspan=1 colspan=1>Number of sensors (N=131)</td><td rowspan=1 colspan=1>Survival rate (%)</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>99.2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>99.2</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>128</td><td rowspan=1 colspan=1>97.7</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>124</td><td rowspan=1 colspan=1>94.7</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>124</td><td rowspan=1 colspan=1>94.7</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>123</td><td rowspan=1 colspan=1>93.9</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>121</td><td rowspan=1 colspan=1>93.1</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>92.4</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>119</td><td rowspan=1 colspan=1>91.6</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>115</td><td rowspan=1 colspan=1>89.3</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>112</td><td rowspan=1 colspan=1>87.7</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>83.8</td></tr><tr><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>81.4</td></tr><tr><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>75</td><td rowspan=1 colspan=1>78.9</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>38</td><td rowspan=1 colspan=1>73.5</td></tr></table>

A subsequent study was conducted in 108 participants in the intended user population to assess the impact of a new sensor patch intended to improve the sensor survival rate. Subjects attended clinic sessions for device insertion and removal. Sensor insertions were performed at the clinic by the subjects. All subjects wore an overlay with the device (also called an overpatch). No blood draws or home self-monitored blood glucose testing were required for this study. No display devices were provided to subjects, so all system data were blinded to the subjects for the full wear period and could not be used for subjects’ diabetes management. A total of 80 of 110 systems lasted until Day 15, 6 of which were intentionally removed on or prior to day 15 and were censored from the survival rate analysis. 17 sensors had early sensor shutoff (ESS) and 5 had an adhesive failure. Survival rates were calculated using the Kaplan Meier method.

Summary of System Survival by Day in Subsequent Study (N Subject=108)   

<table><tr><td rowspan=1 colspan=1>Day of wear</td><td rowspan=1 colspan=1>Number of sensors (N=110)</td><td rowspan=1 colspan=1>Survival rate (%)</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>97.3</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>97.3</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>97.3</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>97.3</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>106</td><td rowspan=1 colspan=1>96.4</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>106</td><td rowspan=1 colspan=1>96.4</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>106</td><td rowspan=1 colspan=1>96.4</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>94.5</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>102</td><td rowspan=1 colspan=1>92.7</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>101</td><td rowspan=1 colspan=1>91.8</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>97</td><td rowspan=1 colspan=1>90.0</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>93</td><td rowspan=1 colspan=1>86.3</td></tr><tr><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>91</td><td rowspan=1 colspan=1>84.4</td></tr><tr><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>89</td><td rowspan=1 colspan=1>82.6</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>80</td><td rowspan=1 colspan=1>77.9</td></tr></table>

# Data Capture Rate

The data capture rate characterizes the reliability of the communication between components of the system. The next table describes the data availability rate as the percentage of readings expected to be calculated throughout the 15-day life span of the sensor life based on information collected in the pivotal trial.

Data Availability Rate by Wear Day $\bf ( N { = } 1 3 0 )$ .   

<table><tr><td rowspan=1 colspan=1>Wear day</td><td rowspan=1 colspan=1>Number of sensors</td><td rowspan=1 colspan=1>Data availability rate (%)</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>99.4</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>99.7</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>99.7</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>128</td><td rowspan=1 colspan=1>99.6</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>124</td><td rowspan=1 colspan=1>99.8</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>124</td><td rowspan=1 colspan=1>99.7</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>123</td><td rowspan=1 colspan=1>99.8</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>121</td><td rowspan=1 colspan=1>99.6</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>99.5</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>119</td><td rowspan=1 colspan=1>99.2</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>115</td><td rowspan=1 colspan=1>98.9</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>112</td><td rowspan=1 colspan=1>98.6</td></tr><tr><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>107</td><td rowspan=1 colspan=1>98.9</td></tr><tr><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>104</td><td rowspan=1 colspan=1>97.8</td></tr><tr><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>75</td><td rowspan=1 colspan=1>97.1</td></tr></table>

# D Clinical Cut-Off:

Not applicable.

# E Expected Values/Reference Range:

Not applicable.

# F Other Supportive Instrument Performance Characteristics Data:

The following supportive performance characteristics were established through nonclinical testing of the predicate device and are applicable to the Stelo Glucose Biosensor System in this 510(k):

• Biocompatibility   
• Chemical/Material Characterization (not Biocompatibility-related) Sterilization Validation Electrical and Mechanical Performance Operating Environmental Conditions Testing Wireless Coexistence   
• Electrical Safety and Electromagnetic Compatibility Packaging Validation Interoperability

The following performance characteristics were verified or validated through studies conducted on the subject device, Stelo Glucose Biosensor System:

# Human Factors

Sixty participants across different regional geographies evaluated four self-selection e-commerce platforms in the HF validation test through both the Dexcom website and e-commerce website via mobile and desktops. Fifteen of the 60 participants who correctly self-identified themselves as intended users of the Stelo System (based off of the above e-commerce websites) completed a simulated Human Factors validation testing using the Stelo System mobile app, Sensor/Applicator and associated instructional materials.

# Software Verification and Validation

Software verification and validation testing was conducted to confirm that the software used in the Stelo Glucose Biosensor System performed in accordance with established specifications, IEC 62304 and FDA Guidance document “Guidance for the Content of Premarket Submissions for Device Software Functions,” June 14, 2023. Evaluation activities included code review, unit, system integration, and system level testing which verified functionality of the device against established software requirements. Results of the software executed protocols for the Stelo Glucose Biosensor System are acceptable for their intended use.

# Cybersecurity

Dexcom has provided cybersecurity risk management documentation for the Stelo Glucose Biosensor System that includes analysis of confidentiality, integrity, and availability for data, information and software related to the Stelo Glucose Biosensor System in accordance with the FDA Guidance Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions” (September 27, 2023). For each identified threat and vulnerability risk event scenario, risk assessment of impact to confidentiality, integrity, and availability was performed and documented within the cybersecurity risk management documentation. Appropriate risk mitigation controls have been implemented and tested. In addition, Dexcom has controls and processes in place to ensure continued support for keeping the device secure and to ensure that the device firmware, software and components are malware free. Additional controls are also in place in manufacturing through distribution to ensure that the medical device firmware and software are malware free from point of origin to the hands of the end user.

# Electrical and Mechanical Performance (session dependent testing):

Performance testing was performed to ensure the device specifications for sensor sensitivity, linearity, and fatigue, as well as wearable battery life and current leakage were met.

# Operating Environmental Conditions Testing:

Environmental testing was performed on the Stelo Glucose Biosensor System to ensure the device specifications for operational robustness, operating conditions (evaluation of performance under various operational temperatures and humidity conditions), and chemical robustness (evaluation of performance when subject to soap water) were met.

# Shelf-Life:

Shelf-life testing was performed to evaluate the stability of Stelo Glucose Sensing Subsystem under real time anticipated storage conditions and supported its useful life to be up to 10 months. The test results for the Stelo Glucose Sensing Subsystem met specifications.

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.