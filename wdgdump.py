import sys,os,re,uuid

WDG_ENTRY_SIZE = 0x14

WMIACPI_REGFLAG_EXPENSIVE = 0x01
WMIACPI_REGFLAG_METHOD =0x02
WMIACPI_REGFLAG_STRING = 0x04
WMIACPI_REGFLAG_EVENT = 0x08

WMIREG_DICT = {0x01:"Expensive", 0x02:"Method", 0x04:"String", 0x08:"Event"}

class WdgObject:
    def __init__(self, guidStr = "", ObjectId = "", NotificationValue = 0, Reserved = 0, InstanceCount = 0, Flags = 0):
        self.guid = uuid.UUID(int=0)
        self.guid_str = guidStr
        self.ObjectId = ObjectId
        self.NotificationValue = NotificationValue
        self.Reserved = Reserved
        self.InstanceCount = InstanceCount
        self.Flags = Flags
    def SetGuidStr(self, guidStr):
        self.guid_str = guidStr
        self.guid = uuid.UUID(self.guid_str)
    def SetGuid(self, guid):
        self.guid = guid
    def SetObjectId(self, ObjectId):
        self.ObjectId = ObjectId
    def SetNotificationValue(self, NotificationValue):
        self.NotificationValue = NotificationValue
    def SetReserved(self, Reserved):
        self.Reserved = Reserved
    def SetInstanceCount(self, InstanceCount):
        self.InstanceCount = InstanceCount
    def SetFlags(self, Flags):
        self.Flags = Flags

def show_help():
    print("\nACPI WMI WDG buffer decoder\n")
    print("Usage:\n")
    print("  python wdgdump.py wdg.txt\n")
    print("  Paste _WDG content to wdg.txt from ACPI DSDT, make it look like:\n")
    print("        Name (_WDG, Buffer (0x3C)")
    print("        {")
    print("            --- Start ---")
    print("            /* 0000 */  0x34, 0xF0, 0xB7, 0x5F, 0x63, 0x2C, 0xE9, 0x45,  // 4.._c,.E")
    print("            /* 0008 */  0xBE, 0x91, 0x3D, 0x44, 0xE2, 0xC7, 0x07, 0xE4,  // ..=D....")
    print("            /* 0010 */  0x50, 0x56, 0x01, 0x02, 0x79, 0x42, 0xF2, 0x95,  // PV..yB..")
    print("            /* 0018 */  0x7B, 0x4D, 0x34, 0x43, 0x93, 0x87, 0xAC, 0xCD,  // {M4C....")
    print("            /* 0020 */  0xC6, 0x7E, 0xF6, 0x1C, 0x81, 0x00, 0x01, 0x08,  // .~......")
    print("            /* 0028 */  0x21, 0x12, 0x90, 0x05, 0x66, 0xD5, 0xD1, 0x11,  // !...f...")
    print("            /* 0030 */  0xB2, 0xF0, 0x00, 0xA0, 0xC9, 0x06, 0x29, 0x10,  // ......).")
    print("            /* 0038 */  0x5A, 0x5A, 0x01, 0x00                           // ZZ..")
    print("            --- End ---")
    print("        })")

def wdg_format(raw):
    buf = ""
    for line in raw:
        # Strip white space and line ending
        new = re.sub(r'\s', '', line)
        # Strip commented offset and decoded ASCII char
        new = re.sub(r'^/\*.*\*/(.*)//.*$', r'\1', new, flags=re.IGNORECASE)
        # Append to same buffer
        buf+=new
    data = buf.split(',')
    return data

def wdg_dump_entry(wdgObj):
    print("\nGUID: %s" %(wdgObj.guid_str))
    if (wdgObj.Flags & WMIACPI_REGFLAG_METHOD):
        print("  WMI Method")
        print("    ObjectId: %s" %(wdgObj.ObjectId))
    elif (wdgObj.Flags & WMIACPI_REGFLAG_EVENT):
        print("  WMI Event")
        print("    NotificationValue: 0x%x" %(wdgObj.NotificationValue))
        print("    Reserved: 0x%x" %(wdgObj.Reserved))
    else:
        print("  WMI Object")
        print("    ObjectId: %s" %(wdgObj.ObjectId))
    print("    InstanceCount: 0x%x" %(wdgObj.InstanceCount))

    flagList = [item[1] for item in WMIREG_DICT.items() if wdgObj.Flags & item[0]]
    flagStr = ""
    if (len(flagList)):
        flagStr = " ".join([item[1] for item in WMIREG_DICT.items() if wdgObj.Flags & item[0]])
        flagStr = ('(' + flagStr + ')')

    print("    Flags: 0x%02x %s\n" %(wdgObj.Flags, flagStr))

