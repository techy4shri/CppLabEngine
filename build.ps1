# Build script for CppLabEngine Windows release
# Creates a standalone distribution with PyInstaller

$ErrorActionPreference = "Stop"

$VERSION = "0.1.0"
$APP_NAME = CppLabEngine$DIST_DIR = "dist"
$BUILD_DIR = "build"
$ZIP_NAME = "$APP_NAME-v$VERSION-win64.zip"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building $APP_NAME v$VERSION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean previous builds
Write-Host "[1/6] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DIST_DIR) {
    Remove-Item -Recurse -Force $DIST_DIR
    Write-Host "  Removed $DIST_DIR/" -ForegroundColor Gray
}
if (Test-Path $BUILD_DIR) {
    Remove-Item -Recurse -Force $BUILD_DIR
    Write-Host "  Removed $BUILD_DIR/" -ForegroundColor Gray
}
if (Test-Path "$APP_NAME.spec") {
    Remove-Item -Force "$APP_NAME.spec"
    Write-Host "  Removed $APP_NAME.spec" -ForegroundColor Gray
}
Write-Host "  Clean complete" -ForegroundColor Green
Write-Host ""

# Step 2: Create/activate virtual environment
Write-Host "[2/6] Setting up Python environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
}
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\.venv\Scripts\Activate.ps1
Write-Host "  Environment ready" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies
Write-Host "[3/6] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  Installing requirements.txt..." -ForegroundColor Gray
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
Write-Host "  Installing PyInstaller..." -ForegroundColor Gray
python -m pip install --quiet pyinstaller
Write-Host "  Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 4: Run PyInstaller
Write-Host "[4/6] Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "  Running pyinstaller..." -ForegroundColor Gray
pyinstaller --onedir `
    --name $APP_NAME `
    --windowed `
    --noconfirm `
    --clean `
    --add-data "src/cpplab/ui;cpplab/ui" `
    --add-data "docs_source;docs_source" `
    src/cpplab/main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyInstaller failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Executable built" -ForegroundColor Green
Write-Host ""

# Step 5: Copy additional resources
Write-Host "[5/6] Copying resources..." -ForegroundColor Yellow

# Copy compilers
if (Test-Path "compilers") {
    Write-Host "  Copying compilers/..." -ForegroundColor Gray
    Copy-Item -Recurse -Force "compilers" "$DIST_DIR\$APP_NAME\compilers"
} else {
    Write-Host "  WARNING: compilers/ not found (skipping)" -ForegroundColor DarkYellow
}

# Copy examples
if (Test-Path "examples") {
    Write-Host "  Copying examples/..." -ForegroundColor Gray
    Copy-Item -Recurse -Force "examples" "$DIST_DIR\$APP_NAME\examples"
} else {
    Write-Host "  WARNING: examples/ not found (skipping)" -ForegroundColor DarkYellow
}

# Copy licenses if exists
if (Test-Path "licenses") {
    Write-Host "  Copying licenses/..." -ForegroundColor Gray
    Copy-Item -Recurse -Force "licenses" "$DIST_DIR\$APP_NAME\licenses"
}

# Copy LICENSE file
if (Test-Path "LICENSE") {
    Write-Host "  Copying LICENSE..." -ForegroundColor Gray
    Copy-Item -Force "LICENSE" "$DIST_DIR\$APP_NAME\LICENSE"
}

# Copy README
if (Test-Path "README.md") {
    Write-Host "  Copying README.md..." -ForegroundColor Gray
    Copy-Item -Force "README.md" "$DIST_DIR\$APP_NAME\README.md"
}

Write-Host "  Resources copied" -ForegroundColor Green
Write-Host ""

# Step 6: Create zip archive
Write-Host "[6/6] Creating release archive..." -ForegroundColor Yellow
Push-Location $DIST_DIR
if (Test-Path $ZIP_NAME) {
    Remove-Item -Force $ZIP_NAME
}
Write-Host "  Compressing $APP_NAME/..." -ForegroundColor Gray
Compress-Archive -Path $APP_NAME -DestinationPath $ZIP_NAME -CompressionLevel Optimal
Pop-Location
Write-Host "  Archive created: $DIST_DIR\$ZIP_NAME" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output:" -ForegroundColor White
Write-Host "  Executable: $DIST_DIR\$APP_NAME\$APP_NAME.exe" -ForegroundColor White
Write-Host "  Archive:    $DIST_DIR\$ZIP_NAME" -ForegroundColor White
Write-Host ""

# Display size
$zipSize = (Get-Item "$DIST_DIR\$ZIP_NAME").Length / 1MB
Write-Host "Archive size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
