# 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION DECISION SUMMARY

A. 510(k) Number: k092333   
B. Purpose for Submission: Addition of new assays on a cleared device   
C. Manufacturer and Instrument Name: BioImagene PATHIAMTM System with iScan for p53 and Ki-67   
D. Type of Test or Tests Performed: Computer-assisted image analyzer for Ki-67 and p53 nuclear proteins detected by immunohistochemistry   
E. System Descriptions: 1. Device Description: The PATHIAMTM System with iScan is a complete system for image acquisition and image analysis by assessment of shape, size, and density of a digital image of a specimen.

In the current application, the system provides a quantitative assessment of p53 or Ki67 staining intensity in the fields chosen by a pathologist, and displays a score, which can be reviewed by the pathologist as he/she views the digital image of the selected field. The system software makes no independent interpretations of the data. PATHIAMTM employs several quality assurance algorithms to assure that only readable images are processed by the software.

Samples are obtained as formalin-fixed, paraffin-embedded tissue blocks. Histologic sections are prepared and mounted onto glass slides. Slides are reacted with either Ki67 or p53 primary antibodies, using validated methods. Slides are visualized using diaminobenzidine (DAB), again using validated methods. Prepared slides are loaded into the iScan scanner and scanned. The resulting digital images are reviewed by the pathologist on a computer monitor, and appropriate fields of view (FOVs) are then selected for analysis by the PATHIAMTM software. The PATHIAMTM software produces a “percent positive” result for the specific immunohistochemical study (Ki67 or p53), and the pathologist has the choice of accepting the result or entering his/her own score.

2. Principles of Operation:

A. System Overview: The PATHIAM™ System is an instrument and software system designed to assist the qualified pathologist in the consistent quantitative assessment of protein expression in immunohistochemically stained histologic sections from formalin-fixed, paraffin-embedded normal and neoplastic tissues. The system consists of a slide scanner (iScan), computer, monitor, keyboard, mouse, image analysis algorithms for specific immunohistochemical markers, and software with a Windows web browser-based user interface. PATHIAMTM is a web-based, end-to-end digital pathology software solution that allows pathology labs to acquire, manage, view, analyze, share, and report on digital images of pathology specimens. Using the PATHIAMTM software, the pathologist can view digital images at various magnifications, add

annotations, make measurements, perform image analysis, and generate reports.

B. Hardware: The iScan slide scanning device captures digital images of formalin-fixed, paraffin-embedded tissues that are suitable for storage and viewing. The device includes a digital slide scanner, racks for loading glass slides, computer, scanner software, keyboard, mouse and monitor.

C. Software: The PATHIAMTM software is designed to complement the routine workflow of a qualified pathologist in the review of immunohistochemically stained histologic slides. It allows the user to select fields of view (FOVs) in the digital image for analysis and provides quantitative data on these FOVs to assist with interpretation. The software makes no independent interpretations of the data and requires competent human intervention at all steps in the analysis process.

D. Assay specific Overview:

PATHIAMTM employs image analysis techniques to obtain Ki-67 or p53 scores. Pre-defined parameters are used to obtain Ki-67 or p53 scores. The identification of the nucleus is carried out automatically by the image analysis algorithms. The steps involved in the analysis algorithms are:

a. Enhancing the image. This process increases the contrast to make the image more suitable for analysis.   
b. Identifying the epithelial area. The epithelial area is the region of the image where there is the possibility of epithelial cells being present.   
c. Identifying the nucleus.   
d. Classifying the cells based on extent, intensity, and thickness of nuclear staining.   
e. Computing the score.

E. Principal of Operation

After the initial image quality check, the algorithm goes through the following steps before generating the analysis results:

1. Field of View (FOV) identification: The algorithm separates the tissue area from the background such that only the tissue area is processed in the following steps.

2. Preprocessing: The algorithm generates two images after preprocessing. One of them is a contrast stretched image, and the other is an image with each of the tissue areas of interest (AOI) pixels classified as stained or non-stained.

3. Segmentation: This processing step consists of extracting the objects of interest from the image. In the current applications, the objects of interest are epithelial cell nuclei. These are separated out from the rest of the identified objects using morphological properties, such as size and shape.

