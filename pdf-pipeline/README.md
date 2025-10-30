# Robust PDF-to-Image Conversion Pipeline

A production-grade, fault-tolerant PDF-to-image converter with 3-layer fallback system, containerized with Docker for scalability and reliability.

## 🎯 Features

- **3-Layer Fallback System**:
  1. **Ghostscript** - Primary (handles 90%+ of complex PDFs, including JBIG2/CCITT)
  2. **ImageMagick** - Secondary fallback
  3. **Tesseract + pdftoppm** - Last resort (OCR rendering path)

- **Industrial Strength**:
  - Handles multi-hundred-page PDFs
  - Supports complex compression (JBIG2, CCITT, etc.)
  - Sequential page-by-page extraction (memory-safe)
  - Comprehensive logging and error tracking
  - Zero tolerance for failure - exhausts all methods

- **Docker Containerized**:
  - Consistent environment across systems
  - Easy deployment and scaling
  - Resource isolation

## 📋 Prerequisites

- Docker installed and running
- Input PDFs located at `~/Desktop/PDF/`
- Sufficient disk space for output images

## 🚀 Quick Start

```bash
# Simple one-command execution
./run.sh
```

This will:
1. Build the Docker image
2. Process all PDFs in `~/Desktop/PDF/`
3. Output images to `./output/` directory

## 📁 Project Structure

```
pdf-pipeline/
├── Dockerfile          # Ubuntu 22.04 base with all tools
├── convertor.py        # Main conversion logic
├── run.sh             # Execution script
├── .dockerignore      # Excludes output/ from build
├── README.md          # This file
└── output/            # Generated images (gitignored)
    └── [PDF_NAME]/    # One folder per PDF
        ├── page-001.png
        ├── page-002.png
        └── ...
```

## 🛠️ Manual Usage

### Build Image
```bash
docker build -t pdf2img-robust .
```

### Run Conversion
```bash
docker run --rm \
  -v "$HOME/Desktop/PDF:/data/pdfs:ro" \
  -v "$PWD/output:/data/output" \
  pdf2img-robust
```

## 📊 Output Format

- **Resolution**: 300 DPI
- **Color Depth**: 16M colors (PNG24)
- **Naming**: `page-001.png`, `page-002.png`, etc.
- **Organization**: One directory per PDF

## 🔍 Monitoring & Debugging

### Check Logs
The converter provides detailed logs including:
- Which method succeeded for each file
- Full command output for failures
- Processing time and status

### Verify Output
```bash
# Count pages extracted from a PDF
ls output/YOUR_PDF_NAME/ | wc -l

# Check file sizes
du -sh output/*
```

## 🔄 Future Enhancements

### Parallel Processing (Optional)
For processing multiple PDFs simultaneously:

```bash
# Process 4 PDFs in parallel
ls ~/Desktop/PDF/*.pdf | xargs -P 4 -I {} bash -c '
  name=$(basename "{}" .pdf)
  docker run --rm \
    -v "$HOME/Desktop/PDF:/data/pdfs:ro" \
    -v "$PWD/output-$name:/data/output" \
    pdf2img-robust
'
```

**Note**: Default is sequential per-file to prevent memory issues.

## 🐛 Troubleshooting

### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### No PDFs Found
- Verify PDFs exist in `~/Desktop/PDF/`
- Check file permissions: `ls -la ~/Desktop/PDF/`

### Out of Memory
- Process files individually
- Increase Docker memory limit
- Use lower DPI (modify `DPI = 300` in convertor.py)

### Specific PDF Failing
Check logs to see which methods were attempted:
```bash
docker run --rm \
  -v "$HOME/Desktop/PDF:/data/pdfs:ro" \
  -v "$PWD/output:/data/output" \
  pdf2img-robust 2>&1 | grep -A5 -B5 "problematic.pdf"
```

## 🔧 Customization

### Change Resolution
Edit `convertor.py`:
```python
DPI = 300  # Change to 150, 600, etc.
```

### Add More Languages (Tesseract)
Edit `Dockerfile`:
```dockerfile
RUN apt install -y \
    tesseract-ocr-ara \  # Arabic
    tesseract-ocr-chi-sim \  # Chinese Simplified
    # etc.
```

Then update `convertor.py`:
```python
cmd1 = ["tesseract", pdf_path, temp_pdf.replace(".pdf", ""), "-l", "fas+eng+ara", "pdf"]
```

## 📄 License

This pipeline is provided as-is for PDF processing tasks. Ensure you have rights to process your PDF content.

## 🤝 Contributing

1. Test thoroughly with various PDF types
2. Add new extraction methods as additional layers
3. Maintain the sequential processing requirement
4. Update documentation for new features

## ⚠️ Important Notes

1. **Input Path**: PDFs must be in `~/Desktop/PDF/`
2. **Memory Usage**: Large PDFs may require significant RAM
3. **Processing Time**: Complex PDFs can take several minutes
4. **Disk Space**: Each page generates a ~1-5MB PNG file

## 🆘 Support

For issues:
1. Check the logs first
2. Verify Docker is running: `docker ps`
3. Ensure input PDFs are valid: `file ~/Desktop/PDF/*.pdf`
4. Test with a simple PDF first
