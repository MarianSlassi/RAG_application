# Error Analysis
### Default model answer looks like this (top-5 naive retrieving): 
```
--------------------
User question:  How do i reinstall printer?
-----retrieved documents: ----- 
 1 009_resetting-a-jammed-printer,
 2 045_configuring-a-network-printer,
 3 071_setting-up-a-secure-connection-to-a-company-issued-printer,
 4 045_configuring-a-network-printer,
 5 045_configuring-a-network-printer
-----LLM answer-----
 To reinstall a printer, follow these steps:

1. First, locate the printer's IP address from your department's printer list or IT representative.
2. For Windows: Open "Devices and Printers" from the Start menu, click "Add a printer," select "Add a network, wireless or Bluetooth printer," enter the printer's IP address, and select the appropriate driver.
3. For Mac: Open System Preferences, click "Printers & Scanners," click the "+" icon, select "IP," enter the printer's IP address, select the driver, and click "Add."
4. If needed, download the printer driver from the manufacturer's website or company software repository.
5. You can set the printer as default by right-clicking it and selecting "Set as default printer" (Windows) or selecting it and clicking "Make Default" (Mac).

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/045_configuring-a-network-printer.md
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/docx/071_setting-up-a-secure-connection-to-a-company-issued-printer.docx

Claude 3 Opus by Anthropic
--------------------
```

### Expirement 1
We will see we got pretty sutissfying answers to our questions:
## Questions:
```
question_answer(question= 'How do i reinstall printer?')
question_answer(question= 'How can I reset my computer’s DNS cache?')
question_answer(question= 'I can’t upload files to SharePoint, what should I check first?')
question_answer(question= 'How do I configure VPN access for remote work?')
question_answer(question= 'What should I do if my company laptop is running very slowly?')
question_answer(question= 'How do I configure email on my Android device?')
question_answer(question= 'How do I reset my computer’s IP address?')
question_answer(question= 'What steps should I take if my company-issued hardware (laptop/desktop) stops working?')
question_answer(question= 'How can I set up a new user account in Dropbox?')
question_answer(question= 'How do I set up a secure connection to a company server?')
question_answer(question= 'What should I include when creating a new IT incident report?')
```

## Answers:
```
--------------------
User question:  How do i reinstall printer?
-----retrieved documents: ----- 
 1 009_resetting-a-jammed-printer,
 2 045_configuring-a-network-printer,
 3 071_setting-up-a-secure-connection-to-a-company-issued-printer,
 4 045_configuring-a-network-printer,
 5 045_configuring-a-network-printer
-----LLM answer-----
 To reinstall a printer, follow these steps:

1. First, locate the printer's IP address from your department's printer list or IT representative.
2. For Windows: Open "Devices and Printers" from the Start menu, click "Add a printer," select "Add a network, wireless or Bluetooth printer," enter the printer's IP address, and select the appropriate driver.
3. For Mac: Open System Preferences, click "Printers & Scanners," click the "+" icon, select "IP," enter the printer's IP address, select the driver, and click "Add."
4. If needed, download the printer driver from the manufacturer's website or company software repository.
5. You can set the printer as default by right-clicking it and selecting "Set as default printer" (Windows) or clicking "Make Default" (Mac).

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/045_configuring-a-network-printer.md
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/docx/071_setting-up-a-secure-connection-to-a-company-issued-printer.docx

Claude 3.5 Sonnet by Anthropic
--------------------
--------------------
User question:  How can I reset my computer’s DNS cache?
-----retrieved documents: ----- 
 1 093_resetting-a-computer-s-dns-cache,
 2 065_resetting-a-computer-s-dns-settings,
 3 065_resetting-a-computer-s-dns-settings,
 4 065_resetting-a-computer-s-dns-settings,
 5 079_resetting-a-computer-s-dhcp-settings
-----LLM answer-----
 To reset your computer's DNS cache:

For Windows:
1. Open Command Prompt as administrator
2. Type `ipconfig /flushdns` and press Enter
3. You'll see a confirmation message that the DNS cache was flushed

For Mac:
1. Open Terminal application
2. Type `dscacheutil -flushcache; sudo killall -HUP mDNSResponder` and press Enter

For Linux:
1. Open Terminal
2. Type `sudo service dns-clean start` and press Enter

For Chrome browser:
1. Type `chrome://net-internals/#dns` in the address bar
2. Click "Clear host cache"

