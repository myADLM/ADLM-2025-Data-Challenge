# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYINSTRUMENT ONLY TEMPLATE

A. 510(k) Number: K123955   
B. Purpose for Submission: Clearance of QuantStudio Dx Real-Time PCR system   
C. Manufacturer and Instrument Name: Life Technologies QuantStudio Dx Real-Time PCR instrument   
D. Type of Test or Tests Performed: Real-Time PCR

# E. System Descriptions:

1. Device Description:

The QuantStudio™ Dx instrument is a bench top Real-Time PCR instrument that uses fluorescent-based polymerase chain reaction (PCR) reagents to provide qualitative or quantitative detection of target nucleic acid sequences (targets) using real-time analysis from a 96-well (or 384-well) plate. Samples are prepared for nucleic acid testing manually by the user using specific reagents indicated by the assay. The QuantStudio™ Dx Instrument system includes the following components:

a. QuantStudio™ Dx Real-Time PCR instrument with touchscreen b. Thermal Block with associated Heated Cover and Plate Adaptor c. Calibration and verification materials for instrument qualification d. Computer workstation with a monitor, keyboard, and mouse e. QuantStudio™ Dx instrument software

There are two distinct types of software associated with the QuantStudio™ Dx instrument:

Embedded software: The QuantStudio™ Dx embedded software is contained within the QuantStudio™ Dx instrument. It includes the embedded graphical user interface (eGUI) software which controls the Touchscreen, the instrument controller software and associated components (firmware), and the Smart Monitor (a monitoring agent). The

QuantStudio™ Dx embedded software manages instrument operations and enables the user to monitor instrument status.

Instrument software: The QuantStudio™ Dx instrument software is installed on a separate computer and communicates with the instrument to control the instrument and collect data. The QuantStudio™ Dx instrument software performs data analysis and outputs analyzed results.

# 2. Principles of Operation:

The QuantStudio™ Dx instrument executes an approved diagnostic test, also known as a run, according to parameters that are pre-determined by the diagnostic test manufacturer. The diagnostic test parameters are established and locked in a Test Definition Document (TDD) that is imported into the QuantStudio™ Dx instrument software.

To initiate a run on the instrument, the user must start the QuantStudio™ Dx instrument software, select an imported TDD file, and enter plate-specific sample information. A user can only start a run from an imported TDD file. TDD files are created and supplied by the reagent kit or test manufacturer.

During the run, the instrument collects raw fluorescence data following each extension step of the PCR. A data collection point, or read, on the instrument consists of three phases:

a. Excitation: The instrument illuminates all wells of the plate, exciting the fluorophores in each reaction.   
b. Emission: The instrument optics collects the residual fluorescence emitted from the wells of the plate. The resulting image collected by the device consists only of light that corresponds to the range of emission wavelengths.   
c. Collection: The instrument assembles a digital representation of the residual fluorescence collected over a fixed time interval. The software stores the raw fluorescent image for analysis.

After a run, the software uses calibration data to determine the location and intensity of the fluorescent signals in each read, the dye associated with each fluorescent signal, and the significance of the signal. This signal information is translated into metrics for each well that are then used for analysis to provide quantitative or qualitative information. The software completes the analysis according to the parameters in the TDD file. Any further interpretation of the analyzed results is determined by instructions provided by the diagnostic test manufacturer.

The Quidel Molecular Direct C. difficile assay that provides the performance data to support this submission is a qualitative assay that provides results of “Negative,” “C. difficile Positive” or “Invalid” based on the detection of a Ct value for Clostridium difficile toxin A gene (tcdA) or toxin B gene (tcdB) with respect to the process control. The probes for tcdA and tcdB are labeled with CAL Fluor Orange 560 and the process control is labeled with Quasar 670, corresponding to filter sets $\tt X 2 - m 2$ and $\mathbf { \Delta x } 5 { \cdot } \mathbf { m } 5$ on the QuantStudio™ Dx RealTime PCR instrument of the 6 available filter sets. The assay run parameters are determined by TDD file 2.01, provided and validated by Quidel Corporation.

Note that, because the QuantStudio™ Dx Real-Time PCR instrument relies on analytical and clinical data from the Quidel Molecular Direct C. difficile assay submission (k123998), that only the filters sets used in that assay $\mathbf { \nabla } \times 2 \mathbf { - } \mathbf { m } 2$ and x5- m5) can be cleared for the In Vitro Diagnostics (IVD) labeling.

# 3. Modes of Operation:

