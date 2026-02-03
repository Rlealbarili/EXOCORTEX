# Moltbook Agent Registration Script
# Run this to bypass the IP rate limit on the cloud agent.

$AgentName = "Prof_Petrovich_Local"
$AgentDesc = "The Monolith. V7. Local Instance."

Write-Host "Registering agent: $AgentName..." -ForegroundColor Cyan

$body = @{
    name = $AgentName
    description = $AgentDesc
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://www.moltbook.com/api/v1/agents/register" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -ErrorAction Stop

    Write-Host "`n[SUCCESS] Agent Registered!" -ForegroundColor Green
    Write-Host "---------------------------------------------------"
    Write-Host "API KEY (SAVE THIS): $($response.agent.api_key)" -ForegroundColor Yellow
    Write-Host "CLAIM URL:           $($response.agent.claim_url)" -ForegroundColor Yellow
    Write-Host "VERIFICATION CODE:   $($response.agent.verification_code)" -ForegroundColor Yellow
    Write-Host "---------------------------------------------------"
    Write-Host "`nPlease verify the agent immediately at the Claim URL."

    # Save to file for the agent to pick up if needed
    $response | ConvertTo-Json | Out-File -Encoding utf8 "local_credentials.json"
    Write-Host "Credentials saved to local_credentials.json"
} catch {
    Write-Host "`n[ERROR] Registration Failed." -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        Write-Host "Server Response: $($reader.ReadToEnd())"
    }
}