def wdg_decode(data):
    # According to MSDN, every 20 bytes represents a mapping
    # https://docs.microsoft.com/en-us/previous-versions/windows/hardware/design/dn614028(v=vs.85)
    #typedef struct
    #{
    #    GUID guid;             // GUID that names data block
    #    union
    #    {
    #        CHAR ObjectId[2];  // 2-character ACPI ID  (Data Blocks and Methods)
    #        struct
    #        {
    #            UCHAR NotificationValue;  // Byte value passed by event handler control method
    #            UCHAR Reserved[1];
    #        } NotifyId;
    #    }
    #    USHORT InstanceCount;  // Number of separate instances of data block
    #    USHORT Flags;          // Flags
    #};
    #define WMIACPI_REGFLAG_EXPENSIVE   0x1
    #define WMIACPI_REGFLAG_METHOD      0x2
    #define WMIACPI_REGFLAG_STRING      0x04
    #define WMIACPI_REGFLAG_EVENT       0x08
    for idx in range(len(data) // WDG_ENTRY_SIZE):
        # Use WdgObject for better processing in future
        entry = WdgObject()

        # Compose GUID based on the define and string format
        # {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
        # typedef struct _GUID {
        #     unsigned long  Data1;
        #     unsigned short Data2;
        #     unsigned short Data3;
        #     unsigned char  Data4[8];
        # } GUID;
        guid_data1 = ""
        for i in range(4):
            guid_data1 = re.sub(r'0x', '', data[idx * WDG_ENTRY_SIZE + i], flags=re.IGNORECASE) + guid_data1
        guid_data2 = ""
        for i in range(2):
            guid_data2 = re.sub(r'0x', '', data[idx * WDG_ENTRY_SIZE + 4 + i], flags=re.IGNORECASE) + guid_data2
        guid_data3 = ""
        for i in range(2):
            guid_data3 = re.sub(r'0x', '', data[idx * WDG_ENTRY_SIZE + 6 + i], flags=re.IGNORECASE) + guid_data3
        guid_data4_1 = ""
        for i in range(2):
            guid_data4_1 += re.sub(r'0x', '', data[idx * WDG_ENTRY_SIZE + 8 + i], flags=re.IGNORECASE)
        guid_data4_2 = ""
        for i in range(6):
            guid_data4_2 += re.sub(r'0x', '', data[idx * WDG_ENTRY_SIZE + 10 + i], flags=re.IGNORECASE)
        entry.SetGuidStr(guid_data1 + '-' + guid_data2 + '-' + guid_data3 + '-' + guid_data4_1 + '-' + guid_data4_2)

        # Get InstanceCount
        entry.SetInstanceCount(int(data[idx * WDG_ENTRY_SIZE + 18], 16))

        # Get Flags
        entry.SetFlags(int(data[idx * WDG_ENTRY_SIZE + 19], 16))

        # Set NotifyId if event, set ObjectId if others
        if (entry.Flags & WMIACPI_REGFLAG_EVENT):
            entry.SetNotificationValue(int(data[idx * WDG_ENTRY_SIZE + 16], 16))
            entry.SetReserved(int(data[idx * WDG_ENTRY_SIZE + 17], 16))
        else:
            entry.SetObjectId(chr(int(data[idx * WDG_ENTRY_SIZE + 16], 16)) + chr(int(data[idx * 20 + 17], 16)))

        wdg_dump_entry(entry)

    if (len(data) % WDG_ENTRY_SIZE != 0):
        print("Still have %d byte(s) unprocessed, corrupted WDG?" %(len(data) % WDG_ENTRY_SIZE))

def main():
    if(len(sys.argv) == 2):
        if(os.path.exists(sys.argv[1])):
            raw = ""
            with open(sys.argv[1], 'r') as wdgbuf:
                wdg_decode(wdg_format(wdgbuf.readlines()))
        else:
            print("Can't open %s" %(sys.argv[1]))
    else:
        show_help()


if __name__== "__main__":
    main()