<#

.OUTPUTS
The script sets errorlevel to reflect results of the check
  0 - all checks pass, proceed to upgrade
  1 - upgrade it not necessary
  2 - some checks fail, do not proceed to upgrade
#>

#Don't make a [CmdletBinding()] here. This will prevent to set %ERRORLEVEL% in PS2.0

$errcode = 0

try
{
	Add-Type -Assembly System.Windows.Forms
	######### Check 0
	$filecheckfailure = $false
	Write-Host "Checking if all necessary files are present..."
	if (!(Test-Path ".\Resilio-Connect-Agent.exe" -PathType Leaf))
	{
		Write-Host "Resilio-Connect-Agent.exe file is missing"
		$filecheckfailure = $true
		$errcode = 2
	}
	
	if (!(Test-Path "Resilio-Connect-Agent_x64.exe" -PathType Leaf))
	{
		Write-Host "Resilio-Connect-Agent_x64.exe file is missing"
		$filecheckfailure = $true
		$errcode = 3
	}
	
	if (!(Test-Path "agent_upgrade.ps1" -PathType Leaf))
	{
		Write-Host "agent_upgrade.ps1 script is missing"
		$filecheckfailure = $true
		$errcode = 4
	}
	
	if (!(Test-Path "ResilioUpgrade.xml" -PathType Leaf))
	{
		Write-Host "ResilioUpgrade.xml configuration file is missing"
		$filecheckfailure = $true
		$errcode = 5
	}
	
	if ($filecheckfailure)
	{
		throw "Some files are missing, upgrade impossile"
	}
	Write-Host "[OK]"
	
	######### Check 1
	Write-Host "Checking for elevated privileges..."
	$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
	if (!$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
	{
		$errcode = 12
		throw "Script is not running with elevated privileges, upgrade impossible"
	}
	Write-Host "[OK]"
	
	######### Check 2
	Write-Host "Checking computer is AC powered..."
	
	if ([System.Windows.Forms.SystemInformation]::PowerStatus.PowerLineStatus -ne 'Online')
	{
		$errcode = 13
		throw "Computer runs on battery power, upgrade is too risky now"
	}
	Write-Host "[OK]"
	
	######### Check 3
	Write-Host "Checking Task Scheduler service is running..."
	if ((Get-Service -Name "schedule").Status -ne 'Running')
	{
		$errcode = 14
		throw "Task Scheduler service is not running, upgrade is not possible"
	}
	Write-Host "[OK]"
	
	######### Check 4
	Write-Host "Checking Agent versions..."
	$ownscriptpathname = (Resolve-Path $MyInvocation.InvocationName).Path
	$ownscriptpath = Split-Path -Path $ownscriptpathname
	$ownscriptname = Split-Path $ownscriptpathname -Leaf
	$processname = "Resilio Connect Agent.exe"
	$agentupgradeablex86 = "Resilio-Connect-Agent.exe"
	$agentupgradeablex64 = "Resilio-Connect-Agent_x64.exe"
	if ([IntPtr]::size -eq 8) { $agentupgradeble = $agentupgradeablex64 }
	else { $agentupgradeble = $agentupgradeablex86 }
	$processpath = (Get-ItemProperty -path 'HKLM:\SOFTWARE\Resilio, Inc.\Resilio Connect Agent\').InstallDir
	$fullexepath = Join-Path -Path $processpath -ChildPath $processname
	$fullupgradeablepath = Join-Path -Path $ownscriptpath -ChildPath $agentupgradeble
	[System.Version]$oldversion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo("$fullexepath").FileVersion
	[System.Version]$newversion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo("$fullupgradeablepath").FileVersion
	if ($oldversion -gt $newversion)
	{
		$errcode = 15
		throw "Attempted to downgrade from $oldversion to $newversion, downgrade is not supported"
	}
	if ($oldversion -eq $newversion)
	{
		Write-Host "Same version detected, no point in launching upgrade"
		exit 1
	}
	Write-Debug "Ugprading from $oldversion to $newversion"
	Write-Host "[OK]"
}
catch
{
	Write-Host "Error during upgrade verifiction: $_"
	exit $errcode
}

exit 0