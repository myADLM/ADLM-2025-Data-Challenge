# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION

# DECISION SUMMARY

A. 510(k) Number:

K143178

# B. Purpose for Submission:

Premarket notification for the FilmArray 2.0 is intended for use with FDA cleared or approved assays which have been cleared or approved for use on the FilmArray 2.0.

# C. Manufacturer and Instrument Name:

BioFire Diagnostics, LLC

The FilmArray 2.0 is composed of the FilmArray 2.0 instrument and FilmArray software.

# D. Type of Test or Tests Performed:

The tests consist of multi-step chemical processes designed to isolate and detect nucleic acid targets using nested amplification followed by DNA melt curve analysis detection in an array format.

# E. System Descriptions:

1. Device Description:

The multi-instrument FilmArray 2.0 is composed of a computer pre-installed with FilmArray Software, a computer stand and printer, a barcode scanner, an external Ethernet switch that allows up to eight instruments to connect to a single computer, and an optional modular rack system to stack multiple instruments. The modular rack system will hold the instruments at a $1 5 ^ { \circ }$ angle. The functional specifications of the individual FilmArray 2.0 instruments (including the steps in the testing process and the data interpretation) are unchanged with respect to the original FilmArray 2.0 instrument.

# 2. Principles of Operation:

The FilmArray 2.0 is an automated in vitro diagnostic (IVD) device designed to work with panel specific reagent pouches to detect multiple nucleic acid targets in clinical specimens. The FilmArray 2.0 instrument interacts with the reagent pouch to purify nucleic acids and amplify targeted nucleic acid sequences using nested multiplex PCR in a closed system. The resulting PCR products are evaluated using DNA melting analysis. The FilmArray Software automatically determines the results and provides a test report.

In order to support higher throughput testing the FilmArray 2.0 was developed to support up to eight instruments connected to one computer and a holding rack. The FilmArray 2.0 was designed to reduce the system footprint, support increased through-put, and update data management capabilities.

# 3. Modes of Operation:

The instrument Dashboard serves as a home screen from which the operator can navigate to instrument Control for individual instruments. The instrument Dashboard is designed to display instrument details and information (e.g. status and availability) for up to eight instruments. The instrument Dashboard allows the operator to view the status of each instrument in the system, view the status of all testing runs (e.g., run details such as sample ID, operator, time remaining and estimated time of completion, and if the test report is available), and navigation to instrument Control. An instrument Information button is available on the dashboard that allows an operator to retrieve error messages and other information associated with an individual instrument.

4. Specimen Identification:

Once the pouch is inserted, the FilmArray Software prompts the operator to scan the pouch barcode (which contains the pouch identification information, including the pouch type and serial number), enter the sample ID, and enter the operator ID and password. When all required information has been entered, the user closes the FilmArray 2.0 instrument lid and clicks “Start Run”

5. Specimen Sampling and Handling:

See assay specific labeling for specimen sampling and handling recommendations.

6. Calibration:

The FilmArray 2.0 does not require reagent specific set-up, calibration, or cleaning procedures in order to perform testing with different reagent panels. The optics system contained in the FilmArray 2.0 instrument is aligned, focused, and calibrated at the manufacturer. Proper operation and calibration of instrument optics is monitored by automated on-board self-tests and pouch control reactions. The barcode reader can be calibrated if there is a functional error. Bar code calibration instructions are provided in the operator’s manual.

7. Quality Control:

See assay specific labeling for quality control information.

8. Software:

FDA has reviewed applicant’s Hazard Analysis and Software Development processes for this line of product types:

Level of Concern: Moderate

Software Description:

