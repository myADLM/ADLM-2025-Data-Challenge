# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY

I Background Information:

A 510(k) Number K232208

# B Applicant

Sectra AB

# C Proprietary and Established Names

Sectra Digital Pathology Module (3.3)

D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QKQ</td><td rowspan=1 colspan=1>Class I</td><td rowspan=1 colspan=1>21 CFR 864.3700 -Whole Slide ImagingSystem</td><td rowspan=1 colspan=1>PA - Pathology</td></tr></table>

# II Submission/Device Overview:

Purpose for Submission: New Device

A Type of Test: Not applicable – software only device

III Intended Use/Indications for Use:

A Intended Use(s):

See Indications for the Use below.

# B Indication(s) for Use:

For In Vitro Diagnostic Use

Sectra Digital Pathology Module (3.3) is a software device intended for viewing and management of digital images of scanned surgical pathology slides prepared from formalin-fixed paraffin embedded (FFPE) tissue. It is an aid to the pathologist to review and interpret these digital images for the purposes of primary diagnosis.

Sectra Digital Pathology Module (3.3) is not intended for use with frozen section, cytology, or non-FFPE hematopathology specimens. It is the responsibility of the pathologist to employ appropriate procedures and safeguards to assure the validity of the interpretation of images using Sectra Digital Pathology Module (3.3).

Sectra Digital Pathology Module (3.3) is intended for use with Leica’s Aperio GT 450 DX scanner and Dell U3223QE display, for viewing and management of the ScanScope Virtual Slide (SVS) and Digital Imaging and Communications in Medicine (DICOM) image formats.

# C Special Conditions for Use Statement(s):

Rx - For Prescription Use Only

# IV Device/System Characteristics:

# A Device Description:

The Sectra Digital Pathology Module (3.3) [henceforth referred to DPAT (3.3)] is a digital slide viewing system for viewing and managing digital pathology images of glass slides obtained from the Aperio GT $4 5 0 \mathrm { D X }$ scanner and viewed on the Dell U3223QE display. The DPAT (3.3) can only be used in combination with the external image server provided by Sectra picture archiving and communications system (PACS). The end user must log in to Sectra Workstation to access the subject device. Sectra Workstation is available in two models: IDS7 and UniView. UniView is an equivalent, web-based version of IDS7. The architecture of DPAT (3.3) consists of the following elements:

Pathology Image Window (PIW) where the scanned slides are viewed and manipulated by end users. The PIW is a web application embedded into Sectra Workstation to offer a seamless user experience. Sectra Pathology Server (SPS) is the main server component of the web-based Pathology Image Window. The SPS supports displaying and manipulating the scanned slides. Database Engine stores metadata such as annotations required by the SPS. Sectra Pathology Import Server (SPIS) is used for importing digital pathology images (from scanned slides) from the Aperio GT 450 DX scanner as an alternative to the scanner sending images to Sectra PACS using the standard DICOM Storage.

The system capabilities include:

• retrieving and displaying digital slides   
• including support for remote intranet access over computer networks   
• providing tools for annotating digital slides and entering and editing metadata associated with digital slides   
• displaying the scanned slide images for primary diagnosis by pathologists

The DPAT (3.3) is operated as follows:

1. The DPAT (3.3) receives quality-controlled images from the Aperio GT $4 5 0 \mathrm { D X }$ scanner and extracts a copy of the images’ metadata. The unaltered images are then sent to the external image storage (Sectra Core). A copy of the image metadata (e.g., the pixel size) is stored locally in the subject device to increase the operational performance (e.g., response times) of the subject device.

2. The reading pathologist selects a case (patient) from a worklist external to the subject device such as the laboratory information system (LIS) whereby the SPS fetches the associated images from the Sectra Core.

3. The reading pathologist uses DPAT (3.3) to view the images and is able to perform the following actions, as needed:

• Zoom and pan the image   
• Measure distances and areas in the image   
• Annotate images View multiple images side by side in a synchronized fashion

After viewing all images belonging to a particular case (patient), the pathologist will make a diagnosis. The diagnosis is documented in another system such as the LIS.

DPAT (3.3) operates with the following components listed below in Table 1.