Sources: /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/pdf/093_resetting-a-computer-s-dns-cache.pdf

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  I can’t upload files to SharePoint, what should I check first?
-----retrieved documents: ----- 
 1 095_troubleshooting-issues-with-microsoft-sharepoint,
 2 015_setting-up-a-secure-ftp-connection,
 3 095_troubleshooting-issues-with-microsoft-sharepoint,
 4 085_setting-up-a-secure-connection-to-a-company-issued-ftp-site,
 5 077_troubleshooting-issues-with-company-issued-software
-----LLM answer-----
 When troubleshooting SharePoint upload issues, you should:

1. Check the file size and type - ensure it's within the 2GB limit and is a supported file type
2. Verify your internet connection stability, which is required for successful uploads
3. Check the SharePoint site's upload center for any errors or pending uploads
4. Verify you have the necessary permissions to upload content
5. Try uploading the file in smaller chunks or using the SharePoint desktop application

Sources: /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/pdf/095_troubleshooting-issues-with-microsoft-sharepoint.pdf

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  How do I configure VPN access for remote work?
-----retrieved documents: ----- 
 1 003_configuring-vpn-access-for-remote-workers,
 2 064_setting-up-a-secure-connection-to-a-company-issued-server,
 3 057_setting-up-a-secure-connection-to-a-company-issued-device,
 4 099_setting-up-a-secure-connection-to-a-company-issued-server,
 5 072_resetting-a-forgotten-vpn-password
-----LLM answer-----
 To configure VPN access for remote work:

1. Download the VPN client software from your company's software portal
2. Install the software following the prompts
3. Launch the VPN client and create a new connection
4. Enter the company's VPN server address (e.g., vpn.company.com)
5. Input your company login credentials
6. Click "Connect" and complete any two-factor authentication if prompted
7. Verify connection by checking that your IP address has changed to a company-assigned one

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/003_configuring-vpn-access-for-remote-workers.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  What should I do if my company laptop is running very slowly?
-----retrieved documents: ----- 
 1 098_troubleshooting-issues-with-a-slow-performing-computer,
 2 042_troubleshooting-issues-with-a-slow-performing-computer,
 3 049_troubleshooting-issues-with-company-issued-laptops,
 4 077_troubleshooting-issues-with-company-issued-software,
 5 091_troubleshooting-issues-with-company-issued-hardware
-----LLM answer-----
 If your company laptop is running slowly, try these steps:

1. Restart your computer to clear temporary files and refresh the system.
2. Check Task Manager (Ctrl+Shift+Esc) to identify and close resource-intensive applications.
3. Disable unnecessary startup programs using System Configuration (msconfig).
4. Ensure your operating system and software are up-to-date.
5. Run disk cleanup to free up storage space.
6. Run an antivirus scan to check for malware.
7. Check for and update outdated drivers.

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/pdf/098_troubleshooting-issues-with-a-slow-performing-computer.pdf
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/042_troubleshooting-issues-with-a-slow-performing-computer.md
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/049_troubleshooting-issues-with-company-issued-laptops.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  How do I configure email on my Android device?
-----retrieved documents: ----- 
 1 010_configuring-email-on-an-android-device,
 2 001_setting-up-a-mobile-device-for-company-email,
 3 017_configuring-a-company-issued-smartphone,
 4 038_configuring-a-company-issued-tablet-for-international-travel,
 5 052_configuring-a-company-issued-smartphone-for-international-travel
-----LLM answer-----
 To configure email on your Android device:

1. Locate and open the Email app on your Android device.
2. Tap "Add account" or "Add email account."
3. Select "Email," "Corporate," or "Exchange" as the account type.
4. Enter your email address and password, then tap "Next."
5. If automatic configuration fails, tap "Manual setup" and enter your incoming/outgoing server details, including server addresses, ports, and security types.
6. Configure additional options like sync frequency and tap "Done" to complete setup.

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/010_configuring-email-on-an-android-device.md
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/001_setting-up-a-mobile-device-for-company-email.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  How do I reset my computer’s IP address?
-----retrieved documents: ----- 
 1 079_resetting-a-computer-s-dhcp-settings,
 2 051_resetting-a-computer-s-ip-address,
 3 079_resetting-a-computer-s-dhcp-settings,
 4 065_resetting-a-computer-s-dns-settings,
 5 093_resetting-a-computer-s-dns-cache
