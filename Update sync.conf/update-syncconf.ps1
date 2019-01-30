<#	
.SYNOPSIS
Modify sync.conf file of Resilio Connect Agent

.DESCRIPTION
Modify sync.conf file by autodetected or specified path. Script can adjust
standard parameters (storage path, fingerprint, host, bootstrap token) as
well as add / modify custom parameters (use_gui, device_name, etc.)
Script requires elevated privileges if your sync.conf stays in Program Files
directory.
Actual directory where script arrives does not matter. 

.PARAMETER SyncConfPath
Specifies path to sync.conf file including sync.conf. If not specified, script
will access the registry to find Agent installation path and sync.conf location

.PARAMETER NewBootstrap
Specifies new bootstrap token you want to get into your sync.conf

.PARAMETER NewHost
Specifies new host and port value (colon separated) to be set into your sync.conf

.PARAMETER NewFingerprint
Specifies new server certificate fingerprint to be set into your sync.conf

.PARAMETER NewStoragePath
Specifies new storage path to be set into your sync.conf

.PARAMETER CustomParameterName
Specifies custom parameter name to be inserted / changed into your sync.conf

.PARAMETER CustomParameterValue
Specifies custom parameter value which will be set into your sync.conf

.PARAMETER RemoveCustomParameter
Set this if you want to delete custom parameter from sync.conf

.PARAMETER RestartAgent
Set this if you want script to restart agent service after changing 
sync.conf. Script will use Windows Task Scheduler to call itself with
PerformGracefulRestart switch set. Recommended if you call the script 
from any of Resilio Connect jobs.

.PARAMETER PerformGracefulRestart
Performs actual restart of the agent service. It's not recommended to call
this method if you run the script from Agent itself (via job). Use
RestartAgent instead. Agent restart is timeoutless and script will wait 
agent service to shut down as long as it needed even if service control
timeouts. After service moves to "Stopped" state, script will start it again.

.EXAMPLE
update-syncconf.ps1 -CustomParameterName "device_name" -CustomParameterValue "%TAG_AGENT_NAME%"

.EXAMPLE
update-syncconf.ps1 -CustomParameterName "use_gui" -CustomParameterValue true -RestartAgent
#>

Param (
	[Parameter(ParameterSetName = 'changestandard')]
	[Parameter(ParameterSetName = 'addcustom')]
	[Parameter(ParameterSetName = 'removecustom')]
	[string]$SyncConfPath,
	[Parameter(ParameterSetName = 'changestandard')]
	[string]$NewBootstrap,
	[Parameter(ParameterSetName = 'changestandard')]
	[string]$NewHost,
	[Parameter(ParameterSetName = 'changestandard')]
	[string]$NewFingerprint,
	[Parameter(ParameterSetName = 'changestandard')]
	[string]$NewStoragePath,
	[Parameter(ParameterSetName = 'addcustom')]
	[Parameter(ParameterSetName = 'removecustom')]
	[string]$CustomParameterName,
	[Parameter(ParameterSetName = 'addcustom')]
	[object]$CustomParameterValue,
	[Parameter(ParameterSetName = 'removecustom')]
	[switch]$RemoveCustomParameter,
	[Parameter(ParameterSetName = 'changestandard')]
	[Parameter(ParameterSetName = 'addcustom')]
	[Parameter(ParameterSetName = 'removecustom')]
	[switch]$RestartAgent,
	[Parameter(ParameterSetName = 'gracefulrestart')]
	[switch]$PerformGracefulRestart
)

$xmlpart1 = '<?xml version="1.0" encoding="UTF-16"?>
		<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
		<RegistrationInfo>
		<Date>2018-11-02T23:15:32</Date>
		<Author>ResilioInc</Author>
		<URI>\ResilioUpgrade</URI>
		</RegistrationInfo>
		<Triggers>
		<TimeTrigger>
		<StartBoundary>1910-01-01T00:00:00</StartBoundary>
		<Enabled>true</Enabled>
		</TimeTrigger>
		</Triggers>
		<Principals>
		<Principal id="Author">
		<UserId>S-1-5-18</UserId>
		<RunLevel>LeastPrivilege</RunLevel>
		</Principal>
		</Principals>
		<Settings>
		<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
		<DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
		<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
		<AllowHardTerminate>true</AllowHardTerminate>
		<StartWhenAvailable>false</StartWhenAvailable>
		<RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
		<IdleSettings>
		<Duration>PT10M</Duration>
		<WaitTimeout>PT1H</WaitTimeout>
		<StopOnIdleEnd>true</StopOnIdleEnd>
		<RestartOnIdle>false</RestartOnIdle>
		</IdleSettings>
		<AllowStartOnDemand>true</AllowStartOnDemand>
		<Enabled>true</Enabled>
		<Hidden>false</Hidden>
		<RunOnlyIfIdle>false</RunOnlyIfIdle>
		<WakeToRun>false</WakeToRun>
		<ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
		<Priority>7</Priority>
		</Settings>
		<Actions Context="Author">
		<Exec>
		<Command>powershell.exe  </Command>
		<Arguments>-NoProfile -ExecutionPolicy Bypass -File "'

