# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY

I Background Information:

A 510(k) Number K241273   
B Applicant Paige.AI, Inc.   
C Proprietary and Established Names FullFocus   
D Regulatory Information

<table><tr><td rowspan=1 colspan=1>ProductCode(s)</td><td rowspan=1 colspan=1>Classification</td><td rowspan=1 colspan=1>RegulationSection</td><td rowspan=1 colspan=1>Panel</td></tr><tr><td rowspan=1 colspan=1>QKQ</td><td rowspan=1 colspan=1>Class I</td><td rowspan=1 colspan=1>21 CRF 864.3700  Wholeslide imaging system</td><td rowspan=1 colspan=1>PA - Pathology</td></tr></table>

II Submission/Device Overview:

A Purpose for Submission New device   
B Type of Test: Software only device

III Intended Use/Indications for Use:

A Intended Use(s): See Indications for Use below. B Indication(s) for Use: For In Vitro Diagnostic Use

FullFocus is a software intended for viewing and management of digital images of scanned surgical pathology slides prepared from formalin-fixed paraffin embedded (FFPE) tissue. It is an aid to the pathologist to review, interpret and manage digital images of pathology slides for primary diagnosis. FullFocus is not intended for use with frozen sections, cytology, or non-FFPE hematopathology specimens.

It is the responsibility of a qualified pathologist to employ appropriate procedures and safeguards to assure the quality of the images obtained and, where necessary, use conventional light microscopy review when making a diagnostic decision. FullFocus is intended to be used with the interoperable components specified in the below Table.

Table: Interoperable Components of FullFocus   

<table><tr><td rowspan=1 colspan=1>Scanner Hardware</td><td rowspan=1 colspan=1>Scanner Output fileformat</td><td rowspan=1 colspan=1>Interoperable Displays</td></tr><tr><td rowspan=1 colspan=1>Leica Aperio GT 450 DXscanner</td><td rowspan=1 colspan=1>DICOM, SVS</td><td rowspan=2 colspan=1>Dell UP3017Dell U3023EDell U3223QEJVC-Kenwood JD-C240BN01A</td></tr><tr><td rowspan=1 colspan=1>Hamamatsu NanoZoomerS360MD Slide Scanner</td><td rowspan=1 colspan=1>NDPI</td></tr></table>

# C Special Conditions for Use Statement(s):

Rx - For Prescription Use Only

# IV Device/System Characteristics:

# A Device Description:

FullFocus, version 2.29, is a web-based software-only device that facilitates the viewing and navigating of digitized pathology images of slides prepared from FFPE tissue specimens acquired from FDA cleared digital pathology scanners on FDA cleared displays as specified in the intended use Table above. FullFocus renders these digitized pathology images for review, management, and navigation for pathology primary diagnosis.

Image acquisition is performed using the intended scanner(s), with the operator conducting quality control on the whole-slide images according to the scanner's instructions for use and lab specifications to determine if re-scans are needed.

Once a whole slide image is acquired using the intended scanner and becomes available in the scanner's database file system, a separate medical image communications software (not part of the device) automatically uploads the image and its corresponding metadata to persistent cloud storage. Integrity checks are performed during the upload to ensure data accuracy.

The WSIs undergo intentional compression and are converted into standardized Paige TIFF files when visualized in FullFocus, as shown in Table below. Testing was conducted to ensure that the compressed images maintain fidelity to their original images.

Table 1. WSIs Compression when Visualized in FullFocus   

