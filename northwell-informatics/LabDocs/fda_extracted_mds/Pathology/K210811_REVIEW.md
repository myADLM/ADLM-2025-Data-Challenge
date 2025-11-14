# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATIONDECISION SUMMARYINSTRUMENT ONLY

I Background Information:

A 510(k) Number K210811   
B Applicant Inspirata, Inc.   
C Proprietary and Established Names Dynamyx Digital Pathology Software   
D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QKQ</td><td rowspan=1 colspan=1>Class II</td><td rowspan=1 colspan=1>21 CFR 864.3700 - WholeSlide Imaging System</td><td rowspan=1 colspan=1>PA - Pathology</td></tr></table>

II Submission/Device Overview:

A Purpose for Submission: New device.   
B Type of Test: Not applicable – software only device.

III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below. B Indication(s) for Use:

Dynamyx Digital Pathology Software is intended for viewing and management of digital images of scanned surgical pathology slides prepared from formalin-fixed, paraffin-embedded (FFPE) tissue. It is an aid to the pathologist to review and interpret these digital images for the purposes of primary diagnosis.

Dynamyx Digital Pathology Software is not intended for use with frozen section, cytology, or non-FFPE hematopathology specimens.

It is the responsibility of the pathologist to employ appropriate procedures and safeguards to assure the validity of the interpretation of images using Dynamyx Digital Pathology Software.

The Dynamyx Digital Pathology Software consists of the Installed Pathologist Client and the Pathologist Workstation Web Client. The Installed Pathologist Client is intended for use with Leica’s Aperio AT2 DX scanner and Dell MR2416 monitor as well as Philips’ Ultra Fast Scanner and Philips PP27QHD monitor. The Pathologist Workstation Web Clinent is intended for use with Philips Ultra Fast Scanner and Philips PP27QHD monitor.

C Special Conditions for Use Statement(s):

Rx - For Prescription Use Only

# IV Device/System Characteristics:

# A Device Description:

Dynamyx Digital Pathology Software is a client-server software device used for importing, displaying, navigating, and annotating whole slide images obtained from the Leica Aperio AT2 DX scanner or the Philips IntelliSite Pathology Solution (PIPS) Ultra-Fast Scanner (UFS).

Whole slide images are created by scanning glass microscope slides using a digital slide scanner which are then imported into the Dynamyx Digital Archive server. Dynamyx uses the image decoding libraries licensed by Leica and Philips for the native images. Dynamyx then uses lossless compression to send the image to the Dynamyx viewers.

Whole slide images are viewed in the Dynamyx image viewer window by pathologists for the purposes of making a primary diagnosis. The pathologist can also navigate (pan and zoom) and annotate the images.

Dynamyx incorporates typical histology/pathology workflow and is operated as follows:

1. The subject device receives whole slide images from the scanner and extracts a copy of the images’ metadata. The unaltered images are then sent to the external image storage (Digital Archive). A copy of the image metadata (e.g., the pixel size) is stored in the subject device’s database to increase the operational performance (e.g., response times) of Dynamyx.   
2. Whole slide images are reviewed first by the scanning technician such as a histologist to confirm image quality and initiate any slide rescans as necessary prior to being viewed by pathologists. The digital slide review quality control (QC) status determined by the scanning technician indicates which whole slide images have been reviewed and have passed QC. The QC status is available to the reading pathologist.

3. The reading pathologist selects a patient case from a selected worklist within Dynamyx whereby the case images are retrieved from the digital archive.

4. The reading pathologist uses Dynamyx to view and perform the following actions on the displayed image:

a. Zoom and pan the image   
b. Adjust the apparent image observed magnification level   
c. Measure distances and areas   
d. Annotate images and cases

5. The above steps are repeated as required.

After viewing all images, the pathologist will render a diagnosis which is documented in a laboratory information system.

# Minimum System Requirements - Computer Environment

The system requirements are given in Tables 1 through 2d below.

Table 1: WSI scanners and displays that can be used with Dynamyx Digital Pathology Software   

<table><tr><td rowspan=1 colspan=1>Manufacturer</td><td rowspan=1 colspan=1>Model</td></tr><tr><td rowspan=2 colspan=1>Philips Medical Systems Nederland B.V.</td><td rowspan=1 colspan=1>Scanner: Ultra-Fast Scanner (UFS)</td></tr><tr><td rowspan=1 colspan=1>Display: MMPC-4127F1/PP27QHD</td></tr><tr><td rowspan=2 colspan=1>Leica Biosystems Imaging, Inc.</td><td rowspan=1 colspan=1>Scanner: Aperio AT2 DX Slide</td></tr><tr><td rowspan=1 colspan=1>Display: MR2416 (Dell)</td></tr></table>