The QuantStudio™ Dx Real-Time PCR instrument has two modes of operation: IVD and Research Use Only (RUO), which cannot be executed simultaneously. The specific protocols that are performed on each instrument for IVD assays depend upon the assay-specific, closed-mode application specifications that are installed on the system.

The QuantStudio™ Dx instrument software is IVD-labeled and controlled; users must log into this software. Only IVD-labeled Test Definition Documents certified by Life Technologies will operate in this software. A separate and distinct Test Development Software package is available that allows the user to perform other work in a (RUO) environment. The Test Development Software allows customers who conduct research to do so using the same instrument. To demonstrate that non-approved functions do not interfere with approved functions, controls and safeguards have been implemented to ensure the distinct separation between the IVD and Test Development workflows. In addition, internal verification testing was performed to demonstrate that co-installation of the Test Development Software with the QuantStudio™ Dx instrument software does not impact the QuantStudio™ Dx instrument software IVD functionality. The FDA is not reviewing, clearing or approving any of the openmode/laboratory-defined functionalities and requires documentation and evidence that these functionalities do not interfere with IVD functionalities.

# 4. Specimen Identification:

An optional barcode scanner can be attached to the computer via a USB port. The barcode scanner can be used to scan the barcodes on plates and reagents used for the approved diagnostic test. In the absence of a barcode scanner, the user can input the plate and reagent information manually using the instrument software. The barcode scanner was installed on the QuantStudio™ Dx Instrument during internal verification testing and during Quide $^ \mathrm { \textregistered }$ Corporation’s non-clinical and clinical performance evaluation studies.

# 5. Specimen Sampling and Handling:

Specific preparation protocols depend on the application specifications of the assay being used on the QuantStudio™ Dx system. There is no automated sample processing instrument offered in conjunction with the QuantStudio™ Dx instrument.

For the Molecular Direct $C .$ . difficile assay, swab specimens of stool are dispersed in $5 0 0 ~ \mu \updownarrow$ of buffer, $3 0 \mu \mathrm { l }$ of which is transferred to $5 7 0 \mu \mathrm { l }$ buffer. $1 5 \mu 1$ of rehydrated Master Mix is added to a 96-well plate followed by $5 \mu \mathrm { l }$ of the diluted specimen, which is then sealed and centrifuged for 15 seconds. The plate is then inserted into the thermocycler.

6. Calibration:

# QuantStudio™ Dx System Optical Calibration

The instrument is calibrated for background fluorescence, Region of Interest (ROI), uniformity, pure dyes, and normalization, and then verified. At instrument installation, a trained service engineer installs the instrument and performs the initial calibration. The user is trained in conjunction with the initial calibration in order to perform the subsequent required calibrations. All required instrument calibration is performed using the QuantStudio™ Dx instrument software. The background fluorescence calibration is required on a monthly basis while the ROI, uniformity, pure dye, and normalization calibrations are required at six month intervals.

a. ROI calibration: Identifies the positions of the wells on the Thermal Block of the instrument.   
b. Background calibration: The software uses the background calibration data to remove background fluorescence from the test data.   
c. Uniformity calibration: Generates data that allows the software to compensate for the physical effects of the instrument filters. The software uses the uniformity calibration to account for well-to-well differences in fluorescence signal.   
d. Pure Dye calibration: The software uses the pure dye calibration data collected from the dye calibration plates to characterize and distinguish the individual contribution of each dye in the total fluorescence collected by the instrument.

e. Normalization calibration: The normalization calibration data is used to normalize the instrument signal to within a standard range to reduce instrument-to-instrument variability.

f. RNase P Instrument Performance Verification: The RNase P instrument verification test confirms the performance of the QuantStudio™ Dx instrument. The RNase P plate is preloaded with the reagents necessary for the detection and quantification of genomic copies of the human RNase $\mathrm { P }$ gene (a single-copy gene encoding the RNase moiety of the RNase $\mathrm { P }$ enzyme). An RNase P plate can be run at any time. It is recommended that the user runs the RNase P plate when the Halogen Lamp is replaced or when the instrument is moved.

The labeled shelf-life for all calibration and verification materials will be 12 months at $- 2 0 \mathrm { { ^ \circ C } }$ .

After installation of the instrument, the user can perform all required regular maintenance and calibration using IVD-labeled calibration plates. Life Technologies provides a service option to users to have a trained Life Technologies service engineer perform the maintenance and calibration if desired. In addition to the required calibration, the user must also maintain the operational condition of the instrument.

# 7. Quality Control:

