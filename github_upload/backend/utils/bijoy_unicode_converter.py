"""
Bijoy to Unicode Converter
Converts legacy Bijoy/ANSI Bengali text to Unicode

This module uses the bijoy2unicode library for comprehensive and accurate conversion.
Source: https://github.com/Mad-FOX/bijoy2unicode
"""

try:
    # Try to import from installed package first
    from bijoy2unicode import converter as bijoy_converter
    BIJOY2UNICODE_AVAILABLE = True
except ImportError:
    try:
        # Try to import from local copy
        from .bijoy2unicode import converter as bijoy_converter
        BIJOY2UNICODE_AVAILABLE = True
    except ImportError:
        BIJOY2UNICODE_AVAILABLE = False
        print("Warning: bijoy2unicode not available. Using fallback implementation.")

class BijoyUnicodeConverter:
    def __init__(self):
        # Use bijoy2unicode if available
        if BIJOY2UNICODE_AVAILABLE:
            self.converter = bijoy_converter.Unicode()
            self.use_advanced = True
        else:
            self.use_advanced = False
        # Complex mappings (must be checked first - longer sequences)
        self.complex_map = {
            # Two-character sequences (must be first to match before single chars)
            'Av': 'আ',
            '¯‹': 'স্ক', '\u00AF\u2039': 'স্ক',  # ska (school pattern)
            # Complex conjuncts
            '±': 'ক্ষ', '²': 'ক্র', '³': 'ঞ্জ', '´': 'হ্ম',
            'µ': 'ক্ত', '¶': 'গ্ধ', '·': 'জ্জ', '¸': 'ঞ্চ',
            '¹': 'ত্ত', '»': 'দ্ধ', '¼': 'দ্ম',
            '½': 'ন্থ', '¾': 'ন্ড', '¿': 'ন্ধ', 'À': 'স্থ',
            'Á': 'ঙ্গ', 'Â': 'ঙ্ক', 'Ã': 'ব্জ', 'Ä': 'ব্দ',
            'Å': 'ব্ধ', 'Æ': 'ভ্র', 'Ç': 'ম্ন', 'È': 'ম্ম',
            'É': 'ল্ল', 'Ê': 'শ্চ', 'Ë': 'শ্র', 'Ì': 'ষ্ণ',
            'Í': 'স্ক', 'Î': 'স্ট', 'Ï': 'স্ন', 'Ð': 'স্ফ',
            'Ñ': 'হ্ন', 'Ò': 'হ্র', 'Ó': '্র', 'Ô': 'র্',
            '©': 'র্', '\u00A9': 'র্',  # Ref (r-phala)
            '¨': 'য়', '¯': '্র', '\u00AF': '্র',  # R-phala
            '°': 'ত্র',
            'Ö': '্রে', '\u00D6': '্রে',  # Ref + e-kar
            '‹': 'ু', '\u2039': 'ু',  # u-kar alternate
        }
        
        # Bijoy to Unicode mapping table
        self.bijoy_map = {
            # Vowels
            'A': 'অ', 'B': 'ই', 'C': 'ঈ', 'D': 'উ', 'E': 'ঊ',
            'F': 'ঋ', 'G': 'এ', 'H': 'ঐ', 'I': 'ও', 'J': 'ঔ',
            
            # Consonants
            'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ',
            'P': 'চ', 'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ',
            'U': 'ট', 'V': 'ঠ', 'W': 'ড', 'X': 'ঢ', 'Y': 'ণ',
            'Z': 'ত', '_': 'থ', '`': 'দ', 'a': 'ধ', 'b': 'ন',
            'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ', 'g': 'ম',
            'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ',
            'm': 'স', 'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়',
            'r': 'র', 's': 'ং',  # s is anusvara (ng), not ষ
            # Note: 't' is handled specially in conversion logic (can be ত or :)
            'u': 'ু',  # u is u-kar
            
            # Kar (vowel signs) - these need special handling for reordering
            'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ূ',
            '~': 'ৃ', 
            '‡': 'ে', '\u2021': 'ে',  # e-kar (both encodings)
            '†': 'ৈ', '\u2020': 'ৈ',  # oi-kar (both encodings)
            'ª': 'ো', 'º': 'ৌ',
            
            # Numbers
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
            
            # Other marks
            '—': 'ঃ', '|': '।', '\\': 'ঁ', '^': 'ঁ',
            '&': 'ং', ':': 'ঃ',
            '„': 'র্', '\u201E': 'র্',  # Ref (r-phala)
            'Ë': 'শ্র', '\u00CB': 'শ্র',  # Shr
            'ÿ': 'ক্ষ', '\u00FF': 'ক্ষ',  # Ksh (ক্ষ)
        }
        
        # Hasanta/Halant
        self.hasanta = '্'
        
        # Vowel signs that need reordering (appear visually before consonant in Unicode)
        self.reorder_kars = ['ি', 'ী']
        
        # Vowel signs that should attach to the NEXT consonant (not previous)
        # When these appear after another vowel sign, they belong to the next consonant
        self.attach_next_kars = ['ে', 'ৈ']
        
    def is_bijoy_text(self, text):
        """Detect if text is in Bijoy encoding"""
        # Check for common Bijoy patterns
        bijoy_indicators = [
            # Bijoy uses ASCII characters for Bengali
            any(c in text for c in ['Av', '©', '¨', '¯', '°']),
            # Check for Bijoy font names
            any(font in text.lower() for font in ['sutonnymj', 'solaiman', 'kalpurush'])
        ]
        
        # Check if text has ASCII-range characters but font suggests Bengali
        has_ascii = any(ord(c) < 128 for c in text if c.isalpha())
        has_bijoy_chars = any(128 <= ord(c) <= 255 for c in text)
        
        return any(bijoy_indicators) or (has_ascii and has_bijoy_chars)
    
    def convert_to_unicode(self, text):
        """Convert Bijoy text to Unicode"""
        if not text:
            return text
        
        # Use bijoy2unicode library if available (more accurate)
        if self.use_advanced:
            try:
                return self.converter.convertBijoyToUnicode(text)
            except Exception as e:
                print(f"Warning: bijoy2unicode conversion failed: {e}. Using fallback.")
                # Fall through to fallback implementation
        
        # Fallback implementation (original code)
        # If already Unicode Bengali, return as is
        if any('\u0980' <= c <= '\u09FF' for c in text):
            return text
        
        result = []
        i = 0
        
        while i < len(text):
            # Try 3-character mapping first (complex conjuncts)
            if i + 2 < len(text):
                three_char = text[i:i+3]
                if three_char in self.complex_map:
                    result.append(self.complex_map[three_char])
                    i += 3
                    continue
            
            # Try 2-character mapping
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in self.complex_map:
                    result.append(self.complex_map[two_char])
                    i += 2
                    continue
            
            # Try single character in complex_map (for special chars)
            char = text[i]
            if char in self.complex_map:
                result.append(self.complex_map[char])
                i += 1
                continue
            
            # Special handling for 't' (can be ত or :)
            if char == 't':
                # Check context: if followed by space or end of text, it's likely a colon
                if i + 1 >= len(text) or text[i + 1] == ' ':
                    result.append(':')
                    i += 1
                    continue
                else:
                    # Within a word, it's the consonant ত
                    result.append('ত')
                    i += 1
                    continue
            
            # Single character mapping from bijoy_map
            if char in self.bijoy_map:
                converted_char = self.bijoy_map[char]
                
                # Check if this is a kar that should attach to next consonant
                # This happens when the kar comes after another vowel sign
                if converted_char in self.attach_next_kars and result:
                    # Check if previous char is a vowel sign (not a consonant)
                    prev_char = result[-1]
                    is_prev_vowel_sign = (prev_char in ['া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ'])
                    
                    if is_prev_vowel_sign:
                        # Look ahead for next consonant
                        if i + 1 < len(text):
                            next_char = text[i + 1]
                            if next_char in self.bijoy_map or next_char in self.complex_map:
                                # We'll add this kar AFTER processing the next consonant
                                # Store it temporarily and process next consonant
                                pending_kar = converted_char
                                i += 1
                                
                                # Now process the next character (consonant)
                                if i < len(text):
                                    next_char = text[i]
                                    if next_char in self.bijoy_map:
                                        next_converted = self.bijoy_map[next_char]
                                        result.append(next_converted)
                                        result.append(pending_kar)
                                        i += 1
                                        continue
                
                # Handle reordering for i-kar and ii-kar
                # These vowel signs appear BEFORE the consonant in Unicode
                # but are typed AFTER in Bijoy
                if converted_char in self.reorder_kars:
                    # Look ahead to find the next consonant to attach to
                    if i + 1 < len(text):
                        next_char = text[i + 1]
                        # Check if next char will be a consonant
                        if next_char in self.bijoy_map:
                            next_converted = self.bijoy_map[next_char]
                            # Check if it's a consonant (not a vowel or kar)
                            if ('\u0995' <= next_converted <= '\u09B9' or 
                                next_converted in ['ড়', 'ঢ়', 'য়']):
                                # Store the kar, it will be reordered when we add the consonant
                                result.append(converted_char)
                                i += 1
                                continue
                    
                    # If no consonant follows, just add it normally
                    result.append(converted_char)
                    i += 1
                    continue
                
                # If previous char is a reorder kar, we need to swap
                if result and result[-1] in self.reorder_kars:
                    # Check if current char is a consonant
                    if ('\u0995' <= converted_char <= '\u09B9' or 
                        converted_char in ['ড়', 'ঢ়', 'য়']):
                        # Swap: consonant should come before kar in result
                        kar = result.pop()
                        result.append(converted_char)
                        result.append(kar)
                        i += 1
                        continue
                
                result.append(converted_char)
                i += 1
            else:
                # Keep unmapped characters as is (spaces, punctuation, English)
                result.append(char)
                i += 1
        
        return ''.join(result)
    
    def convert_to_bijoy(self, text):
        """Convert Unicode text to Bijoy (reverse conversion)"""
        if not text:
            return text
        
        # Only available with bijoy2unicode library
        if self.use_advanced:
            try:
                return self.converter.convertUnicodeToBijoy(text)
            except Exception as e:
                print(f"Warning: Unicode to Bijoy conversion failed: {e}")
                return text
        
        # Fallback: return as-is if library not available
        print("Warning: Unicode to Bijoy conversion requires bijoy2unicode library")
        return text
    
    def convert_with_font_info(self, text, font_name):
        """Convert text based on font name"""
        # List of Bijoy fonts
        bijoy_fonts = [
            'sutonnymj', 'sutonnymj bold', 'sutonnymj italic',
            'solaiman', 'solaiman lipi',
            'kalpurush', 'nikosh', 'likhan',
            'siyam rupali', 'ekushey',
        ]
        
        # Check if font is Bijoy
        is_bijoy_font = any(bf in font_name.lower() for bf in bijoy_fonts)
        
        if is_bijoy_font or self.is_bijoy_text(text):
            return self.convert_to_unicode(text)
        
        return text

# Global converter instance
converter = BijoyUnicodeConverter()

def convert_bijoy_to_unicode(text, font_name=''):
    """Helper function to convert Bijoy to Unicode"""
    return converter.convert_with_font_info(text, font_name)

def is_bijoy_text(text):
    """Helper function to detect Bijoy text"""
    return converter.is_bijoy_text(text)
