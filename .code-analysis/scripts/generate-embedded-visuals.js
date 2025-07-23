const fs = require('fs');
const path = require('path');

/**
 * Convert an image file to base64 data URL
 */
async function convertImageToBase64(imagePath) {
  try {
    if (!fs.existsSync(imagePath)) {
      return null;
    }
    
    const imageBuffer = fs.readFileSync(imagePath);
    const ext = path.extname(imagePath).toLowerCase();
    let mimeType = 'image/png';
    
    if (ext === '.jpg' || ext === '.jpeg') mimeType = 'image/jpeg';
    else if (ext === '.gif') mimeType = 'image/gif';
    else if (ext === '.svg') mimeType = 'image/svg+xml';
    
    return `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
  } catch (error) {
    console.log(`Could not convert image ${imagePath}:`, error.message);
    return null;
  }
}

/**
 * Generate multiple display options for an image (embedded + fallbacks)
 */
function generateImageDisplayOptions(imagePath, title, base64Data) {
  const fileName = path.basename(imagePath);
  let content = `### ${title}\n\n`;
  
  if (base64Data) {
    // Option 1: Base64 embedded image (best compatibility)
    content += `<img src="${base64Data}" alt="${title}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;" />\n\n`;
    
    // Option 2: Provide fallback link in case base64 fails
    content += `<details>\n`;
    content += `<summary>📎 Alternative viewing options</summary>\n\n`;
    content += `- **Direct file:** \`${fileName}\`\n`;
    content += `- **Location:** \`.code-analysis/outputs/${fileName}\`\n`;
    content += `- **Size:** ${(Buffer.byteLength(base64Data.split(',')[1], 'base64') / 1024).toFixed(1)} KB\n`;
    content += `\n</details>\n\n`;
  } else {
    // No image available - provide helpful information
    content += `> **📷 Image not yet generated:** \`${fileName}\`\n\n`;
    content += `This visual will be available when:\n`;
    content += `- Dependencies are properly installed (matplotlib, graphviz, etc.)\n`;
    content += `- Analysis scripts complete successfully\n`;
    content += `- Project structure is compatible with visual generation\n\n`;
    content += `**Check:** \`.code-analysis/outputs/${fileName}\`\n\n`;
  }
  
  return content;
}

/**
 * Main function to generate enhanced image report with embedded PNGs
 */
async function generateEnhancedImageReport() {
  console.log('Generating enhanced image report with PNG displays...');
  
  const outputsDir = '.code-analysis/outputs';
  const images = {
    'dependency_graph_base.png': '📊 Base Branch Dependencies',
    'dependency_graph_pr.png': '📊 PR Branch Dependencies', 
    'change_heatmap.png': '🔥 Change Impact Heatmap',
    'development_flow.png': '🚀 Development Flow',
    'story_arc.gif': '📖 Story Arc Animation'
  };
  
  // Also check for SVG alternatives since we created those
  const svgAlternatives = {
    'dependency_graph_base.svg': '📊 Base Branch Dependencies',
    'dependency_graph_pr.svg': '📊 PR Branch Dependencies', 
    'change_heatmap.svg': '🔥 Change Impact Heatmap',
    'development_flow.svg': '🚀 Development Flow'
  };
  
  let reportContent = '## 🎬 Enhanced PR Visuals\n\n';
  reportContent += '*Displaying generated images with multiple rendering methods for best compatibility*\n\n';
  
  let hasImages = false;
  let totalSize = 0;
  
  // Try PNG files first, then SVG alternatives
  const allImages = { ...images, ...svgAlternatives };
  
  for (const [filename, title] of Object.entries(allImages)) {
    const imagePath = path.join(outputsDir, filename);
    const base64Data = await convertImageToBase64(imagePath);
    
    if (base64Data) {
      hasImages = true;
      const sizeKB = Buffer.byteLength(base64Data.split(',')[1], 'base64') / 1024;
      totalSize += sizeKB;
      
      reportContent += generateImageDisplayOptions(imagePath, title, base64Data);
      console.log(`✓ Embedded ${filename} (${sizeKB.toFixed(1)} KB)`);
    } else {
      reportContent += generateImageDisplayOptions(imagePath, title, null);
      console.log(`✗ Image not found: ${filename}`);
    }
    
    reportContent += '---\n\n';
  }
  
  // Add summary
  if (hasImages) {
    reportContent += `### 📈 Summary\n\n`;
    reportContent += `- **Images Embedded:** ${Object.entries(allImages).filter(([filename]) => fs.existsSync(path.join(outputsDir, filename))).length}\n`;
    reportContent += `- **Total Size:** ${totalSize.toFixed(1)} KB\n`;
    reportContent += `- **Rendering:** Base64 embedded for instant viewing\n\n`;
  } else {
    reportContent += generateNoImagesMessage();
  }
  
  // Add file listing
  reportContent += await generateFileListingSection(outputsDir);
  
  // Save the report
  const reportPath = path.join(outputsDir, 'enhanced_image_report.md');
  fs.writeFileSync(reportPath, reportContent, 'utf8');
  
  console.log(`Enhanced image report saved to: ${reportPath}`);
  console.log(`Report contains ${hasImages ? 'embedded images' : 'no images'}`);
  
  return {
    success: true,
    hasImages,
    totalImages: Object.keys(allImages).length,
    reportPath,
    reportContent,
    totalSizeKB: totalSize
  };
}

function generateNoImagesMessage() {
  return `### ❌ No Images Generated\n\n` +
         `This can happen when:\n` +
         `- **Dependencies Missing:** matplotlib, graphviz, or other required tools\n` +
         `- **No Changes Detected:** Insufficient changes to generate meaningful visuals\n` +
         `- **Project Type:** Some project structures aren't compatible with visual analysis\n` +
         `- **Analysis Errors:** Check workflow logs for specific error messages\n\n` +
         `**To fix this:**\n` +
         `1. Ensure all dependencies are installed in the workflow\n` +
         `2. Check that your project has analyzable dependencies\n` +
         `3. Review the enhanced-pr-visuals workflow logs\n\n`;
}

async function generateFileListingSection(outputsDir) {
  let content = '### 📁 Generated Files\n\n';
  
  try {
    const files = fs.readdirSync(outputsDir);
    if (files.length > 0) {
      content += '| File | Size | Type | Status |\n';
      content += '|------|------|------|--------|\n';
      
      files.forEach(file => {
        const fullPath = path.join(outputsDir, file);
        const stats = fs.statSync(fullPath);
        const sizeKB = (stats.size / 1024).toFixed(1);
        const type = getFileType(file);
        const isImage = /\.(png|jpg|jpeg|gif|svg)$/i.test(file);
        const status = isImage ? '🖼️ Image' : '📄 Data';
        content += `| \`${file}\` | ${sizeKB} KB | ${type} | ${status} |\n`;
      });
      
      content += '\n';
    } else {
      content += '*No files generated in outputs directory.*\n\n';
    }
  } catch (error) {
    console.log('Could not read outputs directory:', error.message);
    content += '*Could not read outputs directory.*\n\n';
  }
  
  return content;
}

function getFileType(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  if (['.json'].includes(ext)) return '📊 Data';
  if (['.md'].includes(ext)) return '📝 Report';
  if (['.txt'].includes(ext)) return '📄 Text';
  if (['.png', '.jpg', '.gif', '.svg'].includes(ext)) return '🖼️ Image';
  return '📁 File';
}

// Main execution
async function main() {
  try {
    const result = await generateEnhancedImageReport();
    console.log('\n✅ Enhanced image report generation complete!');
    console.log(`📄 Report: ${result.reportPath}`);
    console.log(`🖼️ Images: ${result.hasImages ? result.totalImages + ' embedded' : 'None found'}`);
    console.log(`📊 Total size: ${result.totalSizeKB.toFixed(1)} KB`);
    
    // Print a preview of the report content
    console.log('\n' + '='.repeat(80));
    console.log('📋 REPORT PREVIEW (first 500 chars):');
    console.log('='.repeat(80));
    console.log(result.reportContent.substring(0, 500) + '...');
    console.log('\n📄 Full report saved to: ' + result.reportPath);
  } catch (error) {
    console.error('Error generating enhanced image report:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { 
  generateEnhancedImageReport,
  convertImageToBase64,
  generateImageDisplayOptions
};
