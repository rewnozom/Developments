const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

function analyzeBundle() {
  console.log(chalk.blue('📊 Analyzing bundle...'));

  try {
    // Generate stats file
    execSync('vite build --mode analyze', { stdio: 'inherit' });
    
    // Read and parse stats
    const stats = JSON.parse(fs.readFileSync('./stats.json', 'utf8'));
    
    // Analyze bundle size
    const totalSize = stats.assets.reduce((acc, asset) => acc + asset.size, 0);
    const formattedSize = (totalSize / 1024 / 1024).toFixed(2);
    
    console.log(chalk.green(`\nTotal bundle size: ${formattedSize} MB`));
    
    // List largest dependencies
    const dependencies = Object.entries(stats.modules)
      .map(([name, size]) => ({ name, size }))
      .sort((a, b) => b.size - a.size)
      .slice(0, 10);

    console.log(chalk.yellow('\nLargest dependencies:'));
    dependencies.forEach(({ name, size }) => {
      console.log(`${name}: ${(size / 1024).toFixed(2)} KB`);
    });

    // Cleanup
    fs.unlinkSync('./stats.json');
  } catch (error) {
    console.error(chalk.red('❌ Analysis failed:'), error);
    process.exit(1);
  }
}

analyzeBundle();
