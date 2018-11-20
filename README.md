# connect-scripts
Resilio Connect Scripts is a set of recipes and solutions for commonly done tasks in Resilio Connect product

## Agent Upgrade Pack
This folder contains scripts and files to upgrade all agents in your setup via the distribution job. See details inside 

## restore_archive.ps1 ![alt text](https://i.imgur.com/F6NAQyb.png "Script supports standard Get-Help cmdlet")
This script restores deleted files from archive (.sync\Archive folder of any synchronized folder) or just shows files that were deleted and could be restored.

## start-process-under-logged-on-user.ps1
This script allows to start process (`-AppPath`) with arguments (`-AppCmd`) under currently logged on user and show UI for him. Also, you can specify working directory (`-WorkDir`) and wait till process will be ended (`-Wait`).
 