$SourcePath = "c:\Users\91620\Desktop\Code\pulseApp\PulseSense1.docx"
$DestPath = "c:\Users\91620\Desktop\Code\pulseApp\.tmp\PulseSense1.txt"

# Ensure .tmp directory exists
if (-not (Test-Path "c:\Users\91620\Desktop\Code\pulseApp\.tmp")) {
    New-Item -ItemType Directory -Path "c:\Users\91620\Desktop\Code\pulseApp\.tmp" | Out-Null
}

# Initialize Word Application
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    # Open the document
    $doc = $word.Documents.Open($SourcePath)
    
    # Save as Text (Format 2 is wdFormatText)
    $doc.SaveAs([ref]$DestPath, [ref]2)
    
    # Close the document
    $doc.Close($false)
    echo "Success: Created $DestPath"
} catch {
    echo "Error: $($_.Exception.Message)"
} finally {
    # Exit Word
    $word.Quit()
    
    # Cleanup COM object
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
