# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYINSTRUMENT ONLY

I Background Information:

Dexcom, Inc.

# C Proprietary and Established Names

Dexcom G6 Continuous Glucose Monitoring (CGM) System

D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QBJ</td><td rowspan=1 colspan=1>Class II</td><td rowspan=1 colspan=1>21 CFR 862.1355</td><td rowspan=1 colspan=1>CH - ClinicalChemistry</td></tr></table>

# II Submission/Device Overview:

# A Purpose for Submission:

This submission adds application programming interfaces (APIs) to the Dexcom G6 System to facilitate users sharing glucose data with authorized client software for specific and permitted use cases.

B Measurand: Glucose in Interstitial Fluid

C Type of Test: Quantitative, amperometric assay (Glucose Oxidase)

# III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below.

# B Indication(s) for Use:

The Dexcom G6 Continuous Glucose Monitoring System (Dexcom G6 System) is a real time, continuous glucose monitoring device indicated for the management of diabetes in persons age 2 years and older.

The Dexcom G6 System is intended to replace fingerstick blood glucose testing for diabetes treatment decisions. Interpretation of the Dexcom G6 System results should be based on the glucose trends and several sequential readings over time. The Dexcom G6 System also aids in the detection of episodes of hyperglycemia and hypoglycemia, facilitating both acute and longterm therapy adjustments.

The Dexcom G6 System is also intended to autonomously communicate with digitally connected devices, including automated insulin dosing (AID) systems. The Dexcom G6 System can be used alone or in conjunction with these digitally connected medical devices for the purpose of managing diabetes.

# C Special Conditions for Use Statement(s):

Rx - For Prescription Use Only

Remove the Dexcom G6 sensor, transmitter, and receiver before Magnetic Resonance Imaging (MRI), Computed Tomography (CT) scan, or high-frequency electrical heat (diathermy) treatment. The magnetic fields and heat could damage the components of the Dexcom G6 System, which may cause it to display inaccurate blood glucose readings or may prevent alerts.

When wearing the device, ask for hand-wanding or full-body pat-down and visual inspection instead of going through the Advanced Imaging Technology (AIT) body scanner. Also avoid putting any part of the device through baggage x-ray machine.

• This device is not intended for pregnant women, people on dialysis, or critically ill patient • The device should not be used to make diabetes treatment decisions when:

The user has not used the iCGM before or is unfamiliar with the Dexcom G6 System. (It may take days, weeks or months for a user to gain confidence in using the iCGM to make treatment decisions.)   
• The user’s symptoms do not match the glucose values displayed by the device.   
• The device does not show a glucose value or a trend arrow.   
• During the first two hours of sensor warm-up period, the user should use a blood glucose meter to make treatment decisions.   
• The user’s glucose is rising or falling rapidly.

Although standard dosing of acetaminophen ( $1 0 0 0 \mathrm { m g }$ per every 6 hours) does not appear to cause significant bias, higher supra-therapeutic levels of acetaminophen have shown significant positive bias.

• Sensor glucose readings will be falsely higher if the user is taking hydroxyurea. Do not use the device for diabetes treatment decisions when taking hydroxyurea.

Adult users should only use the abdomen and pediatric users should only use the buttock or abdomen. Sensor performance has not been evaluated in other insertion sites and may differ from expected iCGM performance.   
• If a sensor wire breaks or detaches from the sensor, it could remain under the user’s skin. The user should contact their healthcare practitioner if this occurs. The transmitter should not be shared to avoid transmission of bloodborne illnesses. When using Bluetooth headphones, speakers, etc., the user's alarm/alerts may sound on the primary smart device or on the accessory. Each accessory is different. The user should test their device so that they know where they will hear the alarm/alerts. Before updating the smart device hardware or operating system, verify the compatibility of the updated hardware/software with the device system.   
• The software application may not be used in environments not currently cleared for Dexcom G6 CGM System (e.g. hospital for inpatient care). The Partner Web APIs is not intended to be used by automated insulin delivery systems (AID).

