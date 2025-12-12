# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYINSTRUMENT ONLY

I. Background Information:

A. 510(k) Number K193054   
B. Applicant Sectra AB   
C. Proprietary and Established Names Sectra Digital Pathology Module   
D. Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QKQ</td><td rowspan=1 colspan=1>Class I</td><td rowspan=1 colspan=1>21 CFR 864.3700</td><td rowspan=1 colspan=1>Pathology</td></tr></table>

II. Submission/Device Overview:

A. Purpose for Submission: New device   
B. Type of Test: Not applicable – software only device

III. Intended Use/Indications for Use:

A. Intended Use(s): See Indications for Use below.

# B. Indication(s) for Use:

For In Vitro Diagnostic Use

Sectra Digital Pathology Module device is a software intended for viewing and management of digital images of scanned surgical pathology slides prepared from formalin-fixed paraffin embedded (FFPE) tissue. It is an aid to the pathologist to review and interpret these digital images for the purposes of primary diagnosis. Sectra Digital Pathology Module is not intended for use with frozen section, cytology, or non-FFPE hematopathology specimens. It is the responsibility of the pathologist to employ appropriate procedures and safeguards to assure the validity of the interpretation of images using Sectra Digital Pathology Module. Sectra Digital Pathology Module is intended for use with Leica’s Aperio AT2 DX scanner and Dell MR2416 monitor.

C. Special Conditions for Use Statement(s): Rx - For Prescription Use Only

IV. Device/System Characteristics:

# A. Device Description:

Sectra Digital Pathology Module (version 2.2) is a software-only device for viewing and manipulating digital pathology images of glass slides obtained from the Aperio AT2 DX scanner on the Dell MR2416 monitor. Sectra Digital Pathology Module may only be used in combination with Sectra Picture Archiving and Communication System (PACS), which consists of Sectra Workstation IDS7 and Sectra Core. Sectra Digital Pathology Module consists of four elements: Pathology Image Window (PIW), Sectra Pathology Server (SPS), Database Engine (SPDB), and Sectra Pathology Import Server (SPIS). The PIW is a web application embedded in Sectra Workstation IDS7 for end users to view and manipulate digital pathology images. The SPS is the main server component for the PIW client. The SPDB stores the metadata required for the SPS. The SPIS is used for importing digital pathology images from the Aperio AT2 DX scanner.

The subject device is operated as follows:

1. The image acquisition is performed using the predicate device, Aperio AT2 DX scanner. The operator performs quality control of the digital slides using ImageScope DX and Dell MR2416 per the instructions of Aperio AT2 DX to determine if re-scans are necessary.   
2. The digital slides are imported by SPIS and automatically assembled as groups of cases. The unaltered images are then sent to the external storage Sectra Core. Sectra Core offers an application programming interface allowing communication between the Sectra Healthcare Server (SHS), which is part of Sectra Core, and the SPS, which is part of the subject device. The image metadata (e.g. pixel size) is stored locally in the SPDB to improve operational performance.   
3. The laboratory technician performs a quality control by using PIW to verify that all images have been imported.

4. The reading pathologist selects a case (patient) from a worklist external to the subject device such as the laboratory information system (LIS) whereby the SPS fetches the associated images from the Sectra Core.

5. The reading pathologist uses the subject device to view the images and is able to perform the following actions, as needed:

a. Zoom and pan the image   
b. Adjust focus (when different focus depths are available)   
c. Measure distances and areas in the image   
d. Annotate images   
e. Choose to view multiple images side by side in a synchronized fashion

After viewing all images belonging to a particular case (patient), the pathologist will make a diagnosis. The diagnosis is documented in another system such as the LIS.

# Minimum System Requirements - Computer Environment

The system requirements are given in Tables 1 through 4 below.

Table 1: Requirements for PIW   

<table><tr><td rowspan=1 colspan=1>Workstation (Host for subject device)</td><td rowspan=1 colspan=1>IDS7</td></tr><tr><td rowspan=1 colspan=1>Operating System</td><td rowspan=1 colspan=1>MS Windows 10 or MS Windows 7 (64 bit)</td></tr><tr><td rowspan=1 colspan=1>CPU</td><td rowspan=1 colspan=1>4-core CPU, 3.6 GHz</td></tr><tr><td rowspan=1 colspan=1>RAM</td><td rowspan=1 colspan=1>8 GB</td></tr><tr><td rowspan=1 colspan=1>Display (Image Window)</td><td rowspan=1 colspan=1>Dell MR2416 monitor</td></tr><tr><td rowspan=1 colspan=1>Graphics board</td><td rowspan=1 colspan=1>NVIDIA 2 GB Quadro P600 or4 GB Quadro P1000</td></tr><tr><td rowspan=1 colspan=1>Network</td><td rowspan=1 colspan=1>1 Gbit/s LAN connection</td></tr><tr><td rowspan=1 colspan=1>3D mouse</td><td rowspan=1 colspan=1>3Dconnexion SpaceMouse Pro</td></tr></table>