Table 1: Interoperable Components Intended for Use with Sectra Digital Pathology Module (3.3)   

<table><tr><td rowspan=1 colspan=1>Scanner Hardware</td><td rowspan=1 colspan=1>Scanner Outputfile format</td><td rowspan=1 colspan=1>Interoperable ViewingSoftware</td><td rowspan=1 colspan=1>InteroperableDisplay</td></tr><tr><td rowspan=1 colspan=1>Aperio GT 450 DXscanner</td><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>Sectra Digital PathologyModule (3.3)</td><td rowspan=1 colspan=1>Dell U3223QE</td></tr><tr><td rowspan=1 colspan=1>Aperio GT 450 DXscanner</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>Sectra Digital PathologyModule (3.3)</td><td rowspan=1 colspan=1>Dell U3223QE</td></tr></table>

# Minimum System Requirements - Computer Environment

The system requirements are given in Tables 2 through 4 below.

Table 2: Requirements for PIW   

<table><tr><td rowspan=1 colspan=1>Sectra Workstation (Host forsubject device)</td><td rowspan=1 colspan=1>IDS7</td><td rowspan=1 colspan=1>UniView</td></tr><tr><td rowspan=1 colspan=1>Operating system</td><td rowspan=1 colspan=2>MS Windows 11 or 10 (x64)</td></tr><tr><td rowspan=1 colspan=1>CPU</td><td rowspan=1 colspan=2>4-core CPU, 3.6 GHz</td></tr><tr><td rowspan=1 colspan=1>RAM</td><td rowspan=1 colspan=2>8 GB</td></tr><tr><td rowspan=1 colspan=1>Graphics board</td><td rowspan=1 colspan=2>NVIDIA T600 or Quadro P1000 with 4GB</td></tr><tr><td rowspan=1 colspan=1>Network</td><td rowspan=1 colspan=2>1 Gbit/s LAN connection</td></tr><tr><td rowspan=1 colspan=1>3D mouse</td><td rowspan=1 colspan=1>3Dconnexion SpaceMousePro</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Browser</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>Google Chrome or MS Edge</td></tr><tr><td rowspan=1 colspan=1>Hardware acceleration</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>Enabled</td></tr><tr><td rowspan=1 colspan=1>WebGL support</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>Required</td></tr></table>

Table 3: Server (SPDB and SPS) Requirements   

<table><tr><td>Operating system &amp; Database Engine (SPDB)</td><td>•Windows Server 2019 Std Ed, with SQL Server 2019 Std Ed •Windows Server 2016 Std Ed, with SQL Server 2016 SP3 Std Ed (upgrades only) Windows Server 2012 R2 Std Ed, with SQL Server 2012 SP4 Std Ed (upgrades only) • .NET 6</td></tr><tr><td>Operating System &amp; Sectra Pathology Import Service (SPIS)</td><td>Windows Server 2019 Windows Server 2016 (upgrades only) Windows Server 2012 R2 (upgrades only) Windows 11 Windows 10 .NET 6</td></tr></table>

Table 4: Recommended Configurations, Server   

<table><tr><td colspan="2">Sectra Pathology Server (SPDB and SPS)</td></tr><tr><td>CPU RAM Disk Network</td><td>8 cores CPU, e.g., 1x Intel Xeon 4110 CPU 32 GB RAM 2x 146 GB system disk (mirrored)</td></tr><tr><td colspan="2">Gigabit LAN connection Sectra Pathology Import Service - SPIS</td></tr><tr><td>CPU RAM</td><td>4 vCPU</td></tr><tr><td rowspan="3">Disk Network</td><td>8 GB vRAM</td></tr><tr><td>146 GB system disk</td></tr><tr><td>Gigabit LAN connection</td></tr></table>

# B Instrument Description Information:

1. Instrument Name: Sectra Digital Pathology Module (3.3)

2. Specimen Identification:

The Sectra Digital Pathology Module (3.3) uses digital pathology images obtained from the Aperio GT 450 DX scanner of Hematoxylin and Eosin (H&E) stained glass slides. The reading pathologist selects a case (patient) from a worklist external to the subject device whereby the subject device fetches the associated images from the external image storage. The scanned images are identified based on the previously assigned specimen identifier such as the laboratory specimen accession number.

