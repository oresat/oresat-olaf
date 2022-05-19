def strToHex(in_text):
    hex_val = 0x0
    for chrs in in_text:
        print("adding " + str(ord(chrs)) + "to " + str(hex_val))
        hex_val = (hex_val << (8))
        hex_val = hex_val + ord(chrs)

    return hex_val




strToHex("ABCD")
