#!/usr/bin/env python3
"""
Automated test runner for Ram Digital Twin project
Provides comprehensive testing capabilities with various options
"""
import subprocess
import sys
import os
import argparse
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results_dir = self.project_root / "test-results"
        self.reports_dir = self.project_root / "reports"
        
        # Ensure directories exist
        self.test_results_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        try:
            import playwright
            import pytest
            logger.info("✅ All dependencies installed")
            return True
        except ImportError as e:
            logger.error(f"❌ Missing dependency: {e}")
            logger.info("Run: pip install -r requirements.txt")
            return False
    
    def check_browser_installation(self):
        """Check if Playwright browsers are installed"""
        logger.info("🌐 Checking browser installation...")
        
        try:
            result = subprocess.run(
                ["playwright", "install", "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "is already installed" in result.stdout or result.returncode == 0:
                logger.info("✅ Browsers are installed")
                return True
            else:
                logger.warning("⚠️ Browsers may need installation")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Could not verify browser installation")
            return False
    
    def install_browsers(self):
        """Install Playwright browsers"""
        logger.info("📥 Installing browsers...")
        
        try:
            result = subprocess.run(
                ["playwright", "install", "chromium", "firefox"],
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Browsers installed successfully")
                return True
            else:
                logger.error("❌ Failed to install browsers")
                return False
        except subprocess.TimeoutExpired:
            logger.error("❌ Browser installation timeout")
            return False
    
    def run_unit_tests(self, verbose=False):
        """Run unit tests"""
        logger.info("🧪 Running unit tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "--tb=short",
            "-v" if verbose else "-q",
            f"--html={self.reports_dir}/unit_tests.html",
            "--self-contained-html"
        ]
        
        return self._run_test_command(cmd, "Unit tests")
    
    def run_integration_tests(self, verbose=False):
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "--tb=short",
            "-v" if verbose else "-q",
            f"--html={self.reports_dir}/integration_tests.html",
            "--self-contained-html"
        ]
        
        return self._run_test_command(cmd, "Integration tests")
    
    def run_e2e_tests(self, browser="chromium", headless=True, verbose=False):
        """Run end-to-end tests"""
        logger.info(f"🚀 Running E2E tests (browser: {browser}, headless: {headless})...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/",
            f"--browser={browser}",
            "--tb=short",
            "-v" if verbose else "-q",
            f"--html={self.reports_dir}/e2e_tests.html",
            "--self-contained-html",
            "--video=retain-on-failure",
            "--screenshot=only-on-failure"
        ]
        
        if not headless:
            cmd.append("--headed")
        
        return self._run_test_command(cmd, "E2E tests")
    
    def run_smoke_tests(self, browser="chromium"):
        """Run smoke tests for quick validation"""
        logger.info("💨 Running smoke tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "-m", "smoke",
            f"--browser={browser}",
            "--tb=line",
            "-q",
            f"--html={self.reports_dir}/smoke_tests.html",
            "--self-contained-html"
        ]
        
        return self._run_test_command(cmd, "Smoke tests")
    
    def run_all_tests(self, browser="chromium", headless=True, verbose=False):
        """Run all test suites"""
        logger.info("🎯 Running complete test suite...")
        
        results = {
            "unit": self.run_unit_tests(verbose),
            "e2e": self.run_e2e_tests(browser, headless, verbose)
        }
        
        # Only run integration tests if directory exists
        if (self.project_root / "tests" / "integration").exists():
            results["integration"] = self.run_integration_tests(verbose)
        
        return results
    
    def _run_test_command(self, cmd, test_type):
        """Execute test command and handle results"""
        start_time = time.time()
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            result = subprocess.run(
                cmd,
                timeout=600,  # 10 minutes timeout
                capture_output=True,
                text=True
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ {test_type} passed ({execution_time:.1f}s)")
                return {"success": True, "time": execution_time, "output": result.stdout}
            else:
                logger.error(f"❌ {test_type} failed ({execution_time:.1f}s)")
                logger.error(f"Error output: {result.stderr}")
                return {"success": False, "time": execution_time, "output": result.stderr}
        
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {test_type} timeout")
            return {"success": False, "time": 600, "output": "Test timeout"}
        
        except Exception as e:
            logger.error(f"💥 {test_type} error: {str(e)}")
            return {"success": False, "time": 0, "output": str(e)}
        
        finally:
            os.chdir(original_cwd)
    
    def generate_summary_report(self, results):
        """Generate summary report of all test results"""
        logger.info("📊 Generating summary report...")
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["success"])
        total_time = sum(r["time"] for r in results.values())
        
        report = f"""
# Test Execution Summary

## Overall Results
- **Total Test Suites**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Total Time**: {total_time:.1f}s
- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%

## Detailed Results
"""
        
        for test_type, result in results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            report += f"- **{test_type.title()}**: {status} ({result['time']:.1f}s)\n"
        
        # Save report
        report_file = self.reports_dir / "summary.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Summary report saved to {report_file}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("🎯 TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total: {total_tests} | Passed: {passed_tests} | Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}% | Time: {total_time:.1f}s")
        print("="*60)
        
        return passed_tests == total_tests

def main():
    parser = argparse.ArgumentParser(description="Run Ram Digital Twin tests")
    
    # Test type selection
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--all", action="store_true", default=True, help="Run all tests (default)")
    
    # Browser options
    parser.add_argument("--browser", default="chromium", 
                       choices=["chromium", "firefox", "webkit"],
                       help="Browser for E2E tests")
    parser.add_argument("--headed", action="store_true", 
                       help="Run E2E tests in headed mode (visible browser)")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--install-browsers", action="store_true",
                       help="Install Playwright browsers before testing")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    # Check dependencies
    if not runner.check_dependencies():
        sys.exit(1)
    
    # Install browsers if requested
    if args.install_browsers:
        if not runner.install_browsers():
            sys.exit(1)
    
    # Check browser installation for E2E tests
    if args.e2e or args.all or args.smoke:
        if not runner.check_browser_installation():
            logger.warning("Browser installation check failed, attempting to install...")
            if not runner.install_browsers():
                logger.error("Failed to install browsers, E2E tests may fail")
    
    # Determine which tests to run
    results = {}
    
    if args.unit:
        results["unit"] = runner.run_unit_tests(args.verbose)
    elif args.integration:
        results["integration"] = runner.run_integration_tests(args.verbose)
    elif args.e2e:
        results["e2e"] = runner.run_e2e_tests(args.browser, not args.headed, args.verbose)
    elif args.smoke:
        results["smoke"] = runner.run_smoke_tests(args.browser)
    else:  # default: run all
        results = runner.run_all_tests(args.browser, not args.headed, args.verbose)
    
    # Generate summary
    success = runner.generate_summary_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()