Quality control is addressed for each separately cleared specific assay to be run on the instrument. For the Quidel Molecular Direct C. difficile assay, quality is maintained by the process control, used during sample processing and amplification in the assay. Additionally, there are external positive and negative controls available that may be used in accordance with the user lab standards.

# 8. Software:

The latest version of the QuantStudio™ Dx Instrument software is v1.1.6 as of 09/21/2012 and the embedded software is ID C14R18, as of 10/17/2012.

Note that off-the-shelf software is used with this instrument (e.g. MS Windows 7, MS Office 2010), which is co-installed during installation with the instrument software to an off-the-shelf computer. The components important within the guidance document “Off-The-Shelf Software Use in Medical Devices” have been met within the submission.

# a. Level of Concern:

Life technologies has determined this device as a moderate level of concern, based on the potential that software design flaws or failures cause an erroneous diagnosis or minor injury that could result in unnecessary or

delayed treatment. This level of concern meets the requirement and is accepted by FDA.

# b. Software Description:

There are two distinct types of software associated with the QuantStudio™ Dx instrument, embedded and instrument software. The user interfaces with the embedded software through a LCD touchscreen (and an optional barcode scanner), and with the instrument software via an attached computer.

· Embedded software:

The QuantStudio™ Dx embedded software is contained within the thermocycler. It includes the embedded graphical user interface (eGUI) software which controls the Touchscreen, the instrument controller software and associated components (firmware), and the Smart Monitor (a monitoring agent for electromechanical function, not test data). The QuantStudio™ Dx embedded software manages instrument operations and enables the user to monitor instrument status.

Instrument Software:

The QuantStudio™ Dx instrument software is installed on a separate computer and communicates with the instrument to control the instrument and collect data. The QuantStudio™ Dx instrument software performs data analysis and outputs analyzed results. The instrument software is also referred to as the “Data Collection Software.”

The programming language used to develop the QuantStudio™ Dx software was Java v1.6.

# c. Device Hazard Analysis (DHA):

Life Technologies provided a DHA for the QuantStudio™ Dx instrument software including hazards, severity and mitigation. After mitigation, all hazards scored in the Tolerable or Broadly Acceptable Regions (TOL; BAR). The sponsor provided a tabular description of identified hardware and software hazards, including severity assessment and mitigations that meet FDA requirements.

# d. Software Design Specification (SDS):

Life Technologies provided design specification documents, which include a Data Collection Software, eGUI, Firmware, Data Collection Algorithm and the Smart Monitor, which meet FDA software requirements. The sponsor provided adequate SDS descriptions to show how the requirements in the SRS are implemented.

# e. Software Requirements Specifications (SRS):

Life Technologies provided SRS documentation for Data Collection and eGUI software. The hardware platform requirements to operate the QuantStudio™ Dx instrument software are: MS Windows 7 SP1, 32-bit OS; 3.0 GHz

processor; 4GB RAM; 10 GB HDD; $1 2 8 0 \mathrm { ~ x ~ } 1 0 2 4$ pixel monitor; IE v6.0. The submitted description meets FDA requirements. The single-board computer (SBC) embedded software requirements are a 1.8 GHz processor, 4GB RAM and an 8 GB HDD.

The QuantStudio™ Dx instrument software co-installs with Microsoft Office 2010. During initialization, the QuantStudio™ Dx instrument software performs an integrity check to verify that the installed application has not been tampered with and that all software components are available and uncorrupted.

The submitted description meets FDA requirements.

# f. Traceability:

The trace matrix is described from design input to output. Life Technologies provided a diagrammatic overview and comprehensive information showing traceability between user needs, DHA, SRS, SDS and V&V.

g. Verification and Validation (V&V):

Sufficient documentation for V&V testing including pass/fail criteria and results meet FDA requirements.

# h. Revision Level History (RLH):

Life Technologies provided an adequate RLH that details changes made for both the embedded and instrument software that meets the FDA requirement. The latest version of the QuantStudio™ Dx instrument software is v1.1.6 as of 09/21/2012 and the embedded software is ID C14R18, as of 10/17/2012.

# i. Architecture Design Chart:

Adequate flow charts were provided showing detailed depiction of functional units and software modules. The eGUI and firmware is housed on a SBC. The eGUI, Main Instrument Controller and Instrument software communicate via TCP/IP. All firmware components communicate via Controller Area Network. Instrument software communicates with the Laboratory Information System via the Application Programming Interface. Smart Monitor transmission is secured by SSL encryption and LDAP authentication to ensure that only Life Technologies service personnel can access the transmitted data.

