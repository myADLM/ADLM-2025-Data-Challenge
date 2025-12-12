# SPECIAL 510(k): Device Modification OIR Decision Memorandum

This 510(k) submission contains information/data on modifications made to the SUBMITTER’S own Class II, Class III or Class I devices requiring 510(k). The following items are present and acceptable:

1. The name and 510(k) number of the SUBMITTER’S previously cleared device: AggreGuide A100 Instrument and AggreGuide A-100 AA assay (K122162).

2. Submitter’s statement indicated that the INDICATION/INTENDED USE of the modified device as described in its labeling HAS NOT CHANGED along with the proposed labeling which includes instructions for use and package labeling.

3. A description of the device MODIFICATION(S), including clearly labeled diagrams, engineering drawings, photographs, user’s and/or service manuals in sufficient detail, demonstrated that the FUNDAMENTAL SCIENTIFIC TECHNOLOGY of the modified device has not changed.

The changes were for hardware modification, software revision, stability extension and User’s Manual revision. The detailed information of the changes is stated below.

# a. New Laser Diode material

The laser diode manufactured by Sanyo, a key component of the AggreGuide A-100, that generates the laser light used to analyze the platelet-aggregation-induced light scattering was replaced with the laser diode manufactured by QSI and the electrical and optical characteristics of the diodes is summarized in table below. Both Laser diodes demonstrate similar specifications and the use of the substitute laser diode have been validated with the AggreGuide A-100 instruments. The validation results meet the production acceptance criteria. The validation protocol and results summary are included in document of “VAL0110-A” and it can be found in DocMan.

<table><tr><td rowspan=1 colspan=1>Characteristic of Laser</td><td rowspan=1 colspan=1>Sanyo DL-4140-001S</td><td rowspan=1 colspan=1>QSI QL7816SA-L</td></tr><tr><td rowspan=1 colspan=1>Wavelength, (nm), nominal</td><td rowspan=1 colspan=1>785</td><td rowspan=1 colspan=1>785</td></tr><tr><td rowspan=1 colspan=1>Optical Power (mW), required,maximum</td><td rowspan=1 colspan=1>5-2025</td><td rowspan=1 colspan=1>5-2030</td></tr><tr><td rowspan=1 colspan=1>Temperature Range(°C)</td><td rowspan=1 colspan=1>-10 -60 C</td><td rowspan=1 colspan=1>-10-60 C</td></tr><tr><td rowspan=1 colspan=1>Operating Current (mA) &lt; 200</td><td rowspan=1 colspan=1>65</td><td rowspan=1 colspan=1>45</td></tr><tr><td rowspan=1 colspan=1>Light beam format</td><td rowspan=1 colspan=1>Elliptical</td><td rowspan=1 colspan=1>Elliptical</td></tr></table>

# b. Quality Control Cartridge

The QC device (QC2) has been modified to use a fixed diffuser instead of a rotating groove. There are no changes to the principle of how the QC device is used, and there are no changes to the procedure that the user follows. The changes that have been made to the quality control device pertain to the material used to produce the scattering signal in the QC2 device and to the form of the QC2 device, relative to the previous QC cartridge. The QC2 device reduces the possibility of false negative QC check results and variability of QC results. The stability and repeatability verification study was performed on four production prototype QC2 devices and the results demonstrated that the criteria for stability of time is passed and the standard deviation for each device sample was less than $10 \%$ of the mean. The criterion for repeatability between devices is also passed and all means are within $0 . 4 \pm$ 0.05V. The verification protocol and results summary are included in document of “VAL0102-A” and can be found in DocMan.

# c. Software Changes

The software is revised to accommodate the quality control cartridge modifications (QC2). The functional detail of the software changes are documented in table below:

<table><tr><td rowspan=1 colspan=1>Software Function</td><td rowspan=1 colspan=1>Version 5.00</td><td rowspan=1 colspan=1>Version 5.10</td></tr><tr><td rowspan=1 colspan=1>Quality control (QC) cartridge</td><td rowspan=1 colspan=1>Original (QC)</td><td rowspan=1 colspan=1>New (QC2)</td></tr><tr><td rowspan=1 colspan=1>QC software invoked:</td><td rowspan=1 colspan=1>Single software entry-point to qualitycontrol routine, single point return,simple pass/fail result.</td><td rowspan=1 colspan=1>Single software entry-point toquality control routine, single pointreturn, simple pass/fail result.No change.</td></tr><tr><td rowspan=1 colspan=1>Laser power for qualitycontrol testing</td><td rowspan=1 colspan=1>Power decreased to slightly higherthan the lasing threshold.Different than actual bloodplatelet test.</td><td rowspan=1 colspan=1>Power kept at nominally full powersettings of the laser, as during actualblood platelet test.</td></tr><tr><td rowspan=1 colspan=1>Laser status during qualitycontrol testing</td><td rowspan=1 colspan=1>Constant, uses rotation of rotor tocause transient signals.Failure in optics or amplifierobserved.</td><td rowspan=1 colspan=1>Steady state for test of optics.Oscillating for test of amplifier.Failure of optics alone, or opticsplus amplifier observed.</td></tr><tr><td rowspan=1 colspan=1>Quality control cartridgematched to instrument</td><td rowspan=1 colspan=1>Each individual QC cartridge ismarried to an individualinstrument.</td><td rowspan=1 colspan=1>QC2 cartridges use standard-performing optical materials toallow interchangeability of QC2cartridges</td></tr></table>

The new QC2 quality control software allows for testing of the QC2 cartridge at the same power level as an assay using whole blood, introduction of a steady light level to test instrument optics and an oscillating light level to test the amplifier.

# d. The Test Cartridge shelf-life Extension

The test cartridge shelf life has been extended from 12 months to 19 months, using the same isochronous stability testing scheme as described in the original 510(k) clearance. The shelf-life stability study was performed using three lots of the cartridges according to the CLSI guidelines EP25-A and EN134460:20002. Results of the shelf-life stability testing were assessed for each lot in terms of measurand drift as stated in CLSI EP25-A, Evaluation of Stability of In Vitro Diagnostics Reagents, Approved Guideline. The study results demonstrate the assay cartridge is stable for at least 20 months of shelf life and support the shelf-life stability extension claim of 18 months. The verification protocol and results summary are included in document of “VAL-0091-B and can be found in DocMan.

4. Comparison Information (similarities and differences) to applicant’s legally marketed predicate device including labeling, intended use/indication for use, methodology, insert sheet, physical characteristics are located in 510(k) Summary.

# 5. A Design Control Activities Summary which includes:

a) Identification of Risk Analysis method(s) used to assess the impact of the modification on the device and its components, and the results of the analysis.

The risk analysis methods are determined by the identification of known and hypothesized hazards and estimation of the associated risk based on the operation of the device for its intended use. The design verification and validation tests that were performed as a result of this risk analysis assessment are listed in ANL-0015B (Appendix A). In conclusion, the design changes proposed do not affect system performance and the impact of the modification does not raise additional safety concerns.

b) Based on the risk analysis, an identification of the verification and/or validation activities required, including methods or tests used and acceptance criteria to be applied.

Descriptions of verification and validation activities were provided for the AggreGuide A100 hardware and software. The test protocols information and risk management report were also provided.

The labeling for this modified subject device has been reviewed to verify that the indication/intended use for the device is unaffected by the modification. In addition, the submitter’s description of the particular modification(s) and the comparative information between the modified and unmodified devices demonstrate that the fundamental scientific technology has not changed. The submitter has provided the design control information as specified in the New 510(k) Paradigm and on this basis, I recommend the device be determined substantially equivalent to the previously cleared (or their preamendment) device.