param([string]$PptxPath = '', [string]$PdfPath = '')
$ErrorActionPreference = 'Stop'
$projectCodeRoot = Split-Path -Parent $PSScriptRoot
$projectPackageRoot = Split-Path -Parent $projectCodeRoot
if (-not $PptxPath) { $PptxPath = Join-Path $projectPackageRoot '04_Presentation\COMP6704_Group9_Lasso_Presentation.pptx' }
if (-not $PdfPath) { $PdfPath = Join-Path $projectPackageRoot '04_Presentation\COMP6704_Group9_Lasso_Presentation.pdf' }
$app = New-Object -ComObject PowerPoint.Application
$initialCount = $app.Presentations.Count
$pres = $null
try {
  $pres = $app.Presentations.Open($PptxPath, -1, 0, 0)
  $slideCount = $pres.Slides.Count
  $pres.SaveCopyAs($PdfPath, 32)
  Write-Output ('Exported ' + $slideCount + ' slides to ' + $PdfPath)
} finally {
  if ($null -ne $pres) { $pres.Close() }
  if ($initialCount -eq 0 -and $app.Presentations.Count -eq 0) { $app.Quit() }
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