3. Specimen Sampling and Handling:

Specimen sampling and handling are performed upstream and independent of the use of the subject device. Specimen sampling includes biopsy or resection specimens which are processed using histology techniques. The FFPE tissue section is hematoxylin & eosin (H&E) stained. Digital images are then obtained from these glass slides using the Aperio GT 450 DX scanner.

4. Calibration: Not Applicable

5. Quality Control:

The subject device receives quality-controlled images from the scanner. The subject device specific quality control measures are as follows:

• Connect scanner - This test should be performed before connecting the scanner to the subject device in order to verify the on-site integration between the Aperio GT 450 DX scanner and the Sectra Workstation.   
• View pathology images - Every pathologist should perform this test on review workstation   
before reading pathology images using the subject device to ensure that all scanned slide images have been imported and for every case, view the thumbnails in the pathology image window to verify that each slide that should be in the case is present (manually verifying tissue block and staining information from LIS).

Additional details of the quality control procedures are provided in the device User’s Guide and the Installation Guide.

# V Substantial Equivalence Information:

A Predicate Device Name(s): Aperio GT 450 DX B Predicate 510(k) Number(s): K232202 C Comparison with Predicate(s):

<table><tr><td rowspan=1 colspan=1>Device &amp;PredicateDevice(s):</td><td rowspan=1 colspan=1>Sectra Digital PathologyModule (3.3)K232208</td><td rowspan=1 colspan=6>Aperio GT 450 DXK232202</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=7>General Device Characteristic: Similarities</td></tr><tr><td rowspan=6 colspan=1>IntendedUse/Indications for Use</td><td rowspan=6 colspan=1>Sectra Digital PathologyModule (3.3) is a softwaredevice intended forviewing and managementof digital images ofscanned surgicalpathology slides preparedfrom formalin-fixedparaffin embedded(FFPE) tissue. It is an aidto the pathologist toreview and interpret thesedigital images for thepurposes of primarydiagnosis.Sectra Digital PathologyModule (3.3) is notintended for use withfrozen section, cytology,or non-FFPEhematopathologyspecimens. It is theresponsibility of thepathologist to employappropriate proceduresand safeguards to assurethe validity of theinterpretation of images</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td rowspan=1 colspan=2>ScannerHardware</td><td rowspan=1 colspan=1>ScannerOutput fileformat</td><td rowspan=1 colspan=1>InteroperableViewingSoftware</td><td rowspan=1 colspan=1>InteroperableDisplays</td></tr><tr><td></td><td rowspan=1 colspan=2>Aperio GT</td><td rowspan=2 colspan=1>SVS</td><td rowspan=3 colspan=1>AperioWebViewer DX</td><td rowspan=3 colspan=1>BarcoMDPC-8127Dell UP3017Dell U3023EDell U3223QE</td></tr><tr><td></td><td rowspan=2 colspan=2>450 DXscanner</td></tr><tr><td></td><td rowspan=1 colspan=1></td></tr><tr><td></td><td></td><td></td><td rowspan=1 colspan=1></td><td></td><td></td></tr></table>

