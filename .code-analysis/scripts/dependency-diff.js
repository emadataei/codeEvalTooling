const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Generates a dependency graph diff using madge for changed files
 * Returns Mermaid diagram showing dependencies within the PR scope
 */
async function generateDependencyDiff(changedFiles = []) {
  try {
    // Try to use madge if available
    const madge = require('madge');
    
    // Filter for JavaScript/TypeScript files
    const codeFiles = changedFiles.filter(f => 
      f.match(/\.(js|jsx|ts|tsx|mjs|cjs)$/) && 
      !f.includes('node_modules') &&
      !f.includes('.test.') &&
      !f.includes('.spec.')
    );
    
    if (codeFiles.length === 0) {
      return null;
    }
    
    // Generate dependency tree for changed files
    const dependencies = await madge(codeFiles, {
      fileExtensions: ['js', 'jsx', 'ts', 'tsx'],
      excludeRegExp: [/node_modules/, /\.test\./, /\.spec\./],
    });
    
    const graph = dependencies.obj();
    const circular = dependencies.circular();
    
    // Generate Mermaid diagram focused on PR changes
    let mermaidDiagram = '```mermaid\ngraph TD\n';
    
    // Track edges to avoid duplicates
    const edges = new Set();
    
    // Add nodes and edges for changed files and their dependencies
    Object.entries(graph).forEach(([file, deps]) => {
      const fileName = path.basename(file, path.extname(file));
      const nodeId = fileName.replace(/[^a-zA-Z0-9]/g, '_');
      
      deps.forEach(dep => {
        const depName = path.basename(dep, path.extname(dep));
        const depId = depName.replace(/[^a-zA-Z0-9]/g, '_');
        
        edges.add(`    ${nodeId}[${fileName}] --> ${depId}[${depName}]`);
      });
    });
    
    // Add all edges to diagram
    Array.from(edges).forEach(edge => {
      mermaidDiagram += edge + '\n';
    });
    
    // Add styling for circular dependencies
    if (circular.length > 0) {
      mermaidDiagram += '\n    %% Circular dependency styling\n';
      circular.forEach(cycle => {
        cycle.forEach(file => {
          const fileName = path.basename(file, path.extname(file));
          const nodeId = fileName.replace(/[^a-zA-Z0-9]/g, '_');
          mermaidDiagram += `    class ${nodeId} circular\n`;
        });
      });
      
      mermaidDiagram += '    classDef circular fill:#ffebee,stroke:#f44336,stroke-width:3px\n';
    }
    
    // Add styling for changed files
    codeFiles.forEach(file => {
      const fileName = path.basename(file, path.extname(file));
      const nodeId = fileName.replace(/[^a-zA-Z0-9]/g, '_');
      mermaidDiagram += `    class ${nodeId} changed\n`;
    });
    
    mermaidDiagram += '    classDef changed fill:#e8f5e8,stroke:#4caf50,stroke-width:2px\n';
    mermaidDiagram += '```\n';
    
    return {
      diagram: mermaidDiagram,
      stats: {
        totalFiles: codeFiles.length,
        totalDependencies: Object.keys(graph).length,
        circularDependencies: circular,
        maxDepth: getMaxDependencyDepth(graph)
      }
    };
    
  } catch (error) {
    console.log('Madge not available or error generating dependency graph:', error.message);
    
    // Fallback: Simple file relationship analysis
    return generateSimpleDependencyDiff(changedFiles);
  }
}

/**
 * Fallback dependency analysis when madge is not available
 */
function generateSimpleDependencyDiff(changedFiles) {
  const codeFiles = changedFiles.filter(f => 
    f.match(/\.(js|jsx|ts|tsx|mjs|cjs)$/) && 
    !f.includes('node_modules')
  );
  
  if (codeFiles.length === 0) {
    return null;
  }
  
  // Simple import/require analysis
  const dependencies = {};
  
  codeFiles.forEach(file => {
    try {
      if (fs.existsSync(file)) {
        const content = fs.readFileSync(file, 'utf-8');
        const imports = extractImports(content);
        dependencies[file] = imports.filter(imp => 
          changedFiles.some(cf => imp.includes(path.basename(cf, path.extname(cf))))
        );
      }
    } catch (error) {
      console.log(`Error reading file ${file}:`, error.message);
    }
  });
  
  // Generate simple Mermaid diagram
  let mermaidDiagram = '```mermaid\ngraph TD\n';
  
  Object.entries(dependencies).forEach(([file, deps]) => {
    const fileName = path.basename(file, path.extname(file));
    const nodeId = fileName.replace(/[^a-zA-Z0-9]/g, '_');
    
    if (deps.length === 0) {
      mermaidDiagram += `    ${nodeId}[${fileName}]\n`;
    } else {
      deps.forEach(dep => {
        const depName = path.basename(dep, path.extname(dep));
        const depId = depName.replace(/[^a-zA-Z0-9]/g, '_');
        mermaidDiagram += `    ${nodeId}[${fileName}] --> ${depId}[${depName}]\n`;
      });
    }
  });
  
  mermaidDiagram += '    classDef default fill:#e3f2fd,stroke:#1976d2,stroke-width:2px\n';
  mermaidDiagram += '```\n';
  
  return {
    diagram: mermaidDiagram,
    stats: {
      totalFiles: codeFiles.length,
      totalDependencies: Object.keys(dependencies).length,
      circularDependencies: [],
      maxDepth: 1
    }
  };
}

/**
 * Extract import/require statements from file content
 */
function extractImports(content) {
  const imports = [];
  
  // ES6 imports
  const es6ImportRegex = /import.*?from\s+['"`]([^'"`]+)['"`]/g;
  let match;
  while ((match = es6ImportRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  // CommonJS requires
  const requireRegex = /require\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/g;
  while ((match = requireRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  return imports.filter(imp => !imp.startsWith('.') && !imp.includes('node_modules'));
}

/**
 * Calculate maximum dependency depth
 */
function getMaxDependencyDepth(graph, visited = new Set(), currentDepth = 0) {
  let maxDepth = currentDepth;
  
  Object.entries(graph).forEach(([file, deps]) => {
    if (!visited.has(file)) {
      visited.add(file);
      const depth = getMaxDependencyDepth(
        Object.fromEntries(Object.entries(graph).filter(([f]) => deps.includes(f))),
        new Set(visited),
        currentDepth + 1
      );
      maxDepth = Math.max(maxDepth, depth);
      visited.delete(file);
    }
  });
  
  return maxDepth;
}

/**
 * Get changed files from git diff
 */
function getChangedFiles() {
  try {
    const changedFiles = execSync('git diff --name-only origin/main')
      .toString()
      .split('\n')
      .filter(f => f.trim() && fs.existsSync(f.trim()));
    
    return changedFiles;
  } catch (error) {
    console.log('Error getting changed files:', error.message);
    return [];
  }
}

module.exports = {
  generateDependencyDiff,
  generateSimpleDependencyDiff,
  getChangedFiles
};