Note: Philips PP27QHD monitor must be used with Philips Ultra-Fast Scanner and Dell MR2416 monitor must be used with Leica Aperio AT2 DX Scanner. The monitors are not interchangeable.

Table 2a: Computer environment minimum requirements for Dynamyx Digital Pathology Software, Dynamyx Server   

<table><tr><td colspan="1" rowspan="6">Hardware</td><td colspan="1" rowspan="1">Server</td><td colspan="1" rowspan="1">vCPU</td><td colspan="1" rowspan="1">Memory</td><td colspan="1" rowspan="1">Drives</td></tr><tr><td colspan="1" rowspan="1">Workflow Server</td><td colspan="1" rowspan="1">2 cores</td><td colspan="1" rowspan="1">Total - 8 GB</td><td colspan="1" rowspan="1">C Drive - 200 GB</td></tr><tr><td colspan="1" rowspan="1">SQL Server</td><td colspan="1" rowspan="1">2 cores</td><td colspan="1" rowspan="1">Total - 8 GB</td><td colspan="1" rowspan="1">C Drive - 200 GBE Drive - 600 GBF Drive - 600 GB</td></tr><tr><td colspan="1" rowspan="1">Digital Archive Server</td><td colspan="1" rowspan="1">8 cores</td><td colspan="1" rowspan="1">Total - 16 GB</td><td colspan="1" rowspan="1">C Drive - 200 GBE Drive - 200 GBF Drive - Image Store(Drive of appropriate size)</td></tr><tr><td colspan="1" rowspan="1">Web Server</td><td colspan="1" rowspan="1">2 cores</td><td colspan="1" rowspan="1">Total - 8 GB</td><td colspan="1" rowspan="1">C Drive - 200 GBE Drive - 25 GB</td></tr><tr><td colspan="1" rowspan="1">Job Agent Server</td><td colspan="1" rowspan="1">4 cores</td><td colspan="1" rowspan="1">Total - 8 GB</td><td colspan="1" rowspan="1">C Drive - 200 GB</td></tr><tr><td colspan="1" rowspan="2">Software</td><td colspan="1" rowspan="1">Component</td><td colspan="1" rowspan="1">Version</td><td colspan="1" rowspan="1">Comments</td></tr><tr><td colspan="1" rowspan="1">Database</td><td colspan="1" rowspan="1">SQL Server 2016 or 2019 Latest patches recommended</td><td colspan="1" rowspan="1">SQL Server 2016 or 2019 Latest patches recommended</td></tr></table>

Table 2b: Computer environment minimum requirements for Dynamyx Digital Pathology Software, Histology Workstation   

<table><tr><td rowspan=7 colspan=1>Hardware</td><td rowspan=1 colspan=1>Component</td><td rowspan=1 colspan=1>Specifications/Application</td><td rowspan=1 colspan=1>Comments</td></tr><tr><td rowspan=1 colspan=1>Processor</td><td rowspan=1 colspan=1>Intel i5 or greater</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Memory</td><td rowspan=1 colspan=1>8 GB RAM</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Internal Storage</td><td rowspan=1 colspan=1>7200 RPM or faster disks orSSD</td><td rowspan=1 colspan=1>Space requirements arenominal (&lt;10GB)</td></tr><tr><td rowspan=1 colspan=1>Network Connectivity</td><td rowspan=1 colspan=1>100 Mbps Full Duplex</td><td rowspan=1 colspan=1>1Gbps preferred</td></tr><tr><td rowspan=1 colspan=1>Video Adapter</td><td rowspan=1 colspan=1>Web GL compatible</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Display</td><td rowspan=1 colspan=1>If Leica scanner, then use DellMR2416 displayIf Philips scanner, then usePP27QHD display</td><td rowspan=1 colspan=1>Required for Image QCreview</td></tr><tr><td rowspan=1 colspan=1>Software</td><td rowspan=1 colspan=1>Operating System</td><td rowspan=1 colspan=1>Windows 10</td><td rowspan=1 colspan=1>Latest patches recommended</td></tr></table>

Table 2c: Computer environment minimum requirements for Dynamyx Digital Pathology Software, Pathology Workstation (Web based)   