<table><tr><td rowspan=1 colspan=1>Scanner Hardware</td><td rowspan=1 colspan=1>ScannerOutputFileFormat</td><td rowspan=1 colspan=1>Compression Methods</td></tr><tr><td rowspan=2 colspan=1>Leica Aperio GT 450DX scanner</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>FullFocus uses the WebP image format, configured withquality 85 and method 4</td></tr><tr><td rowspan=1 colspan=1>SVS</td><td rowspan=1 colspan=1>FullFocus uses the AVIF image format, configured withquality 70 and 4:4:4 subsampling</td></tr><tr><td rowspan=1 colspan=1>HamamatsuNanoZoomer S360MDSlide scanner</td><td rowspan=1 colspan=1>NDPI</td><td rowspan=1 colspan=1>FullFocus utilizes the AVIF image file formatcompression which is tailored with settings configured toquality 70 and subsampling 4:4:4</td></tr></table>

The subject device enables the reading pathologist to open a patient case, view the images, and perform actions such as zooming, panning, measuring distances and areas, and annotating images as needed. After reviewing all images for a case, the pathologist will render a diagnosis.

The computer environment for during the use of FullFocus is specified in the Table below:

Table 2. Computer Environment/System Requirements   

<table><tr><td rowspan=1 colspan=1>Environment</td><td rowspan=1 colspan=1>Component</td><td rowspan=1 colspan=1>Minimum Requirements</td></tr><tr><td rowspan=3 colspan=1>Hardware</td><td rowspan=1 colspan=1>Processor</td><td rowspan=1 colspan=1>1 CPU, 2 cores, 1.6 GHz</td></tr><tr><td rowspan=1 colspan=1>Memory</td><td rowspan=1 colspan=1>4 GB RAM</td></tr><tr><td rowspan=1 colspan=1>Network</td><td rowspan=1 colspan=1>Bandwidth of 10 Mbps</td></tr><tr><td rowspan=2 colspan=1>Software</td><td rowspan=1 colspan=1>Operating System</td><td rowspan=1 colspan=1>Windows•  macOS</td></tr><tr><td rowspan=1 colspan=1>Browser</td><td rowspan=1 colspan=1>•  Google Chrome (129.0.6668.90 or higher)Microsoft Edge (129.0.2792.79 or higher)</td></tr></table>

# B Instrument Description Information:

1. Instrument Name: FullFocus

2. Specimen Identification:

The FullFocus device utilizes digital pathology images acquired from Hematoxylin and Eosin (H&E) stained glass slides using the Leica Aperio GT $4 5 0 \mathrm { D X }$ scanner or the Hamamatsu NanoZoomer S360MD Slide scanner. A reading pathologist selects a case (patient) from an external worklist, and the subject device retrieves the corresponding images from external image storage. The scanned images are identified using the specimen identifier previously assigned to the case.

# 3. Specimen Sampling and Handling:

Specimen sampling and handling are conducted independently and prior to the use of the subject device. This process involves obtaining biopsy or resection specimens, which are then processed using standard histology techniques. After H&E staining of the FFPE tissue sections, digital images are generated from the glass slides using the Leica Aperio GT 450 DX Scanner, or the Hamamatsu NanoZoomer S360MD Slide scanner.

4. Calibration: Not applicable

5. Quality Control:

The subject device receives whole-slide images from the Paige image storage system. All WSI files are quality-controlled and acquired in accordance with the scanner’s instructions for use. The subject device incorporates specific quality control measures to ensure the accuracy and completeness of the images. Each pathologist must perform quality checks prior to analyzing pathology images using the subject device. This includes verifying that all scanned slide images have been successfully imported. For each case, the pathologist should review the thumbnails in the pathology image window to confirm that all required slides are present. Additionally, the tissue block and staining information should be manually verified against data from the Laboratory Information System (LIS).

# V Substantial Equivalence Information:

A Predicate Device Name(s): Aperio GT450X; NanoZoomer S360MD Slide scanner system   
B Predicate 510(k) Number(s): K232202; K213883   
C Comparison with Predicate(s):   
1. FDA Guidance “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices". April 20, 2016.   
2. FDA Guidance “Applying Human Factors and Usability Engineering to Medical Devices”. February 3, 2016.   
3. FDA Guidance “Content of Premarket Submissions for Device Software Functions”. June   
14, 2023.   
4. FDA Guidance “Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions”. September 27, 2023.   
5. AAMI TIR 45:2012 - Guidance on the use of AGILE practices in the development of medical device software.   
6. IEC 62304 Edition 1.1 2015-06 CONSOLIDATED VERSION, 13-79. Medical device software – Software life cycle processes.   
7. ISO 14971 Third Edition 2019-12, 5-125, Medical devices – Applications of risk management to medical devices.

