from decdat.constants import Flag
from decdat.dat import Dat
from decdat.decompiler import get_instance_code

dat = Dat("E:\\Games\\Steam\\steamapps\\common\\TheChroniclesOfMyrtana\\_work\\tools\\VDFS\\_WORK\\DATA\\SCRIPTS\\_COMPILED\\GOTHIC.DAT", encoding="windows-1251")

for sym in dat.symbols:
    if sym.is_instance and sym.has_flag(Flag.CONST):
        print(get_instance_code(sym))