4. Classification: The segmented nuclei are classified as stained cells or nonstained cells based on the percentage of stained pixels within them.

5. Scoring / Grading: Based on the classification, an overall score for the image is computed using the numbers of stained cells, non-stained cells and total cells for the calculations.

3. Modes of Operation: Semi-automated computer-assisted interpretation

4. Specimen Identification:

Specimens are identified by barcode read or through manual entry into automation software.

5. Specimen Sampling and Handling:

Specimens are prepared microscope slides. The device scans the slides and takes a digital image of these. Slides can be scanned individually or placed in racks and up to 160 may be scanned automatically. Areas of the slide to be analyzed (sampling) are suggested by software algorithm and the subset of these to actually be measured is determined by the user.

6. Calibration:

The instrument does not have calibrators for the assay. Typically, calibration is done on an image capture device through white and black balance.

7. Quality Control:

The quality of results depends on the laboratory following the quality control instructions recommended in the labeling of the immunohistochemistry (IHC) reagents. The software also performs a quality check on the digital images to determine if they are suitable for further analysis using “Image Quality Assessment” algorithms.

8. Software:

FDA has reviewed applicant’s Hazard Analysis and Software Development   
processes for this line of product types:   
Yes_ _X or No

# F. Regulatory Information:

1. Regulation section: 21CFR§864.1860, Immunohistochemistry reagents and kits

2. Classification: Class II

3 Product code: NQN, microscope, automated, image analysis, immunohistochemistry, operator intervention, nuclear intensity & percent positivity

4. Panel: Pathology (88)

# G. Intended Use:

1. Indication(s) for Use:

PATHIAMTM System with iScan for Ki-67

This device is intended for in vitro diagnostic (IVD) use.

The PATHIAMTM System is intended as an aid to the pathologist to detect, count, and classify cells of clinical interest based on recognition of cellular objects of particular color, size, and shape, using appropriate controls to assure the validity of the scores.

The Ki-67 application is intended as an aid to the pathologist to quantify the percentage of positively stained nuclei in formalin-fixed paraffin embedded normal and neoplastic breast tissue specimens immunohistochemically stained with Dako mouse monoclonal anti-human Ki-67 antigen, clone MIB1 visualized with DAB chromogen as specified in the instructions for these reagents. It is the responsibility of a qualified pathologist to employ appropriate morphological studies and controls as specified in the instructions for Dako Ki-67 to assure the validity of the PATHIAMTM -assisted Ki-67 assessment.

# PATHIAMTM System with iScan for p53

This device is intended for in vitro diagnostic (IVD) use.

The PATHIAMTM System is intended as an aid to the pathologist to detect, count, and classify cells of clinical interest based on recognition of cellular objects of particular color, size, and shape, using appropriate controls to assure the validity of the scores.

The p53 application is intended for use as an aid to the pathologist to quantify the percentage of positively stained nuclei in formalin fixed paraffin embedded breast tissue specimens stained with Dako mouse monoclonal anti-human p53 antibody, clone DO7and visualized with DAB chromogen, to detect both wild-type and mutant p53, a nuclear protein, as specified in the instructions for these reagents. It is the responsibility of a qualified pathologist to employ appropriate morphological studies and controls as specified in the instructions for Dako p53 to assure the validity of the PATHIAMTM -assisted p53 assessment.

2. Special Conditions for Use Statement(s): For Prescription Use Only

# H. Substantial Equivalence Information:

1. Predicate Device Name(s) and 510(k) numbers: a. k062428 Tripath Ventana Image Analysis System-p53 b. k053520 Tripath Ventana Image Analysis System-Ki-67

2. Comparison with Predicate Device:

<table><tr><td colspan="3">Similarities</td></tr><tr><td>Item</td><td>Device</td><td>Predicate</td></tr><tr><td>Name Intended Use</td><td>PATHIAMTM System for p53/ki67 k092333 This device is intended for in vitro</td><td>Tripath(VIAS-p53/Ki67) k062428/k053520 The Ventana Image Analysis</td></tr><tr><td></td><td>diagnostic (IVD) use. The PATHIAM™ System is intended to detect, count, and classify cells of clinical interest based on recognition of cellular objects of particular color, size, and shape. The p53 and Ki-67 applications are intended for use in immunohistochemistry with formalin fixed paraffin-embedded breast tissue specimens stained with a primary antibody to p53 protein(Dako mouse monoclonal antihuman p53 antibody, clone DO7) or to Ki-67 protein 67</td><td>System (VIASTM) is an adjunctive computer-assisted image analysis system functionally connected to an interactive microscope. It is intended for use as an aid to the pathologist in the detection, classification and counting of cells of interest based on marker intensity, size and shape using appropriate controls to assure the validity of the VIAS scores.</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">(Dako mouse monoclonal anti-human Ki-67 antigen, cloneMIB1) employing visualizationtechniques that require the DABchromogen to detect both wild-type and mutant p53 or Ki-67nuclear proteins.</td><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Sample Type</td><td colspan="1" rowspan="1">Formalin-fixed, paraffinembedded breast cancerspecimens stained byimmunohistochemistry reagents.</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Interpretation</td><td colspan="1" rowspan="1">By Pathologist</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">Localization of IHCpositive stain</td><td colspan="1" rowspan="1">Nuclear</td><td colspan="1" rowspan="1">Same</td></tr><tr><td colspan="1" rowspan="1">IHC antigen detected</td><td colspan="1" rowspan="1">P53 and Ki-67</td><td colspan="1" rowspan="1">Same</td></tr></table>

<table><tr><td rowspan=1 colspan=3>Differences</td></tr><tr><td rowspan=1 colspan=1>Item</td><td rowspan=1 colspan=1>Device</td><td rowspan=1 colspan=1>Predicate</td></tr><tr><td rowspan=1 colspan=1>Hardware</td><td rowspan=1 colspan=1>Digital Slide Scanner</td><td rowspan=1 colspan=1>Automated Microscope</td></tr><tr><td rowspan=1 colspan=1>Image Capture andInterpretation</td><td rowspan=1 colspan=1>The whole slide is imaged by theslide scanner and the field of viewis determined by pathologist aftercapture, before analysis.</td><td rowspan=1 colspan=1>Focal plane and field of view aredetermined by pathologist beforecapture and analysis.</td></tr></table>

# I. Special Control/Guidance Document Referenced (if applicable):

FDA’s “Guidance for the Content of Premarket Submissions for Software Contained in Medical Devices”, May 11, 2005

# J. Performance Characteristics:

1. Analytical Performance:

Data represented for System Precision involved studies using Tissue micro-arrays (TMAs), rather than whole pathological sections. TMAs were prepared and stained by Ohio State University Medical Center. The final test sets consisted of 188 sample cores placed on 5 slides. As some cores were excluded from one antibody study or the other, the final number of specimens used for testing was reduced to 120 for each antibody. Each tissue core was approximately $2 \mathrm { m m }$ in diameter, which represents approximately 16 fields of View (FOV) with a $4 0 \mathrm { x }$ objective of 4 fields of view with a $2 0 \mathrm { x }$ objective.

# a. Accuracy (Comparison to Manual Method):

Between-Pathologists Agreement: A single pathologist at three sites evaluated 120 cases each for p53 or Ki-67 staining on glass slides. This data is presented in the tables below as Manual vs. Manual scoring. These studies met the minimum criteria of $7 5 \%$ concordance for each clinical cut-off value used.

The same slides were scanned at BioImagene using an iScan™ System and the digital images were presented to the pathologists for evaluation using

PATHIAM™ software. The same pathologists scored 120 cases each for p53 and Ki-67 this is shown in the tables below as PATHIAM™ -assisted vs. PATHIAM™ -assisted scoring.

The scores produced by each pathologist using the two different methods were then compared and these are presented below as Manual vs. PATHIAM™ - assisted scoring.

This data is presented as percent concordance with exact $9 5 \%$ confidence intervals.

p53 data   
Manual vs. Manual p53 Scoring   