Table 2: Requirements for SPDB and SPS   

<table><tr><td>Operating System &amp; Database Engine</td><td></td><td>Windows Server 2016 Std Ed, with SQL Server 2016 SP2 Std Ed Windows Server 2012 R2 Std Ed, with SQL Server 2012 SP4 Std Ed Windows</td></tr><tr><td>.NET Framework</td><td colspan="2">.NET Framework 4.7.1, 4.7.2 or 4.8</td></tr></table>

Table 3: Requirements for SPIS   

<table><tr><td>Operating System</td><td>Windows Server 2016 • Windows Server 2012 R2 (upgrades only) Windows Server 2008 R2 (upgrades • only) Windows 10 Windows 8.1 (upgrades only)</td></tr><tr><td>.NET Framework</td><td>Windows 7 (upgrades only) .NET Framework 4.7.1, 4.7.2 or 4.8</td></tr></table>

Table 4: Recommended Configurations   

<table><tr><td>SPDB and SPS</td><td></td></tr><tr><td>CPU RAM</td><td>8-core CPU, e.g., Intel Xeon 4110 CPU 24 GB RAM</td></tr><tr><td>Disk</td><td>2x 146 GB system disk (mirrored)</td></tr><tr><td>Network</td><td>Gigabit LAN connection</td></tr><tr><td>SPIS</td><td></td></tr><tr><td>CPU</td><td></td></tr><tr><td>RAM</td><td>8-core CPU, e.g. Intel Xeon 4110 CPU 8 GB RAM</td></tr><tr><td>Disk</td><td>146 GB system disk</td></tr><tr><td>Network</td><td></td></tr><tr><td></td><td>Gigabit LAN connection</td></tr></table>

# B. Instrument Description Information:

<table><tr><td rowspan=1 colspan=1>Modes of Operation</td><td rowspan=1 colspan=1>Yes</td><td rowspan=1 colspan=1>No</td></tr><tr><td rowspan=1 colspan=1>Does the applicant&#x27;s device contain the ability to transmit data to a computer,webserver, or mobile device?</td><td rowspan=1 colspan=1>X</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Does the applicant&#x27;s device transmit data to a computer, webserver, or mobile deviceusing wireless transmission?</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>X</td></tr><tr><td rowspan=1 colspan=2>Software</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>FDA has reviewed applicant&#x27;s Hazard Analysis and software development processesfor this line of product types.</td><td rowspan=1 colspan=1>X</td><td rowspan=1 colspan=1></td></tr></table>

1. Instrument Name:

Sectra Digital Pathology Module

2. Specimen Identification:

The Sectra Digital Pathology Module uses digital pathology images obtained from the Aperio AT2 DX scanner of Hematoxylin and Eosin (H&E) stained glass slides. The reading pathologist selects a case (patient) from a worklist external to the subject device whereby the subject device fetches the associated images from the external image storage. The scanned images are identified based on the previously assigned specimen identifier.

3. Specimen Sampling and Handling:

Specimen sampling and handling are performed upstream and independent of the use of the subject device. Specimen sampling includes biopsy or resection specimens which are processed using histology techniques. The FFPE tissue section is H&E stained. Digital images are then obtained from these glass slides using the Aperio AT2 DX scanner.

4. Calibration: Not applicable

5. Quality Control:

The subject device receives quality-controlled images from the scanner. The subject device specific quality control measures are as follows:

• Connect scanner - This test should be performed before connecting the scanner to the subject device in order to verify the on-site integration between the Aperio AT2 Dx scanner and the Sectra Workstation.   
• View pathology images - Every pathologist should perform this test on review workstation before reading pathology images using the subject device to ensure that all scanned slide images have been imported and for every case, view the thumbnails in the pathology image window to verify that each slide that should be in the case is present (manually verifying tissue block and staining information from LIS).

Additional details of the quality control procedures are provided in the device User’s Guide and the Installation Guide.

V. Substantial Equivalence Information:

A. Predicate Device Name(s): Aperio AT2 DX System B. Predicate 510(k) Number(s): K190332 C. Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp; PredicateDevice(s):</td><td colspan="1" rowspan="1">K193054</td><td colspan="1" rowspan="1">K190332</td></tr><tr><td colspan="1" rowspan="1">Device Trade Name</td><td colspan="1" rowspan="1">Sectra Digital PathologyModule</td><td colspan="1" rowspan="1">Aperio AT2 DX System</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristicSimilarities</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use</td><td colspan="1" rowspan="1">Sectra Digital PathologyModule device is asoftware intended forviewing and managementof digital images ofscanned surgical pathologyslides prepared fromformalin-fixed paraffinembedded (FFPE) tissue. Itis an aid to the pathologistto review and interpretthese digital images for thepurposes of primarydiagnosis. Sectra DigitalPathology Module is notintended for use withfrozen section, cytology, ornon-FFPEhematopathologyspecimens. It is theresponsibility of thepathologist to employappropriate procedures andsafeguards to assure thevalidity of theinterpretation of imagesusing Sectra DigitalPathology Module. SectraDigital Pathology Moduleis intended for use withLeica's Aperio AT2 DXscanner, SectraWorkstation IDS7 and DellMR2416 monitor.</td><td colspan="1" rowspan="1">The Aperio AT2 DXSystem is an automateddigital slide creation andviewing system.The Aperio AT2 DXSystem is intended for invitro diagnostic use as anaid to the pathologist toreview and interpret digitalimages of surgicalpathology slides preparedfrom formalin-fixed paraffinembedded (FFPE) tissue.The Aperio AT2 DXSystem is not intended foruse with frozen section,cytology, or non-FFPEhematopathologyspecimens.The Aperio AT2 DXSystem is composed of theAperio AT2 DX scanner,the ImageScope DX reviewapplication and Display.The Aperio AT2 DXSystem is for creation andviewing of digital images ofscanned glass slides thatwould otherwise beappropriate for manualvisualization byconventional lightmicroscopy. It is theresponsibility of a qualifiedpathologist to employappropriate procedures andsafeguards to assure thevalidity of the interpretationof images obtained usingthe Aperio AT2 DXSystem.</td></tr><tr><td colspan="1" rowspan="1">Specimen Type</td><td colspan="1" rowspan="1">Surgical pathology slidesprepared from FFPE tissue(scanned digital images isthe starting point)</td><td colspan="1" rowspan="1">Surgical pathology slidesprepared from FFPE tissue</td></tr><tr><td colspan="1" rowspan="1">Image Storage</td><td colspan="1" rowspan="1">Images are stored in an end</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">user provided imagestorage attached to thelocal network</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Image ManipulationFunctions</td><td colspan="1" rowspan="1">Panning, zooming, gammafunction, annotations, andmeasurements (distance &amp;area)</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">General DeviceCharacteristicDifferences</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Device Components</td><td colspan="1" rowspan="1">Sectra Digital PathologyModule which consistsonly of the image viewingsoftware, SectraWorkstation IDS7, SectraCore</td><td colspan="1" rowspan="1">WSI scanner (Aperio AT2DX scanner), ImageManagement System(ImageScope DXapplication), and colormonitor display</td></tr><tr><td colspan="1" rowspan="1">Principle ofOperation</td><td colspan="1" rowspan="1">After WSI images aresuccessfully acquired byusing Aperio At2 DXscanner, WSI images areimported by SPIS asgroups of cases.The laboratory technicianperforms a quality controlby using PIW to verify thatall images have beenimported. During review,the pathologist selects apatient case and opensWSI images from theSectra Core to read theWSI images and make adiagnosis.</td><td colspan="1" rowspan="1">After conducting QualityControl (QC) on the glassslides per laboratorystandards (e.g., staining,coverslipping, barcodeplacement, etc.), thetechnician loads the slidesinto the Aperio AT2 DXscanner. The scanner scansthe slides and generatesWSI image for each slide.The technician performs QCon scanned WSI images bychecking image data andimage quality. When QC isfailed, the slide will be re-scanned. The acquired WSIimages are stored in an enduser provided image storageattached to the localnetwork. During review, thepathologist opens WSIimages acquired with theAperio AT2 DX scannerfrom the image storage,performs further QC toensure image quality andreads WSI images of theslides to make a diagnosis.</td></tr><tr><td colspan="1" rowspan="1">End User's Interface</td><td colspan="1" rowspan="1">Pathology Image Window</td><td colspan="1" rowspan="1">Aperio ImageScope DX</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">(the client component ofSectra Digital PathologyModule)</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Type of SoftwareApplication</td><td colspan="1" rowspan="1">Web application NativeMS Windows</td><td colspan="1" rowspan="1">Native MS Windows</td></tr></table>

