param (
    [string]$pptxPath,
    [string]$pdfPath
)

$pptxPath = Resolve-Path $pptxPath
$pdfPath = [System.IO.Path]::Combine((Get-Item $pptxPath).DirectoryName, [System.IO.Path]::GetFileNameWithoutExtension($pptxPath) + ".pdf")

$ppt_app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $ppt_app.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $presentation.SaveAs($pdfPath, 32) # 32 is ppSaveAsPDF
    $presentation.Close()
    Write-Host "PDF created successfully at: $pdfPath"
} catch {
    Write-Error "Failed to convert PPTX to PDF: $_"
} finally {
    $ppt_app.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt_app)
}
