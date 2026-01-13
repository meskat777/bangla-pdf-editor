"""
Professional Unicode to Bijoy Converter
Based on industry-standard mapping tables

This module converts Unicode Bengali text to Bijoy (ANSI) encoding
for proper rendering in Bijoy fonts like SutonnyMJ, Sushree, etc.

References:
- Bijoy Keyboard Layout: Standard ANSI encoding for Bengali
- Unicode Bengali Range: U+0980 to U+09FF
- Gemini Recommendation: Use professional converter for production
"""

class UnicodeToBijoyConverter:
    """
    Convert Unicode Bengali to Bijoy ANSI encoding
    
    Key Insight (from Gemini):
    - Unicode 'ক' = U+0995
    - Bijoy 'ক' = 'K' (ASCII 75)
    - যুক্তাক্ষর and কার have completely different positions
    """
    
    def __init__(self):
        # Unicode to Bijoy mapping table
        self.unicode_to_bijoy_map = self._build_mapping()
        
    def _build_mapping(self):
        """Build comprehensive Unicode → Bijoy mapping"""
        
        mapping = {}
        
        # Vowels (স্বরবর্ণ)
        mapping['অ'] = 'A'
        mapping['আ'] = 'Av'  # Two characters!
        mapping['ই'] = 'B'
        mapping['ঈ'] = 'C'
        mapping['উ'] = 'D'
        mapping['ঊ'] = 'E'
        mapping['ঋ'] = 'F'
        mapping['এ'] = 'G'
        mapping['ঐ'] = 'H'
        mapping['ও'] = 'I'
        mapping['ঔ'] = 'J'
        
        # Consonants (ব্যঞ্জনবর্ণ)
        mapping['ক'] = 'K'
        mapping['খ'] = 'L'
        mapping['গ'] = 'M'
        mapping['ঘ'] = 'N'
        mapping['ঙ'] = 'O'
        mapping['চ'] = 'P'
        mapping['ছ'] = 'Q'
        mapping['জ'] = 'R'
        mapping['ঝ'] = 'S'
        mapping['ঞ'] = 'T'
        mapping['ট'] = 'U'
        mapping['ঠ'] = 'V'
        mapping['ড'] = 'W'
        mapping['ঢ'] = 'X'
        mapping['ণ'] = 'Y'
        mapping['ত'] = 'Z'
        mapping['থ'] = '_'
        mapping['দ'] = '`'
        mapping['ধ'] = 'a'
        mapping['ন'] = 'b'
        mapping['প'] = 'c'
        mapping['ফ'] = 'd'
        mapping['ব'] = 'e'
        mapping['ভ'] = 'f'
        mapping['ম'] = 'g'
        mapping['য'] = 'h'
        mapping['র'] = 'i'
        mapping['ল'] = 'j'
        mapping['শ'] = 'k'
        mapping['ষ'] = 'l'
        mapping['স'] = 'm'
        mapping['হ'] = 'n'
        mapping['ড়'] = 'o'
        mapping['ঢ়'] = 'p'
        mapping['য়'] = 'q'
        mapping['ৎ'] = 't'
        
        # Vowel signs (কার)
        mapping['া'] = 'v'   # া-কার
        mapping['ি'] = 'w'   # ি-কার
        mapping['ী'] = 'x'   # ী-কার
        mapping['ু'] = 'y'   # ু-কার
        mapping['ূ'] = 'z'   # ূ-কার
        mapping['ৃ'] = '~'   # ঋ-কার
        mapping['ে'] = '†'   # ে-কার
        mapping['ৈ'] = '‡'   # ৈ-কার
        mapping['ো'] = 'ª'   # ো-কার (ে + া)
        mapping['ৌ'] = 'º'   # ৌ-কার (ে + ৗ)
        
        # Numbers (সংখ্যা)
        mapping['০'] = '0'
        mapping['১'] = '1'
        mapping['২'] = '2'
        mapping['৩'] = '3'
        mapping['৪'] = '4'
        mapping['৫'] = '5'
        mapping['৬'] = '6'
        mapping['৭'] = '7'
        mapping['৮'] = '8'
        mapping['৯'] = '9'
        
        # Special marks
        mapping['ং'] = 's'   # অনুস্বার (ং)
        mapping['ঃ'] = ':'   # বিসর্গ
        mapping['ঁ'] = '^'   # চন্দ্রবিন্দু
        mapping['্'] = '&'   # হসন্ত/হলন্ত
        
        # Common conjuncts (যুক্তাক্ষর)
        mapping['ক্ষ'] = '±'
        mapping['ক্র'] = '²'
        mapping['ক্ত'] = 'µ'
        mapping['ঞ্জ'] = '³'
        mapping['হ্ম'] = '´'
        mapping['গ্ধ'] = '¶'
        mapping['জ্জ'] = '·'
        mapping['ঞ্চ'] = '¸'
        mapping['ত্ত'] = '¹'
        mapping['দ্ধ'] = '»'
        mapping['দ্ম'] = '¼'
        mapping['ন্থ'] = '½'
        mapping['ন্ড'] = '¾'
        mapping['ন্ধ'] = '¿'
        mapping['স্থ'] = 'À'
        mapping['ঙ্গ'] = 'Á'
        mapping['ঙ্ক'] = 'Â'
        mapping['ব্জ'] = 'Ã'
        mapping['ব্দ'] = 'Ä'
        mapping['ব্ধ'] = 'Å'
        mapping['ভ্র'] = 'Æ'
        mapping['ম্ন'] = 'Ç'
        mapping['ম্ম'] = 'È'
        mapping['ল্ল'] = 'É'
        mapping['শ্চ'] = 'Ê'
        mapping['শ্র'] = 'Ë'
        mapping['ষ্ণ'] = 'Ì'
        mapping['স্ক'] = 'Í'
        mapping['স্ট'] = 'Î'
        mapping['স্ন'] = 'Ï'
        mapping['স্ফ'] = 'Ð'
        mapping['হ্ন'] = 'Ñ'
        mapping['হ্র'] = 'Ò'
        mapping['ত্র'] = '°'
        
        # র-ফলা and য-ফলা
        mapping['্র'] = 'Ó'   # র-ফলা
        mapping['র্'] = '©'   # রেফ
        mapping['্য'] = '¨'   # য-ফলা
        
        return mapping
    
    def convert(self, unicode_text):
        """
        Convert Unicode Bengali text to Bijoy encoding
        
        Args:
            unicode_text (str): Unicode Bengali text
            
        Returns:
            str: Bijoy-encoded text (ANSI)
            
        Example:
            >>> converter = UnicodeToBijoyConverter()
            >>> converter.convert('আমি')
            'Avgw'
        """
        if not unicode_text:
            return unicode_text
        
        result = []
        i = 0
        
        while i < len(unicode_text):
            # Try 3-character combinations first (complex যুক্তাক্ষর)
            if i + 2 < len(unicode_text):
                three_char = unicode_text[i:i+3]
                if three_char in self.unicode_to_bijoy_map:
                    result.append(self.unicode_to_bijoy_map[three_char])
                    i += 3
                    continue
            
            # Try 2-character combinations (like আ = Av, or যুক্তাক্ষর)
            if i + 1 < len(unicode_text):
                two_char = unicode_text[i:i+2]
                if two_char in self.unicode_to_bijoy_map:
                    result.append(self.unicode_to_bijoy_map[two_char])
                    i += 2
                    continue
            
            # Single character
            char = unicode_text[i]
            if char in self.unicode_to_bijoy_map:
                result.append(self.unicode_to_bijoy_map[char])
            else:
                # Keep unmapped characters as-is (spaces, English, etc.)
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def is_unicode_bengali(self, text):
        """Check if text contains Unicode Bengali characters"""
        return any('\u0980' <= c <= '\u09FF' for c in text)
    
    def is_bijoy_font(self, font_name):
        """Detect if font is a Bijoy font"""
        if not font_name:
            return False
        
        bijoy_fonts = [
            'sutonnymj', 'sushree', 'solaiman', 'solaimanlpi',
            'kalpurush', 'nikosh', 'likhan', 'siyam', 'ekushey'
        ]
        
        return any(bijoy_font in font_name.lower() for bijoy_font in bijoy_fonts)


# Global converter instance
_converter = UnicodeToBijoyConverter()

def unicode_to_bijoy(text):
    """
    Helper function: Convert Unicode to Bijoy
    
    Usage:
        from backend.utils.unicode_to_bijoy_converter import unicode_to_bijoy
        bijoy_text = unicode_to_bijoy('আমি বাংলায় লিখি')
    """
    return _converter.convert(text)

def is_unicode_bengali(text):
    """Check if text is Unicode Bengali"""
    return _converter.is_unicode_bengali(text)

def is_bijoy_font(font_name):
    """Check if font is Bijoy font"""
    return _converter.is_bijoy_font(font_name)
