#!/bin/bash
# Quick setup script untuk ADK GCP system

echo "🚀 ADK GCP Quick Setup"
echo "========================"

# Check Python version
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python3 not found"
    exit 1
fi

# Check virtual environment
echo "🔧 Checking virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "   ✅ Virtual environment active: $(basename $VIRTUAL_ENV)"
else
    echo "   ⚠️  No virtual environment detected"
    echo "   📝 Recommendation: Create and activate venv"
    echo "      python3 -m venv .venv && source .venv/bin/activate"
fi

# Check if we're in the right directory
echo "📁 Checking project structure..."
if [ -f "adk_cli_agent/tools/gcp/agents/root_agent.py" ]; then
    echo "   ✅ ADK project structure found"
else
    echo "   ❌ Not in ADK project directory"
    echo "   📝 Please run from project root"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if python3 -c "import adk_cli_agent.tools.gcp.agents" 2>/dev/null; then
    echo "   ✅ ADK modules importable"
else
    echo "   ⚠️  Installing in development mode..."
    pip install -e .
fi

# Check for API keys
echo "🔑 Checking API keys..."
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "   ✅ GOOGLE_API_KEY is set"
elif [ -n "$OPENAI_API_KEY" ]; then
    echo "   ✅ OPENAI_API_KEY is set"
else
    echo "   ⚠️  No API keys found"
    echo "   📝 For full functionality, set one of:"
    echo "      export GOOGLE_API_KEY='your-key-here'"
    echo "      export OPENAI_API_KEY='your-key-here'"
fi

# Check GCP credentials (optional)
echo "☁️  Checking GCP credentials..."
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "   ✅ GOOGLE_APPLICATION_CREDENTIALS is set"
elif command -v gcloud &> /dev/null && gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
    echo "   ✅ gcloud authenticated: $ACTIVE_ACCOUNT"
else
    echo "   ⚠️  No GCP credentials found"
    echo "   📝 For real GCP operations, run:"
    echo "      gcloud auth application-default login"
fi

# Run quick test
echo "🧪 Running system test..."
if python3 quick_test.py > /dev/null 2>&1; then
    echo "   ✅ System test passed"
else
    echo "   ❌ System test failed"
    echo "   📝 Run: python3 quick_test.py"
    exit 1
fi

echo ""
echo "========================"
echo "🎉 Setup Complete!"
echo ""
echo "📚 Available Commands:"
echo "   python3 quick_test.py      - Quick system test"
echo "   python3 demo_system.py     - Full demo (no API needed)"
echo "   python3 interactive_demo.py - Interactive CLI"
echo ""
echo "📖 Documentation:"
echo "   cat RUNNING_GUIDE.md       - Full running guide"
echo "   cat GCP_TOOLS_ARCHITECTURE.md - Architecture docs"
echo ""

# Offer to run demo
read -p "🚀 Run interactive demo now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎯 Starting interactive demo..."
    python3 interactive_demo.py
fi