# j. Unresolved Anomalies (UA):

Life Technologies provided a list of Unresolved Anomalies for review. There were seven unresolved anomalies, six of which had severity ratings of minor and one rated as moderate. The moderate severity anomaly (Anomaly ID 1015) is a complication with the eGUI, where it does not allow the calibration expiry interval to be less than the default. The user can access (not modify) this feature in the instrument software. No data are lost and the product or user safety is not impacted. The workaround is to make any desired edits in the instrument software, rather than in the eGUI.

k. User Guide:

A user guide was provided for the QuantStudio™ Dx instrument. Quick reference instructions were provided that demonstrates how to interface with the instrument and prepare the assay for analysis. The user guide was reviewed to ensure that the containing language was appropriate for an IVD label (e.g. removing any RUO language). No instances of non-IVD language were found within the IVD-labeled User Guide or the IVD-labeled Quick Reference.

# F. Regulatory Information:

1. Regulation section: 862.2570 Instrumentation for clinical multiplex test systems

2. Classification: Class II

3 Product code: OOI (Real-Time Nucleic Acid Amplification System) for Real-Time instrument.

4. Panel: Clinical Chemistry (75)

# G. Intended Use:

1. Indication(s) for Use: The QuantStudio™ Dx Real-Time PCR Instrument with QuantStudio™ Dx Software is intended to perform fluorescence-based PCR to provide detection of FDA cleared and approved nucleic acid sequences in human-derived specimens. The QuantStudio™ Dx Real-Time PCR Instrument with QuantStudio™ Dx Software is intended for in vitro diagnostic use by trained laboratory technologists in combination with nucleic acid reagent kits/tests manufactured and labeled for diagnostic purposes on this instrument.

2. Special Conditions for Use Statement(s): Prescription use only

# H. Substantial Equivalence Information:

1. Predicate Device Name(s) and 510(k) number(s): Abbott $m 2 0 0 0 ^ { \mathbf { T M } }$ System (K092705).

# 2. Comparison with Predicate Device:

<table><tr><td colspan="3" rowspan="1">Similarities</td></tr><tr><td colspan="1" rowspan="1">Item</td><td colspan="1" rowspan="1">Subject DeviceQuantStudioTM DxReal-Time PCRInstrument</td><td colspan="1" rowspan="1">Predicate DeviceAbbott m2000TMSystem (K092705)</td></tr><tr><td colspan="1" rowspan="1">Product Code</td><td colspan="1" rowspan="1">OOI: Real-TimeNucleic AcidAmplification Systemfor Real TimeInstruments.</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Device Class</td><td colspan="1" rowspan="1">Class II</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Intended Use</td><td colspan="1" rowspan="1">The QuantStudioTM DxReal-Time PCRInstrument withQuantStudioTM DxSoftware is intended toperform fluorescence-based PCR to providedetection of FDA clearedand approved nucleicacid sequences in human-derived specimens. TheQuantStudioTM Dx Real-Time PCR Instrumentwith QuantStudioTM DxSoftware is intended forin vitro diagnostic use bytrained laboratorytechnologists incombination with nucleicacid reagentkits/tests manufacturedand labeled fordiagnostic purposes onthis instrument.</td><td colspan="1" rowspan="1">The Abbott m2000 systemis intended for in vitrodiagnostic use inperforming FDA clearedand approved nucleic acidtesting in clinicallaboratories. It comprisesthe Abbott m2000sp andthe Abbott m2000rtinstruments. The Abbottm2000sp is an automatedsystem for performingsample preparation fornucleic acid testing. TheAbbott m2000rt is anautomated system forperforming fluorescence-based PCR to providequantitative andqualitative detection ofnucleic acid sequences.</td></tr><tr><td colspan="1" rowspan="1">Technology/Detection</td><td colspan="1" rowspan="1">Real-Time PCR</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Specimen Types</td><td colspan="1" rowspan="1">Nucleic acid</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Assay Format</td><td colspan="1" rowspan="1">Homogeneous, closedtube PCR</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Degree of Automation</td><td colspan="1" rowspan="1">Requires manual transferof amplification mixtureto amplification/detectioninstrumentAutomated control ofamplification, detection,</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">and data analysis</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Primary OperationalAmplification andDetection Components</td><td colspan="1" rowspan="1">Integrated thermocyclerand microvolumefluorimeter for walkaway PCR amplificationand detection</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Heating Method forAmplification</td><td colspan="1" rowspan="1">Peltier device withsample block</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Detection Procedure</td><td colspan="1" rowspan="1">Optical detection ofstimulated fluorescence</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Detection Chemistries</td><td colspan="1" rowspan="1">Fluorescence labeled,target-specific probes</td><td colspan="1" rowspan="1">Same</td></tr></table>