<table><tr><td rowspan=1 colspan=1>Device &amp;PredicateDevice(s):</td><td rowspan=1 colspan=3>K241273</td><td rowspan=1 colspan=5>K232202</td><td rowspan=1 colspan=1>K213883</td></tr><tr><td rowspan=1 colspan=1>Device TradeName</td><td rowspan=1 colspan=3>FullFocus</td><td rowspan=1 colspan=5>Aperio GT450X</td><td rowspan=1 colspan=1>NanoZoomer S360MD Slide scanner system</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=8>General Device Characteristic Similarities</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=10 colspan=1>Intended Use/IndicationsFor Use</td><td rowspan=3 colspan=3>For In Vitro Diagnostic UseFullFocus is a software intended for viewingand management of digital images of scannedsurgical pathology slides prepared fromformalin-fixed paraffin embedded (FFPE)tissue. It is an aid to the pathologist to review,interpret and manage digital images ofpathology slides for primary diagnosis.FullFocus is not intended for use with frozensections, cytology, or non-FFPEhematopathology specimens.It is the responsibility of a qualified pathologistto employ appropriate procedures andsafeguards to assure the quality of the imagesobtained and, where necessary, useconventional light microscopy review whenmaking a diagnostic decision. FullFocus isintended to be used with the interoperablecomponents specified in the below Table.Table: Interoperable components ofFullFocus</td><td rowspan=1 colspan=5>The Aperio GT 450 DX is an automated digital slidecreation and viewing system. The Aperio GT450 DX isintended for in vitro diagnostic use as an aid to thepathologist to review and interpret digital images of surgicalpathology slides prepared from formalin-fixed paraffinembedded (FFPE) tissue. The Aperio GT 450 DX is forcreation and viewing of digital images of scanned glassslides that would otherwise be appropriate for manualvisualization by conventional light microscopy.Aperio GT 450 DX is comprised of the Aperio GT 450 DXscanner, which generates images in the Digital Imaging andCommunications in Medicine (DICOM) and in theScanScope Virtual Slide (SVS) file formats, the AperioWebViewer DX viewer, and the displays. The Aperio GT450 DX is intended to be used with the interoperablecomponents specified in Table 1.Table 1: Interoperable components of Aperio GT 450 DX</td><td rowspan=10 colspan=1>The NanoZoomer S360MD Slide scanner system(&quot;NanoZoomer System&quot;) is an automated digitalslide creation, viewing, and management system.The NanoZoomer System is intended for in vitrodiagnostic use as an aid to the pathologist to reviewand interpret digital images of surgical pathologyslides prepared from formalin-fixed paraffinembedded (&quot;FFPE&quot;) tissue. The NanoZoomerSystem is not intended for use with frozen section,cytology, or non-FFPE hematopathology specimens.The NanoZoomer System comprises theNanoZoomer S360MD Slide scanner, theNZViewMD Software and the JVC Kenwood JD-C240BN01A display. The NanoZoomer System isfor creation and viewing of digital images of scannedglass slides that would otherwise be appropriate formanual visualization by conventional lightmicroscopy. It is the responsibility of a qualifiedpathologist to employ appropriate procedures andsafeguards to assure the validity of the interpretationof images obtained using NanoZoomer System.</td></tr><tr><td rowspan=1 colspan=2>ScannerHardware</td><td rowspan=1 colspan=1>ScannerOutputfileformat</td><td rowspan=1 colspan=1>InteroperableViewingSoftware</td><td rowspan=1 colspan=1>InteroperableDisplays</td></tr><tr><td rowspan=2 colspan=2>Aperio GT450 DXscanner</td><td rowspan=2 colspan=1>SVS</td><td rowspan=2 colspan=1>AperioWebViewer DX</td><td rowspan=2 colspan=1>Barco MDPC-8127Dell UP3017Dell U3023EDell U3223QE</td></tr><tr><td rowspan=2 colspan=1>ScannerHardware</td><td rowspan=2 colspan=1>Scannerutputfileformat</td><td rowspan=2 colspan=1>InteroperableDisplays</td></tr><tr><td></td><td rowspan=2 colspan=1>Aperio GT450 DXscanner</td><td rowspan=2 colspan=1>SVS</td><td rowspan=2 colspan=1>Sectra DigitalPathologyModule (3.3)</td><td rowspan=2 colspan=1>Dell U3223QE</td></tr><tr><td rowspan=2 colspan=1>Leica AperioGT 450 DXscanner</td><td rowspan=2 colspan=1>DICOM,SVS</td><td rowspan=4 colspan=1>Dell UP3017Dell U3023EDell U3223QEJVC KenwoodJD-C240BN01A</td><td></td></tr><tr><td rowspan=2 colspan=2>Aperio GT450 DXscanner</td><td rowspan=2 colspan=1>DICOM</td><td rowspan=2 colspan=1>Sectra DigitalPathologyModule (3.3)</td><td rowspan=2 colspan=1>Dell U3223QE</td></tr><tr><td rowspan=2 colspan=1>HamamatsuNanoZoomerS360MDSlide scanner</td><td rowspan=2 colspan=1>NDPI</td></tr><tr><td rowspan=1 colspan=3>The Aperio GT 450 DX</td><td rowspan=2 colspan=2>The Aperio GT 450 DX is not intended for use with frozensection, cytology, or non-FFPE hematopathology specimens.</td></tr><tr><td rowspan=1 colspan=3></td><td rowspan=1 colspan=3>It is the responsibility of</td></tr></table>

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>appropriate procedures and safeguards to assure the validityof the interpretation of images obtained using the Aperio GT450 DX.</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Principle ofOperation</td><td rowspan=1 colspan=1>After WSI images are successfully acquired byusing Aperio GT 450 DX scanner, orHamamatsu NanoZoomer S360MD Slidescanner, the WSI images are stored in thecloud. During review, the pathologist opensWSI images from storage, perform further QCand reads WSI images of the slides to make adiagnosis.</td><td rowspan=1 colspan=1>The Aperio GT 450 DX is a WSI system. The technicianplaces the slides into the Aperio GT 450 DX scanner. TheAperio GT 450 DX scanner automatically loads the slides,takes the micro images, finds the tissues, and scans theslides. The scanner also automatically performs qualitycontrol (QC) and notifies the user of any image quality issueduring the image acquisition. The image data is sent to end-user-provided image storage attached to the local network.During the review, the pathologist opens WSI imagesacquired with the WSI scanner from the image storage,performs further QC, and reads WSI images of the slides tomake a diagnosis.</td><td rowspan=1 colspan=1>The NanoZoomer S360MD Slide scanner system(&quot;NanoZoomer System&quot;) is an automated digitalslide creation, viewing, and management system.The NanoZoomer System is intended for in vitrodiagnostic use as an aid to the pathologist to reviewand interpret digital images of surgical pathologyslides prepared from formalin-fixed paraffinembedded (&quot;FFPE&quot;) tissue. The NanoZoomerSystem is not intended for use with frozen section,cytology, or non-FFPE hematopathology specimens.The system&#x27;s embedded image processing softwareis responsible for image acquisition and theprocessing of individual tiles prior to imagecomposition or stitching. Hamamatsu&#x27;sNZAcquireMD software organizes all WSI tiles intoa single NDPi file, which is a proprietary file format.During the review, the pathologist opens the WSI onthe NZViewMD software to render a diagnosis.</td><td></td></tr><tr><td rowspan=1 colspan=1>SpecimenType</td><td rowspan=1 colspan=1>Digitized surgical pathology slides preparedfrom FFPE tissue</td><td rowspan=1 colspan=1>Same</td><td rowspan=1 colspan=1>Same</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Type ofSoftwareApplication</td><td rowspan=1 colspan=1>Internet browser-based application</td><td rowspan=1 colspan=1>Same</td><td rowspan=1 colspan=1>PC-based installed application</td><td rowspan=2 colspan=1></td></tr><tr><td rowspan=1 colspan=1>ImageManipulationand ReviewFunctions</td><td rowspan=1 colspan=1>Panning, zooming, annotations, andmeasurements</td><td rowspan=1 colspan=1>Same</td><td rowspan=1 colspan=1>Functions for continuous panning and zooming,annotations, distance/area measurements, trackvisited areas, export images, discrete Z-axisdisplacement, and display of diagnostic status ofimages.</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>General Device Characteristic Differences</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>′</td></tr><tr><td rowspan=1 colspan=1>DeviceComponents</td><td rowspan=1 colspan=1>FullFocus image viewing software</td><td rowspan=1 colspan=1>WSI scanner (Aperio GT450 DX scanner), ImageManagement System (Aperio WebViewer DX imageviewing software), Display</td><td rowspan=1 colspan=1>WSI scanner (NanoZoomer S360MD Slide scanner),Image Management System (NZViewMD), Display</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>DiagnosticImage FileFormat</td><td rowspan=1 colspan=1>Leica SVS and DICOM,Hamamatsu NDPI</td><td rowspan=1 colspan=1>Leica SVS and DICOM</td><td rowspan=1 colspan=1>Hamamatsu NDPI</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>End User&#x27;sInterface</td><td rowspan=1 colspan=1>FullFocus</td><td rowspan=1 colspan=1>Aperio WebViewer DX for Leica SVS,Sectra Digital Pathology Module (3.3) for Leica SVS andDICOM</td><td rowspan=1 colspan=1>NZViewMD</td><td rowspan=1 colspan=1></td></tr></table>