<table><tr><td rowspan=7 colspan=1>Hardware</td><td rowspan=1 colspan=1>Component</td><td rowspan=1 colspan=1>Specification/Application</td><td rowspan=1 colspan=1>Comments</td></tr><tr><td rowspan=1 colspan=1>Processor</td><td rowspan=1 colspan=1>Intel i5 or greater</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Memory</td><td rowspan=1 colspan=1>8 GB RAM</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Internal Storage</td><td rowspan=1 colspan=1>N/A</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Network Connectivity</td><td rowspan=1 colspan=1>100 Mbps Full Duplex</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Video Adapter</td><td rowspan=1 colspan=1>Web GL compatible</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Display</td><td rowspan=1 colspan=1>If Leica scanner, then use DellMR2416 displayIf Philips scanner, then usePP27QHD display</td><td rowspan=1 colspan=1>Required for Diagnostic Use(Dx)</td></tr><tr><td rowspan=2 colspan=1>Software</td><td rowspan=1 colspan=1>Operating System</td><td rowspan=1 colspan=1>Windows 10</td><td rowspan=1 colspan=1>Latest patches recommended</td></tr><tr><td rowspan=1 colspan=1>Browser</td><td rowspan=1 colspan=1>Chrome</td><td rowspan=1 colspan=1>Latest version of browser isrecommended</td></tr></table>

Table 2d: Computer environment minimum requirements for Dynamyx Digital Pathology Software, Pathology Workstation (installed)   

<table><tr><td rowspan=7 colspan=1>Hardware</td><td rowspan=1 colspan=1>Component</td><td rowspan=1 colspan=1>Specification</td><td rowspan=1 colspan=1>Comments</td></tr><tr><td rowspan=1 colspan=1>Processor</td><td rowspan=1 colspan=1>Intel i5 or greater</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Memory</td><td rowspan=1 colspan=1>8 GB RAM</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Internal Storage</td><td rowspan=1 colspan=1>7200 RPM or faster disks orSSD</td><td rowspan=1 colspan=1>Space requirements arenominal (&lt;10GB)</td></tr><tr><td rowspan=1 colspan=1>Network Connectivity</td><td rowspan=1 colspan=1>100 Mbps Full Duplex</td><td rowspan=1 colspan=1>1Gbps preferred</td></tr><tr><td rowspan=1 colspan=1>Video Adapter</td><td rowspan=1 colspan=1>Web GL compatible</td><td rowspan=1 colspan=1>N/A</td></tr><tr><td rowspan=1 colspan=1>Display</td><td rowspan=1 colspan=1>If Leica scanner, then use DellMR2416 displayIf Philips scanner, then usePP27QHD display</td><td rowspan=1 colspan=1>Required for Diagnostic Use(Dx)</td></tr><tr><td rowspan=1 colspan=1>Software</td><td rowspan=1 colspan=1>Operating System</td><td rowspan=1 colspan=1>Windows 10</td><td rowspan=1 colspan=1>Latest patches recommended</td></tr></table>

# B Instrument Description Information:

1. Instrument Name: Dynamyx Digital Pathology Software

2. Specimen Type: Surgical pathology slides prepared from FFPE tissue

3. Specimen Sampling and Handling:

Specimen sampling and handling are performed upstream and independent of the use of the subject device. Specimen sampling includes biopsy or resection specimens which are processed using histology techniques. The FFPE tissue section is H&E stained. Digital images are them obtained from these glass slides using the PIPS UFS or Leica Aperio AT2 DX Slide Scanner.

4. Calibration: Not applicable

5. Quality Control:

When used as part of the Philips IntelliSite Pathology Solution (PIPS) system, the following QC procedure is used: The scanning technician views slide macro images on the Philips’

Ultra-Fast Scanner interface to confirm all tissue is contained in the scanned area and then uses the Dynamyx Digital Pathology Software to confirm the scanned image quality (e.g., focus, color, stitch errors, missing tissue). The QC status is available to pathologist.

When used with the Leica Aperio AT2 DX System, the following QC procedure is used: The scanning technician views the slide macro image on the Leica system’s interface to confirm all tissue is contained in the scanned area and then uses the Dynamyx Digital Pathology Software to confirm the scanned image quality (e.g., focus, color, stitch errors, missing tissue). The QC status is available to pathologist.

Refer to the Dynamyx Digital Pathology Software user guide for additional information.

# V Substantial Equivalence Information:

A Predicate Device Name(s):

Philips IntelliSite Pathology Solution (PIPS) Aperio AT2 DX System

B Predicate 510(k) Number(s):

DEN160056   
K190332

# C Comparison with Predicate(s):

