# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYINSTRUMENT ONLY

I Background Information:

A 510(k) Number K243922   
B Applicant Meridian Bioscience, Inc.   
C Proprietary and Established Names Revogene   
D Regulatory Information

<table><tr><td rowspan=1 colspan=1>Product Code(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>Regulation Section</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>00I</td><td rowspan=1 colspan=1>Class II</td><td rowspan=1 colspan=1>21 CFR 862.2570 - Instrumentation ForClinical Multiplex Test Systems</td><td rowspan=1 colspan=1>CH - Clinical Chemistry</td></tr></table>

# II Submission/Device Overview:

# A Purpose for Submission:

1. To provide supportive data for hardware and software/firmware design modifications of the Revogene instrument. The modifications are intended to enable the addition of a cooling system for reducing the temperature around the instrument’s internal photomultiplier tube (PMT) component, thereby preventing potential PMT malfunctions that may negatively impact the instrument’s operation.

2. To obtain a determination of substantial equivalence for the modified Revogene instrument relative to the previously cleared (K222779) design of the same Revogene instrument as predicate.

# B Type of Test:

Real time (RT) polymerase chain reaction (PCR) with fluorescence-based detection of target analyte nucleic acids.

# III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below.

# B Indication(s) for Use:

The Revogene instrument is intended for in vitro diagnostic (IVD) use in performing nucleic acid testing of specific IVD assays in clinical laboratories. Revogene is capable of automated lysis and dilution of samples originating from various clinical specimen types. Revogene performs automated amplification and detection of target nucleic acid sequences by fluorescence-based realtime PCR.

# C Special Conditions for Use Statement(s):

Rx – For Prescription Use Only   
IVD – For In Vitro Diagnostic Use Only   
Running fewer than eight (8) samples (i.e., eight (8) assay PIEs) may require the use of MOCK   
PIEs to fill up to eight (8) spaces for thermal and rotational balance in the Revogene

# IV Device/System Characteristics:

# A Device Description:

The Revogene instrument is a PCR thermal cycler equipped with components resembling a lowspeed centrifuge (e.g., rotor, centripetal motor) in addition to other mechanical and electrical components that help perform the different steps of nucleic acid amplification-based diagnostic tests. The instrument requires the use of an assay-specific, disposable, single-sample, single-use microfluidic cartridge (also known as a PIE) identifiable with barcodes. A user-friendly touchscreen allows the Operator to interact with the instrument for initiating sample runs and performing other analytical and data management functions.

For the use of Revogene to conduct a cleared Revogene assay, the Operator first identifies the sample, the assay-specific sample buffer tube/SBT (if applicable), and the PIE designated for the sample by scanning respective barcodes with an external barcode scanner or via manual entry. Next, the Operator discharges each patient specimen into the SBT, mixes and transfers the buffered sample into the corresponding PIE, and loads the PIE into Revogene. An internal barcode reader identifies the loaded PIEs to the instrument.

The PIE is a completely integrated device in which the dispensed sample is processed through a series of microfluidic chambers. Within each assay-specific PIE, all PCR reagents are incorporated in a dehydrated form within the PCR wells. In addition, in each PIE, DNA-based assays incorporate a Process Control $\mathrm { ( P r C ) }$ to verify sample processing and amplification steps, whereas RNA-based assays incorporate an Internal Control (IC) and a Microfluidic Control (MFC), respectively, to verify RNA transcription/amplification/detection steps (including detection of potential inhibitors and reagent failure) and to control for PIE fluidics. The Revogene instrument is designed for fully automated sample processing along with subsequent PCR amplification and detection of the target sequence using real-time PCR aided by target-specific primers and fluorogenic probes.

With eight (8) spaces for PIEs, Revogene can simultaneously process 1–8 samples in the same run provided the assays are either identical or different but using the same instrument control protocol. However, each run requires eight (8) PIEs to be present in the instrument. For processing fewer than eight (8) samples within a run, the total PIE number is brought up to eight (8) using MOCK PIEs (catalog number 610208), which are reusable, PIE-simulating placeholders designed to confer thermal and rotational balance in the centrifugation-assisted runs. MOCK PIEs contain individual barcodes enabling recognition by Revogene over repeated uses.

An on-board computer with a Windows 10 IoT Enterprise operating system executes the operational control of Revogene through subsystems that include, e.g., a photomultiplier tube (PMT) detector for signal detection and an internal temperature control assembly. Revogene is a mains-powered instrument with no electrical accessories, no rechargeable battery, no wireless technology, and no intentional Radio Frequency (RF) emitters as hardware components.

For the PCR runs, temperature controllers provide required temperature cycling, whereas the LEDs in the multichannel optical module excite the fluorescent dyes in all PIE wells and fluorescence channels as the targets are progressively amplified by PCR. Revogene is capable of simultaneously detecting signals from four (4) different fluorophores. At each detection cycle, the fluorescence signals generated from the probes are captured and amplified by the PMT for interpretation by the Revogene system using embedded calculation algorithms in accordance with the specific assay run in each PIE. An Assay Definition File (ADF) ensures the use of assay-specific cut-offs by the software algorithms for data analysis and the result generation. Of note, all functional components for signal detection, analysis, and result output (e.g., software algorithm, instrument control protocol, ADF) are developed, determined, and/or defined by Meridian Biosciences and are not user-modifiable. Revogene is intended to be used in a professional healthcare facility environment (e.g., clinical laboratories), operated by trained laboratory personnel.

At the end of the assay run, based on the amplification status of the targets, the status of $\mathrm { P r } { \bf C }$ or of IC/MFC (as appropriate, depending on the assay type), as well as assay cut-offs, Revogene may return a result of (a) POS (Positive), when target is detected; (b) NEG (Negative), when target is not detected; (c) UNR (Unresolved), or (d) IND (Indeterminate), when internal control failures result from inhibitory specimens and/or failures of microfluidics or reagent, or errors in assay processing or data analysis. Repeat testing is recommended for UNR and IND results. Further details are available in the Revogene Operator’s Manual.

In comparison to the predicate (i.e., the previous iteration of Revogene that was previously cleared under K222779), the current Revogene instrument (under review in K243922) introduces several hardware modifications to mitigate the risk of PMT malfunction by addressing the root cause behind fluorescence signal drops, thereby preventing instrument failures, and software/firmware modifications to enable the operation of the modified hardware.

# B Instrument Description Information:

1. Instrument Name: Revogene

2. Specimen Identification:

Unique bar codes individually identify each specimen, Sample Buffer Tube (SBT), and microfluidic cartridge (a.k.a. PIE) for sample processing. The individual bar codes are registered into the Revogene System software via the Revogene external bar code reader. The End User/Operator can either scan in or manually enter the sample ID via the Revogene touchscreen.

# 3. Specimen Sampling and Handling:

User intervention is required for transferring the patient specimen into the SBT for initial processing (e.g., sample mixing, as applicable), transferring the sample into a PIE, and loading/unloading the PIEs into the instrument. The sample preparation and handling procedure is described in further detail in Revogene Operator’s Manual and in the Package Insert of each cleared Revogene assay.

4. Calibration:

Revogene does not require periodic calibration. However, the optical and thermal parameters must be checked once a year to confirm that they are within specification by running “Revogene Check” (Class 1 510(k) exempt device), which is a single-use, qualitative test utilizing automated real-time PCR.

# 5. Quality Control:

No Quality Control is recommended for the Revogene. However, each PIE contains internal process controls appropriate for the type of nucleic acid analyte. For example, for DNA assays, an internal process control $\mathrm { ( P r C ) }$ controls for the inhibition of amplification and effectiveness of assay reagents and sample processing. For RNA assays, an internal control (IC) controls for the inhibition of amplification and effectiveness of assay reagents, whereas a microfluidic control (MFC) monitors the effectiveness of sample processing.

# V Substantial Equivalence Information:

A Predicate Device Name(s): Revogene   
B Predicate 510(k) Number(s): K222779

C Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp; PredicateDevice(s):</td><td colspan="1" rowspan="1">Candidate device: K243922</td><td colspan="1" rowspan="1">Predicate: K222779</td></tr><tr><td colspan="1" rowspan="1">Device Trade Name</td><td colspan="1" rowspan="1">Revogene</td><td colspan="1" rowspan="1">Revogene</td></tr><tr><td colspan="3" rowspan="1">General Device Characteristic Similarities</td></tr><tr><td colspan="1" rowspan="1">Product Code</td><td colspan="1" rowspan="1">OOIReal time nucleic acid amplification system</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Classification</td><td colspan="1" rowspan="1">Class II</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Regulation</td><td colspan="1" rowspan="1">21 CFR §862.2570Instrumentation for clinical multiplex testsystems</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Intended Use/Indications For Use</td><td colspan="1" rowspan="1">The Revogene instrument is intended for invitro diagnostic (IVD) use in performingnucleic acid testing of specific IVD assays inclinical laboratories. Revogene is capable ofautomated lysis and dilution of samplesoriginating from various clinical specimentypes. Revogene performs automatedamplification and detection of target nucleicacid sequences by fluorescence-based real-time PCR</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Test Automation</td><td colspan="1" rowspan="1">Automated cell lysis, DNA amplification andDNA detection with result interpretation</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Test Technology/Detection Technique</td><td colspan="1" rowspan="1">Real-time Polymerase chain reaction withfluorogenic detection of amplified DNA</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Sample analysis andresult determination</td><td colspan="1" rowspan="1">Combination of software, instrument controlprotocols and assay definition files developedand determined by Meridian</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Test Format</td><td colspan="1" rowspan="1">Disposable, single-use, single-sample, assay-specific microfluidic cartridge (also known as"PIE"); up to eight (8) specimens (in eight (8)PIEs) may be processed and analyzed per run</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Internal ProcessControl for DNAassays</td><td colspan="1" rowspan="1">Each PIE contains an Internal Process Control(PrC) that controls for amplification inhibition,assay reagents, and sample processingeffectiveness</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Internal ProcessControl for RNAassays</td><td colspan="1" rowspan="1">Each PIE contains an Internal Control (IC) thatcontrols for amplification inhibition, assayreagents, and sample processing effectiveness;sample processing is monitored by aMicrofluidic Control (MFC)</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Temperature Control</td><td colspan="1" rowspan="1">Heating element/fan assembly and cooling fanfor PCR cycling</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="1" rowspan="1">Test Access</td><td colspan="1" rowspan="1">Prescription Use Only</td><td colspan="1" rowspan="1">-Same-</td></tr><tr><td colspan="3" rowspan="1">General Device Characteristic Differences</td></tr><tr><td colspan="1" rowspan="1">Operating System</td><td colspan="1" rowspan="1">Windows 10 IoT Enterprise (Windows 10)</td><td colspan="1" rowspan="1">Windows EmbeddedStandard 7 (Windows7)</td></tr><tr><td colspan="1" rowspan="1">AdditionalTemperature Control</td><td colspan="1" rowspan="1">Photomultiplier Tube (PMT) cooling system(an assembly of fan and venting canal) withupdated firmware to enable cooling systemoperation</td><td colspan="1" rowspan="1">No PMT coolingsystem</td></tr></table>

# VI Standards/Guidance Documents Referenced:

Instrumentation for Clinical Multiplex Test Systems – Class II Special Controls Guidance for Industry and FDA Staff | FDA

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

1. Precision/Reproducibility and Repeatability:

Studies evaluating the precision of the Revogene instrument were previously conducted to support the clearance or authorization of several molecular assays targeting specific analytes that were previously cleared/authorized for use on the Revogene instrument, e.g.,

(a) K170557 (GenePOC GBS LB, later renamed Revogene GBS LB) (b) K172569 (GenePOC CDiff, later renamed Revogene C. difficile)

(c) K183366 (GenePOC Strep A, later renamed Revogene Strep A)   
(d) K190275 (GenePOC Carba, later renamed Revogene Carba C) and   
(e) EUA210450 (Revogene SARS-CoV-2).   
Further information on the precision of the unmodified Revogene instrument may be obtained from the decision summaries or authorization letter corresponding to these cleared or authorized devices.

Furthermore, the sponsor conducted a head-to-head method comparison study between the candidate Revogene device (with the PMT cooling system hardware and software/firmware modifications) and the unmodified predicate in accordance with Section 7 of FDA’s Class II Special Controls Guidance for Instrumentation for Clinical Multiplex Systems, using three (3) representative, previously cleared Revogene assays that are performed on the Revogene instrument—namely, Revogene Strep A (K183366), Revogene Carba C (K190275), and Revogene SARS-CoV-2 (EUA210450). These studies (discussed in more detail in Section VII.B below) demonstrated statistical equivalence between the unmodified predicate and the modified candidate instrument, with no statistically significant difference between the results obtained from these two (2) sets of instruments, thereby providing the empirical rationale supporting an assumption of no change of precision of the molecular assay devices when run on the candidate Revogene instrument.

2. Linearity: Not applicable.

# 3. Analytical Specificity/Interference:

Analytical specificity/interference of molecular assay devices targeting specific analytes (as indicated in Section VII.A.1 above), when performed on the Revogene instrument, was previously evaluated in studies conducted to support the clearance or authorization of the indicated devices, as noted above. Further information on the analytical specificity of these devices with the unmodified Revogene instrument may be obtained from the decision summaries or authorization letter corresponding to these cleared or authorized devices.

Furthermore, in the head-to-head method comparison study noted in Section VII.A.1 above, the sponsor demonstrated statistical equivalence between the unmodified predicate and the modified candidate device, thereby providing the empirical rationale supporting an assumption of no change of analytical specificity/interference of the molecular assay devices when run on the candidate Revogene instrument.

4. Accuracy (Instrument): Not applicable.

# 5. Carry-Over and Cross-contamination:

The disposable, single-specimen, single-use cartridges (i.e., PIEs) are expected to minimize the possibility of amplicon carry-over or sample cross-contamination. Carry-over and cross contamination for the molecular assay devices targeting specific analytes (as indicated in Section VII.A.1 above), when performed on the Revogene instrument, was previously evaluated in studies conducted to support the clearance or authorization of the indicated devices, as noted above. Further information on carry-over and cross contamination for these devices with the unmodified Revogene instrument may be obtained from the decision summaries or authorization letter corresponding to these cleared or authorized devices.

Furthermore, in the head-to-head method comparison study noted in Section VII.A.1 above, the sponsor demonstrated statistical equivalence between the unmodified predicate and the modified candidate device, thereby providing the empirical rationale supporting an absence of the carry-over and cross-contamination for the molecular assay devices when run on the candidate Revogene instrument.

# B Other Supportive Instrument Performance Characteristics Data:

# Brief Background for Instrument Performance Studies:

The candidate Revogene instrument (K243922) represents an iteration of the previously cleared (K222779) and commercially available Revogene, upon which this iteration implements certain hardware, software, and firmware modifications that are designed to reduce potential issues in performance and instrument operation. The modifications in the current candidate Revogene feature a cooling system for the PMT (intended to prevent temperature-related drops in raw fluorescent signals that may result in instrument failure) and an Operating System upgrade, as compared to the previously cleared (K222779) Revogene, i.e., the predicate.

Therefore, to provide empirical evidence in support of a claim that these modifications in the candidate Revogene instrument do not negatively impact the performance of assays on Revogene, Meridian conducted a head-to-head method comparison/functional testing study between the candidate Revogene instrument and the predicate, respectively with and without the indicated modifications, using three (3) previously cleared Revogene assays currently on the US market, i.e., Revogene Strep A (K183366), Revogene Carba C (K190275), and Revogene SARS-CoV-2 (EUA210450), each representative of one (1) instrument control protocol. Performed in accordance with the principle laid out in Section 7 of FDA’s Class II Special Controls Guidance on Instrumentation for Clinical Multiplex Test Systems, the objective of these head-to-head comparison studies was to demonstrate statistical equivalence between the candidate and predicate Revogene instruments with no statistically significant difference between the assay results obtained from either Revogene.

# Head-to-head Revogene comparison studies:

Fifteen (15) commercial Revogene instruments (K222779) were compared with fifteen (15) candidate Revogene with PMT cooling system and software modifications (K243922) by three (3) different operators, each of whom was assigned five (5) instruments of each type and executed three (3) runs (for Strep A and SARS-CoV-2) or six (6) runs (for Carba C), on each assigned instrument. To reach a total of 360 positive and 360 negative results, each Strep A and SARSCoV-2 assay run included four (4) positive and four (4) negative samples, whereas each Carba C assay run included two (2) each of blaKPC positive, blaIMP positive, and negative samples. The study was conducted on three (3) days (for Strep A and SARS-CoV-2) or six (6) days (for Carba C), with two (2) reagent lots distributed equally over both Revogene instruments and operators. External controls (positive and negative) were incorporated in the study design to test at the end of each study day to ensure absence of reagent failure and reagent or environmental contamination/carry over. Unexpected or anomalous results (e.g., unresolved (UNR), indeterminate (IND), falsely positive or negative results) triggered a root cause identification, and only the anomalous results identified to be unrelated to the Revogene instrument design were considered eligible for repeat testing. Upon repeat testing, samples generating reportable results were considered for statistical analysis, whereas final UNR, IND, and falsely positive or negative results were included only in qualitative analysis (i.e., calculation of the positivity, negativity, and UNR/IND rates).

Acceptance criteria were defined in terms of statistical evaluation of difference in outcomes between the candidate and predicate Revogene instrument sets, for which the rates of positivity (for positive samples), negativity (for negative samples), final UNR and IND results should have a $\mathsf { p } { > } 0 . 0 5$ (i.e., no statistical significance of difference) as estimated with two-proportion comparison tests. Further, statistical equivalence of the performance of candidate and predicate Revogene instruments should be verified by performing a TOST (Two One-Sided Test) for equivalence with a significance level of $5 \%$ ( $\mathbf { \check { a } } = 0 . 0 5 )$ , $90 \%$ Confidence Interval, and final mean Ct values between the candidate and predicate Revogene sets to be within a margin of $\pm 3 \mathrm { C t }$ (which generates a $\mathrm { p } { < } 0 . 0 5$ signifying statistical equivalence). Furthermore, no anomalies related to the control firmware v2.3.0 should be observed.

1. Revogene Strep A (K183366) using contrived specimen prepared by spiking pooled negative throat matrix with Bacillus subtilis DNA to serve as an internal process control $( \mathrm { P r C }$ , negative sample target) without or with Group A Streptococcus pyogenes (GAS, positive sample target) and tested in a PCR.

2. Revogene SARS-CoV-2 (EUA210450) using contrived specimen prepared by spiking pooled negative nasopharyngeal matrix with SARS-CoV-2 to serve as positive sample target, along with a synthetic RNA fragment within the assay master mix to serve as an internal control (IC, negative sample target) for the reverse transcriptase (RT)-PCR.

3. Revogene CARBA C (K190275) using contrived samples prepared in sterile saline with targetappropriate bacterial suspensions, i.e., Klebsiella pneumoniae (for blaKPC-2 gene target) and Escherichia coli (for blaIMP-1 gene target) for positive sample targets and carbapenemasenegative Enterobacter cloacae along with an internal Process Control $\mathrm { ( P r C ) }$ DNA contained within the assay reagents for the negative sample target and tested in a PCR.

Conclusion: All acceptance criteria were met for these three (3) validation studies. Therefore, based on the provided analytical studies, the integration of the PMT cooling system (including the EMC modifications and software/firmware updates) and the Operating System upgrade appear to have no impact on the performance of the Revogene Instrument system when used with Revogene Strep A, Revogene SARS-CoV-2, Revogene CARBA C assays, as well as other Revogene assays performed under the same instrument control protocols, as applicable.

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.