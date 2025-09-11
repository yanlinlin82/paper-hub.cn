#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 源目录和目标目录
const sourceDir = path.join(__dirname, '..', 'node_modules', 'bootstrap', 'dist');
const targetDir = path.join(__dirname, '..', 'static', 'bootstrap');

// 确保目标目录存在
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

// 复制文件的函数
function copyFile(src, dest) {
  const destDir = path.dirname(dest);
  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }
  fs.copyFileSync(src, dest);
  console.log(`Copied: ${path.relative(process.cwd(), src)} -> ${path.relative(process.cwd(), dest)}`);
}

// 复制目录的函数
function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      copyFile(srcPath, destPath);
    }
  }
}

try {
  console.log('Building Bootstrap static files...');
  console.log(`Source: ${sourceDir}`);
  console.log(`Target: ${targetDir}`);
  
  // 复制整个dist目录
  copyDir(sourceDir, targetDir);
  
  console.log('✅ Bootstrap static files built successfully!');
  console.log(`Bootstrap files are now available in: ${path.relative(process.cwd(), targetDir)}`);
} catch (error) {
  console.error('❌ Error building static files:', error.message);
  process.exit(1);
}