# IV Device/System Characteristics:

# A Device Description:

The Dexcom G6 Continuous Glucose Monitoring (CGM) System uses a subcutaneous glucose sensor that measures glucose concentration in interstitial fluid and consists of three main components: a sensor, a Bluetooth Low Energy (BLE) transmitter and a BLE enabled display device (receiver and/or mobile application). The user can view glucose data on the receiver or on the G6 CGM App (i.e., a mobile medical application) running on a compatible mobile device, or on both simultaneously. An adhesive patch sits on the surface of the skin to position and hold the sensor, electrical contact elements, and an attachment point for a transmitter, which receives sensor signals, processes these, and sends glucose information to a dedicated receiver or mobile app.

# G6 CGM SENSOR

The sensor component is a sterile device that consists of the sensor applicator, plastic base (“transmitter holder”), and sensor probe. The applicator is a single use, disposable unit that contains an introducer needle holding the sensor probe. The applicator deploys the needle and inserts the sensor under the skin. The needle is retracted back into the applicator after insertion. The sensor probe continuously measures glucose concentration in interstitial fluid and can be worn for up to 10 days.

# G6 CGM TRANSMITTER

The G6 CGM Transmitter is a miniature radio transmitter that incorporates data processing functionality. The transmitter contains a Bluetooth radio transceiver for communication with a compatible display device (i.e., receiver and/or smart device). The transmitter attaches to the sensor and can be re-used for multiple sensing sessions up to three months.

# G6 CGM RECEIVER

The G6 CGM Receiver is small hand-held device that wirelessly receives glucose information from the transmitter every five minutes and includes a touchscreen display. The 5 receiver displays the current glucose reading and glucose trends to the user. It alerts the user when glucose levels are outside of a target zone and when other important system conditions occur.

DEXCOM G6 System MOBILE APP

The G6 CGM App for iOS and G6 CGM App for Android provides an alternative display device to the receiver for users with a compatible, BLE-enabled smart device and behaves similarly to the receiver. The G6 CGM App is compatible with certain iOS, Android and Smart Device watches. A link to a list of compatible devices is included in the instructions for use.

The Dexcom G6 System is an interoperable connected device that can communicate glucose readings and other information wirelessly and securely to and from interoperable electronic interfaces; including compatible AID systems. The G6 CGM system is designed to communicate with interoperable devices in several ways, such as described below:

• Wireless communication from the transmitter directly to an interoperable device communicating through the same protocol. • The app communicates to another app on a single mobile platform. • The app communicates through the cloud to another software device

DEXCOM Partner Web APIs

The newly added software component, which consists of cloud-based application programming interfaces (APIs) enables communication of iCGM data to client software intended to receive that data through the cloud. The transmitted data can be used by authorized client software for specific and permitted use cases including non-medical device application, medical device data analysis, CGM secondary display alarm, active patient monitoring, and treatment decisions. The Partner Web APIs is not intended to be used by automated insulin delivery systems (AID). Dexcom display devices (receiver and mobile app) continue to serve as a primary display device for the (iCGM) data, which directly receives the data from the transmitter. The receiver and/or mobile app also continues to alert the user when glucose levels are outside of a target zone.

# B Principle of Operation:

The Dexcom G6 CGM System uses a subcutaneous sensor to detect glucose levels from the fluid just beneath the skin (interstitial fluid). The sensor probe continuously measures the glucose concentration in the interstitial fluid via an enzymatic electrochemical reaction using glucose oxidase. The enzyme, glucose oxidase, catalyzes the oxidation of glucose and produces hydrogen peroxide. The production of hydrogen peroxide generates an electrical current that is proportionate to the interstitial glucose concentration. The transmitter converts the signal using an algorithm to a glucose value read in $\mathrm { m g / d L }$ , the data is transmitted to a compatible display device for display to a user.

# C Instrument Description Information:

