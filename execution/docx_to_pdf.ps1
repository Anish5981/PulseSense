$SourcePath = "c:\Users\91620\Desktop\Code\pulseApp\PulseSense1.docx"
$DestPath = "c:\Users\91620\Desktop\Code\pulseApp\PulseSense1.pdf"

# Initialize Word Application
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    # Open the document
    $doc = $word.Documents.Open($SourcePath)
    
    # Export as PDF (Format 17 is wdExportFormatPDF)
    $doc.ExportAsFixedFormat($DestPath, 17)
    
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
