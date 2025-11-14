# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY

A. 510(k) Number: K182886   
B. Purpose for Submission: Instrument modification   
C. Manufacturer and Instrument Name: Beckman Coulter, Inc. Cytomics FC500 MCL and MPL Flow Cytometers   
D. Type of Test or Tests Performed: Flow cytometric immunoassays: cell identification with quantitative cell counts

# E. System Descriptions:

1. Device Description:

The Cytomics $\operatorname { F C } 5 0 0 \operatorname { M C L }$ and MPL Flow Cytometers are instruments for the qualitative and quantitative measurement of biological and physical properties of cells and other particles. These properties are measured when the cells pass through one or two laser beams in single-file. The MCL configuration denotes a carousel-loader unit for sample tubes; the MPL configuration denotes a plate-loader unit, in addition to sample tubes.

These instruments include a $4 8 8 \mathrm { n m }$ excitation laser, and an optional $6 3 3 \mathrm { n m }$ solid-state or 635nm HeNe laser. IVD assays cleared for use on the FC500 cytometers employ the $4 8 8 \mathrm { n m }$ laser for excitation, no assays that employ the 633/635 lasers have been cleared by the FDA and clearance of those lasers is not the subject of this 510(k). All configurations of the FC500 cytometer possess a total of seven detector channels ‒ two avalanche photodiodes (APD), for forward- and side-scatter; and five photomultiplier tubes (PMT, FL1‒FL5) for detection of specific fluorescence. Seven amp boards (one for each detector circuit) amplify and synchronize analog electronic signals from photodetectors, prior to conversion to digital signals.

The software architecture for the FC500 instrument-controlling workstation includes CXP for acquisition and analysis of closed-system IVD assays, MXP for more advanced acquisition and analysis including LDT assays, and BCAP for necessary user and account permissions controls for review of quarantined files.

This 510(k) submission concerns software update patches (CXP v2.3, MXP v2.3), enabling detection of delay line failures in the amp board for each detector channel, as described in RCL181101. As a corrective Change Being Effected (CBE) response, this software update contains three algorithmic processes as part of a Software Detection Tool (SDT) for:

1) electronic detection of pre-acquisition signal failures in amp board delay lines   
2) mid- or post-acquisition detection of signal failures by automated digital analysis of parameter-by-time signal for each detection channel   
3) predictive quarantine of datafiles suspected of being compromised, due to signal failure, for operator review prior to release or dismissal

2. Principles of Operation:

The Cytomics FC500 cytometric instrument contains a fluidics system designed to pass cells or particles through one or more laser beams in succession. Scattered and fluoresced light from these events is collected by APD and PMT detectors, converted to digital signal, and collected by the instrument workstation.

3. Modes of Operation:

Does the applicant’s device contain the ability to transmit data to a computer, webserver, or mobile device?

Yes ___ _X____ or No

Does the applicant’s device transmit data to a computer, webserver, or mobile device using wireless transmission?

Yes or No __ _X

4. Specimen Identification: Barcode reader or manual entry

5. Specimen Sampling and Handling: MCL: 32 ( $1 2 \times 7 2 \mathrm { m m }$ ) tubes MPL: 24- or 96-well plates, or $1 2 \times 7 2 \mathrm { m m }$ tubes

6. Calibration: Assay-dependent

7. Quality Control: Assay-dependent

8. Software:

FDA has reviewed applicant’s Hazard Analysis and Software Development processes for this line of product types:

Yes___X_ _ or No_

# F. Regulatory Information:

1. Regulation section: 21 CFR §864.5220 – Automated Differential Cell Counter

2. Classification: Class II

3 Product code: GKZ: Automated Differential Cell Counter

4. Panel: Hematology (81)

# G. Intended Use:

1. Indication(s) for Use:

K071681 (MPL)

The Cytomics FC ${ 5 0 0 } \mathrm { M P L }$ is a system for the qualitative and quantitative measurement of biological and physical properties of cells and other particles. These properties are measured when the cells pass through one or two laser beams in singlefile.

# K030828 (MCL)