<table><tr><td colspan="1" rowspan="2"></td><td colspan="1" rowspan="2">using Sectra DigitalPathology Module (3.3).Sectra Digital PathologyModule (3.3) is intendedfor use with Leica'sAperio GT450 DXscanner and DellU3223QE display, forviewing and managementof the ScanScope VirtualSlide (SVS) and DigitalImaging andCommunications inMedicine (DICOM)image formats.</td><td colspan="5" rowspan="2">Aperio GT SVS        SectraDell U3223QE450 DX                    Digitalscanner                     PathologyModule(3.3)Aperio GT  DICOM   Sectra450 DX                                            Dell U3223QEDigitalscanner                    PathologyModule(3.3)The Aperio GT 450 DX is not intended for use with frozensection, cytology, or non-FFPE hematopathology specimens. It isthe responsibility of a qualified pathologist to employ appropriateprocedures and safeguards to assure the validity of theinterpretation of images obtained using the Aperio GT 450 DX.</td></tr><tr><td colspan="1" rowspan="1">Aperio GT450 DXscanner</td><td colspan="1" rowspan="1">DICOM</td><td colspan="1" rowspan="1">SectraDigitalPathologyModule(3.3)</td><td colspan="1" rowspan="1">Dell U3223QE</td></tr><tr><td colspan="1" rowspan="1">Type ofSoftwareApplication</td><td colspan="1" rowspan="1">Internet Browser based</td><td colspan="5" rowspan="1">Internet Browser based</td></tr><tr><td colspan="1" rowspan="1">Imagemanipulationfunctions</td><td colspan="1" rowspan="1">Panning, zooming,gamma function,annotations, and distancemeasurements.</td><td colspan="5" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">End User'sInterface</td><td colspan="1" rowspan="1">DPAT (3.3) - PathologyImage Window (the clientcomponent of SectraDPAT (3.3)</td><td colspan="5" rowspan="1">DPAT (3.3) and WebViewer DX</td></tr><tr><td colspan="1" rowspan="1">ImageManipulation Functions</td><td colspan="1" rowspan="1">Panning, zooming, imageadjustments, annotations,and distance/areameasurements</td><td colspan="5" rowspan="1">Same</td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="5" rowspan="1">General Device Characteristic: Differences</td></tr><tr><td colspan="1" rowspan="1">DeviceComponents</td><td colspan="1" rowspan="1">DPAT (3.3)</td><td colspan="5" rowspan="1">Scanner, Webviewer DX, Display</td></tr><tr><td colspan="1" rowspan="1">Image fileformat</td><td colspan="1" rowspan="1">SVS and DICOM</td><td colspan="5" rowspan="1">SVS</td></tr><tr><td colspan="1" rowspan="1">Principle ofOperation</td><td colspan="1" rowspan="1">After WSI images aresuccessfully acquired byusing Aperio GT 450 DXscanner, WSI images areimported by SPIS asgroups of cases. Thelaboratory technician</td><td colspan="5" rowspan="1">After WSI images are successfully acquired by using Aperio GT450 DX scanner, it is data is sent to end-user-provided imagestorage attached to the local network. During the review, thepathologist opens WSI images acquired with the WSI scanner fromthe image storage, performs further QC, and reads WSI images ofthe slides to make a diagnosis.</td></tr><tr><td></td><td>performs a quality control by using PIW to verify that all images have been imported. During review, the pathologist selects a patient case and opens WSI images from the Sectra Core to read the WSI images and make a Diagnosis.</td><td></td></tr></table>

# VI Standards/Guidance Documents Referenced:

1. Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices: Guidance for Industry and Food and Drug Administration Staff, April 20, 2016.   
2. Applying Human Factors and Usability Engineering to Medical Devices: Guidance for Industry and Food and Drug Administration Staff February 3,   
2016.   
3. EN ISO 13485:2016 Medical devices — Quality management systems — Requirements for regulatory purposes.   
4. EN ISO 14971:2019-12 – Medical devices - Application of risk management to medical devices (same as ISO 14971:2007, Corrected version 2007-10-01), Recognition Number: 5-40.   
5. EN 62304:2006- AMD1:2015 – Medical device software - software life-cycle processes, Recognition Number: 13-32. EN ISO 62366-1:2015 - AMD1:2015 – Application of usability engineering to medical devices, Recognition Number: 5-114.   
6. ISO/IEC 27001:2013 – Information technology — Security techniques - Information security management systems — Requirements.   
7. ISO/IEC 27017: 2015 — Security techniques — Code of practice for information security controls based on ISO/IEC 27002 for cloud services.   
8. ISO/IEC 27018: 2019 — Security techniques — Code of practice for protection of personally identifiable information (PII) in public clouds acting as PII processors.

# VII Performance Characteristics (if/when applicable):

A Analytical Performance:

a. Precision/Reproducibility: Not applicable   
b. Linearity: Not applicable   
c. Analytical Specificity/Interference: Not applicable   
d. Accuracy (Instrument): Not applicable   
e. Carry-Over: Not applicable

# B Other Supportive Instrument Performance Characteristics Data:

a. A clinical study was conducted to demonstrate that viewing, reviewing and diagnosing WSIs of H&E stained FFPE tissue slides using the DPAT (3.3) on Sectra Workstation UniView (DPAT (3.3)-UniView) is non-inferior to glass slide reads using optical (light) microscopy. The imaging pipeline/configuration in the clinical study used was as follows: Aperio GT 450 DX scanner images/SVS image format/ DPAT (3.3)-UniView/Chrome web browser/DellU3223QE display.

b. Technical bench testing to demonstrate that DPAT (3.3) generates identical images in the configurations that were not validated in the clinical study. The Aperio GT 450 DX/SVS/DPAT (3.3)-UniView/Chrome configuration which was the imaging pipeline validated in the clinical study, was used as the reference configuration in the pixelwise comparison study to validate the other 4 configurations as described in section b below.

# a. Clinical Validation Study

A clinical study was conducted to demonstrate that using DPAT (3.3)-UniView for use in primary diagnosis of FFPE tissue sections when used with the Aperio GT $4 5 0 \mathrm { D X }$ scanner, which generated WSIs in the SVS image file format is non-inferior to glass slide reads using optical light microscopy (MSR).

The study included 258 randomly selected cases that represented a diverse mixture of pathologic diagnoses and tissue/organ types. Case slides were scanned on the Aperio GT 450 DX scanner, producing WSIs in the SVS format at $4 0 \mathrm { x }$ magnification. Three (3) reading pathologists (the same pathologists who determined MSR diagnosis) at a single site reviewed all study cases using DPAT (3.3) -UniView on the Microsoft Chrome web browser and a Dell U3223QE monitor per user guide, to determine the WSIR diagnosis. The reading pathologists were masked to the reference diagnoses, their own diagnoses from the previous studies and to other reading pathologist’s study diagnoses. Across the 258 selected cases, all 870 WSIs were successfully reviewed. The range of WSIs reviewed per case was 1 to 34.

The WSIR data from the current study and the existing MSR data (diagnoses, concordance scores and consensus scores) from a previous clinical study (K190332) which had the same study cases and readers as the current study were used to estimate study endpoints.

A minimum of two adjudicators independently assessed concordance (concordant, minor discordance, major discordance) of the WSIR diagnosis against the reference diagnosis using predefined rules. If consensus was not reached between the first 2 adjudicators, a third adjudicator reviewed the study diagnosis against the reference diagnosis. If consensus between 2 of 3 adjudicators was still not reached, then the 3 adjudicators would convene as a panel to come to a consensus for the major discordance status. WSIR diagnosis consensus scores were used to estimate WSIR diagnosis major discordance rate. For MSR diagnoses, the consensus scores generated during the previous clinical study (K190332) were used for this study to estimate MSR diagnosis major discordance rate.

A major discordance was defined as a difference in diagnosis that resulted in a clinically important difference in patient management, whereas a minor discordance would not be associated with a clinically important difference in patient management. The adjudicators’ concordance scores for the same case were compared to determine a consensus score for major discordance status [no major discordance (concordant or minor discordance) or major discordance]. The diagnosis consensus scores were used to estimate WSIR diagnosis major discordance rate.

Study Acceptance Criteria: The primary endpoint of the study was the difference in overall major discordance rates between the 2 modalities [Whole slide image review (WSIR) using DPAT (3.3)-UniView and MSR] when compared to the reference diagnosis (original sign-out pathologic diagnosis) which was defined as the ground truth (GT) diagnosis. The secondary endpoint of the study was the major discordance rate of WSIR diagnosis relative to the reference diagnosis. The acceptance criteria associated with each study endpoint were as follows:

Primary Endpoint: The upper bound of the 2-sided $9 5 \%$ CI of the difference between the overall major discordance rates of WSIR diagnosis and MSR diagnosis when compared to the reference diagnosis shall be $\leq 4 \%$ .

Secondary Endpoints: The upper bound of the 2-sided $9 5 \%$ CI of the major discordance rate between WSIR diagnosis and the reference diagnosis shall be $\leq 7 \%$ .

Adjudication Review: For WSIR, there were 767 study diagnoses reviewed by 2 (primary) adjudicators. No diagnoses were deferred by the adjudicators; therefore, 767 WSIR diagnoses had concordance scores. Of these, consensus on major discordance status was obtained for 736 $( 9 6 . 0 \%$ , 736/767) study diagnoses by 2 adjudicators only; 31 ( $4 . 0 \%$ , 31/767) study diagnoses were transferred to a third adjudicator for review, after which consensus was obtained. No study diagnoses required panel review. Adjudication of MSR diagnoses and generation of consensus scores was conducted during the previous clinical study. All 764 MSR diagnoses were successfully adjudicated and had consensus scores.

Study Results: All 774 case reads $( 2 5 8 \mathrm { c a s e s } \times 3$ reading pathologists) were successfully performed by WSIR. Seven WSIR diagnoses were deferred (cases that could not be diagnosed by the reading pathologists), resulting in 767 WSIR diagnoses sent for adjudication.

All 774 case reads were performed by MSR during the previous clinical study. Ten (10) MSR diagnoses were deferred by the reading pathologists, resulting in 764 MSR diagnoses sent for adjudication. Study results are shown in the table below.

Table 5. Clinical Study Results Based on Major Discordance Rates   

<table><tr><td rowspan=1 colspan=1>Modality</td><td rowspan=1 colspan=1>(n/N)</td><td rowspan=1 colspan=1>Discordance Rate (%)</td><td rowspan=1 colspan=1>95% CI (%)</td></tr><tr><td rowspan=1 colspan=1>WSIRD vs GT</td><td rowspan=1 colspan=1>23/767</td><td rowspan=1 colspan=1>3.00</td><td rowspan=1 colspan=1>(1.64, 5.25)</td></tr><tr><td rowspan=1 colspan=1>MSRD vs GT</td><td rowspan=1 colspan=1>23/764</td><td rowspan=1 colspan=1>3.01</td><td rowspan=1 colspan=1>(1.65, 5.27)</td></tr><tr><td rowspan=1 colspan=1>Difference</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>-0.1</td><td rowspan=1 colspan=1>(-1.71, 1.69)</td></tr></table>

The estimated difference in major discordance rates between the 2 modalities when compared to the reference diagnosis was $- 0 . 0 1 \%$ ( $9 5 \%$ CI: $- 1 . 7 1 \%$ to $1 . 6 9 \%$ ). The upper bound of the $9 5 \%$ CI of the estimated difference in major discordance rates was $1 . 6 9 \%$ which met the predefined acceptance criteria of $\leq 4 \%$ for the primary endpoint. The overall major discordance rate between the WSIR diagnosis and the reference diagnosis did not exceed $7 \%$ ; the upper bound of the $9 5 \%$ CI for the overall estimated major discordance rate for WSIR diagnosis was $5 . 2 5 \%$ , which met the predefined acceptance criteria of $\leq 7 \%$ as shown in the table below.

Table 6. Concordance Rate between WSIR Diagnoses and MSR Diagnoses   

<table><tr><td rowspan=1 colspan=1>Number ofConcordances</td><td rowspan=1 colspan=1>Number of Pairs</td><td rowspan=1 colspan=1>Concordance Rate(%)</td><td rowspan=1 colspan=1>95% ConfidenceInterval</td></tr><tr><td rowspan=1 colspan=1>729</td><td rowspan=1 colspan=1>762</td><td rowspan=1 colspan=1>95.7</td><td rowspan=1 colspan=1>[94.2%, 97.1%]</td></tr></table>

Note: $9 5 \%$ CI was produced using the percentile bootstrapping approach on 5000 bootstrap samples

The major discordance rates for WSIR and MSR diagnoses (relative to the reference diagnosis), and the difference between the two modalities, by each organ type is shown in the table below.

Table 7. Major Discordance Rates for WSIR and MSR Diagnoses by Organ Type   

<table><tr><td colspan="1" rowspan="2">Organ Type</td><td colspan="2" rowspan="1">Major Discordance Rate</td><td colspan="1" rowspan="2">Difference in MajorDiscordance Rates(WSIRD - MSRD)</td></tr><tr><td colspan="1" rowspan="1">WSIRD</td><td colspan="1" rowspan="1">MSRD</td></tr><tr><td colspan="1" rowspan="1">Anus/Perianal</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Appendix</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Bladder</td><td colspan="1" rowspan="1">13.73%</td><td colspan="1" rowspan="1">7.84%</td><td colspan="1" rowspan="1">5.88%</td></tr><tr><td colspan="1" rowspan="1">Brain/Neuro</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">9.38%</td><td colspan="1" rowspan="1">-9.38%</td></tr><tr><td colspan="1" rowspan="1">Breast</td><td colspan="1" rowspan="1">9.26%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">9.26%</td></tr><tr><td colspan="1" rowspan="1">Colorectal</td><td colspan="1" rowspan="1">3.85%</td><td colspan="1" rowspan="1">2.56%</td><td colspan="1" rowspan="1">1.28%</td></tr><tr><td colspan="1" rowspan="1">Endocrine</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">GE Junction</td><td colspan="1" rowspan="1">1.96%</td><td colspan="1" rowspan="1">3.92%</td><td colspan="1" rowspan="1">-1.96%</td></tr><tr><td colspan="1" rowspan="1">Gallbladder</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="2">Organ Type</td><td colspan="2" rowspan="1">Major Discordance Rate</td><td colspan="1" rowspan="2">Difference in MajorDiscordance Rates(WSIRD  MSRD)</td></tr><tr><td colspan="1" rowspan="1">WSIRD</td><td colspan="1" rowspan="1">MSRD</td></tr><tr><td colspan="1" rowspan="1">Gynecological</td><td colspan="1" rowspan="1">1.28%</td><td colspan="1" rowspan="1">6.41%</td><td colspan="1" rowspan="1">-5.13%</td></tr><tr><td colspan="1" rowspan="1">Hernial/Peritoneal</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Kidney, Neoplastic</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">3.70%</td><td colspan="1" rowspan="1">-3.70%</td></tr><tr><td colspan="1" rowspan="1">Liver/Bile Duct</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Lung</td><td colspan="1" rowspan="1">4.76%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">4.76%</td></tr><tr><td colspan="1" rowspan="1">Lymph Node</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Prostate</td><td colspan="1" rowspan="1">2.61%</td><td colspan="1" rowspan="1">3.29%</td><td colspan="1" rowspan="1">-0.68%</td></tr><tr><td colspan="1" rowspan="1">Salivary gland</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">3.85%</td><td colspan="1" rowspan="1">-3.85%</td></tr><tr><td colspan="1" rowspan="1">Skin</td><td colspan="1" rowspan="1">3.57%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">3.57%</td></tr><tr><td colspan="1" rowspan="1">Soft Tissue Tumor</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr><tr><td colspan="1" rowspan="1">Stomach</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td><td colspan="1" rowspan="1">0.00%</td></tr></table>

# b. Bench Testing – Pixelwise comparison study

DPAT (3.3) supports multiple file formats, multiple viewers and multiple browsers, constituting various configurations to be tested. The SVS/UniView/Chrome configuration imaging pipeline was validated in the above clinical study. Therefore, it was used as the reference configuration in the pixelwise comparison study to validate 4 additional configurations specified in the table below.

Table 8: DPAT (3.3) Configurations Tested in the Pixelwise Comparison Testing   

<table><tr><td rowspan=1 colspan=1>Configuration</td><td rowspan=1 colspan=1>Image File format</td><td rowspan=1 colspan=1>Viewer/Browser</td></tr><tr><td rowspan=1 colspan=1>DICOM/IDS7</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>IDS7</td></tr><tr><td rowspan=1 colspan=1>DICOM/UniView/Chrome</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>UniView/Chrome</td></tr><tr><td rowspan=1 colspan=1>SVS/IDS7</td><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>IDS7</td></tr><tr><td rowspan=1 colspan=1>SVS/UniView/Edge</td><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>UniView/Edge</td></tr></table>

A total of 30 FFPE tissue slides from various human anatomic sites such as breast, prostate, gastrointestinal tract, lung, ovary, lymph node, bone, etc. were used in the study. This sample set was different from the sample set used in the clinical study.

The 30 glass slides were scanned with a Leica Aperio GT $4 5 0 \mathrm { D X }$ scanner to generate WSI files in the SVS and DICOM file formats. For each of the 30 slides, 3 regions of interests (ROIs) were manually selected by qualified personnel to represent various features in the tissue samples. Blank or blurry areas were excluded from the ROI selection. The ROIs were captured at $1 0 \mathrm { x }$ and $4 0 \mathrm { x }$ magnification levels.

A total of 4 configurations specified in table 8 above were tested in the study. Each of these configurations represented an imaging pipeline and consisted of the specific file format (SVS or DICOM), viewer (IDS7 or UniView), and browser (Chrome or Edge).

The pixelwise comparison study was conducted in the intended computer environment following the labeling of the subject and predicate devices, including the Dell U3223QE display, which has

3840x2160 pixels. For each configuration, 180 image-pairs (30 slides $^ \ast 3$ ROIs $^ { * } 2$ magnification levels) were tested. For each comparison, screenshots were captured from the subject and predicate devices to form an image-pair. Each image-pair was cropped and registered to be pixelwise comparable. The cropped image included most of the pixels in the image except for those in the viewer-specific user interface areas. The testing data, including the screenshots and cropping/registration information of the 5 configurations were provided in the FDA specific format.

For each image-pair, the pixelwise differences between two images were calculated using the CIEDE2000 color difference metric. Two images were considered to be identical if the 95th percentile of the pixelwise color differences is less than 3 CIEDE2000 $( < 3 ~ \Delta \mathrm { E } _ { 0 0 } )$ . A configuration can be validated if all image-pairs are identical to the reference configuration.

Based on analysis of the testing data, the 4 configurations specified in table 9 below were identical, i.e., $< 3 ~ \Delta \mathrm { E } _ { 0 0 }$ to reference configuration SVS/UniView/Chrome.

Table 9: Pixelwise Testing Results   

<table><tr><td rowspan=1 colspan=1>Configuration</td><td rowspan=1 colspan=1>Image File format</td><td rowspan=1 colspan=1>Viewer/Browser</td><td rowspan=1 colspan=1>Comparison toReference Pipeline</td></tr><tr><td rowspan=1 colspan=1>DICOM/IDS7</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>IDS7</td><td rowspan=1 colspan=1>ΔE=0</td></tr><tr><td rowspan=1 colspan=1>DICOM/UniView/Chrome</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>UniView/Chrome</td><td rowspan=1 colspan=1>ΔE =0</td></tr><tr><td rowspan=1 colspan=1>SVS/IDS7</td><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>IDS7</td><td rowspan=1 colspan=1>ΔE =0</td></tr><tr><td rowspan=1 colspan=1>SVS/UniView/Edge</td><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>UniView/Edge</td><td rowspan=1 colspan=1>ΔE=0</td></tr></table>

# c. Turnaround Time

The purpose of this test was to demonstrate that the turnaround time for rendering of images is acceptable. Turnaround times for loading a new image, image panning and zooming for both UniView and IDS7 were tested as well as opening images from SVS files and DICOM files. Test results for different scenarios met the test acceptance criteria and showed acceptable turnaround time for image loading.

# d. Measurements (area and distance)

The purpose of this test was to demonstrate that DPAT (3.3) accurately shows measurement annotations on scanned WSIs from the Aperio GT $4 5 0 \mathrm { D X }$ scanner. Measurements in Uniview and IDS7 on each of the 2 image file formats SVS and DICOM were evaluated. For each combination (UniView/SVS, UniView/DICOM, IDS7/SVS and IDS7/DICOM), 6 measurements of 3 different lengths in 2 different orientations (3 horizontal and 3 vertical) were performed using the built-in measurement tool using the comparator and the DPAT (3.3). The results showed that the measurement values agreed between the comparator and DPAT (3.3). DPAT (3.3) has been found to perform accurate measurements with respect to its intended use.

# e. Human Factors (Usability) Testing

Human factors study designed around critical user tasks and use scenarios performed by representative users were conducted for previously cleared DPAT (2.2) in K193054. No new human factor study was performed for DPAT (3.3).

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.