# VII Performance Characteristics (if/when applicable):

# A Analytical Performance:

1. Precision/Reproducibility: Not applicable

2. Linearity: Not applicable

3. Analytical Specificity/Interference: Not applicable

4. Accuracy (Instrument): Not applicable

5. Carry-Over: Not applicable

# B Other Supportive Instrument Performance Characteristics Data:

Technical performance testing was conducted with the subject device, FullFocus as specified below.

# 1. Bench Testing - Pixelwise comparison test

FullFocus supports multiple file formats, multiple browsers, and multiple displays, constituting various configurations to be tested. Pixel-wise comparison testing to demonstrate identical image reproduction was conducted to compare WSIs reproduced by the subject device and the comparators as listed in Table 3 below. The subject device was compared to the predicate device’s image review manipulation software (IRMS, as defined in FDA

guidance document, “Technical Performance Assessment of Digital Pathology Whole Slide Imaging Devices” dated April 20, 2016) using the quantitative pixel-wise comparison method. The basis for the comparison was the CIEDE2000 color difference equation, $\Delta \mathrm { E 0 0 }$ . The devices were tested as operating with the intended components, including the scanner, specific file format, image management systems (subject device with the intended browsers, comparator [predicate device IRMS]) and displays, as specified in the Table 3 below.

