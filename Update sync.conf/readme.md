# Update sync.conf

This folder contains set of scripts and components necesssary to change your Agent's sync.conf file via Distribution job. Script also restarts agent service if necesary. The script does not care about the folder it runs into.
Minimal set of files that should be present in distribution folder
* update-syncconf.ps1 ![alt text](https://i.imgur.com/F6NAQyb.png "Script supports standard Get-Help cmdlet")

The files *.copy_to_trigger are not necessary to be present in distributed folder but copied to the trigger of update job on MC. 

## update-syncconf.ps1 ![alt text](https://i.imgur.com/F6NAQyb.png "Script supports standard Get-Help cmdlet")
The script is actually doing an update of sync.conf, which includes:
* loading existing sync.conf from standard or specified location
* modifying sync.conf according to specified parameters
* saving sync.conf into the same location
* restarting the agent if requested
* restarting the agent via detached way (using Windows Task Scheduler) if requested

## ResilioRestart.xml
This XML spawned automatically into a target folder by script if agent restart is requested

## upgrade-post-download.cmd.copy_to_trigger
This file contains cmd script which needs to be placed to post-download trigger of the update job. Please note that you need to specify necessary parameterys yourself before firing the job