<table><tr><td colspan="1" rowspan="1">Device &amp;PredicateDevice(s):</td><td colspan="1" rowspan="1">K210811</td><td colspan="1" rowspan="1">DEN160056</td><td colspan="1" rowspan="1">K190332</td></tr><tr><td colspan="1" rowspan="1">Device TradeName</td><td colspan="1" rowspan="1">Dynamyx Digital PathologySoftware</td><td colspan="1" rowspan="1">Philips IntelliSitePathology Solution (PIPS)</td><td colspan="1" rowspan="1">Leica Aperio AT2 DXSystem</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="2" rowspan="1">General Device Characteristics: Similarities</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Intended Use/Indications For Use</td><td colspan="1" rowspan="1">Dynamyx Digital PathologySoftware isintended for viewing andmanagement of digitalimages of scanned surgicalpathology slides preparedfrom formalin fixed,paraffin embedded (FFPE)tissue.It is an aid to thepathologist to review</td><td colspan="1" rowspan="1">The Philips IntelliSitePathology Solution (PIPS)is an automated digitalslide creation, viewing,and management system.The PIPS is intended for invitro diagnostic use as anaid to the pathologist toreview and interpretdigital images of surgicalpathology slides preparedfrom formalin-fixed</td><td colspan="1" rowspan="1">The Leica Aperio AT2DX System is anautomated digital slidecreation and viewingsystem. The Leica AperioAT2 DX System isintended for in vitrodiagnostic use as an aid tothe pathologist to reviewand interpret digitalimages of surgicalpathology slides preparedfrom formalin-fixed</td></tr><tr><td colspan="1" rowspan="3"></td><td colspan="1" rowspan="3">and interpret these digitalimages for the purposes ofprimary diagnosis.Dynamyx Digital PathologySoftware is not intended foruse with frozen section,cytology, or non-FFPEhematopathologyspecimens.It is the responsibility of thepathologist to employappropriate procedures andsafeguards to assure thevalidity of the interpretationof images using DynamyxDigital Pathology Software.The Dynamyx DigitalPathology Software consistsof the Installed PathologistClient and the PathologistWorkstation Web Client.The Installed PathologistClient is intended for usewith Leica's Aperio AT2DX scanner and DellMR2416 monitor as well asPhilips' Ultra Fast Scannerand Philips PP27QHDmonitor. The PathologistWorkstation Web Clinent isintended for use withPhilips' Ultra Fast Scannerand Philips PP27QHDmonitor.</td><td colspan="2" rowspan="2">paraffin embedded (FFPE)tissue. The PIPS is notintended for use withfrozen section, cytology, ornon-FFPEhematopathologyspecimens.The PIPS comprises theImage ManagementSystem (IMS), the UltraFast Scanner (UFS) andDisplay. The PIPS is forcreation and viewing ofdigital images of scannedglass slides that wouldotherwise be appropriatefor manual visualization byconventional lightmicroscopy. It is theresponsibility of aqualified pathologist toemploy appropriateprocedures and safeguards</td><td colspan="1" rowspan="3">paraffin embedded(FFPE) tissue. TheLeica Aperio AT2 DXSystem is not intended foruse with frozen section,cytology, or non-FFPEhematopathologyspecimens.The Leica Aperio AT2DX System is composedof the Leica Aperio AT2DX scanner, theImageScope DX reviewapplication and Display.The Leica Aperio AT2DX System is for creationand viewing of digitalimages of scanned glassslides that wouldotherwise, be appropriatefor manual visualizationby conventional lightmicroscopy. It is theresponsibility of aqualified pathologist toemploy appropriateprocedures and safeguardsto assure the validity ofthe interpretation ofimages obtained usingthe Leica Aperio AT2 DXSystem.</td></tr><tr><td colspan="1" rowspan="1">otherwise</td></tr><tr><td colspan="2" rowspan="1">to assure the validity of theinterpretation of imagesobtained usingPIPS.</td></tr><tr><td colspan="1" rowspan="1">Specimen Type</td><td colspan="1" rowspan="1">Surgical pathology slidesprepared fromFFPE tissue</td><td colspan="2" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Image Storage</td><td colspan="1" rowspan="1">Images are stored in enduser provided image storageattached to the localnetwork</td><td colspan="2" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">ImageManipulationFunctions</td><td colspan="1" rowspan="1">Panning, zooming, imageadjustments, annotations,and distance/areameasurements</td><td colspan="2" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Image Review andDiagnosis</td><td colspan="1" rowspan="1">During review, thepathologist opens WSI</td><td colspan="2" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">images acquired with theWSI scanner from theimage storage, performsfurther QC and interpretsthe WSI images to make adiagnosis</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Diagnostic Statusof Images</td><td colspan="1" rowspan="1">Displays a visual indicatorfor thediagnostic status of animage</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">User Interface</td><td colspan="1" rowspan="1">Full-featured image viewerwith integrated case listcontaining slidethumbnails</td><td colspan="1" rowspan="1">Same</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="4" rowspan="1">General Device Characteristic: Differences</td></tr><tr><td colspan="1" rowspan="1">DeviceComponents</td><td colspan="1" rowspan="1">Dynamyx digital pathologysoftware</td><td colspan="1" rowspan="1">Ultra-Fast Scanner (UFS),Image ManagementSystem (IMS), Display</td><td colspan="1" rowspan="1">Aperio AT2 DX scanner,the ImageScope DXreview application andDisplay</td></tr></table>