For each of the 6 configurations in Table 3 below, the device was tested with multiple slides across multiple regions of interest (ROI) at multiple magnification levels, on multiple displays. A total of 30 H&E-stained, FFPE glass slides of normal and tumor tissues from various human anatomical organs were used in the testing. For each configuration, the glass slides were scanned on a corresponding intended scanner to obtain 30 WSIs. For each of the 30 WSIs, 3 ROIs from different locations were selected by qualified personnel to represent various features in the tissue samples. Each ROI was captured at 2 magnification levels (10x, 40x).

The screenshots were captured for each of the intended display while viewing with the subject device and predicate device IRMS. The screenshots were cropped and registered to be pixelwise comparable. The cropped image included most of the pixels in the image except for those in the viewer-specific user interface areas.

For each configuration and each intended display, two sets of images were collected: comparator (predicate device IRMS) and the subject device (FullFocus with the intended browser). Each image set included 180 images that covered all combinations of 30 slides, 3 ROIs and 2 magnification levels. The testing data, including the overview images of the 30 glass slides with annotations of the ROIs, registration/cropping information, and captured images, were provided in the FDA specific format. The above procedure was repeated for each corresponding intended display.

The comparator (predicate device IRMS) image set was used as the reference to compare the subject device image set to determine whether all the 180 image-pairs were identical for each configuration and each intended display. Two images are considered identical if the 95th percentile of the pixelwise differences, computed using the International Commission on Illumination (CIE) color difference metric CIEDE2000 (ΔE00), is less than 3 ΔE00. Testing results showed that the pixelwise differences across all 180 image-pairs per configuration and per intended display were less than 3 ΔE00. The maximum (max), minimum (min), and mean of the 95th percentile $\Delta \mathrm { E 0 0 }$ value were reported in Table 3. Testing results demonstrated that WSIs reproduced by FullFocus are identical to images reproduced by the predicate devices.