<table><tr><td rowspan=1 colspan=1>p53 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1 vs. 2</td><td rowspan=1 colspan=1>Pathologist 1 vs. 3</td><td rowspan=1 colspan=1>Pathologist 2 vs. 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>95.0% (89.43%-98.14%)</td><td rowspan=1 colspan=1>77.5% (68.98%-84.62%)</td><td rowspan=1 colspan=1>80.8% (72.64%-87.44%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%)</td><td rowspan=1 colspan=1>78.3% (68.89%-85.33%)</td><td rowspan=1 colspan=1>79.2% (70.80%-86.04%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>90.0% (83.18%-94.73%)</td><td rowspan=1 colspan=1>85.8% (78.29%-91.53%)</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%</td></tr></table>

PATHIAMTM -assisted vs PATHIAMTM -assisted p53   
Manual vs. PATHIAMTM -assisted p53 Scoring   

<table><tr><td rowspan=1 colspan=1>p53 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1 vs. 2</td><td rowspan=1 colspan=1>Pathologist 1 vs. 3</td><td rowspan=1 colspan=1>Pathologist 2 vs. 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>95.0% (89.43%-98.14%)</td><td rowspan=1 colspan=1>77.5% (68.98%-84.62%)</td><td rowspan=1 colspan=1>80.8% (72.64%-87.44%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%)</td><td rowspan=1 colspan=1>78.3% (68.89%-85.33%)</td><td rowspan=1 colspan=1>79.2% (70.80%-86.04%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>90.0% (83.18%-94.73%)</td><td rowspan=1 colspan=1>85.8% (78.29%-91.53%)</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%</td></tr></table>

<table><tr><td rowspan=1 colspan=1>p53 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1</td><td rowspan=1 colspan=1>Pathologist 2</td><td rowspan=1 colspan=1>Pathologist 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>86.6%6 (79.09%-92.12%)</td><td rowspan=1 colspan=1>89.9% (83.05%-94.68%)</td><td rowspan=1 colspan=1>81.5% (73.36%-88.04%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>84.9%(77.15%-90.78%)</td><td rowspan=1 colspan=1>84.9% (77.15%-90.78%)</td><td rowspan=1 colspan=1>77.3%(68.73%-84.48%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>89.1%(82.04%-94.05%)</td><td rowspan=1 colspan=1>87.4% (80.06%-92.77%)</td><td rowspan=1 colspan=1>83.2%6 (75.24%-89.42%)</td></tr></table>

# Ki-67 Data

Manual vs. Manual Ki-67 Scoring   

<table><tr><td rowspan=1 colspan=1>Ki-67 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1 vs. 2</td><td rowspan=1 colspan=1>Pathologist 1 vs. 3</td><td rowspan=1 colspan=1>Pathologist 2 vs. 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>95.0% (89.43%-98.14%)</td><td rowspan=1 colspan=1>77.5% (68.98%-84.62%)</td><td rowspan=1 colspan=1>80.8% (72.64%-87.44%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>87.5%(80.22%-92.83%)</td><td rowspan=1 colspan=1>78.3% (68.89%-85.33%)</td><td rowspan=1 colspan=1>79.2% (70.80%-86.04%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>90.0%(83.18%-94.73%)</td><td rowspan=1 colspan=1>85.8% (78.29%-91.53%)</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%</td></tr></table>

PATHIAMTM -assisted vs PATHIAMTM Assisted Ki-67   

<table><tr><td rowspan=1 colspan=1>Ki-67 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1 vs. 2</td><td rowspan=1 colspan=1>Pathologist 1 vs. 3</td><td rowspan=1 colspan=1>Pathologist 2 vs. 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>95.0% (89.43%-98.14%)</td><td rowspan=1 colspan=1>77.5% (68.98%-84.62%)</td><td rowspan=1 colspan=1>80.8% (72.64%-87.44%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%)</td><td rowspan=1 colspan=1>78.3% (68.89%-85.33%)</td><td rowspan=1 colspan=1>79.2% (70.80%-86.04%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>90.0% (83.18%-94.73%)</td><td rowspan=1 colspan=1>85.8% (78.29%-91.53%)</td><td rowspan=1 colspan=1>87.5% (80.22%-92.83%</td></tr></table>

Manual vs. PATHIAMTM -assisted Ki-67   

<table><tr><td rowspan=1 colspan=1>Ki-67 Cut-OffThreshold</td><td rowspan=1 colspan=1>Pathologist 1</td><td rowspan=1 colspan=1>Pathologist 2</td><td rowspan=1 colspan=1>Pathologist 3</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>88.3% (81.20%-93.47%)</td><td rowspan=1 colspan=1>93.3% (87.29%-97.08%)</td><td rowspan=1 colspan=1>93.3% (87.29%-97.08%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>86.7%(79.25%-92.18%)</td><td rowspan=1 colspan=1>90.0% (83.18%-94.73%)</td><td rowspan=1 colspan=1>92.5%(86.24%-96.51%)</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>86.7% (79.25%-92.18%)</td><td rowspan=1 colspan=1>89.2% (82.19%-94.10%)</td><td rowspan=1 colspan=1>80.8%(72.64%-87.44%)</td></tr></table>

# $b$ . Precision/Reproducibility:

Intra-Pathologist Precision: The slides were scanned by BioImagene and the digital images were presented to a single pathologist for evaluation using PATHIAM™ software. This independent pathologist scored a subset of 20 cases (out of the complete 120 TMA sets) 3 times over a minimum of 10 days. The study met the minimum criteria of $7 5 \%$ concordance for each clinical cutoff value used.

Concordance for Intra-Pathologist Scoring of p53   

<table><tr><td rowspan=1 colspan=1>Cut-Off Threshold</td><td rowspan=1 colspan=1>PATHIAMTM-assisted vs.PATHIAMTM-assisted</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>85%</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>80%</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>80%</td></tr></table>

Concordance for Intra-Pathologist Scoring of Ki-67   

<table><tr><td rowspan=1 colspan=1>Cut Off Threshold</td><td rowspan=1 colspan=1>PATHIAMTM-assisted vs.PATHIAMTM-assisted</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>80%</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>85%</td></tr><tr><td rowspan=1 colspan=1>&gt;10%</td><td rowspan=1 colspan=1>85%</td></tr></table>

Intra-Instrument and Instrument-to-Instrument Precision: Eight single cores from a total of four TMA slides were scanned five times on three systems at BioImagene. The three systems included matching computers, monitors and iScan slide scanners.

The Intra-Instrument precision of automated signal detection for each system was measured when the slides were stained with either p53 or Ki-67. The raw data recordings from each machine were at or below $2 . 6 7 \% \mathrm { C V }$ for p53 and at or below $2 . 9 \%$ for Ki-67. All of these values are similar to those achieved with the predicate device and were considered acceptable.

The data from precision testing on the individual PATHIAMTM with iScan systems was compared to provide Instrument-to-Instrument precision. This was calculated to be $4 . 5 5 \ \% \mathrm { C V }$ or lower for p53 and $2 . 1 4 \%$ or lower for Ki67. All of these values are similar to those achieved with the predicate device and were considered acceptable.

# p53 Instrument Precision Data

p53 Intra-Instrument precision-SYSTEM I   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007A7</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 322007E3</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA32007C9</td><td rowspan=1 colspan=1>42.90</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.06</td></tr><tr><td rowspan=1 colspan=1>TMA42007B5</td><td rowspan=1 colspan=1>2.82</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>2.67</td></tr><tr><td rowspan=1 colspan=1>TMA52007E3</td><td rowspan=1 colspan=1>73.50</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>0.07</td></tr><tr><td rowspan=1 colspan=1>TMA12007B9</td><td rowspan=1 colspan=1>16.44</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.09</td></tr><tr><td rowspan=1 colspan=1>TMA4 2007D4</td><td rowspan=1 colspan=1>22.14</td><td rowspan=1 colspan=1>0.07</td><td rowspan=1 colspan=1>0.32</td></tr><tr><td rowspan=1 colspan=1>TMA 4 2007 B3</td><td rowspan=1 colspan=1>24.05</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>0.23</td></tr></table>

p53 Intra-Instrument precision-SYSTEM II   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A7</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E3</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007C9</td><td rowspan=1 colspan=1>42.74</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.05</td></tr><tr><td rowspan=1 colspan=1>TMA 42007B5</td><td rowspan=1 colspan=1>2.57</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.58</td></tr><tr><td rowspan=1 colspan=1>TMA52007E3</td><td rowspan=1 colspan=1>72.89</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.06</td></tr><tr><td rowspan=1 colspan=1>TMA12007B9</td><td rowspan=1 colspan=1>16.51</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.24</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>22.44</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.17</td></tr><tr><td rowspan=1 colspan=1>TMA 4 2007B3</td><td rowspan=1 colspan=1>22.68</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>0.25</td></tr></table>

p53 Intra-Instrument precision-SYSTEM III   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A7</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E3</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007C9</td><td rowspan=1 colspan=1>42.60</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>0.11</td></tr><tr><td rowspan=1 colspan=1>TMA 42007B5</td><td rowspan=1 colspan=1>2.71</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.78</td></tr><tr><td rowspan=1 colspan=1>TMA52007E3</td><td rowspan=1 colspan=1>74.07</td><td rowspan=1 colspan=1>0.13</td><td rowspan=1 colspan=1>0.18</td></tr><tr><td rowspan=1 colspan=1>TMA12007B9</td><td rowspan=1 colspan=1>16.49</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>0.18</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>24.42</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.05</td></tr><tr><td rowspan=1 colspan=1>TMA 4 2007B3</td><td rowspan=1 colspan=1>24.90</td><td rowspan=1 colspan=1>0.10</td><td rowspan=1 colspan=1>0.40</td></tr></table>

p53 Instrument-Instrument precision between 3 systems   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007A7</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E3</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>-</td></tr><tr><td rowspan=1 colspan=1>TMA 32007C9</td><td rowspan=1 colspan=1>42.75</td><td rowspan=1 colspan=1>0.13</td><td rowspan=1 colspan=1>0.30</td></tr><tr><td rowspan=1 colspan=1>TMA 42007B5</td><td rowspan=1 colspan=1>2.70</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>4.32</td></tr><tr><td rowspan=1 colspan=1>TMA52007E3</td><td rowspan=1 colspan=1>7349</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.68</td></tr><tr><td rowspan=1 colspan=1>TMA 12007B9</td><td rowspan=1 colspan=1>16.48</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.25</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>23.00</td><td rowspan=1 colspan=1>1.05</td><td rowspan=1 colspan=1>4.55</td></tr><tr><td rowspan=1 colspan=1>TMA 4 2007B3</td><td rowspan=1 colspan=1>23.88</td><td rowspan=1 colspan=1>0.95</td><td rowspan=1 colspan=1>3.97</td></tr></table>

# Ki-67 Instrument Precision Data

Ki-67 Intra-Instrument precision-SYSTEM I   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007 A2</td><td rowspan=1 colspan=1>31.78</td><td rowspan=1 colspan=1>0.10</td><td rowspan=1 colspan=1>0.31</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E2</td><td rowspan=1 colspan=1>64.53</td><td rowspan=1 colspan=1>0.25</td><td rowspan=1 colspan=1>0.39</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A3</td><td rowspan=1 colspan=1>15.45</td><td rowspan=1 colspan=1>0.15</td><td rowspan=1 colspan=1>0.99</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>17.82</td><td rowspan=1 colspan=1>0.09</td><td rowspan=1 colspan=1>0.50</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007E7</td><td rowspan=1 colspan=1>9.76</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.22</td></tr><tr><td rowspan=1 colspan=1>TMA520077D6</td><td rowspan=1 colspan=1>4.85</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.40</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E5</td><td rowspan=1 colspan=1>9.13</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>1.35</td></tr><tr><td rowspan=1 colspan=1>TMA 2 2007 A1</td><td rowspan=1 colspan=1>0.88</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>1.78</td></tr></table>

Ki-67 Intra-Instrument precision-SYSTEM II   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 32007 A2</td><td rowspan=1 colspan=1>32.77</td><td rowspan=1 colspan=1>0.37</td><td rowspan=1 colspan=1>1.13</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E2</td><td rowspan=1 colspan=1>63.29</td><td rowspan=1 colspan=1>0.08</td><td rowspan=1 colspan=1>0.12</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A3</td><td rowspan=1 colspan=1>15.76</td><td rowspan=1 colspan=1>0.17</td><td rowspan=1 colspan=1>1.09</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>17.91</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.23</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E7</td><td rowspan=1 colspan=1>9.41</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.44</td></tr><tr><td rowspan=1 colspan=1>TMA52007D6</td><td rowspan=1 colspan=1>4.87</td><td rowspan=1 colspan=1>0.14</td><td rowspan=1 colspan=1>2.90</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E5</td><td rowspan=1 colspan=1>9.27</td><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>0.42</td></tr><tr><td rowspan=1 colspan=1>TMA 2 2007 A1</td><td rowspan=1 colspan=1>0.85</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.89</td></tr></table>

Ki-67 Intra-Instrument precision-SYSTEM III   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 32007 A2</td><td rowspan=1 colspan=1>31.53</td><td rowspan=1 colspan=1>0.19</td><td rowspan=1 colspan=1>0.59</td></tr><tr><td rowspan=1 colspan=1>TMA 32007 E2</td><td rowspan=1 colspan=1>62.11</td><td rowspan=1 colspan=1>0.23</td><td rowspan=1 colspan=1>0.36</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A3</td><td rowspan=1 colspan=1>15.05</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>0.78</td></tr><tr><td rowspan=1 colspan=1>TMA 42007 D4</td><td rowspan=1 colspan=1>17.66</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.14</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E7</td><td rowspan=1 colspan=1>9.81</td><td rowspan=1 colspan=1>0.07</td><td rowspan=1 colspan=1>0.72</td></tr><tr><td rowspan=1 colspan=1>TMA52007 D6</td><td rowspan=1 colspan=1>4.95</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>0.68</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007 E5</td><td rowspan=1 colspan=1>9.43</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.24</td></tr><tr><td rowspan=1 colspan=1>TMA 2 2007 A1</td><td rowspan=1 colspan=1>0.86</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.35</td></tr></table>

Ki-67 Instrument-Instrument precision between 3 systems   

<table><tr><td rowspan=1 colspan=1>Sample ID</td><td rowspan=1 colspan=1>Mean</td><td rowspan=1 colspan=1>SD</td><td rowspan=1 colspan=1>%CV</td></tr><tr><td rowspan=1 colspan=1>TMA 32007 A2</td><td rowspan=1 colspan=1>32.03</td><td rowspan=1 colspan=1>0.60</td><td rowspan=1 colspan=1>1.87</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E2</td><td rowspan=1 colspan=1>63.31</td><td rowspan=1 colspan=1>1.04</td><td rowspan=1 colspan=1>1.65</td></tr><tr><td rowspan=1 colspan=1>TMA 32007A3</td><td rowspan=1 colspan=1>15.42</td><td rowspan=1 colspan=1>0.33</td><td rowspan=1 colspan=1>2.14</td></tr><tr><td rowspan=1 colspan=1>TMA 42007D4</td><td rowspan=1 colspan=1>17.79</td><td rowspan=1 colspan=1>0.12</td><td rowspan=1 colspan=1>0.66</td></tr><tr><td rowspan=1 colspan=1>TMA 32007E7</td><td rowspan=1 colspan=1>9.66</td><td rowspan=1 colspan=1>0.19</td><td rowspan=1 colspan=1>1.95</td></tr><tr><td rowspan=1 colspan=1>TMA52007 D6</td><td rowspan=1 colspan=1>4.89</td><td rowspan=1 colspan=1>0.09</td><td rowspan=1 colspan=1>1.84</td></tr><tr><td rowspan=1 colspan=1>TMA 3 2007 E5</td><td rowspan=1 colspan=1>9.28</td><td rowspan=1 colspan=1>0.14</td><td rowspan=1 colspan=1>1.53</td></tr><tr><td rowspan=1 colspan=1>TMA 2 2007 A1</td><td rowspan=1 colspan=1>0.86</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>2.07</td></tr></table>

Lab-to-Lab Reproducibility: A three-center comparative study utilizing 10 deidentified formalin-fixed paraffin embedded breast carcinoma whole tissue sections, stained for the identification of p53 protein using Dako clone $\mathrm { D O 7 ^ { T M } }$ monoclonal antibody and DAB detection and for the identification of Ki-67 protein using Dako clone MIB1 monoclonal antibody and DAB detection. The glass slides required for the study were scanned at each study site to score by one pathologist.

The following two rounds of study were executed, and a minimum of one week was allowed between the two reads for each pathologist.

Round 1 Manual Scoring: Slides were scored by a qualified pathologist at each site using manual microscopy. Each pathologist read the same set of test samples for p53 and Ki-67 on a manual microscope. Each pathologist then assigned a score each test sample, according to the scoring categories.

Round 2 PATHIAM™-Assisted Scoring following digital scanning: The same slides were randomized and presented to the pathologists’ laboratories in a different order from Round 1 above.

The individual laboratories scanned the slides using iScan and three pathologists from Round 1 reviewed the digital images presented by the PATHIAM™ software on the computer monitor.

The pathologist had the ability to navigate freely around the images at various magnifications, select fields of views for scoring. With the assistance of the PATHIAM™ system, each pathologist then assigned a score to each test sample, according to the scoring categories.

Agreement (concordance) percentages were calculated at two clinically accepted standards for positivity, the ${ > } 1 \%$ cutoff and the $5 5 \%$ cutoff. These are shown below as point estimates and exact $9 5 \%$ confidence intervals. Each of the point estimates are at or above the acceptance limit set for the study ( $60 \%$ concordance).

Lab to Lab reproducibility of p53   

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>Site 3Manual vs.PATHIAM TM-Assisted</td><td rowspan=1 colspan=1>Site 2Manual vs.PATHIAMTM- Assisted</td><td rowspan=1 colspan=1>Site 1Manual vs.PATHIAM™ - Assisted</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>80% (44.39%-97.48%)</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td></tr></table>

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>PATHIAMT -AssistedSite 3 vs. Site 2</td><td rowspan=1 colspan=1>PATHIAMT AssistedSite 3 vs. Site 1</td><td rowspan=1 colspan=1>PATHIAMT - AssistedSite 2 vs. Site 1</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>100% (69.15%100%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td></tr></table>

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>ManualSite 3 vs. Site 2</td><td rowspan=1 colspan=1>ManualSite 3 vs. Site 1</td><td rowspan=1 colspan=1>ManualSite 2 vs. Site 1</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td><td rowspan=1 colspan=1>80% (44.39%-97.48%)</td><td rowspan=1 colspan=1>80% (44.39%-97.48%)</td></tr></table>

Lab to Lab reproducibility of Ki-67   

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>Site 3Manual vs.PATHIAM TM-Assisted</td><td rowspan=1 colspan=1>Site 2Manual vs.PATHIAM™ - Assisted</td><td rowspan=1 colspan=1>Site 1Manual vs.PATHIAM™ - Assisted</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td><td rowspan=1 colspan=1>80% (44.39%-97.48%)</td></tr></table>

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>PATHIAMT -AssistedSite 3 vs. Site 2</td><td rowspan=1 colspan=1>PATHIAMT -AssistedSite 3 vs. Site 1</td><td rowspan=1 colspan=1>PATHIAMT - AssistedSite 2 vs. Site 1</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>100%(69.15%-100%)</td><td rowspan=1 colspan=1>90%(55.50%-99.75%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>80% (44.39%-97.48%)</td><td rowspan=1 colspan=1>80%(44.39%-97.48%)</td><td rowspan=1 colspan=1>100%(69.15%-100%)</td></tr></table>

<table><tr><td rowspan=1 colspan=1>Cut OffThreshold</td><td rowspan=1 colspan=1>ManualSite 3 vs. Site 2</td><td rowspan=1 colspan=1>ManualSite 3 vs. Site 1</td><td rowspan=1 colspan=1>ManualSite 2 vs. Site 1</td></tr><tr><td rowspan=1 colspan=1>&gt;1%</td><td rowspan=1 colspan=1>100% (69.15%-100%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td></tr><tr><td rowspan=1 colspan=1>&gt;5%</td><td rowspan=1 colspan=1>60% (26.24%-87.84%)</td><td rowspan=1 colspan=1>90% (55.50%-99.75%)</td><td rowspan=1 colspan=1>70% (34.75%-93.33%)</td></tr></table>

c. Linearity: Not applicable   
d. Carryover: Not applicable   
e. Interfering Substances: Not applicable

2. Other Supportive Instrument Performance Data Not Covered Above: Shelf life was determined using “real world data” on file with the manufacturer

# K. Proposed Labeling:

The labeling is sufficient and it satisfies the requirements of 21 CFR Part 809.10.

# L. Conclusion:

The submitted information in this premarket notification is complete and supports a substantial equivalence decision.