# AlmaPartnerUpdate
Python code to update Parter data from Libraries Australia members &amp; suspensions website  

Python 3.7 script to webscrape data from Libraries Australia website:

https://www.nla.gov.au/librariesaustralia/connect/find-library/ladd-members-and-suspensions
and update Alma partner records accrodingly.

If a partner in Alma is active, but the LADD members and suspensions has them as inactive, the record is changed accordingly.  (And the reverse is also true, ie inactive becomes active.) If the LADD record matches the Alma record, no change occurs.  

Please also read the release notes.
The release contains the following files
AlmaPartnerUpdate_V1.06.py - Screen scrapes Libraries Australia's website for Partner suspensions and updates Alma accordingly.

Readme.txt - this file

ReleaseNotesV0.5.pdf

SampleConfig.yaml - file to be renamed and updated with your specific APIKeys and URL - See Release Notes

GetAll_Alma_PartnerRecords_v0.3.py - extracts all the Partner records in Alma and saves to an XML file

