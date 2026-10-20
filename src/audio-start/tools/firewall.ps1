$rules = @(
    @{ DisplayName = 'Audio Star TCP'; Protocol = 'TCP'; LocalPort = @(22534, 22545) },
    @{ DisplayName = 'Audio Star UDP'; Protocol = 'UDP'; LocalPort = @(1900) }
)
foreach ($rule in $rules) {
    Get-NetFirewallRule -DisplayName $rule.DisplayName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -DisplayName $rule.DisplayName -Direction Inbound -Action Allow -Protocol $rule.Protocol -LocalPort $rule.LocalPort -RemoteAddress LocalSubnet -Profile Private | Out-Null
    Write-Host "added $($rule.DisplayName)"
}