Table 3. FullFocus Pixelwise Comparison Testing Results   

<table><tr><td colspan="1" rowspan="1">Scanner</td><td colspan="1" rowspan="1">ImageFileFormat</td><td colspan="1" rowspan="1">SubjectDevice/Browser</td><td colspan="1" rowspan="1">Comparator(Predicatedevice IRMS/Browser)</td><td colspan="1" rowspan="1">Displays</td><td colspan="1" rowspan="1">Results</td></tr><tr><td colspan="1" rowspan="2">Leica AperioGT450DXscanner</td><td colspan="1" rowspan="2">DICOM</td><td colspan="1" rowspan="1">FullFocus/Chrome</td><td colspan="1" rowspan="1">Sectra UniView/Chrome</td><td colspan="1" rowspan="2">Dell UP3017Dell U3023EDellU3223QE</td><td colspan="1" rowspan="1">max (95th percentile ΔE00) = 2.95min (95thpercentile ΔE00) = 1.61mean (95th percentile ΔE00) = 2.44</td></tr><tr><td colspan="1" rowspan="1">FullFocus/Edge</td><td colspan="1" rowspan="1">Sectra UniView/Edge</td><td colspan="1" rowspan="1">max (95thpercentile ΔE00) = 2.95min (95th percentile ΔE00) = 1.61</td></tr><tr><td colspan="1" rowspan="3">−</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="4">JVC-KenwoodJD-C240BN01A</td><td colspan="1" rowspan="1">mean (95thpercentile ΔE00) = 2.44</td></tr><tr><td colspan="1" rowspan="2">SVS</td><td colspan="1" rowspan="1">FullFocus/Chrome</td><td colspan="1" rowspan="1">AperioWebViewerDX/Chrome</td><td colspan="1" rowspan="1">max (95th percentile ΔE00) = 2.90min (95thpercentile ΔE00) = 1.37mean (95thpercentile ΔE00) = 2.46</td></tr><tr><td colspan="1" rowspan="1">FullFocus/Edge</td><td colspan="1" rowspan="1">AperioWebViewerDX/Edge</td><td colspan="1" rowspan="1">max (95th percentile ΔE00) = 2.90min (95thpercentile ΔE00) = 1.37mean (95th percentile ΔE00) = 2.46</td></tr><tr><td colspan="1" rowspan="2">HamamatsuNanoZoomerS360MDSlide scanner</td><td colspan="1" rowspan="2">NDPI</td><td colspan="1" rowspan="1">FullFocus/Chrome</td><td colspan="1" rowspan="1">NZViewMD</td><td colspan="1" rowspan="1">max (95thpercentile ΔE00) = 2.94min (95thpercentile ΔE00) = 1.43mean (95th percentile ΔE00) = 2.17</td></tr><tr><td colspan="1" rowspan="1">FullFocus/Edge</td><td colspan="1" rowspan="1">NZViewMD</td><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">max (95th percentile ΔE00) = 2.94min (95thpercentile ΔE00) = 1.43mean (95th percentile ΔE00) = 2.17</td></tr></table>