$xmlpart2 = '" -PerformGracefulRestart</Arguments>
		</Exec>
		</Actions>
		</Task>
'
# --------------------------------------------------------------------------------------------------------------------------------
Write-Verbose "Script started"

# Define own paths and names
$ownscriptpathname = Join-Path -path ((Resolve-Path $MyInvocation.InvocationName).Path) -ChildPath $MyInvocation.MyCommand.Name
$ownscriptpath = Split-Path -Path $ownscriptpathname
$ownscriptname = Split-Path $ownscriptpathname -Leaf

try
{
	# Just shut down the agent service and start it again. Gracefully, no pressure
	if ($PerformGracefulRestart)
	{
		Write-Verbose "Stopping service"
		Get-Service -Name "connectsvc" | Stop-Service -ErrorAction Continue
		$ServiceStatus = 'Running'
		while ($ServiceStatus -ne 'Stopped')
		{
			Start-Sleep -Seconds 5
			$ServiceStatus = (Get-Service -Name "connectsvc").Status
		}
		Write-Verbose "Service stopped, restarting"
		Get-Service -Name "connectsvc" | Start-Service
		
		Write-Verbose "Service started, exiting"
		exit
	}
	
	# If path to sync.conf not specified, extract it from regisrty
	if (-not $SyncConfPath)
	{
		$AgentInstallPath = (Get-ItemProperty -path 'HKLM:\SOFTWARE\Resilio, Inc.\Resilio Connect Agent\').InstallDir
		$SyncConfPath = Join-Path -Path $AgentInstallPath -ChildPath 'sync.conf'
	}
	
	# Get sync.conf content
	$syncconf = Get-Content -Path $SyncConfPath | ConvertFrom-Json
	
	# Update standard parameters here
	if ($NewBootstrap) { $syncconf.management_server.bootstrap_token = $NewBootstrap }
	if ($NewHost) { $syncconf.management_server.host = $NewHost }
	if ($NewFingerprint) { $syncconf.management_server.cert_authority_fingerprint = $NewFingerprint }
	if ($NewStoragePath) { $syncconf.folders_storage_path = $NewStoragePath }
	
	# Check for custom parameter
	if ($CustomParameterName)
	{
		if ($RemoveCustomParameter)
		{
			# Remove custom parameter if it exists here
			if ($CustomParameterName -in $syncconf.PSobject.Properties.Name)
			{
				$syncconf.PSObject.Properties.Remove($CustomParameterName)
			}
			else { throw "Parameter `"$CustomParameterName`" not found and therefore not removed" }
		}
		else
		{
			# Update custom parameters here
			Add-Member -InputObject $syncconf -NotePropertyName $CustomParameterName -NotePropertyValue $CustomParameterValue -Force
		}
	}
	
	Set-Content -Path $SyncConfPath -Value (ConvertTo-Json $syncconf)
	Write-Output "sync.conf file updated"
	
	# Restart agent if required
	if ($RestartAgent)
	{
		$SchedulerXML = "$xmlpart1$ownscriptpathname$xmlpart2"
		Set-Content -Path "ResilioRestart.xml" -Value $SchedulerXML
		Start-Process -FilePath "schtasks" -ArgumentList "/create /TN ResilioRestart /XML ResilioRestart.xml /F"
		Start-Sleep -Seconds 3
		Start-Process -FilePath "schtasks" -ArgumentList "/run /tn ResilioRestart"
		Write-Output "Attempting agent restart"
	}
}
catch
{
	Write-Error "$_"
	Write-Output "sync.conf not modified"
}

Write-Verbose "Script done"