The tetraCXP SYSTEM for Cytomics FC 500 flow cytometry systems is an automated analysis method for simultaneous identification and enumeration of lymphocyte subpopulations $\mathrm { C D } 3 + ,$ , $\mathrm { C D 4 + }$ , $\mathrm { C D 8 + }$ , $\mathrm { C D } 1 9 +$ and $\mathrm { C D } 5 6 { } +$ ) combining four-color fluorescent monoclonal antibody reagents, quality control reagents, optional absolute count reagent and CXP software. The systems with CYTO-STAT tetraCHROME CD45-FITC/CD4-PD/CD8-ECD/CD3-PC5 Monoclonal antibody reagent is intended "For In Vitro Diagnostic Use", allowing the identification and enumeration of Total $\mathrm { C D } 3 +$ (T cells), Total $\mathrm { C D 4 + }$ , Total $\mathrm { C D 8 + }$ , Dual $\mathrm { C D 3 + / C D 4 + }$ ,

Dual $\mathrm { C D 3 + / C D 8 + }$ lymphocyte percentages and absolute counts as well as the CD4/CD8 ratio in whole blood flow cytometry. The systems with CD45- FITC/CD56-PC/CD19-ECD/CD3-PC5, the total lymphocyte percentage can be obtained. CD45-FITC/CD56-PE/CD19-ECD/CD3-PC5 monoclonal antibody reagent is intended "For In Vitro Diagnostic Use", allowing the identification and enumeration of total $\mathrm { C D } 1 9 +$ (B cells) and $\mathrm { C D 3 - / C D } 5 6 +$ (NK cells) lymphocyte percentages and absolute counts in whole blood flow cytometry. The total lymphocyte percentage can obtained as well.

2. Special Conditions for Use Statement(s): For In Vitro Diagnostic Use

# H. Substantial Equivalence Information:

1. Predicate Device Name(s) and 510(k) numbers:

K030828: TetraCXP System (MCL) K071681: Cytomics FC500 MPL Flow Cytometer

2. Comparison with Predicate Device:

<table><tr><td colspan="4" rowspan="1">Similarities</td></tr><tr><td colspan="1" rowspan="1">Item</td><td colspan="1" rowspan="1">Device</td><td colspan="1" rowspan="1">Predicate(K030828)</td><td colspan="1" rowspan="1">Predicate(K071681)</td></tr><tr><td colspan="1" rowspan="1">Intended Use</td><td colspan="1" rowspan="1">The Cytomics FC 500MPL is a system for thequalitative and quantitativemeasurement of biologicaland physical properties ofcells and other particles.These properties aremeasured when the cellspass through one or twolaser beams in single-file.The tetraCXP SYSTEMfor Cytomics FC 500 flowcytometry systems is anautomated analysis methodfor simultaneousidentification andenumeration oflymphocyte subpopulations(CD3+, CD4+, CD8+,CD19+ and CD56+)combining four-colorfluorescent monoclonalantibody reagents, quality</td><td colspan="1" rowspan="1">The tetraCXP SYSTEMfor Cytomics FC 500 flowcytometry systems is anautomated analysis methodfor simultaneousidentification andenumeration of lymphocytesubpopulations (CD3+,CD4+, CD8+, CD19+ andCD56+) combining four-color fluorescentmonoclonal antibodyreagents, quality controlreagents, optional absolutecount reagent and CXPsoftware. The systemswith CYTO-STATtetraCHROME CD45-FITC/CD4-PD/CD8-ECD/CD3-PC5Monoclonal antibodyreagent is intended "For InVitro Diagnostic Use",</td><td colspan="1" rowspan="1">The Cytomics FC 500MPL is a system for thequalitative and quantitativemeasurement of biologicaland physical properties ofcells and other particles.These properties aremeasured when the cellspass through one or twolaser beams in single-file.</td></tr><tr><td>Item</td><td>Device control reagents, optional</td><td>Predicate (K030828) allowing the identification</td><td>Predicate (K071681)</td></tr><tr><td></td><td>absolute count reagent and CXP software. The systems with CYTO-STAT tetraCHROME CD45- FITC/CD4-PD/CD8- ECD/CD3-PC5 Monoclonal antibody reagent is intended "For In Vitro Diagnostic Use", allowing the identification and enumeration of Total CD3+ (T cells), Total CD4+, Total CD8+, Dual CD3+/CD4+, Dual CD3+/CD8+ lymphocyte percentages and absolute counts as well as the CD4/CD8 ratio in whole blood flow cytometry. The systems with CD45- FITC/CD56-PC/CD19- ECD/CD3-PC5, the total lymphocyte percentage can be obtained. CD45- FITC/CD56-PE/CD19- ECD/CD3-PC5 monoclonal antibody reagent is intended "For In Vitro Diagnostic Use", allowing the identification and enumeration of total CD19+ (B cells) and CD3- /CD56+ (NK cells) lymphocyte percentages and absolute counts in whole blood flow cytometry. The total</td><td>and enumeration of Total CD3+ (T cells), Total CD4+, Total CD8+, Dual CD3+/CD4+, Dual CD3+/CD8+ lymphocyte percentages and absolute counts as well as the CD4/CD8 ratio in whole blood flow cytometry. The systems with CD45- FITC/CD56-PC/CD19- ECD/CD3-PC5, the total lymphocyte percentage can be obtained. CD45- FITC/CD56-PE/CD19- ECD/CD3-PC5 monoclonal antibody reagent is intended "For In Vitro Diagnostic Use", allowing the identification and enumeration of total CD19+ (B cells) and CD3-/CD56+ (NK cells) lymphocyte percentages and absolute counts in whole blood flow cytometry. The total lymphocyte percentage can obtained as well.</td><td></td></tr><tr><td></td><td>lymphocyte percentage can obtained as well.</td><td></td><td></td></tr><tr><td>Procode Regulation</td><td>GKZ 864.5220</td><td>same same</td><td>same same</td></tr><tr><td>Sample input</td><td>MCL: 32 (12×72 mm) tubes MPL: 24- or 96-well</td><td>32 (12×72 mm) tubes</td><td>24- or 96-well plates, or 12×72mm tubes</td></tr><tr><td>Excitation</td><td>plates, or 12×72mm tubes 488nm</td><td>same</td><td>same</td></tr><tr><td colspan="1" rowspan="1">Item</td><td colspan="1" rowspan="1">Device</td><td colspan="1" rowspan="1">Predicate(K030828)</td><td colspan="1" rowspan="1">Predicate(K071681)</td></tr><tr><td colspan="1" rowspan="1">Lasers</td><td colspan="1" rowspan="1">optional 633nm SSL or635nm HeNe (not FDA-cleared)</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">PhotodetectorCircuits</td><td colspan="1" rowspan="1">FSC: APDSSC: APDFL1: PMTFL2: PMTFL3: PMTFL4: PMTFL5: PMT</td><td colspan="1" rowspan="1">same</td><td colspan="1" rowspan="1">same</td></tr><tr><td colspan="1" rowspan="1">Tarpon AmpBoard DelayLine</td><td colspan="1" rowspan="1">potential signal loss, signalfailure</td><td colspan="1" rowspan="1">same</td><td colspan="1" rowspan="1">same</td></tr></table>

<table><tr><td rowspan=1 colspan=4>Differences</td></tr><tr><td rowspan=1 colspan=1>Item</td><td rowspan=1 colspan=1>Device</td><td rowspan=1 colspan=1>Predicate(K030828)</td><td rowspan=1 colspan=1>Predicate(K071681)</td></tr><tr><td rowspan=1 colspan=1>Detection ofamp boarddelay linesignal loss</td><td rowspan=1 colspan=1>automated pre-acquisition,post-acquisition</td><td rowspan=1 colspan=1>Manual inspection</td><td rowspan=1 colspan=1>Manual inspection</td></tr><tr><td rowspan=1 colspan=1>Disposition ofcompromisedfiles</td><td rowspan=1 colspan=1>Quarantine of listmodedata files suspected ofcomrpromise</td><td rowspan=1 colspan=1>Manual inspection</td><td rowspan=1 colspan=1>Manual inspection</td></tr></table>

# I. Special Control/Guidance Document Referenced (if applicable):

“Deciding When to Submit a 510(k) for a Software Change to an Existing Device”, 25Oct17

“Guidance for the Content of Premarket Submissions for Software Contained in Medical Devices”, 11May05

Blue Book Memo K95-1: “510(k) Requirements During Firm-Initiated Recalls; Guidance on Recall and Premarket Notification Review Procedures During Firm-Initiated Recalls of Legally Marketed Devices”, 21Nov95

# J. Performance Characteristics:

1. Analytical Performance:

a. Accuracy:

