#!/usr/bin/env python3
"""
Test script to verify Claude integration is working
This tests the core components without requiring actual API keys
"""

import asyncio
import sys
import os

def test_claude_client_import():
    """Test that Claude client can be imported"""
    try:
        from claude_client import ClaudeClient
        print("✅ Claude client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Claude client: {e}")
        return False

def test_claude_router_import():
    """Test that Claude router can be imported"""
    try:
        from claude_router import ClaudeRouter, FailureType, RoutingDecision
        print("✅ Claude router imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Claude router: {e}")
        return False

def test_claude_decision_engine_import():
    """Test that Claude decision engine can be imported"""
    try:
        from claude_decision_engine import ClaudeDecisionEngine, AnalysisComplexity
        print("✅ Claude decision engine imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Claude decision engine: {e}")
        return False

def test_main_py_import():
    """Test that main.py can be imported with Claude components"""
    try:
        # Add current directory to path so we can import main
        sys.path.insert(0, os.path.dirname(__file__))
        
        # This will fail if claude_router import fails
        from main import app
        print("✅ Main FastAPI app imported successfully with Claude integration")
        return True
    except ImportError as e:
        print(f"❌ Failed to import main app: {e}")
        return False

async def test_claude_client_instantiation():
    """Test that Claude client can be instantiated (without API key)"""
    try:
        from claude_client import ClaudeClient
        
        # Set a dummy API key to test instantiation
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        client = ClaudeClient()
        print("✅ Claude client instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate Claude client: {e}")
        return False

async def test_claude_router_instantiation():
    """Test that Claude router can be instantiated"""
    try:
        from claude_router import ClaudeRouter
        
        # Set a dummy API key to test instantiation
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        router = ClaudeRouter()
        print("✅ Claude router instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate Claude router: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Claude Integration")
    print("=" * 50)
    
    tests = [
        ("Claude Client Import", test_claude_client_import),
        ("Claude Router Import", test_claude_router_import),
        ("Claude Decision Engine Import", test_claude_decision_engine_import),
        ("Main App Import", test_main_py_import),
        ("Claude Client Instantiation", test_claude_client_instantiation),
        ("Claude Router Instantiation", test_claude_router_instantiation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Claude integration is ready.")
        print("\n📋 Next steps:")
        print("1. Add your ANTHROPIC_API_KEY to the .env file")
        print("2. Install dependencies: pip install anthropic")
        print("3. Start the application")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)