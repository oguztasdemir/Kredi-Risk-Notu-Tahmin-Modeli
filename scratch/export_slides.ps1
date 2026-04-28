param (
    [string]$pptxPath
)

$pptxPath = Resolve-Path $pptxPath
$outputFolder = [System.IO.Path]::Combine((Get-Item $pptxPath).DirectoryName, "Preview")
if (-not (Test-Path $outputFolder)) { New-Item -ItemType Directory -Path $outputFolder }

$ppt_app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $ppt_app.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    for ($i = 1; $i -le [Math]::Min(3, $presentation.Slides.Count); $i++) {
        $slide = $presentation.Slides.Item($i)
        $imagePath = [System.IO.Path]::Combine($outputFolder, "Slide$i.png")
        $slide.Export($imagePath, "PNG")
        Write-Host "Exported Slide $i to $imagePath"
    }
    $presentation.Close()
} catch {
    Write-Error "Failed to export slides: $_"
} finally {
    $ppt_app.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt_app)
}
