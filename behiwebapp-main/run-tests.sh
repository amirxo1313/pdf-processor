#!/bin/bash

# Radio Javan E2E Test Runner Script

set -e

echo "🚀 Radio Javan E2E Test Runner"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if BASE_URL is set
if [ -z "$BASE_URL" ]; then
    echo -e "${YELLOW}⚠️  BASE_URL not set. Using default: http://localhost:3000${NC}"
    export BASE_URL="http://localhost:3000"
fi

echo -e "📍 Testing against: ${GREEN}$BASE_URL${NC}"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "🌐 Installing Playwright browsers..."
    npx playwright install chromium
    npx playwright install-deps
fi

# Create test-results directory
mkdir -p test-results

# Clear previous results
rm -rf test-results/*

# Function to run tests
run_tests() {
    local test_type=$1
    local test_file=$2

    echo -e "\n${GREEN}Running $test_type tests...${NC}"

    if [ -z "$test_file" ]; then
        npx playwright test
    else
        npx playwright test "$test_file"
    fi
}

# Parse command line arguments
case "$1" in
    "all")
        echo "🧪 Running all tests..."
        run_tests "all"
        ;;
    "mobile")
        echo "📱 Running mobile tests..."
        run_tests "mobile" "tests/e2e/mobile.spec.js"
        ;;
    "basic")
        echo "🎵 Running basic Radio Javan tests..."
        run_tests "basic" "tests/e2e/radiojavan.spec.js"
        ;;
    "ui")
        echo "🖥️  Opening Playwright UI mode..."
        npm run test:e2e:ui
        ;;
    "debug")
        echo "🐛 Running tests in debug mode..."
        npm run test:e2e:debug
        ;;
    "headed")
        echo "👀 Running tests in headed mode..."
        npm run test:e2e:headed
        ;;
    "docker")
        echo "🐳 Running tests in Docker..."
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        ;;
    "report")
        echo "📊 Opening test report..."
        npm run test:report
        ;;
    *)
        echo "Usage: ./run-tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  all      - Run all tests (default)"
        echo "  mobile   - Run mobile-specific tests"
        echo "  basic    - Run basic Radio Javan tests"
        echo "  ui       - Open Playwright UI mode"
        echo "  debug    - Run in debug mode"
        echo "  headed   - Run with visible browser"
        echo "  docker   - Run tests in Docker container"
        echo "  report   - Open HTML test report"
        echo ""
        echo "Environment Variables:"
        echo "  BASE_URL - URL of the app to test (default: http://localhost:3000)"
        echo ""
        echo "Examples:"
        echo "  ./run-tests.sh all"
        echo "  BASE_URL=https://myapp.com ./run-tests.sh mobile"
        echo "  ./run-tests.sh ui"
        exit 1
        ;;
esac

# Check test results
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Tests completed successfully!${NC}"

    # Show summary if JSON report exists
    if [ -f "test-results/results.json" ]; then
        echo -e "\n📊 Test Summary:"
        node -e "
        const results = require('./test-results/results.json');
        const stats = results.stats || {};
        console.log('  Total:', stats.expected || 0);
        console.log('  Passed:', (stats.expected || 0) - (stats.unexpected || 0) - (stats.flaky || 0));
        console.log('  Failed:', stats.unexpected || 0);
        console.log('  Flaky:', stats.flaky || 0);
        console.log('  Duration:', ((stats.duration || 0) / 1000).toFixed(2), 'seconds');
        " 2>/dev/null || echo "  (Could not parse results.json)"
    fi

    echo -e "\n📁 Results saved in: ${GREEN}test-results/${NC}"
    echo -e "📊 View HTML report: ${GREEN}npm run test:report${NC}"
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    echo -e "📊 View detailed report: ${GREEN}npm run test:report${NC}"
    exit 1
fi
