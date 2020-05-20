# WMI WDG Dump
Dump Data Block GUID Mapping control method for WMI.

## Usage:

Get the _WDG buffer from ACPI DSDT and save to a text file:

        Name (_WDG, Buffer (0x3C)
        {
            --- Start ---
            /* 0000 */  0x34, 0xF0, 0xB7, 0x5F, 0x63, 0x2C, 0xE9, 0x45,  // 4.._c,.E
            /* 0008 */  0xBE, 0x91, 0x3D, 0x44, 0xE2, 0xC7, 0x07, 0xE4,  // ..=D....
            /* 0010 */  0x50, 0x56, 0x01, 0x02, 0x79, 0x42, 0xF2, 0x95,  // PV..yB..
            /* 0018 */  0x7B, 0x4D, 0x34, 0x43, 0x93, 0x87, 0xAC, 0xCD,  // {M4C....
            /* 0020 */  0xC6, 0x7E, 0xF6, 0x1C, 0x81, 0x00, 0x01, 0x08,  // .~......
            /* 0028 */  0x21, 0x12, 0x90, 0x05, 0x66, 0xD5, 0xD1, 0x11,  // !...f...
            /* 0030 */  0xB2, 0xF0, 0x00, 0xA0, 0xC9, 0x06, 0x29, 0x10,  // ......).
            /* 0038 */  0x5A, 0x5A, 0x01, 0x00                           // ZZ..
            --- End ---
        })

Then run "python wdgdump.py wdg.txt", output looks like:

```bash
python wdgdump.py wdg.asl

GUID: 5FB7F034-2C63-45E9-BE91-3D44E2C707E4
  WMI Method
    ObjectId: PV
    InstanceCount: 0x1
    Flags: 0x02 (Method)


GUID: 95F24279-4D7B-4334-9387-ACCDC67EF61C
  WMI Event
    NotificationValue: 0x81
    Reserved: 0x0
    InstanceCount: 0x1
    Flags: 0x08 (Event)


GUID: 05901221-D566-11D1-B2F0-00A0C9062910
  WMI Object
    ObjectId: ZZ
    InstanceCount: 0x1
    Flags: 0x00
```