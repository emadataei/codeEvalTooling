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
 * Generate display options for an image with base64 embedding
 */
function generateImageDisplayOptions(imagePath, title, base64Data) {
  const fileName = path.basename(imagePath);
  let content = `### ${title}\n\n`;
  
  if (base64Data) {
    // Base64 embedded image - displays directly in GitHub comments
    content += `<img src="${base64Data}" alt="${title}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;" />\n\n`;
    
    // Provide technical details in a collapsible section
    content += `<details>\n`;
    content += `<summary>Image Details</summary>\n\n`;
    content += `- **File:** \`${fileName}\`\n`;
    content += `- **Size:** ${(Buffer.byteLength(base64Data.split(',')[1], 'base64') / 1024).toFixed(1)} KB\n`;
    content += `- **Format:** ${getImageFormat(fileName)}\n`;
    content += `- **Encoding:** Base64 embedded for instant viewing\n`;
    content += `\n</details>\n\n`;
  } else {
    // No image available - provide helpful information without broken links
    content += `> **Image not generated:** \`${fileName}\`\n\n`;
    content += `**Why this might happen:**\n`;
    content += `- Dependencies missing (matplotlib, seaborn, graphviz)\n`;
    content += `- Analysis scripts encountered errors\n`;
    content += `- No data available to visualize\n`;
    content += `- Project structure not compatible with this visual type\n\n`;
    content += `**To fix:** Check the workflow logs for specific error messages.\n\n`;
  }
  
  return content;
}

/**
 * Get readable image format name
 */
function getImageFormat(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  const formats = {
    '.png': 'PNG (Portable Network Graphics)',
    '.svg': 'SVG (Scalable Vector Graphics)', 
    '.jpg': 'JPEG (Joint Photographic Experts Group)',
    '.jpeg': 'JPEG (Joint Photographic Experts Group)',
    '.gif': 'GIF (Graphics Interchange Format)'
  };
  return formats[ext] || 'Unknown format';
}

/**
 * Main function to generate enhanced image report with embedded PNGs
 */
async function generateEnhancedImageReport() {
  console.log('Generating enhanced image report with PNG displays...');
  
  const outputsDir = '.code-analysis/outputs';
  const rootDir = '.';
  
  // Ensure outputs directory exists
  if (!fs.existsSync(outputsDir)) {
    fs.mkdirSync(outputsDir, { recursive: true });
    console.log(`Created outputs directory: ${outputsDir}`);
  }
  
  // Define images with their locations (check root first, then outputs)
  const images = {
    'change_heatmap.png': 'Change Impact Heatmap',
    'impact_heatmap.png': 'Change Impact Heatmap',
    'development_flow.png': 'Development Flow',
    'story_arc.gif': 'Story Arc Animation',
    'dependency_graph_pr.png': 'PR Dependencies'
  };
  
  // Also check for SVG alternatives
  const svgAlternatives = {
    'dependency_graph_pr.svg': 'PR Dependencies', 
    'development_flow.svg': 'Development Flow'
  };
  
  let reportContent = '## Enhanced PR Visuals\n\n';
  reportContent += '*Real-time analytics with embedded images for instant viewing*\n\n';
  
  let hasImages = false;
  let totalSize = 0;
  
  // Helper function to find image in multiple locations
  function findImage(filename) {
    const locations = [rootDir, outputsDir];
    for (const location of locations) {
      const imagePath = path.join(location, filename);
      if (fs.existsSync(imagePath)) {
        return imagePath;
      }
    }
    return null;
  }
  
  // Try PNG files first, then SVG alternatives
  const allImages = { ...images, ...svgAlternatives };
  
  for (const [filename, title] of Object.entries(allImages)) {
    const imagePath = findImage(filename);
    const base64Data = imagePath ? await convertImageToBase64(imagePath) : null;
    
    if (base64Data) {
      hasImages = true;
      const sizeKB = Buffer.byteLength(base64Data.split(',')[1], 'base64') / 1024;
      totalSize += sizeKB;
      
      reportContent += generateImageDisplayOptions(imagePath, title, base64Data);
      console.log(`✓ Embedded ${filename} from ${path.dirname(imagePath)} (${sizeKB.toFixed(1)} KB)`);
    } else {
      reportContent += generateImageDisplayOptions(filename, title, null);
      console.log(`✗ Image not found: ${filename}`);
    }
    
    reportContent += '---\n\n';
  }
  
  // Add summary section
  if (hasImages) {
    reportContent += `### Summary\n\n`;
    reportContent += `- **Images Embedded:** ${Object.entries(allImages).filter(([filename]) => findImage(filename)).length}\n`;
    reportContent += `- **Total Size:** ${totalSize.toFixed(1)} KB\n`;
    reportContent += `- **Rendering Method:** Base64 embedded for instant GitHub viewing\n`;
    reportContent += `- **Compatibility:** Works in all GitHub markdown contexts\n\n`;
    
    if (totalSize > 500) {
      reportContent += `> **Note:** Large total size (${totalSize.toFixed(1)} KB). Consider optimizing images if comments become slow to load.\n\n`;
    }
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
  return `### No Images Generated\n\n` +
         `**Possible reasons:**\n` +
         `- **Missing Dependencies:** matplotlib, seaborn, graphviz, or other visualization tools not installed\n` +
         `- **No Analyzable Content:** Project structure doesn't contain dependency files or code changes\n` +
         `- **Script Errors:** Analysis scripts encountered errors during execution\n` +
         `- **Empty Changes:** No significant changes detected to visualize\n\n` +
         `**To resolve:**\n` +
         `1. Check the workflow logs for specific error messages\n` +
         `2. Ensure all required dependencies are installed in the CI environment\n` +
         `3. Verify your project has dependencies that can be analyzed (package.json, requirements.txt, etc.)\n` +
         `4. Make sure there are actual code changes in the PR\n\n` +
         `*Images will appear here automatically when analysis completes successfully.*\n\n`;
}

async function generateFileListingSection(outputsDir) {
  let content = '### Generated Files\n\n';
  
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
        const status = isImage ? 'Image' : 'Data';
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
  if (['.json'].includes(ext)) return 'Data';
  if (['.md'].includes(ext)) return 'Report';
  if (['.txt'].includes(ext)) return 'Text';
  if (['.png', '.jpg', '.gif', '.svg'].includes(ext)) return 'Image';
  return 'File';
}

// Main execution
async function main() {
  try {
    const result = await generateEnhancedImageReport();
    console.log('\nEnhanced image report generation complete!');
    console.log(`Report: ${result.reportPath}`);
    console.log(`Images: ${result.hasImages ? result.totalImages + ' embedded' : 'None found'}`);
    console.log(`Total size: ${result.totalSizeKB.toFixed(1)} KB`);
    
    // Print a preview of the report content
    console.log('\n' + '='.repeat(80));
    console.log('REPORT PREVIEW (first 500 chars):');
    console.log('='.repeat(80));
    console.log(result.reportContent.substring(0, 500) + '...');
    console.log('\nFull report saved to: ' + result.reportPath);
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