1. Instrument Name: Dexcom G6 Continuous Glucose Monitoring System

2. Specimen Identification: Not applicable.

3. Specimen Sampling and Handling: Not applicable.

4. Calibration:

The Dexcom G6 CGM System does not require user calibration; however, users of this device have the option to calibrate the device manually (e.g., in situations where users do not use the calibration code, or in addition to code-based calibration).

5. Quality Control: Not applicable.

V Substantial Equivalence Information:

A Predicate Device Name(s): Dexcom G6 Continuous Glucose Monitoring System   
B Predicate 510(k) Number(s): K200876

C Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp; PredicateDevice(s):</td><td colspan="1" rowspan="1">K201328</td><td colspan="1" rowspan="1">K200876</td></tr><tr><td colspan="1" rowspan="1">Device Trade Name</td><td colspan="1" rowspan="1">Dexcom G6Continuous GlucoseMonitoring System</td><td colspan="1" rowspan="1">Dexcom G6 ContinuousGlucose Monitoring System</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristicSimilarities</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">An integrated continuousglucose monitoring system(iCGM) is intended toautomatically measure glucosein bodily fluids continuously orfrequently for a specified periodof time. iCGM systems aredesigned to reliably andsecurely transmit glucosemeasurement data to digitallyconnected devices, includingautomated insulin dosingsystems, and are intended to beused alone or in conjunctionwith these digitally connectedmedical devices for the purposeof managing a disease orcondition related to glycemiccontrol.</td></tr><tr><td colspan="1" rowspan="1">Indications For Use</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">The Dexcom G6 ContinuousGlucose Monitoring System(Dexcom G6 System) is a real</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">time, continuous glucosemonitoring device indicated forthe management of diabetes inpersons age 2 years and older.The Dexcom G6 System isintended to replace fingerstickblood glucose testing fordiabetes treatment decisions.Interpretation of the DexcomG6 System results should bebased on the glucose trends andseveral sequential readings overtime. The Dexcom G6 Systemalso aids in the detection ofepisodes of hyperglycemia andhypoglycemia, facilitating bothacute and long-term therapyadjustments.The Dexcom G6 System is alsointended to autonomouslycommunicate with digitallyconnected devices, includingautomated insulin dosing (AID)systems. The Dexcom G6System can be used alone or inconjunction with these digitallyconnected medical devices forthe purpose of managingdiabetes.</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristicDifferences</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Partner WebApplicationProgrammingInterfaces (APIs)</td><td colspan="1" rowspan="1">Addition of theApplicationProgrammingInterface (API) toenablecommunication ofiCGM data to clientsoftware intended toreceive that datathrough the cloud.The Partner WebAPIs is not intendedto be used by</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">automated insulindelivery (AID)systems.</td><td colspan="1" rowspan="1"></td></tr></table>

# VI Standards/Guidance Documents Referenced:

ISO 11137 - 1:2006/ Al :2013, Sterilization of health care products - Radiation, Part 1- Requirements for development, validation and routine control of a sterilization process for medical devices

ISO 11137-2:2 013, Sterilization of health care products - Radiation, Part 2 – Establishing the sterilization dose

ISO 11137-3:2006, Sterilization of health care products - Radiation, Part 3 - Guidance on dosimetric aspects

ISO 11737 -1:2006, Sterilization of Medical Devices - Microbiological Methods, Part 1 - Determination of a population of microorganisms on products

ISO 11737-2:2 00 9, Sterilization of Medical Devices - Microbiological Methods, Part 2 Tests of sterility performed in the definition, validation and maintenance of a sterilization process

ISO/TS 13004:2013, Sterilization of health care products - Radiation - Substantiation of selected sterilization dose: Method VDmaxSD

ISO 10993-1:2009/AC:2010, Biological Evaluation of Medical Devices - Part 1: Evaluation and testing within a risk management process

ISO 10993-2:2006, Biological Evaluation of Medical Devices - Part 2: Animal welfare requirements