The FilmArray 2.0 is controlled by Windows-based software running on a computer configured with a standard version of Microsoft Windows Operating system (Windows 7). The FilmArray Software interfaces with the operator to control the instrument, collect data, report test results, and save and retrieve test data from the database. In addition to the FilmArray Software, each reagent pouch requires a specific FilmArray Software pouch module. The pouch module interacts with the FilmArray Software and provides pouch-specific instructions, including the definition of a pouch, the information required to run a pouch on an instrument, analysis instructions used to interpret the data from a run and to display the results, and instructions for generating the test report. Pouch modules are developed and deployed independently of the core software. Each pouch module contains information necessary to perform a test with the corresponding test panel.

Device Hazard Analysis:

Part of the software and firmware development process includes performing a risk analysis to identify risks, their possible causes, and appropriate controls. Risk Management of the FilmArray Software and Firmware followed the processes stated to comply with ISO 14971:2012, Medical devices – application of risk management to medical devices. In brief, risk management started by identifying the hazards associated with the use of the system. The identified hazards fell into four categories: false positive results, false negative results, assay reporting errors, and delayed test results. Risk scores were calculated as a function of severity and the likelihood of occurrence. After mitigation, all hazards associated with the FilmArray Software have the lowest Risk score as defined by the Firm.

Software Requirements Specification:

Requirements for the FilmArray Software were derived from the system-level design inputs document that describes the instrument and software. The design inputs were converted into high-level software requirements that describe the overall function of the software.

After the high-level requirements were determined, detailed specifications, called subsystem requirements, were developed that describe the function of the software. Appropriate teams reviewed and approved the specification documents, and they were used to drive both the software development and testing processes.

Requirements for the FilmArray Firmware were also derived from the system-level design inputs document. The design inputs were converted into high-level instrument requirements that describe the overall function of the instrument. The instrument requirements then drove the detailed firmware specifications. The firmware was

developed to meet these specifications.

Architecture Design Chart:

A high-level architecture design chart for the FilmArray Software was provided. Additional information about the architecture of the FilmArray Software, including state diagrams and flow charts were provided.

Software Design Specification:

During software and firmware development, detailed development documents were written, formally reviewed, and approved by the project manager and technical leads. These development documents were the design specifications which drove the software and firmware development, dictated the behavior of the modules, and formed the basis of design verification. A complete list of software and firmware design specifications for the FilmArray Software was provided.

Traceability Analysis:

The software traceability analysis was conducted according to procedures defined in the submitted Standard Operating Procedures documentation. FilmArray Software risk analysis links potential hazards to the software requirements that are designed to mitigate each of the identified hazards. A number of individual trace matrices are compiled into a master trace matrix linking each of the FilmArray software requirements to the verification test cases or the validation test cases.

Firmware traceability is conducted according to procedures defined internal to the Firm with each firmware requirement tracing to an associated verification test case.

Software Development Environment:

The Software Development Life Cycle (SDLC) was a modified waterfall method with frequent specification modifications and review. Design inputs cascaded into high-level requirements, software specifications, design specifications, and test cases. However, the waterfall method was modified to allow for changes to requirements at any time before validation. When changes occurred, the process repeated to ensure documentation of dependent features was updated.