-----LLM answer-----
 To reset your computer's IP address:

1. Open Command Prompt as Administrator (right-click and select "Run as Administrator")
2. Type `netsh int ip reset` and press Enter to reset the TCP/IP stack
3. Type `ipconfig /release` to release the current IP address
4. Type `ipconfig /renew` to request a new IP address from the DHCP server
5. If you're using a Mac, go to System Preferences > Network > select your interface > Advanced > TCP/IP tab > click "Renew DHCP Lease"

If you experience connectivity issues afterward, check your network cable connection or contact IT support.

Sources: 
- /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/docx/079_resetting-a-computer-s-dhcp-settings.docx
- /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/051_resetting-a-computer-s-ip-address.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  What steps should I take if my company-issued hardware (laptop/desktop) stops working?
-----retrieved documents: ----- 
 1 091_troubleshooting-issues-with-company-issued-hardware,
 2 063_troubleshooting-issues-with-company-issued-desktops,
 3 077_troubleshooting-issues-with-company-issued-software,
 4 007_troubleshooting-issues-with-company-issued-tablets,
 5 049_troubleshooting-issues-with-company-issued-laptops
-----LLM answer-----
 If your company-issued hardware stops working, follow these steps:

1. Restart the device to see if that resolves the issue
2. Check for loose connections or faulty cables (power cords, USB devices)
3. Ensure proper ventilation to prevent overheating
4. Run diagnostic tests on components (hard drive, RAM, CPU)
5. Check event logs for error messages
6. If the issue persists, document the troubleshooting steps taken and escalate to advanced support or hardware vendor for repair/replacement

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/pdf/091_troubleshooting-issues-with-company-issued-hardware.pdf
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/063_troubleshooting-issues-with-company-issued-desktops.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  How can I set up a new user account in Dropbox?
-----retrieved documents: ----- 
 1 096_setting-up-a-new-user-s-account-in-dropbox,
 2 089_setting-up-a-new-user-s-account-in-box,
 3 082_setting-up-a-new-user-s-account-in-concur,
 4 047_setting-up-a-new-user-s-account-in-salesforce,
 5 054_setting-up-a-new-user-s-account-in-jira
-----LLM answer-----
 To set up a new user account in Dropbox:

1. Navigate to the Dropbox admin console and click on "Users" in the top navigation menu.
2. Click on "Invite users" and enter the new user's email address, first name, and last name.
3. Assign the user to team folders by clicking "Team Folders" > select folder > "Add members" > enter email and set permission level.
4. Configure settings: select language, time zone, set temporary password, and account type.
5. Enable 2FA for security.
6. Send the user instructions with login link, temporary password, and access information.
7. Verify the account setup is correct.

Sources: /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/pdf/096_setting-up-a-new-user-s-account-in-dropbox.pdf

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  How do I set up a secure connection to a company server?
-----retrieved documents: ----- 
 1 078_setting-up-a-secure-connection-to-a-company-issued-database,
 2 064_setting-up-a-secure-connection-to-a-company-issued-server,
 3 026_setting-up-a-secure-connection-to-a-database,
 4 092_setting-up-a-secure-connection-to-a-company-issued-website,
 5 057_setting-up-a-secure-connection-to-a-company-issued-device
-----LLM answer-----
 To set up a secure connection to a company server, follow these steps:

1. Install the company-approved VPN software from the company's intranet portal or IT representative
2. Launch the VPN client on your device
3. Enter your company username and password (and 2FA code if required)
4. Select the correct server from the dropdown menu
5. Click "Connect" to establish the secure connection
6. Verify the connection is established by checking network settings or accessing company resources
7. Ensure your device has the latest security patches and antivirus software

Sources: /Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/064_setting-up-a-secure-connection-to-a-company-issued-server.md

Claude 3 Opus by Anthropic
--------------------
--------------------
User question:  What should I include when creating a new IT incident report?
-----retrieved documents: ----- 
 1 083_creating-a-new-it-incident,
 2 055_creating-a-new-it-incident-report,
 3 069_creating-a-new-it-problem-report,
 4 055_creating-a-new-it-incident-report,
 5 097_creating-a-new-it-problem
-----LLM answer-----
 When creating a new IT incident report, you should include:

- A brief description in the "Summary" or "Incident Title" field
- Detailed description including error messages and symptoms
- Category and subcategory selection from drop-down menus
- Priority level and impact assessment
- Affected services and configuration items
- Any screenshots, logs, or error messages as attachments
- Troubleshooting steps already taken
- Your contact information and preferred communication method