To evaluate the effectiveness of the software detection tool in identifying cases of patient datafiles compromised by amp board signal defect, the Sponsor developed digital, electronic, and physical simulation methods to assess the accuracy of the software tool. For the digital simulation method, the LMD Tool edits listmode data (LMD) files retroactively, simulating amp board signal loss through digital, algorithmic means. For the electronic simulation method, a modified amp board was engineered to include a switch on the delay line to electronically mimic the signal loss defect in compromised amp boards For the physical simulation methods, the Sponsor physically disrupted the fluidic path in the instrument in an intermittent fashion. In addition, real-world data files were collected from instrument users who experienced amp board failures in their laboratory or generated from instruments that had known board failures.

For purposes of testing of the SDT, “positive” results are defined as files flagged by the SDT as compromised, and “negative” results are defined as files that were not flagged as compromised by the SDT. Therefore, “false positive” results are uncompromised files which the SDT flags, and “false negative” results are compromised files which are not flagged by the SDT.

# i. Pre-Acquisition Testing:

To evaluate the ability of the software detection tool to detect pre-acquisition signal failures, the modified amp board was used to simulate signal loss conditions on each channel (FL1-5, FSC, SSC) using Tetra, Stem-Kit, and ClearLLab assays and auto-setup protocols. Out of a total of 247 tests across these parameters, 247 cases were positively identified by the SDT as comrompised signal – the positive agreement rate for this value is $1 0 0 . 0 \%$ ( $9 5 \%$ CI: 98.5‒ $1 0 0 . 0 \% )$ .

# ii. Post-Acquisition Test Case 1:

In the first set of test cases for post-acquisition performance of the SDT, the LMD Tool was applied to a set of 42 datafiles (Retrospective Simulations). In addition, the modified amp board or physically disrupted fluidics were employed (Live Simulations). Together, these methods generated 2344–2726 test datafiles for each assay panel. False negative (FNR) and false positive (FPR) rates were determined for the software detection tool. The FNR evaluates the SDT’s inability to identify a compromised file, and the FPR evaluates the frequency of falsely identifying an uncompromised file. The results are presented in the table below:

<table><tr><td rowspan=1 colspan=3></td><td rowspan=1 colspan=3>FNR1</td><td rowspan=1 colspan=3>FPR{2</td></tr><tr><td rowspan=1 colspan=1>Panel</td><td rowspan=1 colspan=1>Mode</td><td rowspan=1 colspan=1>Total n</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>point est.</td><td rowspan=1 colspan=1>95% CI</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>point est.</td><td rowspan=1 colspan=1>95% CI</td></tr><tr><td rowspan=1 colspan=1>Tetra 13</td><td rowspan=1 colspan=1>FlowCount</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>0.65%</td><td rowspan=1 colspan=1>(0.401.08%)</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>11.54%</td><td rowspan=1 colspan=1>(5.4022.97%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 2</td><td rowspan=1 colspan=1>FlowCount</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>0.22%</td><td rowspan=1 colspan=1>(0.090.51%)</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>9.62%</td><td rowspan=1 colspan=1>(4.1820.61%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 1</td><td rowspan=1 colspan=1>relative</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>64</td><td rowspan=1 colspan=1>2.79%</td><td rowspan=1 colspan=1>(2.193.55%)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.00%</td><td rowspan=1 colspan=1>(0.006.88%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 2</td><td rowspan=1 colspan=1>relative</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>0.22%</td><td rowspan=1 colspan=1>(0.090.51%)</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1.92%</td><td rowspan=1 colspan=1>(0.3410.12%)</td></tr><tr><td rowspan=1 colspan=1>StemKit</td><td rowspan=1 colspan=1>CXP</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>41</td><td rowspan=1 colspan=1>1.79%</td><td rowspan=1 colspan=1>(1.322.42%)</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>7.69%</td><td rowspan=1 colspan=1>(3.0318.17%)</td></tr><tr><td rowspan=1 colspan=1>B1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>2726</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>0.30%</td><td rowspan=1 colspan=1>(0.150.59%)</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1.92%</td><td rowspan=1 colspan=1>(0.34-10.12%)</td></tr><tr><td rowspan=1 colspan=1>B2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>2726</td><td rowspan=1 colspan=1>37</td><td rowspan=1 colspan=1>1.38%</td><td rowspan=1 colspan=1>(1.01-1.90%)</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1.92%</td><td rowspan=1 colspan=1>(0.3410.12%)</td></tr><tr><td rowspan=1 colspan=1>M</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>2726</td><td rowspan=1 colspan=1>21</td><td rowspan=1 colspan=1>0.79%</td><td rowspan=1 colspan=1>(0.511.20%)</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3.85%</td><td rowspan=1 colspan=1>(1.0612.98%)</td></tr><tr><td rowspan=1 colspan=1>T1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>2726</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>0.30%</td><td rowspan=1 colspan=1>(0.150.59%)</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3.85%</td><td rowspan=1 colspan=1>(1.0612.98%)</td></tr><tr><td rowspan=1 colspan=1>T2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>2344</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0.04%</td><td rowspan=1 colspan=1>(0.010.25%)</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>5.77%</td><td rowspan=1 colspan=1>(1.9815.64%)</td></tr></table>

1 False Negative Rate: Compromised files not identified by software detection tool 2 False Positive Rate: Uncompromised file identified by software detection tool as compromised 3 Tetra 1 was considered to be representative of FlowCARE

# iii. Post-Acquisition Test Case 2:

In the second set of test cases, challenging, difficult, or undetected compromised datafiles were modified by the LMD tool, and evaluated by the software detection tool. The ClearLLab assay was selected for this test case, as further demonstration of SDT performance at a greater degree of challenge.

<table><tr><td rowspan=1 colspan=3></td><td rowspan=1 colspan=3>FNR1</td></tr><tr><td rowspan=1 colspan=1>Panel</td><td rowspan=1 colspan=1>Mode</td><td rowspan=1 colspan=1>Total n</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>point est.</td><td rowspan=1 colspan=1>95% CI</td></tr><tr><td rowspan=1 colspan=1>B1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>31</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.011.0%)</td></tr><tr><td rowspan=1 colspan=1>B2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>29</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.011.7%)</td></tr><tr><td rowspan=1 colspan=1>M</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>36</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>8.3%</td><td rowspan=1 colspan=1>(2.919.0%)</td></tr><tr><td rowspan=1 colspan=1>T1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>39</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2.6%</td><td rowspan=1 colspan=1>(0.513.2%)</td></tr><tr><td rowspan=1 colspan=1>T2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>22</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.014.9%)</td></tr><tr><td rowspan=1 colspan=6>1 False Negative Rate: Compromised files not identified by software detection tool;no false positive evaluation (true negative) was performed</td></tr></table>

The results met the Sponsor’s pre-determined acceptance criteria.

iv. Real World Data:

In order to evaluate the performance of the SDT in non-simulated conditions, sample listmode datafiles (LMD) were sourced from customers and end-users. A total of 409 datafiles were collected and categorized into three sets, as described below – by source and assay panel. These sets of datafiles were used to evaluate the performance of the SDT in detecting data compromised by actual amp board failure in laboratories using the affected instruments or prospectively by using a failed amp board in a single instrument.

<table><tr><td rowspan=1 colspan=4></td><td rowspan=1 colspan=3>FNR1</td><td rowspan=1 colspan=3>FPR{2</td></tr><tr><td rowspan=1 colspan=1>Set</td><td rowspan=1 colspan=1>Source</td><td rowspan=1 colspan=1>Panel</td><td rowspan=1 colspan=1>Totaln</td><td rowspan=1 colspan=1>FN/n</td><td rowspan=1 colspan=1>pointest</td><td rowspan=1 colspan=1>(95% CI)</td><td rowspan=1 colspan=1>FP/n</td><td rowspan=1 colspan=1>pointest.</td><td rowspan=1 colspan=1>(95% CI)</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>Customercomplaints3</td><td rowspan=1 colspan=1>various</td><td rowspan=1 colspan=1>32</td><td rowspan=1 colspan=1>2/8</td><td rowspan=1 colspan=1>25.0%6</td><td rowspan=1 colspan=1>(7.1-59.1%)</td><td rowspan=1 colspan=1>1/24</td><td rowspan=1 colspan=1>4.2%</td><td rowspan=1 colspan=1>(0.7-20.2%)</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>Clinical site4</td><td rowspan=1 colspan=1>StemKit</td><td rowspan=1 colspan=1>233</td><td rowspan=1 colspan=1>0/8</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-32.4%)</td><td rowspan=1 colspan=1>5/225</td><td rowspan=1 colspan=1>2.2%</td><td rowspan=1 colspan=1>(1.0-5.1%)</td></tr><tr><td rowspan=2 colspan=1>3</td><td rowspan=2 colspan=1>Re-engineeredinstrument</td><td rowspan=1 colspan=1>StemKit</td><td rowspan=1 colspan=1>33</td><td rowspan=1 colspan=1>0/33</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-10.4%)</td><td rowspan=1 colspan=1>n/a</td><td rowspan=1 colspan=1>n/a</td><td rowspan=1 colspan=1>n/a</td></tr><tr><td rowspan=1 colspan=1>Tetra</td><td rowspan=1 colspan=1>111</td><td rowspan=1 colspan=1>0/111</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-3.3%)</td><td rowspan=1 colspan=1>n/a</td><td rowspan=1 colspan=1>n/a</td><td rowspan=1 colspan=1>n/a</td></tr><tr><td rowspan=1 colspan=10>1 False Negative Rate: Compromised files not identified by software detection tool2 False Positive Rate: Uncompromised files identified by software detection tool as compromised3 Listmode datafiles derived from customer complaint casefiles4 Single clinical site with identified intermittent signal failure on one instrument5 Compromised signal boards installed onto a single instrument for collection of 144 samplesfrom 30 donors6 FN from customer complaints were identified by manual review</td></tr></table>

