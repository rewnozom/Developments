const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const chalk = require('chalk');

// Build configuration
const config = {
  outDir: 'dist',
  analyze: process.argv.includes('--analyze'),
  sourcemap: process.argv.includes('--sourcemap'),
};

function cleanup() {
  console.log(chalk.blue('🧹 Cleaning up...'));
  try {
    fs.rmSync(path.resolve(config.outDir), { recursive: true, force: true });
  } catch (error) {
    console.warn('No dist folder to clean');
  }
}

function buildApp() {
  console.log(chalk.blue('🏗️  Building application...'));
  
  const buildCommand = [
    'vite build',
    config.sourcemap && '--sourcemap',
    config.analyze && '--analyze',
  ]
    .filter(Boolean)
    .join(' ');

  try {
    execSync(buildCommand, { stdio: 'inherit' });
    console.log(chalk.green('✅ Build completed successfully!'));
  } catch (error) {
    console.error(chalk.red('❌ Build failed:'), error);
    process.exit(1);
  }
}

function verifyBuild() {
  console.log(chalk.blue('🔍 Verifying build...'));
  
  const distPath = path.resolve(config.outDir);
  if (!fs.existsSync(distPath)) {
    console.error(chalk.red('❌ Build verification failed: dist folder not found'));
    process.exit(1);
  }

  const files = fs.readdirSync(distPath);
  const hasIndex = files.some(file => file.startsWith('index.'));
  const hasAssets = files.some(file => file === 'assets');

  if (!hasIndex || !hasAssets) {
    console.error(chalk.red('❌ Build verification failed: Missing required files'));
    process.exit(1);
  }

  console.log(chalk.green('✅ Build verification passed!'));
}

// Run build process
cleanup();
buildApp();
verifyBuild();
