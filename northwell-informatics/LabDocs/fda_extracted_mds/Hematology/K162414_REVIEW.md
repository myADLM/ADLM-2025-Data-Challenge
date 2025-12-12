# SPECIAL $\boldsymbol { \mathsf { \mathbf { 5 1 0 } } } ( \boldsymbol { \mathsf { k } } )$ : Device Modification OIR Decision Memorandum

This 510(k) submission contains information/data on modifications made to the SUBMITTER’S own Class II, Class III or Class I devices requiring 510(k). The following items are present and acceptable:

1. The name and 510(k) number of the SUBMITTER’S previously cleared device: UniCel® DxH Slidemaker Stainer Coulte $\textsuperscript { \textregistered }$ Cellular Analysis System (K140911).

2. Submitter’s statement indicated that the INDICATION/INTENDED USE of the modified device as described in its labeling HAS NOT CHANGED along with the proposed labeling which includes instructions for use and package labeling.

3. A description of the device MODIFICATION(S), including clearly labeled diagrams, engineering drawings, photographs, user’s and/or service manuals in sufficient detail, demonstrated that the FUNDAMENTAL SCIENTIFIC TECHNOLOGY of the modified device has not changed.

The changes were for hardware modification and software revision based on the root cause analysis for a fire incident reported in the field and the detailed information of the changes are stated below.

# Hardware:

Pressure relief valves are added to re-circulate the flow of liquid around the pumps when the valve triggers to mitigate the potential pressure buildup along the Stainer module fluidic lines which can cause the silicon tubing to become disconnected or ruptured leading to spills that may not be contained.   
Plastic splash shields are added as a barrier to protect printed circuit board (PCB) electronics from accidental sprays in case of tubing disconnections or other leaks. Neoprene gaskets and insulating tape are added within the frame to reduce the probability of a ribbon cable being damaged during installation and service.   
Room Temperature Vulcanization (RTV) silicone is added to seal the seams of the chassis to contain any leaks and reduce the probability of any reagent falling on the electronics below.

# Software:

The UniCel® DxH Slidemaker Stainer (SMS) embedded software is revised to address the potential failure mode where a damaged fitting on pumps, valves or manifolds anywhere in the fluidics lines results in siphoning from methanol or stain baths. To mitigate this potential failure, the DxH SMS embedded software has been modified to monitor the number of top-offs in a 2-hour period and the median volume of the last four top-offs that occurred in the last 8 hours. If the predefined threshold is exceeded for either of these conditions, the SMS Stainer Module will stop working. To bring the instrument back to an operational status, the root cause investigation performed by a BEC Service representative is required.

4. Comparison Information (similarities and differences) to applicant’s legally marketed predicate device including labeling, intended use/indication for use, methodology, insert sheet, physical characteristics are located in 510(k) Summary.

# 5. A Design Control Activities Summary which includes:

a) Identification of Risk Analysis method(s) used to assess the impact of the modification on the device and its components, and the results of the analysis.

The risk analysis method used to assess the impact of the modifications was a Failure Modes and Effects Analysis (FMEA) and a System Risk Assessment. In conclusion, the design changes proposed do not affect system performance and the impact of the modification does not raise additional safety concerns.

b) Based on the risk analysis, an identification of the verification and/or validation activities required, including methods or tests used and acceptance criteria to be applied.

Descriptions of verification and validation activities were provided for the DxH SMS hardware and software. The test protocols including acceptance criteria and test results were also provided.

The labeling for this modified subject device has been reviewed to verify that the indication/intended use for the device is unaffected by the modification. In addition, the submitter’s description of the particular modification(s) and the comparative information between the modified and unmodified devices demonstrate that the fundamental scientific technology has not changed. The submitter has provided the design control information as specified in The New 510(k) Paradigm and on this basis, I recommend the device be determined substantially equivalent to the previously cleared (or their preamendment) device.