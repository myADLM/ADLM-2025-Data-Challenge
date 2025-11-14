#!/usr/bin/env python3
"""
Test script to verify all query modules can import the new LLM class correctly.
"""

import sys
import os

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_imports():
    """Test that all modules can import properly."""
    print("🧪 Testing module imports...")
    
    try:
        from llm import LLM, create_northwell_llm
        print("✅ LLM module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LLM module: {e}")
        return False
    
    # Change to query directory to test those imports
    query_dir = os.path.join(os.path.dirname(__file__), 'query')
    os.chdir(query_dir)
    
    try:
        from SOPQuery import SOPQuery
        print("✅ SOPQuery module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SOPQuery: {e}")
        return False
    
    try:
        from SOP_or_FDA import SOP_FDA
        print("✅ SOP_or_FDA module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SOP_or_FDA: {e}")
        return False
    
    try:
        from FDAQuery import FDAQuery
        print("✅ FDAQuery module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FDAQuery: {e}")
        return False
    
    return True

def test_instantiation():
    """Test that classes can be instantiated."""
    print("\n🔧 Testing class instantiation...")
    
    try:
        # Import classes
        sys.path.append('../modules')
        from llm import LLM
        
        # Change directory for imports
        query_dir = os.path.join(os.path.dirname(__file__), 'query')
        os.chdir(query_dir)
        
        from SOPQuery import SOPQuery
        from SOP_or_FDA import SOP_FDA
        from FDAQuery import FDAQuery
        
        # Test LLM instantiation
        llm = LLM()
        print(f"✅ LLM instantiated: {llm.provider} with model {llm.model}")
        
        # Test query class instantiation
        sop_query = SOPQuery(model="claude-3.7-sonnet", debug=0)
        print(f"✅ SOPQuery instantiated with model: {sop_query.model}")
        
        sop_fda = SOP_FDA(model="claude-3.7-sonnet", debug=0)
        print(f"✅ SOP_FDA instantiated with model: {sop_fda.model}")
        
        fda_query = FDAQuery(model="claude-3.7-sonnet", debug=0)
        print(f"✅ FDAQuery instantiated with model: {fda_query.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to instantiate classes: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Updated Query Modules")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return
    
    # Test instantiation
    if not test_instantiation():
        print("\n❌ Instantiation tests failed!")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Query modules successfully updated to use new LLM class.")

if __name__ == "__main__":
    main()