The results met the Sponsor’s pre-determined acceptance criteria.

# v. Manual Review Reader Study:

The labeling addendum for use of the SDT specified that all data should be reviewed before release and reporting, irrespective of SDT flagging and quarantine. Therefore, instructions for manual review included in the labeling addendum constitute a critical mitigation for the SDT, and therefore a constituent element of the device.

To address the adequacy of these instructions for manual review, a reader study was performed. 100 data files from Test Case 1 were selected to represent all IVD assay areas (i.e. Tetra, StemKit, and ClearLLab), as well as all relevant types of signal loss and file compromise observed in the recall investigation, specifically signal loss patterns identified as resulting in false negative results from Test Cases 1 and 2. The datafiles included seven failure pattern-imprinted compromised LMD for each panel, and three unaltered “normal” files for each panel.

Analyses were provided to three Tier 1 independent reviewers, blinded to each other and to expected results. To model clinical practice, a second tier of review was further incorporated; to represent post-acquisition reviewers of higher level experience. Only discordant results among Tier 1 operators were resolved by Tier 2 review. Data for discordant results for a total of $n { = } 3 0$ reads for each panel are

presented in the table below.

<table><tr><td rowspan=1 colspan=4></td><td rowspan=1 colspan=3>Discordance</td></tr><tr><td rowspan=1 colspan=1>Panel</td><td rowspan=1 colspan=1>Mode</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>readers</td><td rowspan=1 colspan=1>n</td><td rowspan=1 colspan=1>point est.</td><td rowspan=1 colspan=1>(95% CI)</td></tr><tr><td rowspan=1 colspan=1>Tetra 1</td><td rowspan=1 colspan=1>Flow-Count</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 2</td><td rowspan=1 colspan=1>Flow-Count</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3.3%</td><td rowspan=1 colspan=1>(0.6-16.7%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 1</td><td rowspan=1 colspan=1>relative</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>Tetra 2</td><td rowspan=1 colspan=1>relative</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>StemKit</td><td rowspan=1 colspan=1>CXP</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3.3%</td><td rowspan=1 colspan=1>(0.6-16.7%)</td></tr><tr><td rowspan=1 colspan=1>B1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>B2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>10.0%</td><td rowspan=1 colspan=1>(3.5-25.6%)</td></tr><tr><td rowspan=1 colspan=1>M</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>T1</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr><tr><td rowspan=1 colspan=1>T2</td><td rowspan=1 colspan=1>ClearLLab</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>(0.0-11.4%)</td></tr></table>

Discordant results were further reviewed by a second tier adjudicator, at a pathologist level of training. This secondary review corrected all but one of the discordant results $[ \mathrm { F N } = 1 / 1 0 0$ : FNR $1 . 0 \%$ $( 0 . 2 \substack { - 5 . 5 \% } )$ .

b. Precision/Reproducibility: Not applicable   
c. Linearity: Not applicable   
d. Carryover: Not applicable   
e. Interfering Substances: Not applicable

2. Other Supportive Instrument Performance Data Not Covered Above: Not applicable

# K. Proposed Labeling:

The labeling is sufficient and it satisfies the requirements of 21 CFR Parts 801 and 809, as applicable.

# L. Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.