Sources:
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/docx/083_creating-a-new-it-incident.docx
/Users/marianslassi/Documents/Entry/Code/Git_default/RAG_application/data/01_raw/it-knowledge/canonical/md/055_creating-a-new-it-incident-report.md

Claude 3 Opus by Anthropic
--------------------
```
## Expected answers:
```
Q: How can I reset my computer’s DNS cache?
	•	Windows: open Command Prompt as admin → run ipconfig /flushdns.
	•	Mac OS X: open Terminal → run dscacheutil -flushcache; sudo killall -HUP mDNSResponder.
	•	Linux (Ubuntu): run sudo service dns-clean start.
	•	Chrome OS: go to chrome://net-internals/#dns → click Clear host cache.
Q: I can’t upload files to SharePoint, what should I check first?
	•	Make sure the file size is under 2GB and it’s a supported type.
	•	Check your internet connection.
	•	Look at SharePoint’s upload center for pending errors.
	•	Try uploading in smaller chunks or use the desktop app.
Q: How do I configure VPN access for remote work?
	1.	Download and install the VPN client from the company software portal.
	2.	Create a new connection in the VPN client → enter server address (vpn.company.com) and credentials.
	3.	Click Connect, complete two-factor authentication if required.
	4.	Verify you can access company resources after connecting.
Q: What should I do if my company laptop is running very slowly?
	•	Restart the computer.
	•	Check Task Manager for high CPU/memory apps.
	•	Update OS and software.
	•	Disable unnecessary startup programs.
	•	Run a malware scan.
	•	Clear temp files and ensure enough free disk space.
	•	Update drivers or defragment disk (if HDD).
Q: How do I configure email on my Android device?
	1.	Open the Email app → Add account.
	2.	Enter email + password.
	3.	If auto-setup fails → go to manual setup:
	•	Incoming server: company mail server, port + security type.
	•	Outgoing server: same with auth.
	4.	Adjust sync settings (frequency, size).
	5.	Save and test login.
Q: How do I reset my computer’s IP address?
	•	Open Command Prompt as admin.
	•	Run ipconfig /release → then ipconfig /renew.
	•	Check new IP with ipconfig /all.
    Alternatively:
	•	Go to Network & Sharing Center → Change adapter settings → set to “Obtain IP automatically.”
Q: What steps should I take if my company-issued hardware (laptop/desktop) stops working?
	1.	Restart the device.
	2.	Check cables, power supply, and battery.
	3.	Ensure BIOS/firmware is updated.
	4.	Run virus scan.
	5.	Use diagnostic tools (RAM, HDD/SSD tests).
	6.	If unresolved → escalate to advanced support team with full documentation.
Q: How can I set up a new user account in Dropbox?
	1.	In admin console → Users → Invite new user (email, first/last name).
	2.	Assign to team folder with correct permission (Editor/Viewer).
	3.	Configure settings: language, time zone, temp password, account type.
	4.	Enable two-factor authentication.
	5.	Send instructions and verify access.
Q: How do I set up a secure connection to a company server?
	•	Install company VPN client (Cisco AnyConnect or approved software).
	•	Launch VPN → enter credentials.
	•	Choose the correct server group (e.g., Finance, Marketing).
	•	Click Connect and wait for confirmation.
	•	Verify access to company resources.
Q: What should I include when creating a new IT incident report?
    •	Incident title (short description, e.g., “Unable to access email”).
	•	Detailed description (symptoms, error messages, troubleshooting done).
	•	Category & subcategory.
	•	Priority & impact (single user, multiple, business critical).
	•	Affected services or configuration items.
	•	Attachments (screenshots/logs).
	•	Contact information.
```

### Edge cases:
So, at least it says i
```
--------------------
User question:  What is the best hero in league of legends?
-----retrieved documents: ----- 
 1 054_setting-up-a-new-user-s-account-in-jira,
 2 096_setting-up-a-new-user-s-account-in-dropbox,
 3 061_setting-up-a-new-user-s-account-in-oracle,
 4 075_setting-up-a-new-user-s-account-in-workday,
 5 047_setting-up-a-new-user-s-account-in-salesforce
-----LLM answer-----
 I don't know.

Sources: 

Model: Claude 3.5 Sonnet by Anthropic
--------------------
```