ISO 10993-3: 2014 Biological Evaluation of Medical Devices - Part 3: Tests for genotoxicity, carcinogenicity and reproductive toxicity

ISO 10993 -5:2009, Biological Evaluation of Medical Devices - Part 5: Tests for in vitro toxicity.

ISO 10993-6 :2016, Biological evaluation of Medical Devices - Part 6: Tests for local effects after implantation

ISO 10993-10:2010, Biological Evaluation of Medical Devices - Part 10: Tests for irritation and delayed-type hyper sensitivity

ISO 10993-11:2009, Biological Evaluation of Medical Devices - Part 11: Tests for systemic toxicity

ISO 10993-12:2012, Biological Evaluation of Medical Devices - Part 12: Sample preparation and reference materials

ISO 13485:2016 Medical devices - Quality management systems - Requirements for regulatory purposes

ISO 14971:2012 Medical devices - Application of risk management to medical devices

IEC 62304, Ed 1.1:2015 Medical Device Software - Software Lifecycle Processes ( $2 0 0 6 +$ AMD I:2015)

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

iCGM performance was previously evaluated in clinical studies described in DEN170088. The subject device uses the same updated glucose algorithm as cleared in K200876. Therefore, the same performance data applies for the proposed device.

1. Precision/Reproducibility: See k200876.

2. Linearity: The reportable range for the System is 40 to $4 0 0 \mathrm { m g / d L }$ .

3. Analytical Specificity/Interference: Interference was previously assessed in DEN170088.

4. Assay Reportable Range: See Linearity section above.

5. Traceability, Stability, Expected Values (Controls, Calibrators, or Methods): The sensor has a storage shelf-life of 12 months. Shelf life was evaluated at $3 2 ^ { 0 } – 8 6 ^ { 0 } \mathrm { F }$ and $10 \mathrm { - } 9 0 \%$ relative humidity. Sensors should be stored at $3 2 ^ { \circ } { - } 8 6 ^ { \circ } \mathrm { F }$ .

The Dexcom G6 CGM System transmitter has sufficient battery life to function for 3 months as intended following its maximum storage time of 8 months. Shelf life was evaluated at $3 2 ^ { \mathbf { 0 } } { \mathrm { . } }$ - $1 1 3 ^ { \circ } \mathrm { F }$ and $10 { - } 9 5 \%$ relative humidity.

# 6. Detection Limit:

If a glucose measurement is less than $4 0 \mathrm { m g / d L }$ , the result is displayed by the system as ‘Lo’.   
If a glucose measurement exceeds $4 0 0 \mathrm { m g / d L }$ , result is displayed as ‘Hi’.

7. Assay Cut-Off: Not applicable.

8. Accuracy (Instrument): Not applicable.

9. Carry-Over: Not applicable.

# B Comparison Studies:

1. Method Comparison with Predicate Device: See k200876.

2. Matrix Comparison: Not applicable. Interstitial fluid is the only indicated matrix.

# C Clinical Studies:

1. Clinical Sensitivity: Not applicable.

2. Clinical Specificity: Not applicable.

3. Other Clinical Supportive Data (When 1. and 2. Are Not Applicable): See k200876.

D Clinical Cut-Off: Not applicable.

# E Expected Values/Reference Range:

Not applicable.

# F Other Supportive Instrument Performance Characteristics Data:

The following supportive instrument performance characteristics were established in the predicate for the Dexcom G6 System (k200876), and are not affected by the modifications in glucose algorithm in the current 510(k):

• Sterility   
• Biocompatibility   
• Mechanical Engineering   
• Electromagnetic Compatibility   
• Wireless   
• Electrical Safety   
• Environmental Testing   
Shelf-Life Stability   
• Packaging Integrity/Shipping Integrity   
• Contact Resistance

The following performance characteristics were verified or validated through studies of the current design:

• Human Factors • Interoperability • Cybersecurity

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.