<table><tr><td rowspan=1 colspan=3>Differences</td></tr><tr><td rowspan=1 colspan=1>Item</td><td rowspan=1 colspan=1>Subject DeviceQuantStudioTM DxReal-Time PCRInstrument</td><td rowspan=1 colspan=1>Predicate DeviceAbbott m2000TMSystem (K092705)</td></tr><tr><td rowspan=1 colspan=1>User Interface</td><td rowspan=1 colspan=1>PC with instrument-specific software.Instrument hastouchscreen console.</td><td rowspan=1 colspan=1>PC with instrument-specific software</td></tr><tr><td rowspan=1 colspan=1>Amplification ReactionVolume</td><td rowspan=1 colspan=1>10-30 µL in 96-wellFast PCR plates</td><td rowspan=1 colspan=1>25-100 µL in 96-wellPCR plates</td></tr><tr><td rowspan=1 colspan=1>Sample Preparation</td><td rowspan=1 colspan=1>No automated sampleprocessing instrumentoffered in conjunctionwith the QuantStudioTMDx instrument.</td><td rowspan=1 colspan=1>Pairing with them2000sp instrumentprovides automatedsample processing.</td></tr></table>

# I. Special Control/Guidance Document Referenced (if applicable):

Class II Special Controls Guidance Document: Instrumentation for Clinical Multiplex Test Systems:   
http://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/GuidanceDocum ents/ucm077819.htm

# J. Performance Characteristics:

All assay analytical and clinical testing was reviewed in the clearance of the Molecular Direct C. difficile assay (k123998). This submission is linked to and dependent upon the assay data presented there.

Analytical Performance:   
a. Accuracy: Accuracy was assessed during the clearance of the Molecular Direct $C .$ . difficile assay (k123998) and will be addressed for each assay to be run on this system.   
b. Precision/Reproducibility: Accuracy was assessed during the clearance of the Molecular Direct $C .$ . difficile assay (k123998) and will be addressed for each assay to be run on this system.   
c. Linearity: Not applicable.   
d. Carryover: Carryover was assessed during the clearance of the Molecular Direct $C .$ . difficile assay (k123998) and will be addressed for each assay to be run on this system.   
e. Interfering Substances: Interfering Substances were assessed during the clearance of the Molecular Direct C. difficile assay (k123998) and will be addressed for each assay to be run on this system.

2. Other Supportive Instrument Performance Data Not Covered Above:

# Thermal Cycler Performance Testing

Functional design verification testing demonstrated that the QuantStudio™ Dx instrument design satisfies its design input requirements for thermal accuracy and uniformity.

• Thermal block temperature accuracy is within $\pm 0 . 2 5 ^ { \circ } \mathrm { C }$ from setpoint.   
• Thermal block well temperature nonuniformity within $\pm 0 . 5 ^ { \circ } \mathrm { C }$ range.

# Optical Detection Verification

Performance requirements for optical detection are stated in the QuantStudio™ Dx instrument product requirements. These requirements include:

Dynamic range sufficient to measure fluorescence of $< 0 . 1 6 7 \mathrm { C t }$ from 10- $3 0 ~ \mu \mathrm { L }$ of selected 1-3 dyes per well at a temperature range of 45 to $9 5 ^ { \circ } \mathrm { C }$ . The Instrument System demonstrated the detection of $\leq 1 0$ copies of starting template in $\leq 4 0$ cycles in $1 0 { - } 3 0 ~ \mu \mathrm { L }$ in $< 4 0$ minutes in $1 0 0 ~ \mu \mathrm { L }$ volume 96-well plates using a single-reporter. Linearity of $\mathrm { C t }$ values are such that the square of the correlation coefficient $( \boldsymbol { \mathrm { r } } ^ { 2 } )$ exceeds 0.99 over the dye concentration range. Run-to-run signal variability is $< 2 . 5 \%$ for the same instrument and $< 5 \%$ between instruments, with $< 0 . 2 5 \mathrm { C t S D } < 0 . 1 6 7$ from well to well.

This performance testing was executed by Life technologies, documented in their verification and validation testing records.

# K. Proposed Labeling:

The labeling is sufficient and it satisfies the requirements of 21 CFR Part 809.10.

# L. Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.