# VI. Standards/Guidance Documents Referenced:

1. Guidance for Industry “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices", dated April 20, 2016.   
2. Special controls under 21 CFR Sec. 864.3700 Whole slide imaging system.   
3. EN ISO 14971:2012 – Medical devices - Application of risk management to medical devices (same as ISO 14971:2007, Corrected version 2007-10-01), Recognition Number: 5-40.   
4. EN 62304:2006 – Medical device software - software life-cycle processes, Recognition Number: 13-79.   
5. EN ISO 62366-1:2015 – Application of usability engineering to medical devices, Recognition Number: 5-114.

VII. Performance Characteristics (if/when applicable):

A. Analytical Performance:

1. Precision/Reproducibility: Not applicable

2. Linearity: Not applicable

3. Analytical Specificity/Interference: Not applicable

4. Accuracy (Instrument): Not applicable

5. Carry-Over: Not applicable

# B. Other Supportive Instrument Performance Characteristics Data:

Technical performance testing for Sectra Digital Pathology Module device was performed. The new device was compared to the image management software component of the predicate device. The following testing was performed:

Pixel-wise comparison with the predicate device including zooming and panning operations across multiple tiles and vertical/horizontal stitching seams The equivalence between the subject and predicate image review manipulation software (IRMS, as defined in the FDA guidance titled “Guidance for Industry “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices", dated April 20, 2016 [TPA guidance, IV(A)(9)] was supported by bench testing data based on pixel-level comparison. The subject IRMS was tested as operating with the intended components, including the scanner, image management system and display. The scanner color profile embedded in the whole slide image (WSI) file as well as the display color profile associated with the intended display were included in the tests. WSI files from 30 FFPE tissue glass slides from different anatomic locations that were H&E stained were used as the test input. For each region of interest (ROI), the differences between the views generated by the subject and predicate IRMS were evaluated with the 1976 International Commission on Illumination (CIE) color difference metric $\Delta \mathrm { E }$ for each corresponding pixel pair. The two views generated by the subject and predicate IRMS were adjusted and registered by using only the graphical user interface without image processing. The test cases of ROIs included relevant biological features at different magnification levels such as $2 0 \mathrm { x }$ and $4 0 \mathrm { x }$ . Horizontal/vertical stitching seams between the tiles were included in the ROIs when possible. For each ROI, zooming to an odd magnification level and panning across multiple tiles that require interpolated rendering were also tested. The average color difference of all pixels within each ROI was reported. The image data of all ROIs were also provided for verification. The test results demonstrated that the $9 9 ^ { \mathrm { t h } }$ percentile of the difference is below $2 . 0 6 \Delta \mathrm { E }$ . The subject device has been found to adequately reproduce digital pathology images at the pixel level with respect to its intended use.

b. Turnaround Time for the image to be fully loaded while opening a slide from a medical device data system (MDDS) and for panning/zooming

Comparison with predicate device: The predicate device ImageScopeDX has the following reported turnaround times: “should not take longer than 7 secs till the image is fully loaded while opening a slide from a MDDS." and "Panning on the image should not take longer than 0.5 sec in order to load and show all image data.” The turnaround times for opening an image and panning have been measured in the subject device. The results are similar to that of the predicate device ImageScopeDX.

Turnaround time zooming and panning: Long-time running performance test simulating normal usage: A long-time running client test simulating normal end user behavior, measuring performance and executing for at least 6 hours. This test showed no signs of any memory leak or performance issues. The subject device has been found to have an acceptable turnaround time with respect to its intended use.

# c. Measurements – area and distance

Measurement accuracy has been verified using a test image containing objects of known sizes. The following set of tests were used to validate the measurement accuracy of the subject device.

Comparison with predicate device: The same measurements are performed using the subject device and using the Predicate device ImageScopeDX. The results are verified to correspond.

Measurements verified using calibration slide with known distances: An image of a calibration slide with known distances was used to verify the measurement accuracy of the subject device. Test results showed that the subject device performed accurate measurements with respect to its intended use.

# d. Human Factors Testing

Human factors study designed around critical user tasks and use scenarios performed by representative users were conducted. A systematic evaluation of task-based usability including critical tasks required for operation of the device were evaluated at multiple sites using multiple users. All tasks associated with reviewing and reporting results for cases including confirmation that all slides belonging to specific cases are reviewed before reporting results, were included in the study. After having completed all the tasks, all the participants were asked a set of overall satisfaction questions followed by the System Usability Scale (SUS) questionnaire. Overall, the results of the human factors testing were acceptable.

# VIII. Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX. Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.