The FilmArray Software was written in an object-oriented style using .NET technology and the $\mathbf { C \# }$ programming language. The software is based on the FilmArray shell application that uses the Composite Application Library from Microsoft to dynamically discover and configure loosely coupled modules at run time. The analysis software for FilmArray was written in MatLab.

Firmware development follows a V-model method with frequent reviews. system-level design inputs lead to high-level instrument requirements, firmware specifications, and verification test cases. Changes to requirements may occur at any time up to firmware verification.

Verification and Validation:

Verification of the FilmArray Software consisted of automated scripts and manual test cases designed to test requirements of the software. To verify software to instrument interactions, the automated test suite requires an instrument simulator. The simulator is a software program written to mimic the FilmArray 2.0 instrument. The simulator accepts instructions from the software and sends messages and data in return.

For requirements not easily tested through automated scripts, manual test cases were written, approved, and executed to verify the software. Both automated and manual test cases were used to ensure complete coverage of the software requirements.

The system level software validation was performed by laboratory personnel who execute formal written test cases that validate each of the high level requirements. This testing uses production pouches and instruments, and provides an independent software validation. In addition to the test cases, laboratory personnel assess whether the software meets personal usability criteria not captured in the specifications. A validation test report is created at the end of the testing phase. Because the firmware is used to perform this system level testing, the software validation also serves to validate the firmware.

Revision Level History:

There is one released version of the FilmArray software.

<table><tr><td>Version</td><td>Build Date</td><td>Release Number</td></tr><tr><td>2.0.1014</td><td>March 25, 2014</td><td>DX-CO-018194</td></tr></table>

Unresolved Anomalies:

All software defects were evaluated during software design reviews and tracked using unique identifiers. Four minor defects were reported which required no mitigation. One defect was reported as “the instrument lost power during a run, which resulted in the loss of that run. The user was able to run the pouch again because the pouch serial number was not in the database.” This hazard associated with this defect was mitigated by the adding specific instructions for pouch handling after loss of power during a run to the product labeling.

# F. Regulatory Information:

1. Regulation section:

21 CFR 862.2570 Instrumentation for clinical multiplex test systems

2. Classification: Class II

3 Product code: NSU

4. Panel: Microbiology

# G. Intended Use:

1. Indication(s) for Use:

The FilmArray 2.0 is an automated in vitro diagnostic (IVD) device designed for use with FilmArray panels. The FilmArray 2.0 is intended for use in combination with assay specific reagent pouches to detect multiple nucleic acid targets contained in clinical specimens. The FilmArray 2.0 instrument interacts with the reagent pouch to both purify nucleic acids and amplify targeted nucleic acid sequences using nested multiplex PCR in a closed system. The resulting PCR products are evaluated using DNA melting analysis. The software automatically determines the results and provides a test report.

The FilmArray 2.0 is composed of one to eight instruments connected to a computer running FilmArray 2.0 software, which controls the function of each instrument and collects, analyzes, and stores data generated by each instrument.

Special Conditions for Use Statement(s):

For prescription use only

# H. Substantial Equivalence Information:

1. Predicate Device Name(s) and 510(k) numbers:

2. Comparison with Predicate Device:   

<table><tr><td colspan="3">Similarities</td></tr><tr><td>Item</td><td>Current Device: FilmArray 2.0</td><td>Predicate Device FilmArray (K103175) Same</td></tr><tr><td>Intended Use</td><td>The FilmArray 2.0 is an automated in vitro diagnostic (IVD) device designed for use with FDA cleared or approved IVD FilmArray panels. The FilmArray 2.0 is intended for use in combination with assay specific reagent pouches to detect multiple nucleic acid targets contained in clinical specimens. The FilmArray 2.0 instrument interacts with the reagent pouch to both purify nucleic acids and amplify targeted nucleic acid sequences using nested multiplex PCR in a closed system. The resulting PCR products are evaluated using DNA melting analysis. The software automatically determines the results and provides a test report. The FilmArray 2.0 is composed of one to eight instruments connected to a computer running FilmArray 2.0 software which controls the function of each instrument and collects, analyzes, and stores data generated by each instrument.</td><td></td></tr><tr><td>Assays</td><td>For use with FDA cleared FilmArray panels</td><td>Same</td></tr><tr><td colspan="1" rowspan="1">Protocol Processing Steps</td><td colspan="1" rowspan="1">Cell disruption, nucleic acidextraction, PCR1thermocycling, PCR2thermocycling, DNA melt and</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="3" rowspan="1">Similarities</td></tr><tr><td colspan="1" rowspan="1">Item</td><td colspan="1" rowspan="1">Current Device:FilmArray 2.0</td><td colspan="1" rowspan="1">Predicate DeviceFilmArray (K103175)</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">signal detection.</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Time to result</td><td colspan="1" rowspan="1">Approximately 1 hour persample</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Technological Principles</td><td colspan="1" rowspan="1">Nested multiplex nucleic acidamplification (includingreverse transcription asappropriate) followed by high-resolution melting analysis toconfirm the identity of theamplified product.</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Required Accessory</td><td colspan="1" rowspan="1">FilmArray Reagent Pouch</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Sample Preparation Method</td><td colspan="1" rowspan="1">Minimal sample processingand hands- on time.</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Test Interpretation and ResultsReporting</td><td colspan="1" rowspan="1">Automated resultsdetermination and reportgeneration. User cannot accessraw data. Report can beprinted.</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">User Complexity</td><td colspan="1" rowspan="1">Moderate</td><td colspan="1" rowspan="1">Same</td></tr></table>

<table><tr><td colspan="3" rowspan="1">Differences</td></tr><tr><td colspan="1" rowspan="1">Item</td><td colspan="1" rowspan="1">Current Device:FilmArray 2.0</td><td colspan="1" rowspan="1">Predicate Device:FilmArray (K103175)</td></tr><tr><td colspan="1" rowspan="1">Instrument Optics</td><td colspan="1" rowspan="1">Charge-coupled device (CCD)camera.Soft-coated filters.</td><td colspan="1" rowspan="1">Complimentary metal-oxide semiconductor(CMOS) cameraHard-coated filters.</td></tr><tr><td colspan="1" rowspan="1">Instrument - SoftwareCommunication</td><td colspan="1" rowspan="1">Communication travels viaFirewire and USB cables/ports.</td><td colspan="1" rowspan="1">Communication travels viaEthernet cable/port.Communication formultiple instrumentsmediated by a multi-portswitch.</td></tr><tr><td colspan="1" rowspan="1">System configuration</td><td colspan="1" rowspan="1">Up to eight FilmArray 2.0instruments to one computer withmouse, barcode scanner andpouch loading station.Single-sample test capacity perinstrument with random-accessmulti-sample test capacity persystem.Printer provided with the system.Interlocking two-instrument racksavailable to stack instruments andreduce system footprint.(Optional)Instrument held at 0° angle whenno rack is used. instrument held at15° angle on rack.</td><td colspan="1" rowspan="1">One FilmArray 2.0instrument to one laptopcomputer with mouse,barcode scanner and pouchloading station.Single-sample testcapacity.Printer optional.Instrument held at 0° angle.</td></tr></table>

# I. Guidance Documents and Standards Referenced:

The FilmArray 2.0 instrument was certified by a third party to meet the following electrical standards:

• EN 61010-1:2001, Safety requirements for electrical equipment for measurement, control, and laboratory use. EN 61010-2-101:2002, Safety requirements for electrical equipment for measurement, control and laboratory use – Particular requirements for in vitro diagnostic (IVD) medical equipment

• EN 61326-1:2006, Electrical Equipment for Measurement, Control and Laboratory Use – EMC Requirements: General Requirements

• EN 61326-2-6:2006, Electrical Equipment for Measurement, Control and Laboratory Use – EMC Requirements: Particular Requirements IVD Medical Equipment

# J. Performance Characteristics:

1. Analytical Performance:

a. Accuracy: Analytical accuracy was assessed during the clearance of the K103175 and will be addressed for each assay to be run on this system.

b. Precision/

Reproducibility:

See K143171

c. Linearity: Not applicable

d. Carryover: See K143171 and K103175

e. Interfering Substances:

The effect of interfering substances was assessed during the clearance of the K103175 and will be addressed for each assay to be run on this system.

2. Other Supportive Instrument Performance Data Not Covered Above:

A method comparison study using archived clinical and contrived samples was performed using the FilmArray 2.0 during the clearance of K143171.

# K. Proposed Labeling:

The labeling is sufficient and it satisfies the requirements of 21 CFR Part 809.10.

# L. Conclusion:

1. The submitted information in this premarket notification is complete and supports a substantial equivalence decision.