# VI Standards/Guidance Documents Referenced:

1. Guidance for Industry “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices", dated April 20, 2016   
2. ANSI AAMI IEC 62304:2006 & A1:2016 - Medical device software - Software life cycle processes   
3. ANSI AAMI IEC 62366-1:2015+AMD1:2020 – Application of usability engineering to medical devices   
4. ANSI AAMI ISO 14971: 2019 – Applications of risk management to medical devices   
5. AAMI TIR 45:2012 - Guidance on the use of AGILE practices in the development of medical device software

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

1. Precision/Reproducibility: Not applicable.   
2. Linearity: Not applicable.

3. Analytical Specificity/Interference: Not applicable.

4. Accuracy (Instrument): Not applicable.

5. Carry-Over: Not applicable.

# B Other Supportive Instrument Performance Characteristics Data:

Technical performance testing for Dynamyx Digital Pathology Software device was performed. The new device was compared to the Image Management Software (IMS) component of the Philips PIPS device and the ImageScope DX viewer software of Leica Aperio AT2 DX System. The following testing was performed:

a. Pixel-wise comparison with the predicate device including zooming and panning operations

The equivalence between the subject and predicate image review manipulation software (IRMS, as defined in the FDA guidance titled “Guidance for Industry “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices", dated April 20, 2016 [TPA guidance, $\mathrm { I V } ( \mathrm { A } ) ( 9 ) ]$ was supported by bench testing data based on pixel-level comparison. The subject IRMS was tested as operating with the intended components, including the scanner, image management system and display. Scanned images from 33 FFPE tissue glass slides from different anatomic locations were used as the test input. For each region of interest (ROI), the differences between the views generated by the subject and predicate IRMS were evaluated with the 1976 International Commission on Illumination (CIE) color difference metric $\Delta \mathrm { E }$ for each corresponding pixel pair. The two views generated by the subject and predicate IRMS were adjusted and registered by using only the graphical user interface without image processing. The test cases of ROIs included relevant biological features at different magnification levels such as 40x, 20x and 10x. Horizontal/vertical stitching seams between the tiles were included in the ROIs when possible.

Sixty image pairs at 40x, 20x, and $1 0 \mathrm { x }$ were used to test Dynamyx Digital Pathology Software Installed Pathologist Client against the predicate Leica AT2 DX. Similarly, sixty image pairs at $4 0 \mathrm { x }$ and $2 0 \mathrm { x }$ were used to test Dynamyx Digital Pathology Software Installed Pathologist Client against the predicate Philips PIPS. In addition, sixty image pairs at $4 0 \mathrm { x }$ and $2 0 \mathrm { x }$ were used to test Dynamyx Digital Pathology Software Pathologist Workstation Web Client running in the Chrome browser against Philips PIPS.

The color differences of all pixels within each ROI were reported. The image data of all ROIs were also provided for verification. The test results demonstrated that all image pairs are identical with zero ΔE. The subject device has been found to adequately reproduce digital pathology images at the pixel level with respect to its intended use.

# b. Turnaround Time

Turnaround time test was performed to verify the streaming indicator functionality and to measure the turnaround time for initial image load, panning via mouse drag and zooming with 10 concurrent users using Leica Aperio AT2 DX scanner images and Philips UFS images. Test results are acceptable.

# c. Measurement Accuracy

Measurement accuracy testing was performed to verify the calculated measurement for each annotation (e.g., length and area) is accurate to within $5 \%$ of the reference measurement using a certified micron scale image created using a Leica Aperio AT2 DX scanner and a Philips UFS. Test results showed that the subject device performed accurate measurements with respect to its intended use.

# d. Human Factors (Usability) Testing

Formative and summative usability testing was conducted on the Dynamyx Pathology Workstation and the Histologist Workstation interfaces in accordance with FDA Guidance on “Applying Human Factors and Usability Engineering to Medical Devices.

A systematic evaluation of task-based usability including critical tasks required for operation of the device were evaluated at multiple sites using multiple users. All tasks associated with reviewing and reporting results for cases including confirmation that all slides belonging to specific cases are reviewed before reporting results, were included in the study. Overall, the results of the human factors testing were acceptable.

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.