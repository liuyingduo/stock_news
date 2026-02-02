
"""
SSE WAF Solver
Solves the Acunetix/Aliyun WAF challenge (acw_sc__v2)
"""
import re

def solve_sse_waf(html_content: str) -> str:
    """
    Solves the JS challenge and returns the acw_sc__v2 cookie value.
    
    Args:
        html_content: The HTML content containing the JS challenge
        
    Returns:
        The calculated acw_sc__v2 cookie value
    """
    # 1. Extract arg1
    # var arg1='6A1BD91A326E6D59624B3D30A11D8797179D2ABF';
    match = re.search(r"var arg1='([0-9A-F]+)';", html_content)
    if not match:
        print("Could not find arg1 in HTML")
        return ""
    
    arg1 = match.group(1)
    
    # 2. Define constants
    # From the JS: var posList=[...]
    pos_list = [
        0xf, 0x23, 0x1d, 0x18, 0x21, 0x10, 0x1, 0x26, 0xa, 0x9, 
        0x13, 0x1f, 0x28, 0x1b, 0x16, 0x17, 0x19, 0xd, 0x6, 0xb, 
        0x27, 0x12, 0x14, 0x8, 0xe, 0x15, 0x20, 0x1a, 0x2, 0x1e, 
        0x7, 0x4, 0x11, 0x5, 0x3, 0x1c, 0x22, 0x25, 0xc, 0x24
    ]
    
    # Base64 decoded 'MzAwMDE3NjAwMDg1NjAwNjA2MTUwMTUzMzAwMzY5MDAyNzgwMDM3NQ=='
    mask = "3000176000856006061501533003690027800375"
    
    # 3. Permutation (reordering)
    # JS: if(posList[j]==i+0x1){outPutList[j]=this_i;}
    output_list = [''] * 40
    for i in range(len(arg1)):
        this_i = arg1[i]
        for j in range(len(pos_list)):
            if pos_list[j] == i + 1:
                output_list[j] = this_i
                break
                
    arg2 = "".join(output_list)
    
    # 4. XOR with Mask
    arg3 = ""
    for i in range(0, len(arg2), 2):
        if i >= len(mask):
            break
            
        # Get 2 chars from arg2 and mask
        str_char_hex = arg2[i:i+2]
        mask_char_hex = mask[i:i+2]
        
        # Convert to int
        str_char = int(str_char_hex, 16)
        mask_char = int(mask_char_hex, 16)
        
        # XOR
        xor_char = str_char ^ mask_char
        
        # Convert back to hex (lowercase usually not strict but JS toString(16) is lowercase)
        xor_char_hex = format(xor_char, 'x')
        
        # Pad with 0 if length is 1
        if len(xor_char_hex) == 1:
            xor_char_hex = '0' + xor_char_hex
            
        arg3 += xor_char_hex
        
    return arg3

if __name__ == "__main__":
    # Test with user provided example
    # var arg1='6A1BD91A326E6D59624B3D30A11D8797179D2ABF';
    test_html = "var arg1='6A1BD91A326E6D59624B3D30A11D8797179D2ABF';"
    cookie = solve_sse_waf(test_html)
    print(f"Calculated Cookie: {cookie}")
    # Expected result? We don't have it, but we can verify logic matches JS