# 2. Turnaround Time

The turnaround times of the subject device were measured for the operations of image opening, panning, and zooming for different scenarios. Below acceptance criteria was used:

• $< 1 0$ seconds to load first image in FOV across all images $< 7$ seconds to render the Field of View (FOV) while zooming and panning across all images

Test results for different scenarios met the test acceptance criteria and showed acceptable turnaround time for the intended use of the subject device.

Table 4. FullFocus Turnaround Time Testing Results   

<table><tr><td rowspan=1 colspan=1>Scanner</td><td rowspan=1 colspan=1>Image FileFormat</td><td rowspan=1 colspan=1>SubjectDevice/Browser</td><td rowspan=1 colspan=1>Turnaround Time Results</td></tr><tr><td rowspan=1 colspan=1>Leica Aperio GT450 DX scanner</td><td rowspan=1 colspan=1>DICOM</td><td rowspan=1 colspan=1>FullFocus/ChromeFullFocus/Edge</td><td rowspan=1 colspan=1>The overall median load time(sec) for first image is 1.63, forpanning is 0.93 and zooming is1.86.</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SVs</td><td rowspan=1 colspan=1>FullFocus/ChromeFullFocus/Edge</td><td rowspan=1 colspan=1>The overall median load time(sec) for first image is 1.68, forpanning is 1.03 and zooming2.00.</td></tr><tr><td rowspan=1 colspan=1>HamamatsuNanoZoomerS360MD Slidescanner</td><td rowspan=1 colspan=1>NDPI</td><td rowspan=1 colspan=1>FullFocus/ChromeFullFocus/Edge</td><td rowspan=1 colspan=1>The overall median load time(sec) for first image is 2.27, forpanning is 0.84 and zooming is1.45.</td></tr></table>

# 3. Measurement – distance and area

The length and area measurement accuracy of the subject device was tested across multiple magnification levels. An image of a calibration scale slide with known object sizes was used to verify the measurement accuracy. A series of annotations were created to cover different orientations and different magnification levels in 4 intended browsers. The differences between the actual and reported measurements were calculated for each annotation. The acceptance criteria were as follows: 1) The $1 \mathrm { m m }$ measured line should match the reference value exactly $1 \mathrm { m m } \pm 0 \mathrm { m m }$ and 2). The measured area must match the reference area exactly $0 . 2 \mathrm { ~ x ~ } 0 . 2 \mathrm { ~ m m }$ for a total of $0 . 0 4 \mathrm { m } \mathrm { m } ^ { 2 } \pm 0 \mathrm { m } \mathrm { m } ^ { 2 }$ . Test results showed that the subject device performed accurate measurements of length and area and all line and area measurements compared to the reference value were exactly the same with no error, across multiple magnification settings with respect to its intended use.

# 4. Human Factor (Usability) Testing

Human factors study designed around critical user tasks and use scenarios performed by representative users were conducted for previously cleared FullFocus, version 1.2.1, in K201005, per FDA guidance “Applying Human Factors and Usability Engineering to Medical Devices (2016)”. Human factors validation testing is not necessary as the user interface and workflow remain unchanged.

# VIII Proposed Labeling:

The labeling supports the finding of substantial equivalence for this device.

# IX Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.