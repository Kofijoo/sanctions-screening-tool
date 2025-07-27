"""Test preprocessing components"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.preprocessing.cleaner import TextCleaner
from app.preprocessing.normalizer import NameNormalizer
from app.preprocessing.processor import NameProcessor

def test_text_cleaner():
    """Test text cleaning functionality"""
    cleaner = TextCleaner()
    
    # Test basic cleaning
    result = cleaner.clean("DR. MOHAMMED AL-QAEDA!!!")
    expected = "dr mohammed alqaeda"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    
    # Test title removal
    result = cleaner.remove_titles("dr mohammed al qaeda")
    expected = "mohammed al qaeda"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("✅ Text cleaner tests passed")

def test_name_normalizer():
    """Test name normalization"""
    normalizer = NameNormalizer()
    
    # Test transliteration
    result = normalizer.transliterate("محمد")  # Arabic for Mohammed
    assert len(result) > 0, "Transliteration should produce output"
    
    # Test Arabic name normalization
    result = normalizer.normalize_arabic_names("al qaeda")
    expected = "al qaeda"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("✅ Name normalizer tests passed")

def test_name_processor():
    """Test complete name processing pipeline"""
    processor = NameProcessor()
    
    # Test single name processing
    result = processor.process_single("DR. MOHAMMED AL-QAEDA")
    
    assert 'original' in result
    assert 'cleaned' in result
    assert 'normalized' in result
    assert 'tokens' in result
    assert 'variants' in result
    
    assert result['original'] == "DR. MOHAMMED AL-QAEDA"
    assert len(result['tokens']) > 0
    assert len(result['variants']) > 0
    
    print("✅ Name processor tests passed")

if __name__ == "__main__":
    test_text_cleaner()
    test_name_normalizer()
    test_name_processor()
    print("🎉 All preprocessing tests passed!")